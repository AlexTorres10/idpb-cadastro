import streamlit as st
import pandas as pd
import qrcode
import io
import base64
from datetime import datetime

st.set_page_config(page_title="Cadastro + QR Pix", layout="centered")
st.title("Cadastro da Célula e Oferta via Pix")

# --- Formulário ---
nome = st.text_input("Nome completo")
idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
igreja = st.radio("Qual igreja?", ["Sede", "Extensao", "Outra igreja"])
linhagem = st.text_input("Linhagem")
tempo_convertido = st.text_input("Tempo de convertido")

st.markdown("**Esportes (ordem de habilidade)**")
esporte1 = st.selectbox("1º Esporte", ["", "Futebol", "Vôlei", "Natação", "Tênis de mesa"])
esporte2 = st.selectbox("2º Esporte", ["", "Futebol", "Vôlei", "Natação", "Tênis de mesa"])
esporte3 = st.selectbox("3º Esporte", ["", "Futebol", "Vôlei", "Natação", "Tênis de mesa"])

conhecimento_midia = st.radio("Conhecimento em Mídia?", ["Sim", "Não"])
quiz = st.radio("Quiz 'Sou melhor' em:", ["Conhecimentos Gerais", "Conhecimento Bíblico", "Nenhuma das alternativas"])

# --- Processamento ---
if st.button("Enviar e Gerar Pix"):
    # Validação simples
    if not nome or not linhagem or not tempo_convertido or not esporte1:
        st.warning("Por favor, preencha os campos obrigatórios.")
    else:
        data = {
            "Nome": nome,
            "Idade": idade,
            "Igreja": igreja,
            "Linhagem": linhagem,
            "Tempo de convertido": tempo_convertido,
            "Esportes": f"{esporte1}, {esporte2}, {esporte3}",
            "Conhecimento em Mídia": conhecimento_midia,
            "Quiz": quiz,
            "DataHora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Salvar no Excel
        try:
            df = pd.read_excel("cadastros.xlsx")
        except FileNotFoundError:
            df = pd.DataFrame()

        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_excel("cadastros.xlsx", index=False)

        st.success("Cadastro salvo com sucesso!")

        # Geração do QR Pix
        chave_pix = "sua-chave@pix.com"
        nome_loja = "Igreja Local"
        cidade = "Manaus"
        valor = 10.00  # Valor fixo para o exemplo

        payload = f"00020126580014BR.GOV.BCB.PIX01{len(chave_pix):02d}{chave_pix}" \
                  f"5204000053039865802BR5912{nome_loja[:12]}6007{cidade[:7]}62070503***6304"

        qr = qrcode.make(payload)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="Escaneie o QR Pix com seu banco")

        # Baixar planilha se desejar
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="cadastros.csv">📥 Baixar lista de cadastros</a>'
        st.markdown(href, unsafe_allow_html=True)
