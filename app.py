import os
import json
import time
import streamlit as st
from google import genai
from google.genai import types, errors

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


def analisar(client, texto, tentativas=4):
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
                time.sleep(10 * tentativa)
            else:
                return {"erro": f"O servidor falhou (erro {e.code}). Tente de novo em alguns minutos."}
        except json.JSONDecodeError:
            return {"erro": "A resposta da IA não veio em JSON válido."}
    return {"erro": "Não foi possível analisar a decisão."}


st.set_page_config(page_title="Extrator de decisões judiciais", page_icon="⚖️")
st.title("⚖️ Extrator de decisões judiciais")
st.write(
    "Cole uma decisão ou escolha um exemplo, e a IA organiza as informações principais. "
    "Os exemplos são **fictícios**, criados para testar a ferramenta."
)

modo = st.radio("Como quer informar a decisão?", ["Escolher um exemplo", "Colar um texto"])

texto = ""
if modo == "Escolher um exemplo":
    if os.path.isdir(PASTA):
        arquivos = sorted(f for f in os.listdir(PASTA) if f.endswith(".txt"))
    else:
        arquivos = []
    if arquivos:
        escolhido = st.selectbox("Exemplo", arquivos)
        with open(os.path.join(PASTA, escolhido), "r", encoding="utf-8") as f:
            texto = f.read()
        with st.expander("Ver o texto da decisão"):
            st.write(texto)
    else:
        st.warning("Nenhum exemplo encontrado na pasta 'documentos'.")
else:
    texto = st.text_area("Cole aqui o texto da decisão", height=200)

if st.button("Analisar decisão"):
    if not texto.strip():
        st.warning("Informe o texto de uma decisão antes de analisar.")
    elif not os.environ.get("GEMINI_API_KEY"):
        st.error("A chave GEMINI_API_KEY não foi encontrada. Configure-a no PowerShell e rode o app de novo.")
    else:
        client = genai.Client()
        with st.spinner("Analisando a decisão..."):
            dados = analisar(client, texto)

        if "erro" in dados:
            st.error(dados["erro"])
        else:
            st.subheader("Resultado")
            st.markdown(f"**Resumo:** {dados.get('resumo', 'não informado')}")
            st.markdown(f"**Réu:** {dados.get('tipo_reu', 'não informado')}")
            st.markdown(f"**Resultado:** {dados.get('resultado', 'não informado')}")
            st.markdown(f"**Valores:** {dados.get('valores', 'não informado')}")
            st.markdown(f"**Data da decisão:** {dados.get('data', 'não informado')}")

st.caption(
    "Protótipo de estudo. A IA pode errar, e os resultados precisam de revisão humana."
)