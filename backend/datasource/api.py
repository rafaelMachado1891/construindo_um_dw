import requests
from contracts.schema import GenericSchema
from typing import Any, Dict, List
import pandas as pd
from io import BytesIO
from datetime import datetime
import pyarrow.parquet as pq

class ApiCollector:
    def __init__(self, schema: Dict[str, type], aws_client=None):
        self._schema = schema
        self._aws_client = aws_client
        self._buffer = None
        return
    
    def start(self, param: int) -> List[GenericSchema]:
        response = self.get_data(param)
        response = self.extract_data(response)
        response = self.transform_data(response)
        response = self.convertTOparquet(response)        

        if self._buffer is not None:
            file_name = self.file_name()
            print(file_name)
            self._aws_client.upload_file(response, file_name)
            return True

        return False

    
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
    
    def transform_data(self, response):
        result = pd.DataFrame(response)
        return result

    def convertTOparquet(self, response):
        self._buffer = BytesIO()
        try:
            response.to_parquet(self._buffer)
            return self._buffer
        except:
            raise Exception("Erro ao converter para parquet")
            self._buffer = None

    def file_name(self):
        data_atual = datetime.now().isoformat()
        match = data_atual.split(".")
        return f"api/api-response-compra{match[0]}.parquet"
        

    # Backward compatibility with previous method names.
    def getData(self, param: int) -> List[Dict[str, Any]]:
        return self.get_data(param)

    def extractData(self, response: List[Dict[str, Any]]) -> List[GenericSchema]:
        return self.extract_data(response)


# Backward compatibility with previous class name.
ApiColector = ApiCollector
