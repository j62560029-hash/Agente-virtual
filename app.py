import os
import streamlit as st
from dotenv import load_dotenv
from agent_service import SalesAgent

# Carrega configurações locais do arquivo .env se existir
load_dotenv()

st.set_page_config(
    page_title="AutoDrive | Atendimento",
    page_icon="🚗",
    layout="centered"
)

# Resgata variáveis de ambiente do Render ou do .env local
api_key = os.getenv("OPENROUTER_API_KEY", "")
# Define um modelo gratuito padrão moderno do OpenRouter caso não exista no ambiente
model_env = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Bem-vindo à AutoDrive. 🚗 Como posso te ajudar a encontrar seu carro ideal hoje?"}
    ]

st.title("🚗 AutoDrive — Atendimento Virtual")
st.write("Converse em tempo real com nosso consultor inteligente sobre o nosso estoque.")

# Adiciona controle de seleção de modelo na barra lateral para facilitar testes e evitar erros 404
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    selected_model = st.selectbox(
        "Selecione o Modelo de IA:",
        options=[
            "google/gemini-2.5-flash",
            "meta-llama/llama-3-8b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "google/gemma-2-9b-it:free"
        ],
        index=0
    )
    st.info("Caso o modelo padrão falhe com erro 404, mude o seletor acima para testar outra IA gratuita disponível no OpenRouter.")

# Define o modelo ativo
active_model = selected_model if selected_model else model_env

if not api_key:
    st.error("⚠️ Chave de API do OpenRouter não configurada. Certifique-se de definir a variável 'OPENROUTER_API_KEY' nas configurações de ambiente (Environment) do seu painel do Render ou no arquivo local .env.")
else:
    # Instancia o agente com os parâmetros tratados
    agent = SalesAgent(api_key=api_key, model=active_model)

    # Renderiza o histórico de conversação
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Captura a nova mensagem do usuário
    if user_input := st.chat_input("Digite sua mensagem aqui..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Solicita a resposta do agente inteligente
        with st.chat_message("assistant"):
            with st.spinner("Consultando estoque..."):
                history_payload = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                response = agent.generate_response(history_payload)
                st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
