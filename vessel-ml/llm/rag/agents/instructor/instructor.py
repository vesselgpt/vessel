from rag.agents.interface import Pipeline
from openai import OpenAI
import instructor
from vessel_parse.extractor.unstructured_processor import UnstructuredProcessor
from vessel_parse.extractor.markdown_processor import MarkdownProcessor
from vessel_parse.extractor.html_extractor import HTMLExtractor
from pydantic import create_model
from typing import List
from rich.progress import Progress, SpinnerColumn, TextColumn
import timeit
from rich import print
from typing import Any
import json
import box
import yaml
import warnings


warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# Import config vars
with open('config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))


class InstructorPipeline(Pipeline):
    def run_pipeline(self,
                     payload: str,
                     query_inputs: [str],
                     query_types: [str],
                     query: str,
                     file_path: str,
                     index_name: str,
                     options: List[str] = None,
                     debug: bool = False,
                     local: bool = True) -> Any:
        print(f"\nRunning pipeline with {payload}\n")

        # Import config vars
        with open('config.yml', 'r', encoding='utf8') as ymlfile:
            cfg = box.Box(yaml.safe_load(ymlfile))

        start = timeit.default_timer()

        strategy = cfg.STRATEGY_INSTRUCTOR
        model_name = cfg.MODEL_INSTRUCTOR

        answer = '{}'

        validate_options = self.validate_options(options)
        if validate_options:
            if options and "tables" in options:
                content, table_content = None, None
                if "html" in options:
                    processor = UnstructuredProcessor()
                    content, table_content = processor.extract_data(file_path, strategy, model_name,
                                                                    ['tables', 'html'], local, debug)
                elif "markdown" in options:
                    processor = MarkdownProcessor()
                    content, table_content = processor.extract_data(file_path, ['tables', 'markdown'], local, debug)

                query_inputs_form, query_types_form = self.filter_fields_query(query_inputs, query_types, "form")
                if debug:
                    print(f"Query form inputs: {query_inputs_form}")
                    print(f"Query form types: {query_types_form}")
                if len(query_inputs_form) > 0:
                    query_form = "retrieve " + ", ".join(query_inputs_form)
                    answer = self.execute(query_inputs_form, query_types_form, content, query_form, 'form',
                                          debug, local)

                # Convert the answer JSON string to a dictionary
                answer = json.loads(answer)

                if table_content is not None:
                    query_targets, query_targets_types = self.filter_fields_query(query_inputs, query_types, "table")
                    extractor = HTMLExtractor()
                    i = 0
                    for table in table_content:
                        if len(query_targets) > 0:
                            i += 1
                            content_table = table
                            answer_table, targets_unprocessed = extractor.read_data(query_targets, content_table,
                                                                                    None,
                                                                                    True, local, debug)
                            query_targets = targets_unprocessed
                            answer = self.add_answer_section(answer, "items" + str(i), answer_table)

                answer = self.format_json_output(answer)
            else:
                # No options provided
                processor = UnstructuredProcessor()
                content, table_content = processor.extract_data(file_path, strategy, model_name, None, local, debug)
                answer = self.execute(query_inputs, query_types, content, query, 'all', debug, local)
        else:
            raise ValueError(
                "Invalid combination of options provided. Only 'tables and html' or 'tables and markdown' are allowed.")

        end = timeit.default_timer()

        print(f"\nJSON response:\n")
        print(answer + '\n')
        print('=' * 50)

        print(f"Time to retrieve answer: {end - start}")

        return answer

    def execute(self, query_inputs, query_types, content, query, mode, debug, local):
        if mode == 'form' or mode == 'all':
            ResponseModel = self.invoke_pipeline_step(lambda: self.build_response_class(query_inputs, query_types),
                                                      "Building dynamic response class for " + mode + " data...",
                                                      local)

        answer = self.invoke_pipeline_step(
            lambda: self.execute_query(query, content, ResponseModel, mode),
            "Executing query for " + mode + " data...",
            local
        )

        return answer

    def execute_query(self, query, content, ResponseModel, mode):
        client = instructor.from_openai(
            OpenAI(
                base_url=cfg.OLLAMA_BASE_URL_INSTRUCTOR,
                api_key="ollama",
            ),
            mode=instructor.Mode.JSON,
        )

        resp = []
        if mode == 'form' or mode == 'all':
            resp = client.chat.completions.create(
                model=cfg.LLM_INSTRUCTOR,
                messages=[
                    {
                        "role": "user",
                        "content": f"{query} from the following content {content}. if query field value is missing, return None."
                    }
                ],
                response_model=ResponseModel,
                max_retries=3
            )

        answer = resp.model_dump_json(indent=4)

        return answer

    def filter_fields_query(self, query_inputs, query_types, mode):
        fields = []

        for query_input, query_type in zip(query_inputs, query_types):
            if mode == "form" and query_type.startswith("List") is False:
                fields.append((query_input, query_type))
            elif mode == "table" and query_type.startswith("List") is True:
                fields.append((query_input, query_type))

        # return filtered query_inputs and query_types as two array of strings
        query_inputs = [field[0] for field in fields]
        query_types = [field[1] for field in fields]

        return query_inputs, query_types

    # Function to safely evaluate type strings
    def safe_eval_type(self, type_str, context):
        try:
            return eval(type_str, {}, context)
        except NameError:
            raise ValueError(f"Type '{type_str}' is not recognized")

    def build_response_class(self, query_inputs, query_types_as_strings):
        # Controlled context for eval
        context = {
            'List': List,
            'str': str,
            'int': int,
            'float': float
            # Include other necessary types or typing constructs here
        }

        query_types_as_strings = [s.replace('Array', 'List') for s in query_types_as_strings]

        # Convert string representations to actual types
        query_types = [self.safe_eval_type(type_str, context) for type_str in query_types_as_strings]

        # Create fields dictionary
        fields = {name: (type_, ...) for name, type_ in zip(query_inputs, query_types)}

        DynamicModel = create_model('DynamicModel', **fields)

        return DynamicModel

    def validate_options(self, options: List[str]) -> bool:
        # Define valid combinations
        valid_combinations = [
            ["tables", "html"],
            ["tables", "markdown"]
        ]

        # Check for valid combinations or empty list
        if not options:  # Valid if no options are provided
            return True
        if sorted(options) in (sorted(combination) for combination in valid_combinations):
            return True
        return False

    def add_answer_section(self, answer, section_name, answer_table):
        if not isinstance(answer, dict):
            raise ValueError("The answer should be a dictionary.")

        # Parse answer_table if it is a JSON string
        if isinstance(answer_table, str):
            answer_table = json.loads(answer_table)

        answer[section_name] = answer_table
        return answer

    def format_json_output(self, answer):
        formatted_json = json.dumps(answer, indent=4)
        formatted_json = formatted_json.replace('", "', '",\n"')
        formatted_json = formatted_json.replace('}, {', '},\n{')
        return formatted_json

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
