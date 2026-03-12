from datasource.api import ApiCollector
from contracts.schema import CompraSchema


schema = CompraSchema
minha_api = ApiCollector(schema).start(3)

print(minha_api)
