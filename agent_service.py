import os
import logging
import requests
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Estoque real de veículos da AutoDrive
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
    """Orquestrador do Agente de Vendas."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        inventory_str = ""
        for car in VEHICLE_INVENTORY:
            inventory_str += (
                f"- {car['marca']} {car['modelo']} ({car['ano']}) | "
                f"Combustível: {car['combustivel']} | Preço: R$ {car['preco']:,.2f} | "
                f"Cor: {car['cor']} | Destaque: {car['descricao']}\n"
            )

        return (
            "Você é o 'Consultor AutoDrive', um assistente virtual de vendas de veículos. "
            "Seu tom deve ser profissional, prestativo e focado em fechar negócios.\n\n"
            "### ESTOQUE ATUAL DA CONCESSIONÁRIA:\n"
            f"{inventory_str}\n"
            "### REGRAS:\n"
            "1. Sempre direcione o cliente para os carros do estoque acima.\n"
            "2. Se ele pedir um carro fora da lista, diga que não tem e ofereça um similar da lista.\n"
            "3. Se ele demonstrar interesse real, peça o NOME e o TELEFONE para agendamento."
        )

    def generate_response(self, chat_history: List[Dict[str, str]]) -> str:
        if not self.api_key:
            return "Erro: Configure a sua chave de API do OpenRouter."

        messages = [{"role": "system", "content": self.system_prompt}] + chat_history

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Erro de conexão com o OpenRouter: {e}"