import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

st.set_page_config(page_title="Inscrição ACAMP 2025", layout="centered")
st.title("Inscrição ACAMP 2025")

# CSS para fundo com imagem e sobreposição preta
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("/app/static/IDPB.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        position: relative;
    }}
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 0;
    }}
    .stApp > * {{
        position: relative;
        z-index: 1;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Autenticação com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google"], scope)
client = gspread.authorize(creds)
sheet = client.open("ACAMP 2025").sheet1  # Nome da planilha e aba


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

if st.button("Enviar e Ir para Oferta"):
    esportes = [esporte1, esporte2, esporte3]
    esportes_unicos = set([e for e in esportes if e])

    if not nome or not linhagem or not tempo_convertido or not esporte1:
        st.warning("Por favor, preencha os campos obrigatórios.")
    elif len(esportes_unicos) < 3:
        st.warning("Por favor, escolha 3 esportes diferentes.")
    else:
        dados = [
            nome,
            idade,
            igreja,
            linhagem,
            tempo_convertido,
            f"{esporte1}, {esporte2}, {esporte3}",
            conhecimento_midia,
            quiz,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Pendente"
        ]

        # Verifica se a planilha está vazia ou sem cabeçalho na primeira linha
        primeira_linha = sheet.row_values(1)
        cabecalho = [
            "Nome", "Idade", "Igreja", "Linhagem", "Tempo de convertido",
            "Esportes", "Conhecimento em Mídia", "Quiz",
            "DataHora", "Pagamento"
        ]

        if primeira_linha != cabecalho:
            sheet.insert_row(cabecalho, index=1)

        # Sempre adiciona os dados após o cabeçalho
        sheet.append_row(dados)

        st.success("Cadastro salvo com sucesso! Você será redirecionado para o link de pagamento de inscrição.")

        # Redirecionamento automático
        js = "window.location.href = 'https://mpago.la/2yY4qZJ'"
        html = f'<script>{js}</script>'
        components.html(html, height=0)

        # Fallback link visível
        st.markdown("[🔗 Clique aqui se não for redirecionado automaticamente](https://mpago.la/2yY4qZJ)")