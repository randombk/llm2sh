#!/usr/bin/env python3

import argparse
import os
import subprocess

from typing import List, Optional, Dict, Set, Tuple

from .config import Config
from .util import ethrow, eprint
from .dispatchers.DefaultDispatcher import DefaultDispatcher
from .dispatchers.AnthropicDispatcher import AnthropicDispatcher

class Cli(object):
  def __init__(self):
    parser = argparse.ArgumentParser(
      description='Ask GPT to run a command',
      usage='llm2sh [options] <request>',
      add_help = True,
    )

    parser.add_argument('request', help = 'request for gpt', action='store', nargs='*')
    # parser.add_argument('--setup', help = 'configure llm2sh', action = 'store_true')
    parser.add_argument('-c', '--config', help = 'specify config file, (Default: ~/.config/llm2sh/llm2sh.json)',
                        action = 'store', default = '~/.config/llm2sh/llm2sh.json')
    parser.add_argument('-d', '--dry-run', help = 'do not run the generated command', action = 'store_true')
    parser.add_argument('-l', '--list-providers', help = 'list available model providers', action = 'store_true')
    parser.add_argument('-m', '--model', help = 'specify which model to use', action = 'store')
    parser.add_argument('-s', '--silent', help = 'don\'t ask bash to output each command before running it.', action = 'store_true')
    parser.add_argument('-t', '--temperature', help = 'use a custom sampling temperature', action = 'store')
    parser.add_argument('-v', '--verbose', help = 'print verbose debug information', action = 'store_true')
    parser.add_argument('-f', '--yolo', '--force', help = 'run whatever GPT wants, without confirmation', action = 'store_true')
    parser.add_argument('--setup', help = 'Open an editor to the configuration file', action = 'store_true')

    #
    # Load Config
    #
    self.args = parser.parse_args()
    config_file = os.path.expanduser(self.args.config)
    self.config = self.load_config(config_file)

    # open the config file in the user's preferred text editor
    if self.args.setup:
      if 'EDITOR' not in os.environ:
        eprint('No EDITOR set. Please set the EDITOR environment variable to your preferred text editor')
        return

      subprocess.run([os.environ['EDITOR'], config_file])
      return

    #
    # Load Models
    #
    self.provider_list = self.load_model_providers()
    self.providers = {i[0]: i for i in self.provider_list if i[1]}

    if self.args.list_providers:
      self.list_providers()
      return

    (self.selected_provider, self.selected_model) = self.parse_model_specifier(self.args.model or self.config.default_model)
    if self.selected_provider not in self.providers:
      eprint(f"Provider {self.selected_provider} not available! Configure {self.args.config} or use --list-providers to see available providers.")

      # Print additional information if no providers are available, i.e. on a fresh install
      # Don't consider local providers for this check
      if len([v for k, v in self.providers.items() if k != 'local']) == 0:
        eprint("\nNo providers are configured. Use `llm2sh --setup` to configure a provider.")
        eprint("For first time users, we recommend using Groq or Cerebras Llama3.1. Both are free and provide"
               " a good balance between latency and quality.")
        eprint("Sign up for an API key at https://console.groq.com/ or https://cerebras.ai/inference")

      return

    #
    # Run Request
    #
    if len(self.args.request) == 0:
      parser.print_help()
      return
    self.request_str = ' '.join(self.args.request)
    response = self.dispatch_request(self.request_str)
    self.run_request(response)


  def load_config(self, config_file: str) -> Config:
    if not os.path.exists(config_file):
      if self.args.verbose:
        eprint(f"[DEBUG] Config file {config_file} not found, creating a new one.")
      config = Config()
    else:
      config = Config.load_config(config_file)

    # Try to write the config back in case new fields were added.
    config.save_config(config_file)
    return config


  @staticmethod
  def parse_model_specifier(model_id: str) -> Tuple[str, str]:
    # Process backwards compat for pre-0.4 specifiers
    model_id = {
      'gpt-4o': 'openai/gpt-4o',
      'gpt-4o-mini': 'openai/gpt-4o-mini',
      'gpt-3.5-turbo-instruct': 'openai/gpt-3.5-turbo-instruct',
      'gpt-4-turbo': 'openai/gpt-4-turbo',
      'claude-3-5-sonnet': 'anthropic/claude-3-5-sonnet-20240620',
      'claude-3-opus': 'anthropic/claude-3-opus-20240229',
      'claude-3-sonnet': 'anthropic/claude-3-sonnet-20240229',
      'claude-3-haiku': 'anthropic/claude-3-haiku-20240307',
      'groq-llama3-8b': 'groq/llama3-8b-8192',
      'groq-llama3-70b': 'groq/llama3-70b-8192',
      'groq-mixtral-8x7b': 'groq/mixtral-8x7b-32768',
      'groq-gemma-7b': 'groq/gemma-7b-it',
      'cerebras-llama3-8b': 'cerebras/llama3.1-8b',
      'cerebras-llama3-70b': 'cerebras/llama3.1-70b',
    }.get(model_id, model_id)

    if '/' in model_id:
      return model_id.split('/', 1)
    else:
      return (model_id, '')

  def list_providers(self):
    print(f'Providers can be configured via {self.args.config}\n')

    max_just_name = max([len(module) for (module, _, _) in self.provider_list])
    max_just_avail = len('NOT AVAILABLE')

    print('Available model providers:')
    for (model, avail, help) in self.provider_list:
      print(
        model.ljust(max_just_name + 2) +
        ('OK' if avail else 'NOT AVAILABLE').rjust(max_just_avail) +
        " | "
        f"{help}"
      )


  def load_model_providers(self) -> List[Tuple[str, bool, str]]:
    openai_available = len(self.config.effective_openai_key) > 0
    openai_str = "Ready" if openai_available else f"Requires OpenAI API key"

    anthropic_available = len(self.config.effective_anthropic_key) > 0
    claude_str = "Ready" if anthropic_available else f"Requires Claude API key"

    groq_available = len(self.config.effective_groq_key) > 0
    groq_str = "Ready" if groq_available else f"Requires Groq API key"

    cerebras_available = len(self.config.effective_cerebras_key) > 0
    cerebras_str = "Ready" if cerebras_available else f"Requires Cerebras API key"

    openrouter_available = len(self.config.effective_openrouter_key) > 0
    openrouter_str = "Ready" if openrouter_available else f"Requires OpenRouter API key"

    gemini_available = len(self.config.effective_gemini_key) > 0
    gemini_str = "Ready" if gemini_available else f"Requires Gemini API key"

    local_available = len(self.config.local_uri) > 0
    local_str = f"Ready - {self.config.local_uri}" if local_available else f"Requires local LLM API URI"

    return [
      ('local', local_available, local_str),
      ('openai', openai_available, openai_str),
      ('anthropic', anthropic_available, claude_str),
      ('groq', groq_available, groq_str),
      ('cerebras', cerebras_available, cerebras_str),
      ('openrouter', openrouter_available, openrouter_str),
      ('gemini', gemini_available, gemini_str),
    ]


  def dispatch_request(self, request: str) -> List[str]:
    temperature = self.args.temperature or self.config.temperature

    # TOTO: Implement dispatcher selection based on the chosen model
    if self.selected_provider == 'openai':
      dispatcher = DefaultDispatcher(
        uri = '',  # Defaults to None, which uses the OpenAI API
        key = self.config.effective_openai_key,
        model = self.selected_model,
        config = self.config,
        temperature=temperature,
        verbose=self.args.verbose,
      )
    elif self.selected_provider == 'anthropic':
      dispatcher = AnthropicDispatcher(
        key = self.config.effective_anthropic_key,
        model = self.selected_model,
        config = self.config,
        temperature=temperature,
        verbose=self.args.verbose,
      )
    elif self.selected_provider == 'groq':
      dispatcher = DefaultDispatcher(
        uri = 'https://api.groq.com/openai/v1',
        key = self.config.effective_groq_key,
        model = self.selected_model,
        config = self.config,
        temperature=temperature,
        verbose=self.args.verbose,
      )
    elif self.selected_provider == 'cerebras':
      dispatcher = DefaultDispatcher(
        uri = 'https://api.cerebras.ai/v1',
        key = self.config.effective_cerebras_key,
        model = self.selected_model,
        config = self.config,
        temperature=temperature,
        verbose=self.args.verbose,
      )
    elif self.selected_provider == 'openrouter':
      dispatcher = DefaultDispatcher(
        uri = 'https://openrouter.ai/api/v1',
        key = self.config.effective_openrouter_key,
        model = self.selected_model,
        config = self.config,
        temperature=temperature,
        verbose=self.args.verbose,
        additional_headers={
          "HTTP-Referer": "https://github.com/randombk/llm2sh",
          "X-Title": "llm2sh",
        },
      )
    elif self.selected_provider == 'gemini':
      dispatcher = DefaultDispatcher(
        uri = 'https://generativelanguage.googleapis.com/v1beta/openai',
        key = self.config.effective_gemini_key,
        model = self.selected_model,
        config = self.config,
        temperature=temperature,
        verbose=self.args.verbose,
      )
    elif self.selected_provider == 'local':
      dispatcher = DefaultDispatcher(
        uri = self.config.local_uri,
        key = self.config.local_api_key,
        model = self.selected_model,
        config = self.config,
        temperature=temperature,
        verbose=self.args.verbose,
      )
    else:
      ethrow(f"Unknown model provider {self.selected_provider}")

    return dispatcher.dispatch(request)


  def run_request(self, response: List[str]):
    if not self.args.dry_run:
      print('You are about to run the following commands:')
    else:
      print('(Dry Run) The LLM suggested these commands:')

    for command in response:
      print(f'  $ {command}')

    if self.args.dry_run:
      return

    # Prompt the user for confirmation
    if (not self.args.yolo) and (not self.config.i_like_to_live_dangerously):
      print('Run the above commands? [y/N]')
      if input().lower() != 'y':
        print('Request canceled')
        return

    self.run_commands(response)


  def run_commands(self, commands: List[str]):
    # Create a Popen object with shell=True to run commands in a bash shell
    process = subprocess.Popen(
        ["bash"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        text=True,
        shell=True
    )

    # Configure the target shell - abort on errors
    process.stdin.write('set -e\n')
    if not self.args.silent:
      process.stdin.write('set -o xtrace\n')
    process.stdin.flush()

    # Send all the commands at once and terminate the input stream so
    # we don't hang on reading the output
    for command in commands:
      process.stdin.write(command + '\n')
      process.stdin.flush()
    process.stdin.close()

    # Read the output of the command
    while process.stdout.readable():
        output = process.stdout.readline()
        if not output:
            break
        print(output.rstrip())

    # Close the stdin and wait for the process to finish
    process.wait()
