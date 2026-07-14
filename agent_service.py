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
    """Orquestrador do Agente de Vendas com integração direta e segura com o OpenRouter."""
    
    def __init__(self, api_key: str, model: str):
        # Remove espaços em branco acidentais da chave de API
        self.api_key = api_key.strip() if api_key else ""
        
        # Se o modelo passado for inválido ou vazio, usa um modelo gratuito confiável e atual
        self.model = model.strip() if model else "google/gemini-2.5-flash"
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
            "Seu tom deve ser extremamente profissional, entusiasmado, prestativo e persuasivo.\n\n"
            "### ESTOQUE ATUAL DA CONCESSIONÁRIA:\n"
            f"{inventory_str}\n"
            "### REGRAS DE ATENDIMENTO:\n"
            "1. Sempre tente indicar um dos carros do nosso estoque listados acima.\n"
            "2. Se o cliente pedir um carro fora da lista, diga educadamente que não o temos no momento e ofereça "
            "uma das opções semelhantes que nós temos no estoque real.\n"
            "3. Se o cliente demonstrar intenção de compra ou quiser agendar uma visita, peça educadamente o NOME e o TELEFONE."
        )

    def generate_response(self, chat_history: List[Dict[str, str]]) -> str:
        """Envia o payload para a API do OpenRouter e trata retornos de erro."""
        if not self.api_key:
            return "Erro: Chave de API do OpenRouter não configurada no sistema. Insira a sua chave para continuar."

        messages = [{"role": "system", "content": self.system_prompt}] + chat_history

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
            logger.info(f"Enviando POST para {self.api_url} utilizando o modelo: {self.model}")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=15)
            
            # Se a resposta falhar, tenta capturar detalhes extras enviados pela API do OpenRouter
            if response.status_code != 200:
                try:
                    error_details = response.json()
                    error_msg = error_details.get("error", {}).get("message", "")
                    logger.error(f"Erro da API do OpenRouter: {error_msg}")
                    return f"Erro {response.status_code} retornado pelo OpenRouter: {error_msg if error_msg else 'Verifique se o ID do modelo selecionado está correto.'}"
                except Exception:
                    response.raise_for_status()

            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return "Desculpe, a API do OpenRouter retornou um formato inesperado ou resposta vazia."
                
        except requests.exceptions.HTTPError as http_err:
            return f"Erro HTTP ({response.status_code}): Verifique se a sua API Key é válida e se o modelo '{self.model}' está disponível."
        except Exception as e:
            return f"Não foi possível obter resposta: {str(e)}"
