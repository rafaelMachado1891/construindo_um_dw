# Construindo um DW

Projeto de engenharia de dados para consolidar dados de duas fontes operacionais:

- API de um sistema de e-commerce
- ERP em SQL Server

O objetivo e coletar os dados dessas fontes, padronizar a ingestao em arquivos Parquet no S3 e, depois, consultar os dados com DuckDB para analise exploratoria e construcao de camadas analiticas.

## Como rodar

### 1. Criar e ativar o ambiente virtual

No PowerShell:

```powershell
cd construindo_um_dw
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Git Bash:

```bash
cd construindo_um_dw
source activate_git_bash.sh
```

### 2. Instalar as dependencias

```bash
python -m pip install -r requirements.txt
```

### 3. Configurar as variaveis de ambiente

Crie o arquivo `backend/.env` com base em `backend/.env_example`.

Variaveis principais:

```env
AWS_ACCESS_KEY_ID=#
AWS_SECRET_ACCESS_KEY=#
S3_BUCKET_NAME=bucketdwtozero
AWS_REGION=us-east-2

DB_HOST1=localhost
DB_NAME1=transactions
DB_PORT1=
DB_DRIVER1=ODBC Driver 17 for SQL Server
DB_TABLE1=transactions
DB_TRUSTED_CONNECTION1=yes
DB_ENCRYPT1=no
DB_TRUST_SERVER_CERTIFICATE1=yes
```

### 4. Subir a API fake de e-commerce

Em um terminal:

```bash
cd backend
python -m uvicorn fake_api.start:app --reload
```

### 5. Popular o banco SQL Server com dados fake

Em outro terminal:

```bash
cd backend
python -m backend.db.seed_fake_transactions
```

Esse script cria a tabela `transactions` se ela ainda nao existir e insere 2000 registros fake com base no arquivo `products.csv`.

### 6. Rodar as coletas

Em outro terminal:

```bash
cd backend
python start.py
```

O `start.py` agenda duas coletas:

- coleta da API do e-commerce
- coleta do SQL Server do ERP

Cada coleta gera um Parquet em memoria e envia o arquivo para o S3.

### 7. Consultar os dados no S3 com DuckDB

Na raiz do projeto:

```bash
python analytics/query_s3.py
```

O script:

- identifica automaticamente o parquet mais recente de `api/`
- identifica automaticamente o parquet mais recente de `sqlserver/`
- registra as tabelas no DuckDB
- exibe previews e metricas em formato tabular no terminal

## Sobre o projeto

Este projeto simula um fluxo de consolidacao de dados de um ambiente transacional, unindo:

- dados de vendas gerados por uma API de e-commerce
- dados de transacoes vindos do ERP em SQL Server

As duas fontes sao ingeridas separadamente, mas armazenadas no mesmo data lake em S3, em formato Parquet. Isso permite:

- padronizar a camada de ingestao
- simplificar consultas analiticas
- comparar dados entre canais e sistemas
- preparar a base para camadas futuras como staging, marts e indicadores

## Arquitetura

```text
                    +----------------------+
                    |  API Fake E-commerce |
                    |   FastAPI / Faker    |
                    +----------+-----------+
                               |
                               v
                      +-------------------+
                      |   ApiCollector    |
                      | extract/transform |
                      +---------+---------+
                                |
                                v
                           Parquet em memoria
                                |
                                v
+-------------------+   +-------------------+   +----------------------+
| ERP SQL Server    |-->| SqlServerCollector|-->|      S3 Bucket       |
| tabela transactions|  | extract/transform |   | api/ e sqlserver/    |
+-------------------+   +-------------------+   +----------+-----------+
                                                           |
                                                           v
                                                 +------------------+
                                                 | DuckDB + Parquet |
                                                 | analytics/query  |
                                                 +------------------+
```

## Fluxo de dados

1. A API fake gera compras de e-commerce a partir de uma base de produtos.
2. O SQL Server local armazena transacoes do ERP na tabela `transactions`.
3. O `ApiCollector` consome a API e gera Parquet no prefixo `api/`.
4. O `SqlServerCollector` consulta o banco e gera Parquet no prefixo `sqlserver/`.
5. O `S3Client` envia os arquivos para o bucket S3.
6. O DuckDB consulta os arquivos Parquet diretamente no S3.
7. As consultas permitem comparar valores da API e do ERP em uma camada analitica simples.

## Estrutura do projeto

```text
construindo_um_dw/
|-- .gitignore
|-- .python-version
|-- activate_git_bash.sh
|-- requirements.txt
|-- README.md
|-- analytics/
|   |-- query.sql
|   `-- query_s3.py
`-- backend/
    |-- .env_example
    |-- start.py
    |-- aws/
    |   |-- __init__.py
    |   `-- client.py
    |-- contracts/
    |   |-- __init__.py
    |   `-- schema.py
    |-- datasource/
    |   |-- __init__.py
    |   |-- api.py
    |   `-- sql.py
    |-- db/
    |   |-- database_conection.py
    |   |-- models.py
    |   `-- seed_fake_transactions.py
    `-- fake_api/
        |-- products.csv
        `-- start.py
```

## Componentes principais

- `backend/start.py`: agenda a execucao recorrente das coletas.
- `backend/datasource/api.py`: coleta dados da API de e-commerce e grava no S3 em Parquet.
- `backend/datasource/sql.py`: coleta dados do SQL Server e grava no S3 em Parquet.
- `backend/db/database_conection.py`: gerencia a conexao com SQL Server via SQLAlchemy.
- `backend/db/models.py`: define o modelo `Transaction`.
- `backend/db/seed_fake_transactions.py`: cria e popula a tabela `transactions` com dados fake.
- `backend/aws/client.py`: envia os arquivos para o S3.
- `analytics/query_s3.py`: consulta os Parquet mais recentes do S3 com DuckDB.

## Consultas analiticas atuais

O script `analytics/query_s3.py` entrega:

- preview dos dados vindos do SQL Server
- preview dos dados vindos da API
- total de vendas da API
- total de vendas por loja no SQL Server
- consolidado de total de vendas por fonte

## Dependencias principais

- `fastapi` e `uvicorn` para a API fake
- `faker` para gerar dados de exemplo
- `pandas` para transformacao tabular
- `pyarrow` para escrita em Parquet
- `boto3` para integracao com S3
- `sqlalchemy` e `pyodbc` para leitura do SQL Server
- `duckdb` para consultas analiticas em Parquet
- `schedule` para agendamento simples
- `python-dotenv` para configuracao por ambiente