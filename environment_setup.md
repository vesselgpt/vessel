**Python environment setup** 

*Setup Python Environment (Vessel is tested with Python 3.10.4) with `pyenv`:*

1. Install `pyenv`:

If you haven't already installed `pyenv`, you can do so using Homebrew with the following command:

```
brew update
brew install pyenv

```

2. Install the desired Python version:

With `pyenv` installed, you can now install a specific version of Python. For example, to install Python 3.10.4, you would use:

```
pyenv install 3.10.4
```

You can check available Python versions by running `pyenv install --list`.

3. Set the global Python version:

Once the installation is complete, you can set the desired Python version as the default (global) version on your system:

```
pyenv global 3.10.4
```

This command sets Python 3.10.4 as the default version for all shells.

4. Verify the change:

To ensure the change was successful, you can verify the current Python version by running:

```
python --version
```

If the output doesn’t reflect the change, you may need to restart your terminal or add `pyenv` to your shell's initialization script as follows:

5. Configure your shell's initialization script:

Add `pyenv` to your shell by adding the following lines to your `~/.bash_profile`, `~/.zprofile`, `~/.bashrc`, or `~/.zshrc` file:

```
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

After adding these lines, restart your terminal or source your profile script with `source ~/.bash_profile` (or the appropriate file for your shell).

**Create Virtual Environments to Run Vessel Agents**

1. Create virtual environments in `vessel-ml/llm` folder:

```
python -m venv .env_vessel_parse
python -m venv .env_instructor
```

`.env_vessel_parse` is used for `vessel-parse` agent. `.env_instructor` is used for LLM function calling with `fcall` agent and for `instructor` RAG agent.

2. Create virtual environment in `vessel-data/ocr` folder, only if you plan to run OCR service:

```
python -m venv .env_ocr
```

*Activate Virtual Environments and Install Dependencies*

Activate each environment and install its dependencies using the corresponding `requirements.txt` file.

For `vessel-parse` environment:

1. Activate the environment:

```
source .env_vessel_parse/bin/activate
```

2. Install dependencies:

```
pip install -r requirements_vessel_parse.txt
```

Repeat the same for `instructor` environments.
