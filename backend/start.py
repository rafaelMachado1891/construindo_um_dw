import time

import schedule

from aws.client import S3Client
from contracts.schema import CompraSchema
from datasource.api import ApiCollector
from datasource.sql import SqlServerCollector

schema = CompraSchema
aws_client = S3Client()


def api_collector(schema, aws_client, repeat):
    response = ApiCollector(schema, aws_client).start(repeat)
    print(f"Coleta da API finalizada: {response}")
    return response


def sqlserver_collector(aws_client, db_id):
    response = SqlServerCollector(aws_client, db_id).start()
    print(f"Coleta do SQL Server finalizada: {response}")
    return response


schedule.every(1).minutes.do(api_collector, schema, aws_client, 10)
schedule.every(1).minutes.do(sqlserver_collector, aws_client, 1)


while True:
    schedule.run_pending()
    time.sleep(1)
