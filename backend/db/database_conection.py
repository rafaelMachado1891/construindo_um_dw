import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class SqlServerConnection:
    def __init__(self, connection_id: int):
        self._connection_id = connection_id
        self._configs = {
            "DB_USER": os.getenv(f"DB_USER{connection_id}"),
            "DB_PASSWORD": os.getenv(f"DB_PASSWORD{connection_id}"),
            "DB_HOST": os.getenv(f"DB_HOST{connection_id}"),
            "DB_NAME": os.getenv(f"DB_NAME{connection_id}"),
            "DB_PORT": os.getenv(f"DB_PORT{connection_id}"),
            "DB_DRIVER": os.getenv(
                f"DB_DRIVER{connection_id}", "ODBC Driver 17 for SQL Server"
            ),
            "DB_TRUSTED_CONNECTION": os.getenv(
                f"DB_TRUSTED_CONNECTION{connection_id}", "no"
            ),
            "DB_ENCRYPT": os.getenv(f"DB_ENCRYPT{connection_id}", "no"),
            "DB_TRUST_SERVER_CERTIFICATE": os.getenv(
                f"DB_TRUST_SERVER_CERTIFICATE{connection_id}", "yes"
            ),
        }

        required_vars = ("DB_HOST", "DB_NAME")
        if self._configs["DB_TRUSTED_CONNECTION"].lower() != "yes":
            required_vars = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME")

        for var in required_vars:
            if self._configs[var] is None:
                print(f"A variavel de ambiente {var}{connection_id} nao esta definida.")
                sys.exit(1)

        self._engine = create_engine(self._build_database_uri())
        self._session_factory = sessionmaker(bind=self._engine)

    def _build_database_uri(self) -> str:
        driver = quote_plus(self._configs["DB_DRIVER"])
        host = self._configs["DB_HOST"]
        if self._configs["DB_PORT"]:
            host = f"{host}:{self._configs['DB_PORT']}"

        if self._configs["DB_TRUSTED_CONNECTION"].lower() == "yes":
            return (
                f"mssql+pyodbc://@{host}/{self._configs['DB_NAME']}"
                f"?driver={driver}"
                f"&trusted_connection=yes"
                f"&encrypt={self._configs['DB_ENCRYPT']}"
                f"&TrustServerCertificate={self._configs['DB_TRUST_SERVER_CERTIFICATE']}"
            )

        return (
            f"mssql+pyodbc://{self._configs['DB_USER']}:{self._configs['DB_PASSWORD']}"
            f"@{host}/{self._configs['DB_NAME']}"
            f"?driver={driver}"
            f"&encrypt={self._configs['DB_ENCRYPT']}"
            f"&TrustServerCertificate={self._configs['DB_TRUST_SERVER_CERTIFICATE']}"
        )

    def get_session(self):
        return self._session_factory()


def get_db_connection_by_id(connection_id: int):
    return SqlServerConnection(connection_id).get_session()


def getDbConnectionById(id: int):
    return get_db_connection_by_id(id)
