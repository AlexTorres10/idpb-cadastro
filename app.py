import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import base64
from zoneinfo import ZoneInfo
import time
import random
import csv
import os

# --- Função de background ---
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- Função para append com resiliência ---
def append_com_resiliencia(sheet, dados, tentativas=5):
    for i in range(tentativas):
        try:
            sheet.append_row(dados)
            return True
        except Exception as e:
            espera = (2 ** i) + random.random()
            st.warning(f"Tentando novamente em {espera:.1f} segundos...")
            time.sleep(espera)
    st.error("Tente novamente. O servidor está recebendo muitas inscrições no momento.")
    return False


# --- Configurações iniciais ---
st.set_page_config(page_title="Inscrição ACAMP 2025", layout="centered")

img_base64 = get_base64_of_image("MRJ.png")

# --- Estilo CSS ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
    }}
    html, body, [class*="css"]  {{
        color: white !important;
        background-color: transparent;
    }}
    input, textarea, select, .stButton > button, .stRadio label, .stSelectbox div, .stNumberInput input, .stTextInput input {{
        color: white !important;
    }}
    label, .stMarkdown, .stRadio, .stSelectbox div, .stTextInput, .stNumberInput {{
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Inscrição ACAMP 2025")

# --- Formulário ---
nome = st.text_input("Nome completo")
idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
igreja = st.radio("Qual igreja?", ["Sede (IDPB Redenção)", "Extensão", "Outra igreja"])
linhagem = st.text_input("Linhagem")
tempo_convertido = st.text_input("Tempo de convertido")

st.markdown("**Esportes (ordem de habilidade)**")
esporte1 = st.selectbox("1º Esporte", ["", "Futebol", "Vôlei", "Natação", "Tênis de mesa", "Corrida"])
esporte2 = st.selectbox("2º Esporte", ["", "Futebol", "Vôlei", "Natação", "Tênis de mesa", "Corrida"])
esporte3 = st.selectbox("3º Esporte", ["", "Futebol", "Vôlei", "Natação", "Tênis de mesa", "Corrida"])

conhecimento_midia = st.radio("Possui conhecimento em Mídia?", ["Sim, em social media", "Sim, em gravação e edição de vídeos", "Não"])
quiz = st.radio("Em quiz, sou melhor em:", ["Conhecimentos Gerais", "Conhecimento Bíblico", "Nenhuma das alternativas"])

st.warning("""
> 🔔 **Atenção:** Ao clicar no botão de cadastro, você será automaticamente redirecionado a um link do Mercado Pago para pagar sua inscrição.
""")

# --- Autenticação Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google"], scope)
client = gspread.authorize(creds)
sheet = client.open("ACAMP 2025").sheet1

if st.button("Cadastrar-se e Pagar a Inscrição"):
    esportes = [esporte1, esporte2, esporte3]
    esportes_unicos = set([e for e in esportes if e])

    if not nome or not linhagem or not tempo_convertido or not esporte1:
        st.warning("Por favor, preencha os campos obrigatórios.")
    elif len(esportes_unicos) < 3:
        st.warning("Por favor, escolha 3 esportes diferentes.")
    else:
        hora_manaus = datetime.now(ZoneInfo("America/Manaus"))
        dados = [
            nome,
            idade,
            igreja,
            linhagem,
            tempo_convertido,
            f"{esporte1}, {esporte2}, {esporte3}",
            conhecimento_midia,
            quiz,
            hora_manaus.strftime("%Y-%m-%d %H:%M:%S"),
            "Pendente"
        ]

        # Verifica se a planilha está vazia ou sem cabeçalho na primeira linha
        primeira_linha = sheet.row_values(1)
        cabecalho = [
            "Nome", "Idade", "Igreja", "Linhagem", "Tempo de convertido",
            "Esportes", "Conhecimento em Mídia", "Quiz",
            "Data e Hora", "Pagamento"
        ]

        if primeira_linha != cabecalho:
            sheet.insert_row(cabecalho, index=1)

        if append_com_resiliencia(sheet, dados):

            st.success("Cadastro salvo com sucesso! Você será redirecionado para o link de pagamento de inscrição.")

            st.markdown("""
            <meta http-equiv="refresh" content="0; url=https://mpago.la/2yY4qZJ" />
            <p style='margin-top:10px;'>Se não for redirecionado, <a href="https://mpago.la/2yY4qZJ" target="_blank">clique aqui</a>.</p>
            """, unsafe_allow_html=True)
        else:
            st.warning("Você pode tentar novamente clicando no botão de cadastro.")
