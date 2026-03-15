from datasource.api import ApiCollector
from contracts.schema import CompraSchema
from aws.client import S3Client
import time
import schedule


schema = CompraSchema
aws_client = S3Client()


def collector(schema, aws_client, repeat):
    response = ApiCollector(schema, aws_client).start(repeat)
    print("executei")
    return

schedule.every(1).minutes.do(collector, schema, aws_client,10)

while True:
    schedule.run_pending()
    time.sleep(1)
