from fastapi import FastAPI
from faker import Faker
import pandas as pd
from pathlib import Path
import random

app = FastAPI()
fake = Faker()


dir_path = Path(__file__).resolve().parent
file_name = dir_path / "products.csv"

df = pd.read_csv(file_name)
df['indice'] = range(1, len(df) + 1)
df.set_index('indice', inplace=True)

lojaonline = 11

@app.get("/gerar_compra")
async def gerar_compra():
    index = random.randint(1, len(df) - 1)
    row = df.iloc[index]
    return [
        {
        "client": fake.name(),
        "credit_card": fake.credit_card_provider(),
        "product_name": str(row['product_name']),
        "ean": int(row['codigo_ean']),
        "price": round(float(row['price']*1.2),2),
        "store": lojaonline,
        "dateTime": fake.iso8601(),
        "position_client": list(fake.location_on_land())
        }
    ]
    
@app.get("/gerar_compra/{numero_registro}")
async def gerar_compra_lote(numero_registro: int):

    if numero_registro < 1: 
        return {"error": "Numero de registro deve ser maior que 1"}
    
    respostas = []

    for _ in range(numero_registro):
        index = random.randint(1, len(df) - 1)
        row = df.iloc[index]
        compra = {
            "client": fake.name(),
            "credit_card": fake.credit_card_provider(),
            "product_name": str(row['product_name']),
            "ean": int(row['codigo_ean']),
            "price": round(float(row['price']*1.2),2),
            "store": lojaonline,
            "dateTime": fake.iso8601(),
            "position_client": fake.location_on_land()
            }
        respostas.append(compra)

    return respostas

