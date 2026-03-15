# Construindo um DW

Projeto de ingestao de dados de e-commerce com foco em consolidar dados coletados de APIs e, na evolucao do fluxo, de banco de dados em um bucket S3. Esses arquivos podem ser consultados posteriormente com DuckDB para exploracao, analise e construcao de camadas analiticas.

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
python -m venv .venv
source .venv/Scripts/activate
```

### 2. Instalar as dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar as variaveis de ambiente

Crie o arquivo `backend/.env` com base em `backend/.env_example`.

Exemplo:

```env
AWS_ACCESS_KEY_ID=seu_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
S3_BUCKET_NAME=seu_bucket
AWS_REGION=us-east-2
DELTA_LAKE_S3_PATH=s3://seu-bucket/seu-prefixo
```

Observacoes:

- `AWS_REGION` deve conter apenas o codigo da regiao, por exemplo `us-east-2`.
- O processo atual valida `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` e `S3_BUCKET_NAME`.
- `DELTA_LAKE_S3_PATH` ja esta preparado para a evolucao do projeto, mas ainda nao e obrigatorio no fluxo atual.

### 4. Subir a API fake de e-commerce

Em um terminal separado:

```bash
cd backend
uvicorn fake_api.start:app --reload
```

A API ficara disponivel em `http://127.0.0.1:8000`.

### 5. Rodar o coletor

Em outro terminal:

```bash
cd backend
python start.py
```

O coletor faz chamadas para a API fake, valida o schema basico, transforma os dados em DataFrame, gera um arquivo Parquet em memoria e envia o resultado para o S3.

## Fluxo do projeto

Hoje o fluxo implementado funciona assim:

1. A API fake simula compras de um e-commerce.
2. O coletor consome os endpoints locais.
3. Os dados recebidos passam por uma validacao simples de tipos com base no schema.
4. O resultado e transformado em `pandas.DataFrame`.
5. O DataFrame e convertido para Parquet com `pyarrow`.
6. O arquivo e enviado para o bucket S3 com `boto3`.
7. Depois dessa etapa, os arquivos podem ser consultados com DuckDB em uma camada analitica posterior.

## Estrutura do projeto

```text
construindo_um_dw/
|-- .gitignore
|-- .python-version
|-- requirements.txt
|-- README.md
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
    |   `-- api.py
    `-- fake_api/
        |-- products.csv
        `-- start.py
```

## O que cada pasta faz

- `backend/start.py`: agenda a execucao periodica do coletor.
- `backend/aws/client.py`: encapsula a conexao com o S3 e o upload dos arquivos.
- `backend/contracts/schema.py`: define o schema esperado para os dados de compra.
- `backend/datasource/api.py`: busca os dados, aplica validacao, transforma em DataFrame e gera Parquet.
- `backend/fake_api/start.py`: sobe a API fake usada para simular eventos de compra.
- `backend/fake_api/products.csv`: base de produtos usada pela API fake.

## Endpoints da API fake

### Gerar uma compra

```http
GET /gerar_compra
```

### Gerar varias compras

```http
GET /gerar_compra/{numero_registro}
```

Exemplo:

```http
GET /gerar_compra/10
```

## Dependencias principais

- `fastapi` e `uvicorn` para a API fake.
- `requests` para consumir os dados.
- `pandas` para transformacao tabular.
- `pyarrow` para escrita em Parquet.
- `boto3` para integracao com S3.
- `schedule` para execucao periodica.
- `python-dotenv` para carregar variaveis do arquivo `.env`.

## Proximos passos sugeridos

- adicionar a camada de leitura de dados de banco de dados;
- separar landing, bronze e silver no S3;
- consultar os arquivos com DuckDB;
- automatizar testes do fluxo de ingestao;
- versionar schemas e contratos de dados.
