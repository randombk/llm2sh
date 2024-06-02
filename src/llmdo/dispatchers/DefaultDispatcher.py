#!/usr/bin/env python3

import getpass
import os
from typing import List
import textwrap

from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from ..config import Config


class DefaultDispatcher:
  """
  Default fallback dispatcher for llmdo, used when there isn't a more specific
  dispatcher available. This dispatcher can be extended to customize the
  system prompt or to use a different API.
  """

  def __init__(self, uri: str, key: str, model: str, config: Config, verbose: bool = False):
    self.uri = uri
    self.key = key
    self.model = model
    self.verbose = verbose
    self.config = config


  def dispatch(self, request_str: str):
    """
    Sends the request to the LLM, returning the series of commands to run.
    """

    system_prompt = self._get_system_prompt(request_str)
    if self.verbose:
      print(f"[DEBUG]: System prompt:\n{system_prompt}")

    client = OpenAI(
      base_url=None if self.uri == '' else self.uri,
      api_key='NA' if self.key == '' else self.key,
    )
    response = client.chat.completions.create(
        model=self.model,
        temperature=self.config.temperature,
        messages=[
          { "role": "system", "content": system_prompt },
          { "role": "user", "content": request_str }
        ],
    )

    return self._clean_output(response.choices[0].message.content.split('\n'))


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
    take_n = min(int(len(items) * summarize_factor), 20)
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
        You are an AI helping the user perform tasks in a POSIX-compliant shell. The user will give you a request,
        and you will generate one or more shell commands to fulfill that request. You can use any shell constructs,
        including pipes, redirection, and loops. You can also use any commands available in the shell environment.
        The shell is configured with `set -e`, so generate appropriate error handling for commands that are allowed
        to fail.

        The user is currently logged in as `{self._whoami()}` and the current working directory is `{self._cwd()}`.

        The current directory contains the following files: \n{nl.join([f"         - {i}" for i in self._ls(factor)])}

        You can refer to the following environment variables: \n{nl.join([f"         - {i}" for i in self._available_env(factor)])}

        YOU MUST RESPOND WITH ONLY VALID SHELL COMMANDS. DO NOT INCLUDE ANYTHING ELSE IN YOUR RESPONSE.
        Make sure you output valid shell commands, paying special attention to quoting and escaping.
        Do not wrap the response in quotes or backticks. If you want to provide additional information,
        please include it in a shell comment (i.e. `#`) or use `echo`.
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
    return [
      i.strip()
      for i in output
      if i.strip() != '' and i.strip() != '```'
    ]
