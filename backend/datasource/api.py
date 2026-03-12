import requests
import pandas as pd
from contracts.schema import GenericSchema
from typing import Any, Dict, List


class ApiCollector:
    def __init__(self, schema: Dict[str, type]):
        self._schema = schema
        self.aws = None
        self.buffer = None
        return
    
    def start(self, param: int) -> List[GenericSchema]:
        response = self.get_data(param)
        response = self.extract_data(response)
        return response
    
    def get_data(self, param: int) -> List[Dict[str, Any]]:
        if param > 1:
            response = requests.get(
                f"http://localhost:8000/gerar_compra/{param}", timeout=10
            ).json()
        else:
            response = requests.get(
                "http://localhost:8000/gerar_compra", timeout=10
            ).json()

        if isinstance(response, dict):
            return [response]
        return response
    
    def extract_data(self, response: List[Dict[str, Any]]) -> List[GenericSchema]:
        result: List[GenericSchema] = []
        for item in response:
            index = {}
            for key, value in self._schema.items():
                if isinstance(item.get(key), value):
                    index[key] = item[key]
                else:
                    index[key] = None

        result.append(index)
        return result
    
    def transform_data(self):
        return

    # Backward compatibility with previous method names.
    def getData(self, param: int) -> List[Dict[str, Any]]:
        return self.get_data(param)

    def extractData(self, response: List[Dict[str, Any]]) -> List[GenericSchema]:
        return self.extract_data(response)


# Backward compatibility with previous class name.
ApiColector = ApiCollector
