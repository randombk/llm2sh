#!/usr/bin/env python3

import getpass
import os
from typing import List, Optional
import textwrap

from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from ..config import Config
from ..util import unquote_all, eprint

class DefaultDispatcher:
  """
  Default fallback dispatcher for llm2sh, used when there isn't a more specific
  dispatcher available. This dispatcher can be extended to customize the
  system prompt or to use a different API.
  """

  def __init__(self, uri: str, key: str, model: str, config: Config,
               temperature: float, verbose: bool = False,
               additional_headers: Optional[dict[str, str]] = None):
    self.uri = uri
    self.key = key
    self.model = model
    self.verbose = verbose
    self.config = config
    self.temperature = temperature
    self.additional_headers = additional_headers


  def dispatch(self, request_str: str):
    """
    Sends the request to the LLM, returning the series of commands to run.
    """

    system_prompt = self._get_system_prompt(request_str)
    if self.verbose:
      eprint(f"[DEBUG]: System prompt:\n{system_prompt}")

    client = OpenAI(
      base_url=None if self.uri == '' else self.uri,
      api_key='NA' if self.key == '' else self.key,
    )
    message = client.chat.completions.create(
        model=self.model,
        temperature=self.temperature,
        extra_headers=self.additional_headers,
        messages=[
          { "role": "system", "content": system_prompt },
          { "role": "user", "content": request_str }
        ],
    )

    response = message.choices[0].message.content
    if self.verbose:
      eprint(f"[DEBUG]: Response:\n{response}")

    return self._clean_output(response.split('\n'))


  def _max_context_length(self) -> int:
    """
    Returns the input maximum length of the LLM model.
    """
    return 4096  # Assume the worst case scenario (i.e. gpt-3.5-turbo-instruct supports a 4K window)


  def _max_system_prompt_length(self, request_str: str) -> int:
    """
    Returns the input maximum length of the system prompt.
    Reserve half the context length for the output, and the remaining amount (less the request length) as
    system prompt length.

    Assume each token is ~4 characters long.
    """
    return (self._max_context_length() // 2) - (len(request_str) // 4) + 1


  def _whoami(self) -> str:
    """
    Returns the current user.
    """
    return getpass.getuser()


  def _cwd(self) -> str:
    """
    Returns the current working directory.
    """
    return os.getcwd()


  def _ls(self, summarize_factor: int) -> List[str]:
    """
    Returns the contents of the current working directory.
    The `summarize_factor` is used to suppress overly long directory listings.
    """
    items = os.listdir()
    return items[:int(len(items) * summarize_factor)]


  def _additional_context(self, summarize_factor: int) -> str:
    """
    Returns additional situational context to be included in the system prompt.
    """

    lines = []

    # If lsb_release is available, include the OS version
    if os.path.exists('/usr/bin/lsb_release'):
      lines.append('The OS is:')
      lines.append(os.popen('/usr/bin/lsb_release -d').read().strip())

    return '\n'.join(lines)


  def _available_env(self, summarize_factor: int) -> List[str]:
    """
    Returns the list of available environment variables.
    The `summarize_factor` is used to limit the number of results.
    This method also omits some common environment variables that are usually not useful.
    """
    items = set(os.environ.keys())

    # Remove common junk environment variables by name. Additional ones are filtered out via patterns.
    omit = {
      # Terminal color settings
      'color_prompt', 'force_color_prompt',
      'COLORTERM', 'LSCOLORS', 'LS_COLORS', 'LS_OPTIONS', 'CLICOLOR',

      # GUI & Auth implementation details
      'SESSION_MANAGER', 'TERM_PROGRAM_VERSION', 'VDPAU_DRIVER',
      'SSH_AUTH_SOCK', 'SYSTEMD_EXEC_PID', 'XAUTHORITY',

      # Misc others
      'MOTD_SHOWN', 'PYTHONSTARTUP', 'INVOCATION_ID'
    }
    items = items - omit
    items = [
      i for i in items
      if (
        # Inserted when running in a VSCode terminal
        (not i.startswith('VSCODE_'))

        # Color codes
        and (not i.startswith('COLOR_'))

        # Misc others
        and (not i.startswith('XDG_'))
        and (not i.startswith('DBUS_'))
        and (not i.startswith('GJS_'))
        and (not i.startswith('GDM_'))
        and (not i.startswith('GIO_'))
      )
    ]

    # Always keep a minimum of 20 items - there's more opportunity to remove items from the
    # directory contents listing than the environment variables listing.
    take_n = max(int(len(items) * summarize_factor), 20)
    return items[:take_n]


  def _get_system_prompt(self, request_str: str) -> str:
    """
    Returns the system prompt.
    """
    max_length = self._max_system_prompt_length(request_str)
    summarize_factor = 1.0  # Percentage of the env and directory information to include in the prompt

    def get_prompt(factor: float) -> str:
      nl = '\n'
      return textwrap.dedent(f"""
        You are an AI helping the user perform tasks in a Bash shell. The user will give you a request,
        and you will generate one or more shell commands to fulfill that request. You can use any shell constructs,
        including pipes, redirection, and loops. You can also use any commands available in the shell environment.
        The shell is configured with `set -e`, so generate appropriate error handling for commands that are allowed
        to fail.

        The user is currently logged in as `{self._whoami()}` and the current working directory is `{self._cwd()}`.

        The current directory contains the following files: \n{nl.join([f"         - {i}" for i in self._ls(factor)])}

        You can refer to the following environment variables: \n{nl.join([f"         - {i}" for i in self._available_env(factor)])}

        \n{self._additional_context(factor)}

        Make sure you output valid shell commands. Everything you output must be ready to copy+paste directly into a terminal.
        This means:
          * Pay special attention to quoting and escaping.
          * Do not wrap the response in quotes, backticks, markdown, etc.
          * If you want to provide additional information or commentary, please
            include it in a shell comment (i.e. `#`) or use `echo "..."`.

        For more complex tasks, you can use `cat` to write a Python script to a file and then execute it.

        YOU MUST RESPOND WITH ONLY VALID SHELL COMMANDS. DO NOT INCLUDE ANYTHING ELSE IN YOUR RESPONSE.
      """)

    prompt = get_prompt(summarize_factor)
    while len(prompt) // 4 > max_length:
      # Reduce the amount of information in the prompt
      summarize_factor = summarize_factor * 0.9 * (max_length / (len(prompt) // 4))
      prompt = get_prompt(summarize_factor)

    return prompt


  def _clean_output(self, output: List[str]) -> List[str]:
    """
    Cleans the output by removing any leading or trailing whitespace and other common mistakes.
    """

    # Remove trailing whitespace. Keep leading whitespace in case the LLM is trying to
    # generate a Python script or something similar.
    cleaned = [i.rstrip() for i in output]

    cleaned = [
      # Remove quotes around the commands
      unquote_all(i, ['`', '"', "'"])

      for i in cleaned

      if not (
        # Heuristic: Remove empty lines and code blocks
        (i == '')
        or (i == '```')
        or (i == '```bash')
        or (i == '```shell')
        or (i == '```sh')

        # Heuristic: Remove lines where the LLM is trying to be conversational
        or (i.startswith('Sure'))  # i.e. "Sure! Here is..."
        or (i.startswith('Here'))  # i.e. "Here is..."
      )
    ]

    return cleaned
