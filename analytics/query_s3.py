import os
from pathlib import Path

import boto3
import duckdb as db
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "backend" / ".env")

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION = os.getenv("AWS_REGION")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
API_PREFIX = os.getenv("DUCKDB_API_PREFIX", "api/")
SQLSERVER_PREFIX = os.getenv("DUCKDB_SQLSERVER_PREFIX", "sqlserver/")


def create_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )


def get_latest_parquet_path(s3_client, prefix: str) -> str:
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    contents = response.get("Contents", [])
    parquet_files = [item for item in contents if item["Key"].endswith(".parquet")]

    if not parquet_files:
        raise FileNotFoundError(
            f"Nenhum arquivo parquet encontrado em s3://{BUCKET_NAME}/{prefix}"
        )

    latest_file = max(parquet_files, key=lambda item: item["LastModified"])
    return f"s3://{BUCKET_NAME}/{latest_file['Key']}"


def create_connection():
    con = db.connect()
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")
    con.execute(f"SET s3_region='{REGION}';")
    con.execute(f"SET s3_access_key_id='{ACCESS_KEY}';")
    con.execute(f"SET s3_secret_access_key='{SECRET_KEY}';")
    return con


def register_tables(con, transaction_path: str, api_path: str):
    con.execute(
        f"""
        CREATE OR REPLACE TABLE transacao AS
        SELECT *
        FROM read_parquet('{transaction_path}')
        """
    )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE ecommerce AS
        SELECT *
        FROM read_parquet('{api_path}')
        """
    )


def execute_query_df(con, title: str, query: str):
    df = con.execute(query).fetchdf()
    print(f"\n{title}")
    print_table(df)


def print_table(df):
    try:
        print(df.to_markdown(index=False, tablefmt="grid"))
    except Exception:
        print(df.to_string(index=False))


def main():
    s3_client = create_s3_client()
    latest_sqlserver_file = get_latest_parquet_path(s3_client, SQLSERVER_PREFIX)
    latest_api_file = get_latest_parquet_path(s3_client, API_PREFIX)

    print(f"Arquivo mais recente SQL Server: {latest_sqlserver_file}")
    print(f"Arquivo mais recente API: {latest_api_file}")

    con = create_connection()
    register_tables(con, latest_sqlserver_file, latest_api_file)

    execute_query_df(con, "Preview SQL Server", "SELECT * FROM transacao LIMIT 5;")
    execute_query_df(con, "Preview API", "SELECT * FROM ecommerce LIMIT 5;")
    execute_query_df(
        con,
        "Total Sales API",
        """
        SELECT
            COUNT(*) AS total_registros,
            ROUND(SUM(price), 2) AS total_sales_api
        FROM ecommerce
        """,
    )
    execute_query_df(
        con,
        "Total Sales Loja SQL",
        """
        SELECT
            store,
            COUNT(*) AS total_registros,
            ROUND(SUM(price), 2) AS total_sales_loja_sql
        FROM transacao
        GROUP BY store
        ORDER BY total_sales_loja_sql DESC
        """,
    )
    execute_query_df(
        con,
        "Total Sales Consolidado",
        """
        SELECT
            'api' AS fonte,
            ROUND(SUM(price), 2) AS total_sales
        FROM ecommerce
        UNION ALL
        SELECT
            'sqlserver' AS fonte,
            ROUND(SUM(price), 2) AS total_sales
        FROM transacao
        """,
    )


if __name__ == "__main__":
    main()
