"""
Integração com Kommo CRM
"""
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class KommoCRM:
    """Cliente para integração com Kommo CRM"""
    
    def __init__(self, domain: str, access_token: str):
        """
        Inicializa o cliente Kommo CRM
        
        Args:
            domain: Domínio do Kommo (ex: exemplo.kommo.com)
            access_token: Token de acesso da API
        """
        self.domain = domain.replace('https://', '').replace('http://', '')
        self.access_token = access_token
        self.base_url = f"https://{self.domain}/api/v4"
        
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Faz uma requisição para a API do Kommo
        
        Args:
            method: Método HTTP (GET, POST, PATCH, DELETE)
            endpoint: Endpoint da API
            data: Dados para enviar na requisição
            
        Returns:
            Resposta da API
            
        Raises:
            Exception: Se a requisição falhar
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            else:
                return {}
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição para Kommo CRM: {str(e)}")
    
    def get_account_info(self) -> Dict:
        """
        Obtém informações da conta
        
        Returns:
            Informações da conta
        """
        return self._make_request('GET', 'account')
    
    def get_leads(self, limit: int = 250, page: int = 1, filters: Optional[Dict] = None) -> Dict:
        """
        Obtém lista de leads
        
        Args:
            limit: Limite de resultados por página (máximo 250)
            page: Número da página
            filters: Filtros adicionais
            
        Returns:
            Lista de leads
        """
        params = {
            'limit': min(limit, 250),
            'page': page
        }
        
        if filters:
            params.update(filters)
        
        return self._make_request('GET', 'leads', params)
    
    def get_lead(self, lead_id: int) -> Dict:
        """
        Obtém um lead específico
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Dados do lead
        """
        return self._make_request('GET', f'leads/{lead_id}')
    
    def create_lead(self, lead_data: Dict) -> Dict:
        """
        Cria um novo lead
        
        Args:
            lead_data: Dados do lead
            
        Returns:
            Lead criado
        """
        return self._make_request('POST', 'leads', lead_data)
    
    def update_lead(self, lead_id: int, lead_data: Dict) -> Dict:
        """
        Atualiza um lead
        
        Args:
            lead_id: ID do lead
            lead_data: Dados para atualizar
            
        Returns:
            Lead atualizado
        """
        return self._make_request('PATCH', f'leads/{lead_id}', lead_data)
    
    def get_contacts(self, limit: int = 250, page: int = 1, filters: Optional[Dict] = None) -> Dict:
        """
        Obtém lista de contatos
        
        Args:
            limit: Limite de resultados por página
            page: Número da página
            filters: Filtros adicionais
            
        Returns:
            Lista de contatos
        """
        params = {
            'limit': min(limit, 250),
            'page': page
        }
        
        if filters:
            params.update(filters)
        
        return self._make_request('GET', 'contacts', params)
    
    def create_contact(self, contact_data: Dict) -> Dict:
        """
        Cria um novo contato
        
        Args:
            contact_data: Dados do contato
            
        Returns:
            Contato criado
        """
        return self._make_request('POST', 'contacts', contact_data)
    
    def get_pipelines(self) -> Dict:
        """
        Obtém lista de pipelines
        
        Returns:
            Lista de pipelines
        """
        return self._make_request('GET', 'leads/pipelines')
    
    def get_pipeline_statuses(self, pipeline_id: int) -> Dict:
        """
        Obtém status de um pipeline
        
        Args:
            pipeline_id: ID do pipeline
            
        Returns:
            Status do pipeline
        """
        return self._make_request('GET', f'leads/pipelines/{pipeline_id}/statuses')
    
    def move_lead_to_status(self, lead_id: int, status_id: int, pipeline_id: int) -> Dict:
        """
        Move um lead para um status específico
        
        Args:
            lead_id: ID do lead
            status_id: ID do status
            pipeline_id: ID do pipeline
            
        Returns:
            Lead atualizado
        """
        lead_data = {
            'status_id': status_id,
            'pipeline_id': pipeline_id
        }
        
        return self.update_lead(lead_id, lead_data)
    
    def add_note_to_lead(self, lead_id: int, note_text: str, note_type: str = 'common') -> Dict:
        """
        Adiciona uma nota a um lead
        
        Args:
            lead_id: ID do lead
            note_text: Texto da nota
            note_type: Tipo da nota (common, call_in, call_out, etc.)
            
        Returns:
            Nota criada
        """
        note_data = {
            'entity_id': lead_id,
            'entity_type': 'leads',
            'note_type': note_type,
            'params': {
                'text': note_text
            }
        }
        
        return self._make_request('POST', 'leads/notes', note_data)
    
    def search_leads(self, query: str) -> Dict:
        """
        Busca leads por texto
        
        Args:
            query: Texto de busca
            
        Returns:
            Resultados da busca
        """
        params = {'query': query}
        return self._make_request('GET', 'leads', params)
    
    def get_custom_fields(self, entity_type: str = 'leads') -> Dict:
        """
        Obtém campos customizados
        
        Args:
            entity_type: Tipo de entidade (leads, contacts, companies)
            
        Returns:
            Lista de campos customizados
        """
        return self._make_request('GET', f'{entity_type}/custom_fields')


def create_kommo_client(domain: str, access_token: str) -> KommoCRM:
    """
    Cria uma instância do cliente Kommo CRM
    
    Args:
        domain: Domínio do Kommo
        access_token: Token de acesso
        
    Returns:
        Instância do cliente Kommo CRM
    """
    return KommoCRM(domain, access_token)


def test_kommo_connection(domain: str, access_token: str) -> Dict:
    """
    Testa a conexão com o Kommo CRM
    
    Args:
        domain: Domínio do Kommo
        access_token: Token de acesso
        
    Returns:
        Resultado do teste
    """
    try:
        client = create_kommo_client(domain, access_token)
        account_info = client.get_account_info()
        
        return {
            'success': True,
            'message': 'Conexão com Kommo CRM estabelecida com sucesso',
            'account_name': account_info.get('name', 'N/A'),
            'account_id': account_info.get('id', 'N/A')
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Erro ao conectar com Kommo CRM: {str(e)}'
        }

