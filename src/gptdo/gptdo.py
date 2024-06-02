#!/usr/bin/env python3

import argparse
import os
import subprocess

from typing import List, Optional, Dict, Set, Tuple

from .config import Config
from .util import eprint, ethrow
from .dispatchers.DefaultDispatcher import DefaultDispatcher

class GPTDo(object):
  def __init__(self):
    parser = argparse.ArgumentParser(
      description='Ask GPT to run a command',
      usage='gptdo [options] <request>',
      add_help = True,
    )

    parser.add_argument('request', help = 'request for gpt', action='store', nargs='*')
    # parser.add_argument('--setup', help = 'configure gptdo', action = 'store_true')
    parser.add_argument('-c', '--config', help = 'specify config file, (Default: ~/.config/gptdo/gptdo.json)',
                        action = 'store', default = '~/.config/gptdo/gptdo.json')
    parser.add_argument('-l', '--list-models', help = 'list available models', action = 'store_true')
    parser.add_argument('-m', '--model', help = 'specify which model to use', action = 'store')
    parser.add_argument('-v', '--verbose', help = 'print verbose debug information', action = 'store_true')
    parser.add_argument('-y', '--yolo', help = 'run whatever GPT wants, without confirmation', action = 'store_true')

    #
    # Load Config
    #
    self.args = parser.parse_args()

    # if self.args.setup:
    #   # self.setup()
    #   ethrow('[ERROR]: Setup not implemented')

    self.config = self.load_config(self.args.config)

    #
    # Load Models
    #
    self.model_list = self.load_models()
    self.models = {i[0]: i for i in self.model_list if i[1]}

    if self.args.list_models:
      self.list_models()
      return

    self.selected_model = self.args.model or self.config.default_model
    if self.selected_model not in self.models:
      ethrow(f"Model {self.selected_model} not available! Configure {self.args.config} or use --list-models to see available models.")

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
    config_file = os.path.expanduser(config_file)

    if not os.path.exists(config_file):
      if self.args.verbose:
        print(f"[DEBUG] Config file {config_file} not found, creating a new one.")
      config = Config()
    else:
      config = Config.load_config(config_file)

    # Try to write the config back in case new fields were added.
    config.save_config(config_file)
    return config


  def list_models(self):
    print('Available models:')
    print(f'Models can be configured via {self.args.config}\n')

    max_just_name = max([len(module) for (module, _, _, _) in self.model_list])
    max_just_avail = len('NOT AVAILABLE')

    for (model, avail, help, _) in self.model_list:
      print(
        model.ljust(max_just_name + 2) +
        ('OK' if avail else 'NOT AVAILABLE').rjust(max_just_avail) +
        " | "
        f"{help}"
      )


  def load_models(self) -> List[Tuple[str, bool, str, str]]:
    openai_available = len(self.config.openai_api_key) > 0
    openai_str = "Ready" if openai_available else f"Requires OpenAI API key"

    claude_available = len(self.config.claude_api_key) > 0
    claude_str = "Ready" if claude_available else f"Requires Claude API key"

    local_available = len(self.config.local_uri) > 0
    local_str = f"Ready - {self.config.local_uri}" if local_available else f"Requires local LLM API URI"

    return [
      ('local', local_available, local_str, 'LOCAL'),
      ('gpt-4o', openai_available, openai_str, 'OPENAI'),
      ('gpt-3.5-turbo-instruct', openai_available, openai_str, 'OPENAI'),
      ('gpt-4-turbo', openai_available, openai_str, 'OPENAI'),
      ('claude-3-opus', claude_available, claude_str, 'CLAUDE'),
      ('claude-3-sonnet', claude_available, claude_str, 'CLAUDE'),
      ('claude-3-haiku', claude_available, claude_str, 'CLAUDE'),
    ]


  def dispatch_request(self, request: str) -> List[str]:
    (model_id, _, _, model_type) = self.models[self.selected_model]

    # TOTO: Implement dispatcher selection based on the chosen model
    if model_type == 'OPENAI':
      dispatcher = DefaultDispatcher(
        uri = '',  # Defaults to None, which uses the OpenAI API
        key = self.config.openai_api_key,
        model = model_id,
        config = self.config,
        verbose=self.args.verbose,
      )
    elif model_type == 'CLAUDE':
      ethrow('Claude API not implemented yet')
    elif model_type == 'LOCAL':
      dispatcher = DefaultDispatcher(
        uri = self.config.local_uri,
        key = self.config.local_api_key,
        model = model_id,
        config = self.config,
        verbose=self.args.verbose,
      )

    return dispatcher.dispatch(request)


  def run_request(self, response: List[str]):
    if not self.args.yolo and not self.config.i_like_to_live_dangerously:
      # Prompt the user for confirmation
      print('You are about to run the following commands:')
      for command in response:
        print(f'  $ {command}')
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

    # Send all the commands at once and terminate the input stream so
    # we don't hang on reading the output
    for command in commands:
      escaped = "'" + "$ " + command.replace("'", "'\\''") + "'"
      process.stdin.write(f"echo {escaped}\n")
      process.stdin.write(command + '\n')
      process.stdin.flush()
    process.stdin.close()

    # Read the output of the command
    while process.stdout.readable():
        output = process.stdout.readline()
        if not output:
            break
        print(output.strip())

    # Close the stdin and wait for the process to finish
    process.wait()
