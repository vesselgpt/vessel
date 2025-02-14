# OCR Module for Vessel

## Overview

This repository contains the Optical Character Recognition (OCR) component of the Vessel project. For comprehensive information about Vessel, please refer to our [main documentation](https://github.com/vesselgpt/vessel).

## Development Setup

### Python Environment Configuration

This module requires Python 3.10.4. We recommend using `pyenv` for Python version management.

#### Setting up pyenv

For macOS users:
```bash
brew update && brew install pyenv
```

For Linux users, please follow the [pyenv installation guide](https://github.com/pyenv/pyenv#installation).

#### Configure Python Version

```bash
# Install Python 3.10.4
pyenv install 3.10.4

# Set as your default Python version
pyenv global 3.10.4

# Verify installation
python --version  # Should display Python 3.10.4
```

If you encounter any issues with pyenv recognition, add these lines to your shell configuration file (~/.zshrc, ~/.bashrc, etc.):
```bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

### Project Setup

1. Create a virtual environment:
```bash
cd vessel-data/ocr
python -m venv .env_ocr
```

2. Activate the environment:
```bash
source .env_ocr/bin/activate  # Unix/macOS
# or
.env_ocr\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install system dependencies:

For macOS:
```bash
brew install poppler
```

For Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils libpoppler-cpp-dev
pip install python-poppler
```

## Running the OCR Service

1. Navigate to the OCR module directory
2. Start the API server:
```bash
python api.py
```

Note: The default port is 8001. You can modify this in api.py if needed.

## Testing the OCR Service

Here's a sample API request to test the OCR functionality:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8001/api/v1/vessel-ocr/inference' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=' \
  -F 'image_url=https://raw.githubusercontent.com/vesselgpt/vessel/main/vessel-ml/llm/data/inout-20211211_001.jpg'
```

## Licensing Information

### Open Source License
This project is available under the GPL 3.0 license, ensuring that modifications remain open source.

### Free Commercial Use
- Available for free commercial use to organizations with annual revenue under $5M USD
- No registration or special license required for qualifying organizations

### Commercial Licensing
For organizations that:
- Have annual revenue exceeding $5M USD
- Need proprietary license terms
- Require integration with closed-source software
- Need custom development or support