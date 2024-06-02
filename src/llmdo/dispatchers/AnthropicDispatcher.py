#!/usr/bin/env python3

from typing import List

from anthropic import Anthropic

from .DefaultDispatcher import DefaultDispatcher
from ..config import Config


class AnthropicDispatcher(DefaultDispatcher):
  def __init__(self, key: str, model: str, config: Config, verbose: bool = False):
    super().__init__('', key, model, config, verbose)


  def dispatch(self, request_str: str):
    """
    Sends the request to the LLM, returning the series of commands to run.
    """

    system_prompt = self._get_system_prompt(request_str)
    if self.verbose:
      print(f"[DEBUG]: System prompt:\n{system_prompt}")

    client = Anthropic(api_key=self.key)
    message = client.messages.create(
        model=self.model,
        max_tokens=2000,
        temperature=self.config.temperature,
        system=system_prompt,
        messages=[
          { "role": "user", "content": request_str }
        ],
    )

    response = message.content[0].text
    if self.verbose:
      print(f"[DEBUG]: Response:\n{response}")

    return self._clean_output(response.split('\n'))


  def _max_context_length(self) -> int:
    """
    Returns the input maximum length of the LLM model.
    """
    return 16*1024  # Technically larger than this, but this is a reasonable upper bound
