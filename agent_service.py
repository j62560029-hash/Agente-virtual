import os
import logging
import requests
from typing import Dict, Any, List

# Configuração de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Inventário de veículos da concessionária
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
    """Orquestrador do Agente de Vendas integrado ao OpenRouter com suporte a Cohere."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key.strip() if api_key else ""
        # Modelo padrão caso não venha nenhum valor
        self.model = model.strip() if model else "cohere/command-r-08-2024"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Gera as instruções de comportamento do vendedor e o estoque de carros."""
        inventory_str = ""
        for car in VEHICLE_INVENTORY:
            inventory_str += (
                f"- {car['marca']} {car['modelo']} ({car['ano']}) | "
                f"Combustível: {car['combustivel']} | Preço: R$ {car['preco']:,.2f} | "
                f"Cor: {car['cor']} | Destaque: {car['descricao']}\n"
            )

        return (
            "Você é o 'Consultor AutoDrive', um assistente virtual e consultor de vendas de veículos. "
            "Seu tom deve ser profissional, simpático e muito focado em ajudar o cliente.\n\n"
            "### ESTOQUE ATUAL DA CONCESSIONÁRIA:\n"
            f"{inventory_str}\n"
            "### REGRAS DE ATENDIMENTO:\n"
            "1. Indique sempre os carros do nosso estoque real listados acima.\n"
            "2. Se o cliente pedir um carro que não temos, diga educadamente que não está disponível e sugira uma opção similar do nosso estoque.\n"
            "3. Se ele quiser agendar um teste ou fechar negócio, peça o NOME e o TELEFONE dele para contato."
        )

    def generate_response(self, chat_history: List[Dict[str, str]]) -> str:
        """Envia a conversa para o OpenRouter utilizando o modelo Cohere configurado."""
        if not self.api_key:
            return "Erro: Chave de API do OpenRouter não configurada."

        messages = [{"role": "system", "content": self.system_prompt}] + chat_history

        # Cabeçalhos recomendados pelo OpenRouter para evitar bloqueios ou erros 404/403
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://render.com",  # Identificador opcional útil para o OpenRouter
            "X-Title": "AutoDrive Agent"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3 # Temperatura ligeiramente mais baixa para manter o Cohere focado no estoque
        }

        try:
            logger.info(f"Fazendo chamada via Cohere no OpenRouter utilizando: {self.model}")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=20)
            
            if response.status_code != 200:
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", "Sem detalhes do erro.")
                    return f"Erro {response.status_code} do OpenRouter: {error_detail}"
                except Exception:
                    response.raise_for_status()

            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return "Erro: Resposta retornada da API do OpenRouter está vazia."

        except Exception as e:
            return f"Erro na requisição: {str(e)}"
