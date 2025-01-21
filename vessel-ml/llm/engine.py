import warnings
import typer
from typing_extensions import Annotated, List
from rag.agents.interface import get_pipeline
import tempfile
import os
from rich import print


# Disable parallelism in the Huggingface tokenizers library to prevent potential deadlocks and ensure consistent behavior.
# This is especially important in environments where multiprocessing is used, as forking after parallelism can lead to issues.
# Note: Disabling parallelism may impact performance, but it ensures safer and more predictable execution.
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def run(query: Annotated[str, typer.Argument(help="The list of fields to fetch")],
        file_path: Annotated[str, typer.Option(help="The file to process")] = None,
        agent: Annotated[str, typer.Option(help="Selected agent")] = "vessel-parse",
        options: Annotated[List[str], typer.Option(help="Options to pass to the agent")] = None,
        crop_size: Annotated[int, typer.Option(help="Crop size for table extraction")] = None,
        debug_dir: Annotated[str, typer.Option(help="Debug folder for multipage")] = None,
        debug: Annotated[bool, typer.Option(help="Enable debug mode")] = False):

    user_selected_agent = agent  # Modify this as needed

    try:
        rag = get_pipeline(user_selected_agent)
        answer = rag.run_pipeline(user_selected_agent, query, file_path, options, crop_size, debug_dir,
                                  debug, False)

        print(f"\nJSON response:\n")
        print(answer)
    except ValueError as e:
        print(f"Caught an exception: {e}")


async def run_from_api_engine(user_selected_agent, query, options_arr, file, debug_dir, debug):
    try:
        rag = get_pipeline(user_selected_agent)

        if file is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = os.path.join(temp_dir, file.filename)

                # Save the uploaded file to the temporary directory
                with open(temp_file_path, 'wb') as temp_file:
                    content = await file.read()
                    temp_file.write(content)

                answer = rag.run_pipeline(user_selected_agent, query, temp_file_path, options_arr, debug_dir, debug, False)
        else:
            answer = rag.run_pipeline(user_selected_agent, query, options_arr, debug_dir, debug, False)
    except ValueError as e:
        raise e

    return answer


if __name__ == "__main__":
    typer.run(run)
