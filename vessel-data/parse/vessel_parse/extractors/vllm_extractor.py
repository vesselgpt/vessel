from vessel_parse.vllm.inference_factory import InferenceFactory
from vessel_parse.helpers.pdf_optimizer import PDFOptimizer
from rich import print
import os
import shutil


class VLLMExtractor(object):
    def __init__(self):
        pass

    def run_inference(self, model_inference_instance, input_data,
                      generic_query=False, debug_dir=None, debug=False, mode=None):
        # Modify input for generic queries
        if generic_query:
            input_data[0]["text_input"] = "retrieve document data. return response in JSON format"

        if debug:
            print("Input Data:", input_data)

        # Check if the input file is a PDF
        file_path = input_data[0]["file_path"]
        if self.is_pdf(file_path):
            return self._process_pdf(model_inference_instance, input_data, debug_dir, mode)

        # Default processing for non-PDF files
        input_data[0]["file_path"] = [file_path]
        results_array = model_inference_instance.inference(input_data)
        return results_array, 1


    def _process_pdf(self, model_inference_instance, input_data, debug_dir, mode):
        """Handles processing and inference for PDF files."""
        pdf_optimizer = PDFOptimizer()
        num_pages, output_files, temp_dir = pdf_optimizer.split_pdf_to_pages(input_data[0]["file_path"],
                                                                             debug_dir,
                                                                             True)
        # Update file paths for PDF pages
        input_data[0]["file_path"] = output_files

        # Run inference on PDF pages
        results_array = model_inference_instance.inference(input_data, mode)

        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        return results_array, num_pages

    @staticmethod
    def is_pdf(file_path):
        """Checks if a file is a PDF based on its extension."""
        return file_path.lower().endswith('.pdf')

if __name__ == "__main__":
    # run locally: python -m vessel_parse.extractors.vllm_extractor

    extractor = VLLMExtractor()

    # # export HF_TOKEN="hf_"
    # config = {
    #     "method": "mlx",  # Could be 'huggingface', 'mlx' or 'local_gpu'
    #     "model_name": "mlx-community/Qwen2-VL-72B-Instruct-4bit",
    #     # "hf_space": "vesselgpt/vessel-qwen2-vl-7b",
    #     # "hf_token": os.getenv('HF_TOKEN'),
    #     # Additional fields for local GPU inference
    #     # "device": "cuda", "model_path": "model.pth"
    # }
    #
    # # Use the factory to get the correct instance
    # factory = InferenceFactory(config)
    # model_inference_instance = factory.get_inference_instance()
    #
    # input_data = [
    #     {
    #         "file_path": "/Users/dldiego1/Work/vessel-git/vessel/vessel-ml/llm/data/oracle_10k_2014_q1_small.pdf",
    #         "text_input": "retrieve table, description, latest_amount, previous_amount. return response in JSON format, by strictly following this JSON schema: {\"table\": [{\"description\": \"str\", \"latest_amount\": 0, \"previous_amount\": 0}]}"
    #     }
    # ]
    #
    # # Now you can run inference without knowing which implementation is used
    # results_array, num_pages = extractor.run_inference(model_inference_instance, input_data, generic_query=False,
    #                                  debug_dir=None,
    #                                  debug=True,
    #                                  mode=None)
    #
    # for i, result in enumerate(results_array):
    #     print(f"Result for page {i + 1}:", result)
    # print(f"Number of pages: {num_pages}")