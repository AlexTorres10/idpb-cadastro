import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import base64
from zoneinfo import ZoneInfo

def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

st.set_page_config(page_title="Inscrição ACAMP 2025", layout="centered")
st.title("Inscrição ACAMP 2025")
img_base64 = get_base64_of_image("IDPB.png")

# CSS para fundo com imagem e sobreposição preta
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
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

st.warning("""
> 🔔 **Atenção:** Ao clicar no botão de cadastro, você será automaticamente redirecionado a um link do Mercado Pago para pagar sua inscrição.
""")

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

        # Sempre adiciona os dados após o cabeçalho
        sheet.append_row(dados)

        st.success("Cadastro salvo com sucesso! Você será redirecionado para o link de pagamento de inscrição.")

        st.markdown("""
        <meta http-equiv="refresh" content="0; url=https://mpago.la/2yY4qZJ" />
        <p style='margin-top:10px;'>Se não for redirecionado, <a href="https://mpago.la/2yY4qZJ" target="_blank">clique aqui</a>.</p>
        """, unsafe_allow_html=True)
