# llm2sh

`llm2sh` is a command-line utility that leverages Large Language Models (LLMs) to translate plain-language requests
into shell commands. It provides a convenient way to interact with your system using natural language.

## Features

- Translates plain language requests into corresponding shell commands
- Supports multiple LLMs for command generation
- Customizable configuration file
- YOLO mode for running commands without confirmation
- Easily extensible with new LLMs and system prompts
- Verbose mode for debugging

## Installation

```bash
pip install llm2sh
```

## Usage

`llm2sh` uses OpenAI, Claude, and other LLM APIs to generate shell commands based on the user's requests.
For OpenAI, Claude, and Groq, you will need to have an API key to use this tool.

- OpenAI: You can sign up for an API key on the [OpenAI website](https://platform.openai.com/).
- Claude: You can sign up for an API key on the [Claude API Console](https://console.anthropic.com/dashboard).
- Groq: You can sign up for an API key on the [GroqCloud Console](https://console.groq.com/).

### Configuration

Running `llm2sh` for the first time will create a template configuration file at `~/.config/llm2sh/llm2sh.json`.
You can specify a different path using the `-c` or `--config` option.

Before using `llm2sh`, you need to set up the configuration file with your API keys and preferences.
You can also use the `OPENAI_API_KEY`, `CLAUDE_API_KEY`, and `GROQ_API_KEY` environment variables to specify the
API keys.

### Basic Usage

To use `llm2sh`, run the following command followed by your request:

```bash
llm2sh [options] <request>
```

**For example:**

1. Basic usage:

```bash
$ llm2sh "list all files in the current directory"

You are about to run the following commands:
  $ ls -a
Run the above commands? [y/N]
```

2. Use a specific model for command generation:

```bash
$ llm2sh -m gpt-3.5-turbo "find all Python files in the current directory, recursively"

You are about to run the following commands:
  $ find . -type f -name "*.py"
Run the above commands? [y/N]
```

3. `llm2sh` supports running multiple commands in sequence, and supports interactive commands like `sudo`:

```bash
llm2sh "install docker in rootless mode"

You are about to run the following commands:
  $ sudo newgrp docker
  $ sudo pacman -Sy docker-rootless-extras
  $ sudo usermod -aG docker "$USERNAME"
  $ dockerd-rootless-setuptool.sh install
Run the above commands? [y/N]
```

4. Run the generated command without confirmation:

```bash
llm2sh --force "delete all temporary files"
```

### Options

```text
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        specify config file, (Default: ~/.config/llm2sh/llm2sh.json)
  -d, --dry-run         do not run the generated command
  -l, --list-models     list available models
  -m MODEL, --model MODEL
                        specify which model to use
  -t TEMPERATURE, --temperature TEMPERATURE
                        use a custom sampling temperature
  -v, --verbose         print verbose debug information
  -f, --yolo, --force   run whatever GPT wants, without confirmation
```

## Supported Models

`llm2sh` currently supports the following LLMs for command generation:

| Model Name | Provider | Accuracy | Cost | Requirements | Notes |
|----------|----------|----------|----------|----------|----------|
| `local` | N/A | ¯\_(ツ)_/¯ | **FREE** | Local LLM Api Endpoint (i.e. llama.cpp) | |
| `gpt-4o` | OpenAI | 🧠🧠🧠 | 💲💲💲 | OpenAI API Key | Default model |
| `gpt-4-turbo` | OpenAI | 🧠🧠🧠 | 💲💲💲💲 | OpenAI API Key | |
| `gpt-3.5-turbo-instruct` | OpenAI | 🧠🧠 | 💲💲 | OpenAI API Key | |
| `claude-3-opus` | Claude | 🧠🧠🧠🧠 | 💲💲💲💲 | Claude API Key | Fairly slow (>10s) |
| `claude-3-sonnet` | Claude | 🧠🧠🧠 | 💲💲💲 | Claude API Key | Somewhat slow (~5s) |
| `claude-3-haiku` | Claude | 🧠 | 💲💲 | Claude API Key | |
| `groq-llama3-70b` | Groq | 🧠🧠🧠 | **FREE** *(with rate limits)* | Groq API Key | Blazing fast; recommended |
| `groq-llama3-8b` | Groq | 🧠🧠 | **FREE** *(with rate limits)* | Groq API Key | Blazing fast |
| `groq-mixtral-8x7b` | Groq | 🧠 | **FREE** *(with rate limits)* | Groq API Key | Blazing fast |
| `groq-gemma-7b` | Groq | 🧠 | **FREE** *(with rate limits)* | Groq API Key | Blazing fast |

*(Based on my subjective opinion and experience. Your mileage may vary.)*

## Roadmap

- ✅ Support multiple LLMs for command generation
- ⬜ User-customizable system prompts
- ⬜ Integrate with tool calling for more complex commands
- ⬜ More complex RAG for efficiently providing relevant context to the LLM
- ⬜ Better support for executing complex interactive commands
- ⬜ Interactive configuration & setup via the command line

## Privacy

`llm2sh` does not store any user data or command history, and it does not record or send any telemetry
by itself. However, the LLM APIs may collect and store the requests and responses for their own purposes.

To help LLMs generate better commands, `llm2sh` may send the following information as part of the LLM
prompt in addition to the user's request:

- Your operating system and version
- The current working directory
- Your username
- Names of files and directories in your current working directory
- Names of environment variables available in your shell. (Only the names/keys are sent, not the values).

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/randombk/llm2sh).

## License

This project is licensed under the [GPLv3](LICENSE).

## Disclaimer

`llm2sh` is an experimental tool that relies on LLMs for generating shell commands. While it can be helpful, it's important to review and understand the generated commands before executing them, especially when using the YOLO mode. The developers are not responsible for any damages or unintended consequences resulting from the use of this tool.

This project is not affiliated with OpenAI, Claude, or any other LLM provider or creator.
This project is not affiliated with my employer in any way. It is an independent project created for educational and research purposes.
