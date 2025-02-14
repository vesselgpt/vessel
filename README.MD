# Vessel
<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![GitHub Stars](https://img.shields.io/github/stars/vesselgpt/vessel?style=for-the-badge&logo=github)](https://github.com/vesselgpt/vessel/stargazers)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-green.svg?style=for-the-badge&logo=gnu)](https://opensource.org/licenses/GPL-3.0)
</div>


Intelligent Document Analysis & Data Extraction Platform

<p align="center">
  <img width="300" height="300" src="https://github.com/vesselgpt/vessel/blob/main/vessel-ui/assets/vessel_logo_5.png">
</p>

## Introduction

Vessel is your bridge between unstructured documents and actionable data. Using advanced AI, it extracts meaningful information from any document type - from invoices to medical records, turning complex content into clean, structured outputs.

Built with flexibility in mind, Vessel lets you choose your preferred processing environment. Run locally with frameworks like vLLM, Ollama, PyTorch, or Apple MLX, or leverage cloud computing for enhanced performance. The heart of Vessel - its vision-language models - excel at understanding document context and delivering precise data extraction.

Connect Vessel to your existing systems through its robust API for seamless automation of document processing workflows.

![Vessel Architecture](https://github.com/vesselgpt/vessel/blob/main/vessel-ui/assets/vessel_architecture.jpeg)

### System Components

* **[Neural Core](https://github.com/vesselgpt/vessel/tree/main/vessel-ml/llm)** - Advanced ML pipeline orchestration
* **[Document Intelligence](https://github.com/vesselgpt/vessel/tree/main/vessel-data/parse)** - Smart document parsing with vision-language models
* **[Text Recognition](https://github.com/vesselgpt/vessel/tree/main/vessel-data/ocr)** - High-accuracy text extraction
* **[Control Center](https://github.com/vesselgpt/vessel/tree/main/vessel-ui/)** - Intuitive management interface

## Feature Showcase

### Banking Document Analysis

```json
{
  "bank": "Evergreen Credit Union",
  "address": "456 Pine Valley Road, Seattle, WA 98101",
  "account_holder": "Sarah M. Chen",
  "account_number": "9876543210987",
  "statement_date": "5/1/2024",
  "period_covered": "4/1/2024 - 4/30/2024",
  "account_summary": {
    "ending_balance": "$67,892.45",
    "deposits": "$12,450.67",
    "withdrawals": "$8,923.12"
  },
  "transactions": [
    {
      "date": "04/02",
      "description": "Salary - Quantum Technologies",
      "withdrawal": "",
      "deposit": "5,678.90",
      "balance": "64,647.23"
    }
    // Additional transactions omitted for brevity
  ],
  "valid": "true"
}
```

### Investment Analysis

```json
{
  "data": [
    {
      "instrument_name": "FIDELITY TOTAL MARKET INDEX FUND",
      "valuation": 245670
    },
    {
      "instrument_name": "SCHWAB EMERGING MARKETS EQUITY ETF",
      "valuation": 98450
    },
    {
      "instrument_name": "BLACKROCK SUSTAINABLE BOND FUND",
      "valuation": 167890
    }
    // Additional holdings omitted for brevity
  ],
  "valid": "true"
}
```

## Quick Setup

1. Configure Python environment with `pyenv`
2. Set up pipeline-specific virtual environments
3. Install required dependencies
4. Choose deployment method (CLI/API)
5. Begin processing with JSON templates

See detailed instructions below.

## Configuration

1. Environment Setup
   Refer to [setup documentation](environment_setup.md)

2. Deployment Options
   - Command Line: Execute via `vessel.sh`
   - Service: Deploy as API endpoint

3. Access Control
   Configure `PROTECTED_ACCESS` in config.yml

## Implementation Examples

### Local Deployment with MLX

```bash
./vessel.sh "[{"instrument_name":"str", "valuation":0}]" \
  --pipeline "vessel-parse" \
  --debug \
  --options mlx \
  --options mlx-community/Qwen2-VL-72B-Instruct-4bit \
  --file-path "/data/portfolio_summary.png"
```

### Cloud-Based Processing

```bash
./vessel.sh "[{"instrument_name":"str", "valuation":0}]" \
  --pipeline "vessel-parse" \
  --debug \
  --options huggingface \
  --options vesselgpt/vessel-qwen2-vl-7b \
  --file-path "/data/portfolio_summary.png"
```

### Multi-Document Processing

```bash
./vessel.sh "{"table": [{"description": "str", "latest_amount": 0, "previous_amount": 0}]}" \
  --pipeline "vessel-parse" \
  --debug \
  --options mlx \
  --options mlx-community/Qwen2-VL-72B-Instruct-4bit \
  --file-path "/data/quarterly_report.pdf" \
  --debug-dir "/data/"
```

## REST API

Launch Vessel as a REST service:

1. Start Service
```bash
python api.py [--port 8001]
```

2. View API Documentation
```
http://127.0.0.1:8000/api/v1/vessel-llm/docs
```

## License Options


Choose the right license for your needs:

- Community Edition: GPL 3.0 license
- Startup Edition: Free for organizations under $5M annual revenue
- Enterprise Edition: Custom licensing for larger organizations