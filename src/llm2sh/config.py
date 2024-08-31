import json
import os
from io import StringIO
from dataclasses import dataclass, asdict

@dataclass
class Config:
  default_model: str = 'groq-llama3-70b'

  openai_api_key: str = ''
  claude_api_key: str = ''
  groq_api_key: str = ''
  cerebras_api_key: str = ''

  local_uri: str = 'http://localhost:5000/v1'
  local_api_key: str = ''
  local_model_name: str = ''

  temperature: float = 0.2

  # Always run in yolo mode
  i_like_to_live_dangerously: bool = False


  @staticmethod
  def load_config(config_file: str) -> "Config":
    with open(config_file, 'r') as f:
      return Config.from_dict(json.load(f))


  @classmethod
  def from_dict(cls, d: dict) -> "Config":
    return cls(
      default_model = d.get('default_model', 'groq-llama3-70b'),
      openai_api_key = d.get('openai_api_key', ''),
      claude_api_key = d.get('claude_api_key', ''),
      groq_api_key = d.get('groq_api_key', ''),
      cerebras_api_key = d.get('cerebras_api_key', ''),
      local_uri = d.get('local_uri', 'http://localhost:5000/v1'),
      local_api_key = d.get('local_api_key', ''),
      temperature = d.get('temperature', 0.2),
      i_like_to_live_dangerously = d.get('i_like_to_live_dangerously', False),
    )


  @property
  def effective_openai_key(self) -> str:
    if len(self.openai_api_key) > 0:
      return self.openai_api_key
    elif len(os.environ.get('OPENAI_API_KEY', '')) > 0:
      return os.environ['OPENAI_API_KEY']
    else:
      return ''


  @property
  def effective_claude_key(self) -> str:
    if len(self.claude_api_key) > 0:
      return self.claude_api_key
    elif len(os.environ.get('ANTHROPIC_API_KEY', '')) > 0:
      return os.environ['ANTHROPIC_API_KEY']
    else:
      return ''


  @property
  def effective_groq_key(self) -> str:
    if len(self.groq_api_key) > 0:
      return self.groq_api_key
    elif len(os.environ.get('GROQ_API_KEY', '')) > 0:
      return os.environ['GROQ_API_KEY']
    else:
      return ''


  @property
  def effective_cerebras_key(self) -> str:
    if len(self.cerebras_api_key) > 0:
      return self.cerebras_api_key
    elif len(os.environ.get('CEREBRAS_API_KEY', '')) > 0:
      return os.environ['CEREBRAS_API_KEY']
    else:
      return ''


  def save_config(self, config_file: str):
    # There are cases where the config location is read-only. Swallow the exception
    try:
      os.makedirs(os.path.dirname(config_file), exist_ok=True)
      with open(config_file, 'w') as f:
        json.dump(asdict(self), f, indent=4)
    except Exception as e:
      pass
