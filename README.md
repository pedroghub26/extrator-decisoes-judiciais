\# Extrator de dados de decisões judiciais com IA



Protótipo que usa um LLM (Gemini) para ler decisões judiciais em texto livre e extrair as informações principais, organizadas em planilha ou numa página web.



\## O problema



Decisões judiciais são textos longos e pouco padronizados. Quem precisa de informações delas (resultado, valores, tipo de réu, data) normalmente abre cada documento, lê e anota à mão numa planilha. Com muitas decisões, isso é lento, repetitivo e sujeito a erro.



\## O que a ferramenta faz



Recebe o texto de uma decisão e devolve:



\- \*\*Resumo\*\* em até 2 frases

\- \*\*Tipo de réu\*\* (banco, companhia aérea, plano de saúde, loja, município etc.)

\- \*\*Resultado\*\* (procedente, parcialmente procedente, improcedente, acordo homologado, extinto sem resolução do mérito ou não informado)

\- \*\*Valores\*\* em reais, indicando para que servem e se foram pedidos pelo autor ou decididos pelo juiz

\- \*\*Data da decisão\*\*



Há duas formas de usar:



1\. `processar.py` lê todos os `.txt` da pasta `documentos` e gera uma planilha CSV.

2\. `app.py` abre uma página (Streamlit) onde dá para escolher um exemplo ou colar um texto.



\## Dados



As 9 decisões em `documentos/` são \*\*fictícias\*\*, escritas por mim para testar a ferramenta. Não contêm dados pessoais nem números de processo. Os documentos 6 a 9 foram criados de propósito com casos difíceis: pedido improcedente, dois réus com valores pedidos e concedidos diferentes, decisão sem data e acordo homologado.



\## Como rodar (Windows, PowerShell)



1\. Instale o Python e crie um ambiente virtual:



```powershell

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

```



2\. Crie uma chave gratuita da API do Gemini no Google AI Studio e configure-a como variável de ambiente (nunca coloque a chave no código):



```powershell

$env:GEMINI\_API\_KEY="sua-chave-aqui"

```



O código usa o modelo `gemini-3.8-flash` (variável `MODELO`). Se o Google aposentar esse nome, troque-o pelo modelo Flash disponível na sua conta.



3\. Gere os documentos de exemplo e processe:



```powershell

python criar\_docs.py

python criar\_docs\_dificeis.py

python processar.py

```



O resultado fica em `resultados.csv`.



4\. Para abrir a interface web:



```powershell

streamlit run app.py

```



\## Estrutura



| Arquivo | Função |

|---|---|

| `criar\_docs.py`, `criar\_docs\_dificeis.py` | Criam as decisões fictícias em `documentos/` |

| `documentos/` | As 9 decisões fictícias usadas nos testes |

| `processar.py` | Processa todas as decisões e salva a planilha |

| `app.py` | Interface web em Streamlit |

| `requirements.txt` | Bibliotecas necessárias (google-genai e streamlit) |

| `resultados\_v1.csv`, `resultados\_v2.csv` | Resultados com cada versão do prompt |



\## Como o prompt foi melhorado



Testei a versão 1 do prompt nas 9 decisões e comparei cada campo com o texto original. Encontrei:



\- \*\*Erro claro:\*\* no doc9 (acordo homologado), o campo `resultado` saiu como "não informado", porque o prompt só oferecia as opções procedente, parcialmente procedente e improcedente.

\- \*\*Ponto discutível:\*\* no doc6, o réu era descrito apenas como "empresa", e o campo `tipo\_reu` saiu como "não informado".



Na versão 2, fiz quatro mudanças, cada uma ligada a um problema:



1\. Lista fechada de opções para `resultado`, incluindo "acordo homologado".

2\. Regra para `tipo\_reu`: citar todos os réus e escrever "empresa (tipo não especificado)" quando o texto não detalhar.

3\. Em `valores`, indicar se cada valor foi pedido pelo autor ou decidido pelo juiz.

4\. Em `data`, usar apenas a data da decisão, e não datas de fatos ou de parcelas futuras.



Resultado: o erro do doc9 foi corrigido e o campo do doc6 passou a ser preenchido.



\## Avaliação



Conferi manualmente 4 campos (`tipo\_reu`, `resultado`, `valores`, `data`) em cada uma das 9 decisões, ou seja, 36 campos por versão.



| Versão | Erros claros | Pontos discutíveis | Campos corretos |

|---|---|---|---|

| v1 | 1 | 1 | 34 de 36 |

| v2 | 0 | 2 | 34 de 36 |



Pontos discutíveis da v2:



\- \*\*doc4:\*\* o texto diz "julgo procedente o pedido", mas a v2 respondeu "parcialmente procedente" (o pedido de danos morais foi negado). A v1 havia respondido "procedente".

\- \*\*doc8:\*\* a v2 escreveu "R$ 312,00 em dobro pedido pela autora", redação ambígua, pois pode ser lida como o valor multiplicado por dois.



A amostra é pequena (9 documentos fictícios), então esses números mostram uma tendência, e não uma medida confiável de desempenho.



No app web, o doc9 foi classificado como "acordo homologado", confirmando que a correção da v2 também funciona na interface.



\## Limitações



\- O modelo pode errar ou interpretar por conta própria, como no doc4. Em uso real, os resultados precisariam de revisão humana.

\- O mesmo prompt pode gerar respostas ligeiramente diferentes a cada execução.

\- Os testes usaram textos curtos e fictícios. Decisões reais são mais longas e variadas.

\- Em dados reais seria necessário cuidar de privacidade e proteção de dados pessoais. No plano gratuito da API, os dados enviados podem ser usados pelo provedor, por isso usei apenas textos fictícios.

\- A API gratuita sofre com sobrecarga (erro 503). O código repete a chamada automaticamente algumas vezes e, se continuar falhando, pula o documento.



\## Próximos passos



\- Testar com decisões públicas reais e anonimizadas.

\- Ampliar a avaliação com mais documentos e comparar modelos.

\- Permitir enviar vários arquivos de uma vez na interface web.



\## Autor



Pedro H. dos Santos Corrêa · \[LinkedIn](https://www.linkedin.com/in/pedro-henrique-santos-correa/)

