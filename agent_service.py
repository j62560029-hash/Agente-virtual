import os
import logging
import requests
from typing import Dict, Any, List

# Configuração de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Inventário de veículos simulado para o Agente ter como referência real
VEHICLE_INVENTORY = [
    {
        "marca": "Toyota",
        "modelo": "Corolla XEi 2.0",
        "ano": 2023,
        "preco": 145000.00,
        "quilometragem": 18000,
        "combustivel": "Flex",
        "cor": "Prata",
        "descricao": "Sedã médio extremamente confiável, único dono, todas as revisões na concessionária."
    },
    {
        "marca": "Jeep",
        "modelo": "Compass Longitude T270",
        "ano": 2022,
        "preco": 159900.00,
        "quilometragem": 32000,
        "combustivel": "Turbo Flex",
        "cor": "Preto",
        "descricao": "SUV robusto e moderno, teto solar, central multimídia gigante, excelente estado."
    },
    {
        "marca": "BYD",
        "modelo": "Dolphin EV",
        "ano": 2024,
        "preco": 139800.00,
        "quilometragem": 5000,
        "combustivel": "Elétrico",
        "cor": "Cinza",
        "descricao": "100% elétrico, autonomia fantástica, tecnologia de ponta, IPVA pago proporcional."
    },
    {
        "marca": "Chevrolet",
        "modelo": "Onix Hatch Premier 1.0 Turbo",
        "ano": 2022,
        "preco": 89900.00,
        "quilometragem": 25000,
        "combustivel": "Flex",
        "cor": "Branco",
        "descricao": "Muito econômico, Wi-Fi nativo, assistente de estacionamento, ideal para o dia a dia."
    }
]

class SalesAgent:
    """Orquestrador do Agente de Vendas com integração direta com OpenRouter."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        # URL oficial do endpoint do OpenRouter corrigida
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Configura a personalidade do vendedor e passa a lista de veículos."""
        inventory_str = ""
        for car in VEHICLE_INVENTORY:
            inventory_str += (
                f"- {car['marca']} {car['modelo']} ({car['ano']}) | "
                f"Combustível: {car['combustivel']} | Preço: R$ {car['preco']:,.2f} | "
                f"Cor: {car['cor']} | Destaque: {car['descricao']}\n"
            )

        return (
            "Você é o 'Consultor AutoDrive', um assistente virtual e consultor de vendas de veículos. "
            "Seu tom deve ser extremamente profissional, entusiasmado, prestativo e persuasivo.\n\n"
            "### ESTOQUE ATUAL DA CONCESSIONÁRIA:\n"
            f"{inventory_str}\n"
            "### REGRAS DE ATENDIMENTO:\n"
            "1. Sempre tente indicar um dos carros do nosso estoque listados acima.\n"
            "2. Se o cliente pedir um carro fora da lista, diga educadamente que não o temos no momento e ofereça "
            "uma das opções que nós temos no estoque real.\n"
            "3. Se o cliente demonstrar intenção de compra ou quiser agendar uma visita, peça educadamente o NOME e o TELEFONE."
        )

    def generate_response(self, chat_history: List[Dict[str, str]]) -> str:
        """Envia o histórico de mensagens para o OpenRouter e retorna a resposta de vendas."""
        if not self.api_key:
            return "Erro: Chave de API do OpenRouter não configurada no sistema."

        # Garante a inserção das regras do prompt de sistema antes do histórico do usuário
        messages = [{"role": "system", "content": self.system_prompt}] + chat_history

        # Cabeçalhos limpos requisitados pelo protocolo da API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }

        try:
            logger.info(f"Enviando POST para {self.api_url} com o modelo {self.model}")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return "Desculpe, a API do OpenRouter retornou um formato de resposta vazio."
                
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Erro HTTP encontrado: {http_err}")
            return f"Erro de comunicação de rede ({response.status_code}): Certifique-se de que sua chave de API está ativa e que o modelo selecionado é suportado."
        except Exception as e:
            logger.error(f"Erro geral: {e}")
            return f"Ocorreu um erro ao processar sua resposta: {str(e)}"
