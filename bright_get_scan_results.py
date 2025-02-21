import requests
import json
import csv
import logging
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Classe responsável por autenticação e comunicação com a API da Bright
class BrightAPI:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None

    # Autentica o usuário e obtém o token de acesso
    def autenticar(self):
        logging.info("Autenticando usuário...")
        payload = {"email": self.email, "password": self.password}
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://app.brightsec.com",
            "referer": "https://app.brightsec.com/login"
        }
        response = requests.post(LOGIN_URL, json=payload, headers=headers)
        response.raise_for_status()
        self.token = response.json().get("accessToken")
        logging.info("Autenticação bem-sucedida!")

    # Gera os headers de autorização para as requisições
    def _get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    # Retorna todos os projetos disponíveis para o usuário autenticado
    def obter_projetos(self):
        logging.info("Obtendo lista de projetos...")
        response = requests.get(PROJETOS_URL, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    # Obtém o ID de um projeto com base no nome fornecido
    def obter_id_projeto(self, nome_projeto):
        projetos = self.obter_projetos()
        for projeto in projetos:
            if projeto.get("name") == nome_projeto:
                logging.info(f"Projeto '{nome_projeto}' encontrado com ID: {projeto.get('id')}")
                return projeto.get("id")
        logging.warning(f"Projeto '{nome_projeto}' não encontrado.")
        return None

    # Retorna o ID do scan mais recente para o projeto especificado
    def obter_scan_mais_atual(self, project_id):
        logging.info("Buscando scan mais atual...")
        params = {"projectId[]": project_id}
        response = requests.get(SCANS_URL, headers=self._get_headers(), params=params)
        response.raise_for_status()
        scans = response.json().get("items", [])
        if scans:
            logging.info(f"Scan mais atual encontrado: {scans[0].get('id')}")
            return scans[0].get("id")
        logging.warning("Nenhum scan encontrado para o projeto especificado.")
        return None

    # Retorna as vulnerabilidades do scan 
    def obter_issues_scan(self, scan_id):
        logging.info("Obtendo vulnerabilidades do scan...")
        issues_url = ISSUES_URL_TEMPLATE.format(scan_id)
        response = requests.get(issues_url, headers=self._get_headers())
        response.raise_for_status()
        logging.info("Vulnerabilidades obtidas com sucesso!")
        return response.json()

# Classe responsável por salvar os dados em arquivos JSON e CSV
class FileHandler:

    # Salva os dados fornecidos em um arquivo JSON
    @staticmethod
    def salvar_json(dados, caminho_arquivo):
        logging.info(f"Salvando dados em {caminho_arquivo}...")
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        logging.info("Dados salvos com sucesso em JSON.")

    # Salva os dados fornecidos em um arquivo CSV, com colunas definidas
    @staticmethod
    def salvar_csv(dados, caminho_arquivo):
        logging.info(f"Salvando dados em {caminho_arquivo}...")
        campos_csv = ["name", "severity", "status", "lastReported", "createdAt", "details", "cwe", "certainty"]
        with open(caminho_arquivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos_csv)
            writer.writeheader()
            for vulnerabilidade in dados:
                details = vulnerabilidade.get("details", "")
                # Substitui as quebras de linha por um espaço ou qualquer outro caractere
                details = details.replace("\n", " ")
                
                writer.writerow({
                    "name": vulnerabilidade.get("name"),
                    "severity": vulnerabilidade.get("severity"),
                    "status": vulnerabilidade.get("status"),
                    "lastReported": vulnerabilidade.get("lastReported"),
                    "createdAt": vulnerabilidade.get("createdAt"),
                    "details": details,
                    "cwe": vulnerabilidade.get("cwe"),
                    "certainty": vulnerabilidade.get("certainty")
                })

# Constantes com URLs da API
LOGIN_URL = "https://app.brightsec.com/api/v1/auth/login"
PROJETOS_URL = "https://app.brightsec.com/api/v1/projects"
SCANS_URL = "https://app.brightsec.com/api/v2/scans"
ISSUES_URL_TEMPLATE = "https://app.brightsec.com/api/v1/scans/{}/issues"


# Script principal para executar as operações de autenticação, obtenção de vulnerabilidades e salvamento dos dados.
    
if __name__ == "__main__":
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    if not EMAIL or not PASSWORD:
        logging.error("As variáveis de ambiente EMAIL e PASSWORD não foram encontradas.")
        exit(1)

    try:
        brightsec_api = BrightAPI(EMAIL, PASSWORD)
        brightsec_api.autenticar()

        nome_projeto = input("Digite o nome do projeto: ")
        projeto_id = brightsec_api.obter_id_projeto(nome_projeto)

        if projeto_id:
            scan_id = brightsec_api.obter_scan_mais_atual(projeto_id)
            if scan_id:
                vulnerabilidades = brightsec_api.obter_issues_scan(scan_id)
                FileHandler.salvar_json(vulnerabilidades, f"vulnerabilidades_{nome_projeto}.json")
                FileHandler.salvar_csv(vulnerabilidades, f"vulnerabilidades_{nome_projeto}.csv")
            else:
                logging.error("Não foi possível encontrar um scan para o projeto especificado.")
        else:
            logging.error("ID do projeto não encontrado.")

    except requests.HTTPError as http_err:
        logging.error(f"Erro HTTP: {http_err}")
    except Exception as err:
        logging.error(f"Erro inesperado: {err}")
