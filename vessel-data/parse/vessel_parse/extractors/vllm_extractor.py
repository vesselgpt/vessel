import json

from vessel_parse.vllm.inference_factory import InferenceFactory
from vessel_parse.helpers.pdf_optimizer import PDFOptimizer
from vessel_parse.processors.table_structure_processor import TableDetector
from rich import print
import os
import tempfile
import shutil


class VLLMExtractor(object):
    def __init__(self):
        pass

    def run_inference(self, model_inference_instance, input_data, tables_only=False,
                      generic_query=False, debug_dir=None, debug=False, mode=None):
        """
        Main entry point for processing input data using a model inference instance.
        Handles generic queries, PDFs, and table extraction.
        """
        if generic_query:
            input_data[0]["text_input"] = "retrieve document data. return response in JSON format"

        if debug:
            print("Input data:", input_data)

        file_path = input_data[0]["file_path"]
        if self.is_pdf(file_path):
            return self._process_pdf(model_inference_instance, input_data, tables_only, debug, debug_dir, mode)

        return self._process_non_pdf(model_inference_instance, input_data, tables_only, debug, debug_dir)


    def _process_pdf(self, model_inference_instance, input_data, tables_only, debug, debug_dir, mode):
        """
        Handles processing and inference for PDF files, including page splitting and optional table extraction.
        """
        pdf_optimizer = PDFOptimizer()
        num_pages, output_files, temp_dir = pdf_optimizer.split_pdf_to_pages(input_data[0]["file_path"],
                                                                             debug_dir, convert_to_images=True)

        results = self._process_pages(model_inference_instance, output_files, input_data, tables_only, debug, debug_dir)

        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        return results, num_pages


    def _process_non_pdf(self, model_inference_instance, input_data, tables_only, debug, debug_dir):
        """
        Handles processing and inference for non-PDF files, with optional table extraction.
        """
        file_path = input_data[0]["file_path"]
        if tables_only:
            return self._extract_tables(model_inference_instance, file_path, input_data, debug, debug_dir), 1
        else:
            input_data[0]["file_path"] = [file_path]
            results = model_inference_instance.inference(input_data)
            return results, 1

    def _process_pages(self, model_inference_instance, output_files, input_data, tables_only, debug, debug_dir):
        """
        Processes individual pages (PDF split) and handles table extraction or inference.

        Args:
            model_inference_instance: The model inference object.
            output_files: List of file paths for the split PDF pages.
            input_data: Input data for inference.
            tables_only: Whether to only process tables.
            debug: Debug flag for logging.
            debug_dir: Directory for saving debug information.

        Returns:
            List of results from the processing or inference.
        """
        results_array = []

        if tables_only:
            if debug:
                print(f"Processing {len(output_files)} pages for table extraction.")
            # Process each page individually for table extraction
            for i, file_path in enumerate(output_files):
                tables_result = self._extract_tables(
                    model_inference_instance, file_path, input_data, debug, debug_dir, page_index=i
                )
                # Since _extract_tables returns a list with one JSON string, unpack it
                results_array.extend(tables_result)  # Unpack the single JSON string
        else:
            if debug:
                print(f"Processing {len(output_files)} pages for inference at once.")
            # Pass all output files to the inference method for processing at once
            input_data[0]["file_path"] = output_files
            results = model_inference_instance.inference(input_data)
            results_array.extend(results)

        return results_array


    def _extract_tables(self, model_inference_instance, file_path, input_data, debug, debug_dir, page_index=None):
        """
        Detects and processes tables from an input file.
        """
        table_detector = TableDetector()
        cropped_tables = table_detector.detect_tables(file_path, local=False, debug_dir=debug_dir, debug=debug)
        results_array = []
        temp_dir = tempfile.mkdtemp()

        for i, table in enumerate(cropped_tables):
            table_index = f"page_{page_index + 1}_table_{i + 1}" if page_index is not None else f"table_{i + 1}"
            print(f"Processing {table_index} for document {file_path}")

            output_filename = os.path.join(temp_dir, f"{table_index}.jpg")
            table.save(output_filename, "JPEG")

            input_data[0]["file_path"] = [output_filename]
            result = self._run_model_inference(model_inference_instance, input_data)
            results_array.append(result)

        shutil.rmtree(temp_dir, ignore_errors=True)

        # Merge results_array elements into a single JSON structure
        merged_results = {"page_tables": results_array}

        # Format the merged results as a JSON string with indentation
        formatted_results = json.dumps(merged_results, indent=4)

        # Return the formatted JSON string wrapped in a list
        return [formatted_results]


    @staticmethod
    def _run_model_inference(model_inference_instance, input_data):
        """
        Runs model inference and handles JSON decoding.
        """
        result = model_inference_instance.inference(input_data)[0]
        try:
            return json.loads(result) if isinstance(result, str) else result
        except json.JSONDecodeError:
            return {"message": "Invalid JSON format in LLM output", "valid": "false"}


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
    #         "file_path": "/Users/dldiego1/Work/vessel-git/vessel/vessel-ml/llm/data/invoice_1.jpg",
    #         "text_input": "retrieve document data. return response in JSON format"
    #     }
    # ]
    #
    # # Now you can run inference without knowing which implementation is used
    # results_array, num_pages = extractor.run_inference(model_inference_instance, input_data, tables_only=True,
    #                                                    generic_query=False,
    #                                                    debug_dir="/Users/dldiego1/Work/vessel-git/vessel/vessel-ml/llm/data/",
    #                                                    debug=True,
    #                                                    mode=None)
    #
    # for i, result in enumerate(results_array):
    #     print(f"Result for page {i + 1}:", result)
    # print(f"Number of pages: {num_pages}")