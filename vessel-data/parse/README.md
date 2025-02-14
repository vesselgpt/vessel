# Vessel Parse

## Overview

Vessel Parse is a specialized data processing toolkit. It leverages Visual Language Models and Table Transformers to handle document analysis, information extraction, and data preprocessing tasks. This module is a core component of the Vessel ecosystem - see the main [Vessel documentation](https://github.com/vesselgpt/vessel) for more details.

## Quick Start

Clone the repository and install locally:
```bash
git clone https://github.com/vesselgpt/vessel.git
cd vessel/vessel-data/parse
pip install -e .
```

## Core Features

### Document Analysis with Vision-Language Models 

The library supports multiple inference backends including MLX, local GPU, and Hugging Face Cloud. Here's a basic example:

```python
from vessel_parse.vllm.inference_factory import InferenceFactory
from vessel_parse.extractors.vllm_extractor import VLLMExtractor

# Initialize extractor
extractor = VLLMExtractor()

# Configure your inference backend
inference_config = {
    "method": "mlx",  # Options: 'mlx', 'huggingface', 'local_gpu'
    "model_name": "mlx-community/Qwen2-VL-72B-Instruct-4bit",
}

# Set up inference pipeline
factory = InferenceFactory(inference_config)
inference_engine = factory.get_inference_instance()

# Prepare document for analysis
documents = [{
    "file_path": "path/to/your/document.jpg",
    "text_input": "extract data in JSON format"
}]

# Process documents
results, page_count = extractor.run_inference(
    inference_engine, 
    documents,
    tables_only=False,
    crop_size=80,
    debug=True
)

# View results
for idx, result in enumerate(results):
    print(f"Page {idx + 1} Results:", result)
```

Key Parameters:
- `tables_only`: Set to True to focus only on table extraction
- `crop_size`: Remove N pixels from document edges (useful for cleaning scanned documents)
- `mode="static"`: Test pipeline without actual LLM processing

For Hugging Face cloud deployment, use this configuration:

```python
hf_config = {
    "method": "huggingface",
    "hf_space": "vesselgpt/vessel-qwen2-vl-7b",
    "hf_token": os.getenv('HF_TOKEN'),
}
```

Note: Access to `vesselgpt/vessel-qwen2-vl-7b` requires setting up your own Hugging Face space using the [provided infrastructure code](https://github.com/vesselgpt/vessel/tree/main/vessel-data/parse/vessel_parse/vllm/infra/qwen2_vl_7b).

### Document Processing Utilities

#### PDF Processing
```python
from vessel_parse.extractor.pdf_optimizer import PDFOptimizer

optimizer = PDFOptimizer()
pages, output_files, temp_directory = optimizer.split_pdf_to_pages(
    pdf_path,
    debug_directory,  # Optional: for troubleshooting
    convert_to_images=False  # Keep as PDFs by default
)
```

#### Image Processing
```python
from vessel_parse.helpers.image_optimizer import ImageOptimizer

img_processor = ImageOptimizer()
processed_image = img_processor.crop_image_borders(
    image_path,
    temp_directory,
    debug_directory,  # Optional
    border_crop_size
)
```

## Licensing Options

Vessel Parse offers flexible licensing to accommodate different needs:

- **Open Source**: Available under GPL 3.0, ensuring code remains open and shareable
- **Free Commercial Use**: Available for organizations with annual revenue under $5M USD
- **Enterprise Licensing**: Custom commercial licenses available for larger organizations or those needing proprietary integration
