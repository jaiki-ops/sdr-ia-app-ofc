"""
Rotas para gerenciar workflows n8n
"""
from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.cliente import Cliente, ConfiguracaoCliente
from src.models.administrador import Administrador
from src.utils.security import login_required, admin_required, cliente_required, sanitizar_entrada
from src.integrations.n8n_workflows import create_sdr_processor, test_n8n_connection
import os

n8n_bp = Blueprint('n8n', __name__)

@n8n_bp.route('/test', methods=['POST'])
@admin_required
def test_n8n():
    """Testa a conexão com n8n"""
    try:
        data = request.get_json()
        
        if not data or 'base_url' not in data:
            return jsonify({'erro': 'URL base do n8n é obrigatória'}), 400
        
        base_url = sanitizar_entrada(data['base_url'])
        api_key = sanitizar_entrada(data.get('api_key', '')) or None
        
        # Testa a conexão
        result = test_n8n_connection(base_url, api_key)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@n8n_bp.route('/process/message', methods=['POST'])
@cliente_required
def process_message():
    """Processa mensagem através do workflow n8n"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.usar_n8n:
            return jsonify({'erro': 'N8N não está habilitado para este cliente'}), 400
        
        data = request.get_json()
        
        if not data or 'message_data' not in data:
            return jsonify({'erro': 'Dados da mensagem são obrigatórios'}), 400
        
        # Configurações do n8n (podem vir do ambiente ou configuração)
        n8n_base_url = os.environ.get('N8N_BASE_URL', 'https://n8n.exemplo.com')
        app_base_url = os.environ.get('APP_BASE_URL', 'https://sdria.alveseco.com.br')
        n8n_api_key = os.environ.get('N8N_API_KEY')
        
        # Cria processador SDR
        processor = create_sdr_processor(n8n_base_url, app_base_url, n8n_api_key)
        
        # Processa mensagem
        result = processor.process_whatsapp_message(cliente_id, data['message_data'])
        
        if result['success']:
            return jsonify({
                'sucesso': True,
                'mensagem': result['message'],
                'resultado': result.get('result')
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': result['message'],
                'erro': result.get('error')
            }), 400
            
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@n8n_bp.route('/process/audio', methods=['POST'])
@cliente_required
def process_audio():
    """Processa áudio através do workflow n8n"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.usar_n8n:
            return jsonify({'erro': 'N8N não está habilitado para este cliente'}), 400
        
        data = request.get_json()
        
        if not data or 'audio_data' not in data:
            return jsonify({'erro': 'Dados do áudio são obrigatórios'}), 400
        
        # Configurações do n8n
        n8n_base_url = os.environ.get('N8N_BASE_URL', 'https://n8n.exemplo.com')
        app_base_url = os.environ.get('APP_BASE_URL', 'https://sdria.alveseco.com.br')
        n8n_api_key = os.environ.get('N8N_API_KEY')
        
        # Cria processador SDR
        processor = create_sdr_processor(n8n_base_url, app_base_url, n8n_api_key)
        
        # Processa áudio
        result = processor.process_audio_message(cliente_id, data['audio_data'])
        
        if result['success']:
            return jsonify({
                'sucesso': True,
                'mensagem': result['message'],
                'resultado': result.get('result')
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': result['message'],
                'erro': result.get('error')
            }), 400
            
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@n8n_bp.route('/process/image', methods=['POST'])
@cliente_required
def process_image():
    """Processa imagem através do workflow n8n"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.usar_n8n:
            return jsonify({'erro': 'N8N não está habilitado para este cliente'}), 400
        
        data = request.get_json()
        
        if not data or 'image_data' not in data:
            return jsonify({'erro': 'Dados da imagem são obrigatórios'}), 400
        
        # Configurações do n8n
        n8n_base_url = os.environ.get('N8N_BASE_URL', 'https://n8n.exemplo.com')
        app_base_url = os.environ.get('APP_BASE_URL', 'https://sdria.alveseco.com.br')
        n8n_api_key = os.environ.get('N8N_API_KEY')
        
        # Cria processador SDR
        processor = create_sdr_processor(n8n_base_url, app_base_url, n8n_api_key)
        
        # Processa imagem
        result = processor.process_image_message(cliente_id, data['image_data'])
        
        if result['success']:
            return jsonify({
                'sucesso': True,
                'mensagem': result['message'],
                'resultado': result.get('result')
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': result['message'],
                'erro': result.get('error')
            }), 400
            
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@n8n_bp.route('/change-stage', methods=['POST'])
@cliente_required
def change_lead_stage():
    """Muda etapa de um lead através do workflow n8n"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.usar_n8n:
            return jsonify({'erro': 'N8N não está habilitado para este cliente'}), 400
        
        data = request.get_json()
        
        if not data or 'lead_data' not in data or 'new_stage' not in data:
            return jsonify({'erro': 'Dados do lead e nova etapa são obrigatórios'}), 400
        
        # Configurações do n8n
        n8n_base_url = os.environ.get('N8N_BASE_URL', 'https://n8n.exemplo.com')
        app_base_url = os.environ.get('APP_BASE_URL', 'https://sdria.alveseco.com.br')
        n8n_api_key = os.environ.get('N8N_API_KEY')
        
        # Cria processador SDR
        processor = create_sdr_processor(n8n_base_url, app_base_url, n8n_api_key)
        
        # Muda etapa
        result = processor.change_lead_stage(
            cliente_id, 
            data['lead_data'], 
            sanitizar_entrada(data['new_stage'])
        )
        
        if result['success']:
            return jsonify({
                'sucesso': True,
                'mensagem': result['message'],
                'resultado': result.get('result')
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': result['message'],
                'erro': result.get('error')
            }), 400
            
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@n8n_bp.route('/webhook-url/<int:cliente_id>', methods=['GET'])
@login_required
def get_webhook_url(cliente_id):
    """Obtém URL do webhook para um cliente"""
    try:
        # Verificar se é admin ou o próprio cliente
        user_type = session.get('tipo_usuario')
        user_id = session.get('usuario_id')
        
        if user_type != 'administrador' and user_id != cliente_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        # Buscar cliente
        cliente = Cliente.query.filter_by(id=cliente_id, ativo=True).first()
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        # URL base da aplicação
        app_base_url = os.environ.get('APP_BASE_URL', 'https://sdria.alveseco.com.br')
        
        webhook_urls = {
            'sdr_webhook': f"{app_base_url}/api/webhook/sdr?clienteId={cliente_id}",
            'config_webhook': f"{app_base_url}/api/webhook/config/{cliente_id}",
            'test_webhook': f"{app_base_url}/api/webhook/test/{cliente_id}",
            'n8n_webhooks': {
                'sdr_webhook_path': 'sdr-webhook',
                'muda_etapa_webhook_path': 'muda-etapa-webhook'
            }
        }
        
        return jsonify({
            'sucesso': True,
            'cliente_id': cliente_id,
            'webhook_urls': webhook_urls
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@n8n_bp.route('/status/<int:cliente_id>', methods=['GET'])
@login_required
def get_n8n_status(cliente_id):
    """Obtém status do n8n para um cliente"""
    try:
        # Verificar se é admin ou o próprio cliente
        user_type = session.get('tipo_usuario')
        user_id = session.get('usuario_id')
        
        if user_type != 'administrador' and user_id != cliente_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        # Buscar configurações
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        status = {
            'n8n_habilitado': config.usar_n8n if config else False,
            'configurado': bool(config and config.usar_n8n),
            'webhook_url': f"/api/webhook/sdr?clienteId={cliente_id}",
            'workflows_disponiveis': [
                'SDR WHATSAPP IA - DINÂMICO',
                'MUDA ETAPA IA TAG - DINÂMICO'
            ]
        }
        
        return jsonify({
            'sucesso': True,
            'status': status
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

