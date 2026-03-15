import datetime
import os
import sys
from io import BytesIO

import pandas as pd
from sqlalchemy import text

from aws.client import S3Client
from db.database_conection import getDbConnectionById
from db.models import Transaction


class SqlServerCollector:
    def __init__(self, aws_client: S3Client, db_id: int):
        self._envs = {
            "file_name": os.environ.get(f"DB_NAME{db_id}"),
            "table_name": os.environ.get(f"DB_TABLE{db_id}", Transaction.__tablename__),
        }
        self._db_id = db_id
        self._model = Transaction
        self._buffer = None
        self._aws = aws_client

        if self._envs["file_name"] is None:
            print(f"A variavel de ambiente DB_NAME{db_id} nao esta definida.")
            sys.exit(1)

    def start(self):
        df = self.extract_data()
        print("Processo extract com sucesso")

        if df.empty:
            print("Nenhum dado encontrado no SQL Server para o periodo informado.")
            return False

        df = self.transform_add_columns(df, "sqlserver")
        print("Processo transform com sucesso")
        self.convert_to_parquet(df)

        if self._buffer is not None:
            file_name = self.file_name()
            print(file_name)
            self._aws.upload_file(self._buffer, file_name)
            return True

        return False

    def extract_data(self):
        session = getDbConnectionById(self._db_id)
        try:
            query, params = self.create_yesterday_query()
            return pd.read_sql(query, session.bind, params=params)
        finally:
            session.close()

    def transform_add_columns(self, df, datasource_value):
        df["created_at"] = datetime.datetime.now().isoformat()
        df["datasource"] = datasource_value
        return df

    def convert_to_parquet(self, df):
        self._buffer = BytesIO()
        try:
            df.to_parquet(self._buffer)
            self._buffer.seek(0)
            return self._buffer
        except Exception as e:
            print(f"Erro ao transformar o DataFrame em Parquet: {e}")
            self._buffer = None
            return None

    def file_name(self):
        current_date = datetime.datetime.now().isoformat()
        match = current_date.split(".")
        file_name = self._envs["file_name"]
        return f"sqlserver/{file_name}-{match[0]}.parquet"

    def create_yesterday_query(self):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        table = self._envs["table_name"]
        columns = ", ".join(column.name for column in self._model.__table__.columns)
        query = text(
            f"SELECT {columns} "
            f"FROM {table} "
            f"WHERE transaction_time >= :yesterday"
        )
        return query, {"yesterday": yesterday}

    # Backward compatibility with the naming style used in older files.
    def fileName(self):
        return self.file_name()

    def createYesterdayQuery(self):
        return self.create_yesterday_query()
