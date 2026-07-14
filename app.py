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

# Resgata as variáveis de ambiente (do Render ou do .env)
api_key = os.getenv("OPENROUTER_API_KEY", "")
# Define o modelo padrão da Cohere caso não esteja configurado no ambiente
model_env = os.getenv("OPENROUTER_MODEL", "cohere/command-r-08-2024")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Bem-vindo à AutoDrive. 🚗 Como posso te ajudar a encontrar seu carro ideal hoje?"}
    ]

st.title("🚗 AutoDrive — Atendimento Virtual")
st.write("Converse em tempo real com nosso consultor inteligente sobre o nosso estoque.")

# Barra lateral para controle de modelos da Cohere e alternativas
with st.sidebar:
    st.markdown("### ⚙️ Configurações de IA")
    selected_model = st.selectbox(
        "Selecione o Modelo:",
        options=[
            "cohere/command-r-08-2024",
            "cohere/command-r-plus-08-2024",
            "google/gemini-2.5-flash",
            "meta-llama/llama-3.3-70b-instruct:free"
        ],
        index=0  # Mantém o Cohere Command R como primeira opção padrão
    )
    st.info("O Command R da Cohere é excelente para entender o estoque e manter conversas fluidas com os clientes!")

# Define o modelo ativo
active_model = selected_model if selected_model else model_env

if not api_key:
    st.error("⚠️ Chave de API do OpenRouter não encontrada. Configure a variável 'OPENROUTER_API_KEY' nas configurações de ambiente (Environment) do painel do Render.")
else:
    # Instancia o agente de vendas
    agent = SalesAgent(api_key=api_key, model=active_model)

    # Exibe o histórico de conversa
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Entrada do usuário
    if user_input := st.chat_input("Digite sua mensagem aqui..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Gera a resposta com o assistente
        with st.chat_message("assistant"):
            with st.spinner("Consultando estoque..."):
                history_payload = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                response = agent.generate_response(history_payload)
                st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
