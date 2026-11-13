import os
import json
import csv
import time
from google import genai
from google.genai import types, errors

client = genai.Client()
MODELO = "gemini-3.8-flash"
PASTA = "documentos"

PROMPT = """Você é um assistente que analisa decisões judiciais.
Leia a decisão abaixo e responda SOMENTE com um JSON com estas chaves:

"resumo": resumo em no máximo 2 frases
"tipo_reu": todos os réus citados (banco, companhia aérea, plano de saúde, loja, município, pessoa física etc.). Se o texto disser apenas "empresa", escreva "empresa (tipo não especificado)"
"resultado": use exatamente uma destas opções: procedente, parcialmente procedente, improcedente, acordo homologado, extinto sem resolução do mérito, não informado
"valores": todos os valores em reais citados, indicando para que servem e se foram pedidos pelo autor ou decididos pelo juiz
"data": data da decisão (não datas de fatos ou de parcelas futuras)

Use apenas informações presentes no texto. Se algo não estiver no texto, escreva "não informado".

DECISÃO:
"""

def analisar(texto, tentativas=6):
    """Envia o texto ao Gemini e repete se o servidor estiver sobrecarregado."""
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = client.models.generate_content(
                model=MODELO,
                contents=PROMPT + texto,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            return json.loads(resposta.text)
        except errors.APIError as e:
            if e.code in (429, 500, 503) and tentativa < tentativas:
                espera = 20 * tentativa
                print(f"  Servidor ocupado (erro {e.code}). Tentando de novo em {espera}s...")
                time.sleep(espera)
            else:
                print(f"  Falhou (erro {e.code}). Pulando este documento.")
                return None
        except json.JSONDecodeError:
            print("  A resposta não veio em JSON válido.")
            return None
    return None


linhas = []
arquivos = sorted(f for f in os.listdir(PASTA) if f.endswith(".txt"))

for nome in arquivos:
    print(f"Processando {nome}...")
    with open(os.path.join(PASTA, nome), "r", encoding="utf-8") as f:
        texto = f.read()

    dados = analisar(texto)
    if dados is None:
        dados = {"resumo": "ERRO AO PROCESSAR"}

    dados["arquivo"] = nome
    linhas.append(dados)
    time.sleep(4)  # pausa curta para respeitar o limite gratuito

colunas = ["arquivo", "resumo", "tipo_reu", "resultado", "valores", "data"]
with open("resultados.csv", "w", newline="", encoding="utf-8-sig") as f:
    escritor = csv.DictWriter(f, fieldnames=colunas, extrasaction="ignore", delimiter=";")
    escritor.writeheader()
    escritor.writerows(linhas)

print("Pronto! Resultados salvos em resultados.csv")