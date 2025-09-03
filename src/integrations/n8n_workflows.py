"""
Integração com workflows n8n
"""
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class N8NWorkflowManager:
    """Gerenciador de workflows n8n"""
    
    def __init__(self, n8n_base_url: str, api_key: Optional[str] = None):
        """
        Inicializa o gerenciador de workflows n8n
        
        Args:
            n8n_base_url: URL base do n8n (ex: https://n8n.exemplo.com)
            api_key: Chave da API do n8n (opcional)
        """
        self.base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Faz uma requisição para a API do n8n
        
        Args:
            method: Método HTTP
            endpoint: Endpoint da API
            data: Dados para enviar
            
        Returns:
            Resposta da API
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
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
            raise Exception(f"Erro na requisição para n8n: {str(e)}")
    
    def trigger_webhook(self, webhook_path: str, data: Dict) -> Dict:
        """
        Dispara um webhook do n8n
        
        Args:
            webhook_path: Caminho do webhook
            data: Dados para enviar
            
        Returns:
            Resposta do webhook
        """
        webhook_url = f"{self.base_url}/webhook/{webhook_path}"
        
        try:
            response = requests.post(webhook_url, json=data)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            else:
                return {'success': True}
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao disparar webhook: {str(e)}")
    
    def get_workflows(self) -> List[Dict]:
        """
        Obtém lista de workflows
        
        Returns:
            Lista de workflows
        """
        return self._make_request('GET', '/api/v1/workflows')
    
    def get_workflow(self, workflow_id: str) -> Dict:
        """
        Obtém um workflow específico
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            Dados do workflow
        """
        return self._make_request('GET', f'/api/v1/workflows/{workflow_id}')
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """
        Ativa um workflow
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            Resultado da ativação
        """
        return self._make_request('POST', f'/api/v1/workflows/{workflow_id}/activate')
    
    def deactivate_workflow(self, workflow_id: str) -> Dict:
        """
        Desativa um workflow
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            Resultado da desativação
        """
        return self._make_request('POST', f'/api/v1/workflows/{workflow_id}/deactivate')
    
    def get_executions(self, workflow_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """
        Obtém execuções de workflows
        
        Args:
            workflow_id: ID do workflow (opcional)
            limit: Limite de resultados
            
        Returns:
            Lista de execuções
        """
        params = {'limit': limit}
        if workflow_id:
            params['workflowId'] = workflow_id
        
        return self._make_request('GET', '/api/v1/executions', params)


class SDRWorkflowProcessor:
    """Processador específico para workflows SDR"""
    
    def __init__(self, n8n_manager: N8NWorkflowManager, app_base_url: str):
        """
        Inicializa o processador de workflows SDR
        
        Args:
            n8n_manager: Instância do gerenciador n8n
            app_base_url: URL base da aplicação
        """
        self.n8n = n8n_manager
        self.app_base_url = app_base_url.rstrip('/')
    
    def process_whatsapp_message(self, cliente_id: int, message_data: Dict) -> Dict:
        """
        Processa mensagem do WhatsApp através do workflow SDR
        
        Args:
            cliente_id: ID do cliente
            message_data: Dados da mensagem
            
        Returns:
            Resultado do processamento
        """
        webhook_data = {
            'cliente_id': cliente_id,
            'webhook_url': f"{self.app_base_url}/api/webhook/sdr",
            'message_data': message_data,
            'timestamp': datetime.now().isoformat(),
            'action': 'process_message'
        }
        
        try:
            result = self.n8n.trigger_webhook('sdr-webhook', webhook_data)
            return {
                'success': True,
                'result': result,
                'message': 'Mensagem processada com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erro ao processar mensagem'
            }
    
    def change_lead_stage(self, cliente_id: int, lead_data: Dict, new_stage: str) -> Dict:
        """
        Muda etapa de um lead através do workflow
        
        Args:
            cliente_id: ID do cliente
            lead_data: Dados do lead
            new_stage: Nova etapa
            
        Returns:
            Resultado da mudança
        """
        webhook_data = {
            'cliente_id': cliente_id,
            'webhook_url': f"{self.app_base_url}/api/webhook/sdr",
            'lead_data': lead_data,
            'new_stage': new_stage,
            'timestamp': datetime.now().isoformat(),
            'action': 'change_stage'
        }
        
        try:
            result = self.n8n.trigger_webhook('muda-etapa-webhook', webhook_data)
            return {
                'success': True,
                'result': result,
                'message': 'Etapa alterada com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erro ao alterar etapa'
            }
    
    def process_audio_message(self, cliente_id: int, audio_data: Dict) -> Dict:
        """
        Processa mensagem de áudio através do workflow
        
        Args:
            cliente_id: ID do cliente
            audio_data: Dados do áudio
            
        Returns:
            Resultado do processamento
        """
        webhook_data = {
            'cliente_id': cliente_id,
            'webhook_url': f"{self.app_base_url}/api/webhook/sdr",
            'audio_data': audio_data,
            'timestamp': datetime.now().isoformat(),
            'action': 'process_audio'
        }
        
        try:
            result = self.n8n.trigger_webhook('sdr-webhook', webhook_data)
            return {
                'success': True,
                'result': result,
                'message': 'Áudio processado com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erro ao processar áudio'
            }
    
    def process_image_message(self, cliente_id: int, image_data: Dict) -> Dict:
        """
        Processa mensagem de imagem através do workflow
        
        Args:
            cliente_id: ID do cliente
            image_data: Dados da imagem
            
        Returns:
            Resultado do processamento
        """
        webhook_data = {
            'cliente_id': cliente_id,
            'webhook_url': f"{self.app_base_url}/api/webhook/sdr",
            'image_data': image_data,
            'timestamp': datetime.now().isoformat(),
            'action': 'process_image'
        }
        
        try:
            result = self.n8n.trigger_webhook('sdr-webhook', webhook_data)
            return {
                'success': True,
                'result': result,
                'message': 'Imagem processada com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erro ao processar imagem'
            }


def create_n8n_manager(base_url: str, api_key: Optional[str] = None) -> N8NWorkflowManager:
    """
    Cria uma instância do gerenciador n8n
    
    Args:
        base_url: URL base do n8n
        api_key: Chave da API (opcional)
        
    Returns:
        Instância do gerenciador n8n
    """
    return N8NWorkflowManager(base_url, api_key)


def create_sdr_processor(n8n_base_url: str, app_base_url: str, 
                        api_key: Optional[str] = None) -> SDRWorkflowProcessor:
    """
    Cria uma instância do processador SDR
    
    Args:
        n8n_base_url: URL base do n8n
        app_base_url: URL base da aplicação
        api_key: Chave da API n8n (opcional)
        
    Returns:
        Instância do processador SDR
    """
    n8n_manager = create_n8n_manager(n8n_base_url, api_key)
    return SDRWorkflowProcessor(n8n_manager, app_base_url)


def test_n8n_connection(base_url: str, api_key: Optional[str] = None) -> Dict:
    """
    Testa a conexão com n8n
    
    Args:
        base_url: URL base do n8n
        api_key: Chave da API (opcional)
        
    Returns:
        Resultado do teste
    """
    try:
        manager = create_n8n_manager(base_url, api_key)
        workflows = manager.get_workflows()
        
        return {
            'success': True,
            'message': 'Conexão com n8n estabelecida com sucesso',
            'workflows_count': len(workflows) if workflows else 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Erro ao conectar com n8n: {str(e)}'
        }

