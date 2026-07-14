import os
import streamlit as st
from dotenv import load_dotenv
from agent_service import SalesAgent

# Carrega configurações locais
load_dotenv()

# Configuração da página Streamlit
st.set_page_config(
    page_title="AutoDrive | Atendimento",
    page_icon="🚗",
    layout="centered"
)

# Recupera variáveis de ambiente
api_key = os.getenv("OPENROUTER_API_KEY", "")
model = os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free")

# Inicializa o histórico de conversas
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Bem-vindo à AutoDrive. 🚗 Como posso te ajudar a encontrar seu carro ideal hoje?"}
    ]

st.title("🚗 AutoDrive — Atendimento Virtual")
st.write("Converse em tempo real com nosso consultor inteligente sobre o nosso estoque.")

# Se a chave não estiver configurada no .env, exibe um aviso
if not api_key:
    st.error("Chave de API do OpenRouter não configurada. Verifique o seu arquivo .env.")
else:
    # Instancia o agente
    agent = SalesAgent(api_key=api_key, model=model)

    # Mostra o histórico de mensagens
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Entrada do usuário
    if user_input := st.chat_input("Digite sua mensagem aqui..."):
        # Adiciona a mensagem do usuário na tela e no histórico
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Gera a resposta com o indicador de carregamento
        with st.chat_message("assistant"):
            with st.spinner("Consultando estoque..."):
                # Passa apenas o histórico de mensagens formatado para o agente
                history_payload = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                response = agent.generate_response(history_payload)
                st.write(response)
        
        # Salva a resposta no histórico do estado da sessão
        st.session_state.messages.append({"role": "assistant", "content": response})