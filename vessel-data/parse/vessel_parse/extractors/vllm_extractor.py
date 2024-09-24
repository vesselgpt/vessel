from vessel_parse.vllm.inference_factory import InferenceFactory
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
import os


class VLLMExtractor(object):
    def __init__(self):
        pass

    def run_inference(self, model_inference_instance, input_data):
        result = model_inference_instance.inference(input_data)

        return result

if __name__ == "__main__":
    extractor = VLLMExtractor()

    # export HF_TOKEN="hf_"
    config = {
        "method": "huggingface",  # Could be 'huggingface' or 'local_gpu'
        "hf_space": "vesselgpt/vessel-qwen2-vl-7b",
        "hf_token": os.getenv('HF_TOKEN'),
        # Additional fields for local GPU inference
        # "device": "cuda", "model_path": "model.pth"
    }

    # Use the factory to get the correct instance
    factory = InferenceFactory(config)
    model_inference_instance = factory.get_inference_instance()

    input_data = [
        {
            "image": "/Users/dldiego1/Documents/work/epik/bankstatement/bonds_table.png",
            "text_input": "retrieve financial instruments data. return response in JSON format"
        }
    ]

    # Now you can run inference without knowing which implementation is used
    result = extractor.run_inference(model_inference_instance, input_data)
    print("Inference Result:", result)