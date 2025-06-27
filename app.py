import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

st.set_page_config(page_title="Inscrição ACAMP 2025", layout="centered")
st.title("Inscrição ACAMP 2025")

# Autenticação com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_json = json.loads(st.secrets["google"].to_json())
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_json, scope)
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

if st.button("Cadastrar e Pagar Inscrição"):
    # Validação simples
    if not nome or not linhagem or not tempo_convertido or not esporte1:
        st.warning("Por favor, preencha os campos obrigatórios.")
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

        # Verifica se a planilha está vazia e adiciona cabeçalho
        if len(sheet.get_all_values()) == 0:
            cabecalho = [
                "Nome", "Idade", "Igreja", "Linhagem", "Tempo de convertido",
                "Esportes", "Conhecimento em Mídia", "Quiz",
                "Data e Hora", "Pagamento"
            ]
            sheet.append_row(cabecalho)

        sheet.append_row(dados)

        st.success("Cadastro salvo com sucesso! Você será redirecionado para a página de oferta.")

        # Redirecionamento automático
        js = "window.location.href = 'https://mpago.la/2yY4qZJ'"
        html = f'<script>{js}</script>'
        components.html(html, height=0)

        # Fallback link visível
        st.markdown("[🔗 Clique aqui se não for redirecionado automaticamente](https://mpago.la/2yY4qZJ)")