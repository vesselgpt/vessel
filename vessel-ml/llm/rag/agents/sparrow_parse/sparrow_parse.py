from rag.agents.interface import Pipeline
from vessel_parse.vllm.inference_factory import InferenceFactory
from vessel_parse.extractors.vllm_extractor import VLLMExtractor
import timeit
import box
import yaml
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Any, List
import json
from .vessel_validator import Validator
import warnings
import os


warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class VesselParsePipeline(Pipeline):

    def __init__(self):
        pass

    def run_pipeline(self,
                     payload: str,
                     query_inputs: [str],
                     query_types: [str],
                     keywords: [str],
                     query: str,
                     file_path: str,
                     index_name: str,
                     options: List[str] = None,
                     group_by_rows: bool = True,
                     update_targets: bool = True,
                     debug: bool = False,
                     local: bool = True) -> Any:
        print(f"\nRunning pipeline with {payload}\n")

        # Import config vars
        with open('config.yml', 'r', encoding='utf8') as ymlfile:
            cfg = box.Box(yaml.safe_load(ymlfile))

        start = timeit.default_timer()

        query_all_data = False
        if query == "*":
            query_all_data = True
            query = None
        else:
            query, query_schema = self.invoke_pipeline_step(lambda: self.prepare_query_and_schema(query, debug),
                                                      "Preparing query and schema", local)

        llm_output = self.invoke_pipeline_step(lambda: self.execute_query(cfg, query_all_data, query, file_path, debug),
                                        "Executing query", local)

        validation_result = None
        if query_all_data is False:
            validation_result = self.invoke_pipeline_step(lambda: self.validate_result(llm_output, query_all_data, query_schema, debug),
                                                      "Validating result", local)

        end = timeit.default_timer()

        print(f"Time to retrieve answer: {end - start}")

        return validation_result if validation_result is not None else llm_output


    def prepare_query_and_schema(self, query, debug):
        is_query_valid = self.is_valid_json(query)
        if not is_query_valid:
            return "Invalid query. Please provide a valid JSON query."

        query_keys = self.get_json_keys_as_string(query)
        query_schema = query
        query = "retrieve " + query_keys

        query = query + ". return response in JSON format, by strictly following this JSON schema: " + query_schema
        if debug:
            print("Query:", query)

        return query, query_schema


    def execute_query(self, cfg, query_all_data, query, file_path, debug):
        extractor = VLLMExtractor()

        # export HF_TOKEN="hf_"
        config = {
            "method": cfg.VLLM_INFRA_SPARROW_PARSE,  # Could be 'huggingface' or 'local_gpu'
            "hf_space": cfg.VLLM_HF_SPACE_SPARROW_PARSE,
            "hf_token": os.getenv('HF_TOKEN')
        }

        # Use the factory to get the correct instance
        factory = InferenceFactory(config)
        model_inference_instance = factory.get_inference_instance()

        input_data = [
            {
                "image": file_path,
                "text_input": query
            }
        ]

        # Now you can run inference without knowing which implementation is used
        llm_output = extractor.run_inference(model_inference_instance, input_data, generic_query=query_all_data,
                                             debug=debug)

        return llm_output


    def validate_result(self, llm_output, query_all_data, query_schema, debug):
        validator = Validator(query_schema)

        validation_result = validator.validate_json_against_schema(llm_output, validator.generated_schema)
        if validation_result is not None:
            return validation_result
        else:
            if debug:
                print("LLM output is valid according to the schema.")


    def is_valid_json(self, json_string):
        try:
            json.loads(json_string)
            return True
        except json.JSONDecodeError:
            return False


    def get_json_keys_as_string(self, json_string):
        try:
            # Load the JSON string into a Python object
            json_data = json.loads(json_string)

            # If it's a list of dictionaries, collect keys in order
            if isinstance(json_data, list):
                keys = []
                for item in json_data:
                    if isinstance(item, dict):
                        for key in item:
                            if key not in keys:  # To avoid duplicates while preserving order
                                keys.append(key)
                return ', '.join(keys)

            # If it's a single dictionary
            elif isinstance(json_data, dict):
                return ', '.join(json_data.keys())

            else:
                return ''  # Not a valid JSON structure with keys

        except json.JSONDecodeError:
            print("Invalid JSON string.")
            return ''


    def invoke_pipeline_step(self, task_call, task_description, local):
        if local:
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=False,
            ) as progress:
                progress.add_task(description=task_description, total=None)
                ret = task_call()
        else:
            print(task_description)
            ret = task_call()

        return ret