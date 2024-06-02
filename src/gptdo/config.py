import json
import os
from io import StringIO
from dataclasses import dataclass, asdict

@dataclass
class Config:
  default_model: str = 'gpt-3.5-turbo'

  openai_api_key: str = ''
  claude_api_key: str = ''

  local_uri: str = 'http://localhost:8000/v1'
  local_api_key: str = ''

  temperature: float = 0.4

  # Always run in yolo mode
  i_like_to_live_dangerously: bool = False


  @staticmethod
  def load_config(config_file: str) -> "Config":
    with open(config_file, 'r') as f:
      return Config.from_dict(json.load(f))


  @classmethod
  def from_dict(cls, d: dict) -> "Config":
    return cls(
      default_model = d.get('default_model', 'gpt-3.5-turbo'),
      openai_api_key = d.get('openai_api_key', ''),
      claude_api_key = d.get('claude_api_key', ''),
      local_uri = d.get('local_uri', 'http://localhost:8000/v1'),
      local_api_key = d.get('local_api_key', ''),
      temperature = d.get('temperature', 0.4),
      i_like_to_live_dangerously = d.get('i_like_to_live_dangerously', False),
    )


  def save_config(self, config_file: str):
    # There are cases where the config location is read-only. Swallow the exception
    try:
      os.makedirs(os.path.dirname(config_file), exist_ok=True)
      with open(config_file, 'w') as f:
        json.dump(asdict(self), f, indent=4)
    except Exception as e:
      pass
