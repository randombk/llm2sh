# llmdo

`llmdo` is a Python application that leverages Large Language Models (LLMs) to translate English requests into shell commands. It provides a convenient way to interact with your system using natural language.

## Features

- Translates English requests into corresponding shell commands
- Supports multiple LLMs for command generation
- Customizable configuration file
- Verbose mode for debugging
- YOLO mode for running commands without confirmation

## Installation

```bash
pip install llmdo
```

## Usage

`llmdo` uses OpenAI, Claude, and local LLM APIs to generate shell commands based on the user's requests.
For OpenAI and Claude, you will need to have an API key to use this tool.

- OpenAI: You can sign up for an API key on the [OpenAI website](https://platform.openai.com/).
- Claude: You can sign up for an API key on the [Claude website](https://claude.ai/).

To use `llmdo`, run the following command followed by your request:

```bash
llmdo [options] <request>
```

### Options

- `-h`, `--help`: Show the help message and exit.
- `-c CONFIG`, `--config CONFIG`: Specify the path to the configuration file. Default is `~/.config/llmdo/llmdo.json`.
- `-l`, `--list-models`: List the available LLMs.
- `-m MODEL`, `--model MODEL`: Specify which LLM to use for command generation.
- `-v`, `--verbose`: Print verbose debug information.
- `-y`, `--yolo`: Run the generated command without confirmation.

### Examples

1. Translate a request to a shell command:

```bash
llmdo "list all files in the current directory"
```

2. Use a specific LLM for command generation:

```bash
llmdo -m gpt-3.5-turbo "find all Python files in the project"
```

3. Run the generated command without confirmation:

```bash
llmdo -y "delete all temporary files"
```

## Configuration

The configuration file for `llmdo` is located at `~/.config/llmdo/llmdo.json` by default. You can specify a different path using the `-c` or `--config` option.

The configuration file allows you to customize the behavior of `llmdo`, such as specifying the default LLM, setting API keys, and defining custom aliases.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/randombk/llmdo).

## License

This project is licensed under the [GPLv3](LICENSE).

## Disclaimer

`llmdo` is an experimental tool that relies on LLMs for generating shell commands. While it can be helpful, it's important to review and understand the generated commands before executing them, especially when using the YOLO mode. The developers are not responsible for any damages or unintended consequences resulting from the use of this tool.

This project is not affiliated with OpenAI, Claude, or my employer in any way. It is an independent project created for educational and research purposes.
