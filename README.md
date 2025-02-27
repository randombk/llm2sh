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
- Cerebras: You can sign up for an API key on the [Cerebras Developer Platform](https://cloud.cerebras.ai/).
- OpenRouter: You can sign up for an API key on [OpenRouter](https://openrouter.ai/).

### Configuration

Running `llm2sh` for the first time will create a template configuration file at `~/.config/llm2sh/llm2sh.json`.
You can specify a different path using the `-c` or `--config` option.

Before using `llm2sh`, you need to set up the configuration file with your API keys and preferences.
You can also use the `OPENAI_API_KEY`, `CLAUDE_API_KEY`, `GROQ_API_KEY`, and `OPENROUTER_API_KEY` environment
variables to specify the API keys.

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
  -l, --list-providers  list available model providers
  -m MODEL, --model MODEL
                        specify which model to use
  -t TEMPERATURE, --temperature TEMPERATURE
                        use a custom sampling temperature
  -v, --verbose         print verbose debug information
  -f, --yolo, --force   run whatever GPT wants, without confirmation
```

## Supported Models

`llm2sh` supports any LLM endpoint that accepts the OpenAI or Claude APIs. There is a balancing act
between response time, cost, and accuracy that you must find. Some personal commentary:

* Groq and Cerebras are good for simple everyday tasks with near-instant response times and a
  free API, but struggle with more complex tasks.
* Anthropic and OpenAI non-reasoning models can handle a surprising number of complex tasks,
  but can be pricy and will take a few seconds before replying.
* Reasoning models provide amazing results, but take a long time to return a result. The
  current `llm2sh` UX does not do a great job of handling long thinking periods.

Notably:

* For models on OpenAI, Anthropic, Groq, and Cerebras, specify the model ID as
  `'<provider>/<model>'`. For example:
  * OpenAI `gpt-4o` => `'openai/gpt-4o'`
  * Anthropic `claude-3-7-sonnet-latest` => `'anthropic/claude-3-7-sonnet-latest'`
  * Groq `llama-3.1-8b-instant` => `'groq/llama-3.1-8b-instant'`
  * Cerebras `llama3.1-8b` => `'cerebras/llama3.1-8b'`
* Local models: set `default_model` to `'local'` and update the configuration to point
  at a local OpenAI API compatible LLM Api Endpoint (i.e. llama.cpp).
* OpenRouter can be used by setting model to `'openrouter/<model>'`. This can result in
  model IDs like `'openrouter/openai/gpt-4o'`, and that's alright.

**For backwards compatibility with <v0.4**, the following model names are given special treatment and
map to specific models:

 * `gpt-4o` => `openai/gpt-4o`
 * `gpt-4o-mini` => `openai/gpt-4o-mini`
 * `gpt-3.5-turbo-instruct` => `openai/gpt-3.5-turbo-instruct`
 * `gpt-4-turbo` => `openai/gpt-4-turbo`
 * `claude-3-5-sonnet` => `anthropic/claude-3-5-sonnet-20240620`
 * `claude-3-opus` => `anthropic/claude-3-opus-20240229`
 * `claude-3-sonnet` => `anthropic/claude-3-sonnet-20240229`
 * `claude-3-haiku` => `anthropic/claude-3-haiku-20240307`
 * `groq-llama3-8b` => `groq/llama3-8b-8192`
 * `groq-llama3-70b` => `groq/llama3-70b-8192`
 * `groq-mixtral-8x7b` => `groq/mixtral-8x7b-32768`
 * `groq-gemma-7b` => `groq/gemma-7b-it`
 * `cerebras-llama3-8b` => `cerebras/llama3.1-8b`
 * `cerebras-llama3-70b` => `cerebras/llama3.1-70b`

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

## Breaking Changes from pre-0.4

* The `local_model_name` configuration option is now removed. Specify names for local models via the model name.
  * Before: `model = 'local'` and `local_model_name = 'llama3.1-8b-q4'`
  * After: `model = 'local/llama3.1-8b-q4'`

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/randombk/llm2sh).

## License

This project is licensed under the [GPLv3](LICENSE).

## Disclaimer

`llm2sh` is an experimental tool that relies on LLMs for generating shell commands. While it can be helpful, it's important to review and understand the generated commands before executing them, especially when using the YOLO mode. The developers are not responsible for any damages or unintended consequences resulting from the use of this tool.

This project is not affiliated with OpenAI, Claude, or any other LLM provider or creator.
This project is not affiliated with my employer in any way. It is an independent project created for educational and research purposes.
