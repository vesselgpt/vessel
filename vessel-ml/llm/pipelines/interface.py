from abc import ABC, abstractmethod
from typing import Any
from typing import List
import warnings


warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# Abstract Interface
class Pipeline(ABC):
    @abstractmethod
    def run_pipeline(self,
                     pipeline: str,
                     query: str,
                     file_path: str,
                     options: List[str] = None,
                     crop_size: int = None,
                     debug_dir: str = None,
                     debug: bool = False,
                     local: bool = True) -> Any:
        pass


# Factory Method
def get_pipeline(pipeline_name: str) -> Pipeline:
    if pipeline_name == "vessel-parse":
        from pipelines.vessel_parse.vessel_parse import VesselParsePipeline
        return VesselParsePipeline()
    elif pipeline_name == "stocks":
        from pipelines.instructor.stocks import Stocks
        return Stocks()
    else:
        raise ValueError(f"Unknown pipeline: {pipeline_name}")

