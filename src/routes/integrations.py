"""
Rotas para gerenciar integrações (Kommo CRM e ChatGPT)
"""
from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.cliente import ConfiguracaoCliente
from src.models.administrador import Administrador
from src.utils.security import login_required, admin_required, cliente_required, sanitizar_entrada
from src.integrations.kommo_crm import test_kommo_connection, create_kommo_client
from src.integrations.chatgpt import test_chatgpt_connection, create_chatgpt_client

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/test/kommo', methods=['POST'])
@login_required
def test_kommo():
    """Testa a conexão com Kommo CRM"""
    try:
        data = request.get_json()
        
        if not data or 'domain' not in data or 'token' not in data:
            return jsonify({'erro': 'Domínio e token são obrigatórios'}), 400
        
        domain = sanitizar_entrada(data['domain'])
        token = sanitizar_entrada(data['token'])
        
        # Testa a conexão
        result = test_kommo_connection(domain, token)
        
        if result['success']:
            return jsonify({
                'sucesso': True,
                'mensagem': result['message'],
                'dados': {
                    'account_name': result.get('account_name'),
                    'account_id': result.get('account_id')
                }
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@integrations_bp.route('/test/chatgpt', methods=['POST'])
@login_required
def test_chatgpt():
    """Testa a conexão com ChatGPT"""
    try:
        data = request.get_json()
        
        if not data or 'api_key' not in data:
            return jsonify({'erro': 'API Key é obrigatória'}), 400
        
        api_key = sanitizar_entrada(data['api_key'])
        model = sanitizar_entrada(data.get('model', 'gpt-3.5-turbo'))
        
        # Testa a conexão
        result = test_chatgpt_connection(api_key, model)
        
        if result['success']:
            return jsonify({
                'sucesso': True,
                'mensagem': result['message'],
                'dados': {
                    'model': result.get('model'),
                    'response': result.get('response')
                }
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@integrations_bp.route('/kommo/pipelines', methods=['GET'])
@cliente_required
def get_kommo_pipelines():
    """Obtém pipelines do Kommo CRM do cliente"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.kommo_token or not config.kommo_domain:
            return jsonify({'erro': 'Configurações do Kommo CRM não encontradas'}), 400
        
        # Cria cliente Kommo
        kommo_client = create_kommo_client(config.kommo_domain, config.kommo_token)
        
        # Obtém pipelines
        pipelines = kommo_client.get_pipelines()
        
        return jsonify({
            'sucesso': True,
            'pipelines': pipelines
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter pipelines: {str(e)}'}), 500

@integrations_bp.route('/kommo/pipeline/<int:pipeline_id>/statuses', methods=['GET'])
@cliente_required
def get_kommo_pipeline_statuses(pipeline_id):
    """Obtém status de um pipeline específico"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.kommo_token or not config.kommo_domain:
            return jsonify({'erro': 'Configurações do Kommo CRM não encontradas'}), 400
        
        # Cria cliente Kommo
        kommo_client = create_kommo_client(config.kommo_domain, config.kommo_token)
        
        # Obtém status do pipeline
        statuses = kommo_client.get_pipeline_statuses(pipeline_id)
        
        return jsonify({
            'sucesso': True,
            'statuses': statuses
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter status do pipeline: {str(e)}'}), 500

@integrations_bp.route('/kommo/leads', methods=['GET'])
@cliente_required
def get_kommo_leads():
    """Obtém leads do Kommo CRM"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.kommo_token or not config.kommo_domain:
            return jsonify({'erro': 'Configurações do Kommo CRM não encontradas'}), 400
        
        # Parâmetros da requisição
        limit = min(int(request.args.get('limit', 50)), 250)
        page = int(request.args.get('page', 1))
        
        # Cria cliente Kommo
        kommo_client = create_kommo_client(config.kommo_domain, config.kommo_token)
        
        # Obtém leads
        leads = kommo_client.get_leads(limit=limit, page=page)
        
        return jsonify({
            'sucesso': True,
            'leads': leads
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao obter leads: {str(e)}'}), 500

@integrations_bp.route('/kommo/lead', methods=['POST'])
@cliente_required
def create_kommo_lead():
    """Cria um novo lead no Kommo CRM"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.kommo_token or not config.kommo_domain:
            return jsonify({'erro': 'Configurações do Kommo CRM não encontradas'}), 400
        
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'erro': 'Nome do lead é obrigatório'}), 400
        
        # Cria cliente Kommo
        kommo_client = create_kommo_client(config.kommo_domain, config.kommo_token)
        
        # Dados do lead
        lead_data = {
            'name': sanitizar_entrada(data['name']),
            'price': data.get('price', 0),
            'pipeline_id': data.get('pipeline_id', config.pipeline_id),
            'status_id': data.get('status_id')
        }
        
        # Remove campos vazios
        lead_data = {k: v for k, v in lead_data.items() if v is not None}
        
        # Cria lead
        result = kommo_client.create_lead(lead_data)
        
        return jsonify({
            'sucesso': True,
            'lead': result
        })
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao criar lead: {str(e)}'}), 500

@integrations_bp.route('/chatgpt/analyze', methods=['POST'])
@cliente_required
def analyze_with_chatgpt():
    """Analisa conteúdo usando ChatGPT"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config or not config.chatgpt_api_key:
            return jsonify({'erro': 'Configurações do ChatGPT não encontradas'}), 400
        
        data = request.get_json()
        
        if not data or 'content' not in data or 'type' not in data:
            return jsonify({'erro': 'Conteúdo e tipo são obrigatórios'}), 400
        
        content = sanitizar_entrada(data['content'])
        analysis_type = sanitizar_entrada(data['type'])
        
        # Cria cliente ChatGPT
        chatgpt_client = create_chatgpt_client(config.chatgpt_api_key, config.chatgpt_model)
        
        # Analisa baseado no tipo
        if analysis_type == 'audio':
            custom_prompt = config.prompt_audio if config.prompt_audio else None
            result = chatgpt_client.analyze_audio_transcript(content, custom_prompt)
        elif analysis_type == 'image':
            custom_prompt = config.prompt_imagem if config.prompt_imagem else None
            result = chatgpt_client.analyze_image_description(content, custom_prompt)
        elif analysis_type == 'intent':
            result = chatgpt_client.classify_lead_intent(content)
        elif analysis_type == 'contact':
            result = chatgpt_client.extract_contact_info(content)
        elif analysis_type == 'response':
            context = data.get('context', '')
            custom_prompt = config.prompt_agente_ia if config.prompt_agente_ia else None
            result = chatgpt_client.generate_sales_response(context, content, custom_prompt)
        else:
            return jsonify({'erro': 'Tipo de análise não suportado'}), 400
        
        if result['success']:
            return jsonify({
                'sucesso': True,
                'analise': result['response'],
                'usage': result.get('usage')
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': f'Erro na análise: {result["error"]}'
            }), 400
            
    except Exception as e:
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

@integrations_bp.route('/admin/test/kommo', methods=['POST'])
@admin_required
def admin_test_kommo():
    """Testa conexão Kommo para administrador"""
    try:
        data = request.get_json()
        
        if not data or 'domain' not in data or 'token' not in data:
            return jsonify({'erro': 'Domínio e token são obrigatórios'}), 400
        
        domain = sanitizar_entrada(data['domain'])
        token = sanitizar_entrada(data['token'])
        
        result = test_kommo_connection(domain, token)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@integrations_bp.route('/admin/test/chatgpt', methods=['POST'])
@admin_required
def admin_test_chatgpt():
    """Testa conexão ChatGPT para administrador"""
    try:
        data = request.get_json()
        
        if not data or 'api_key' not in data:
            return jsonify({'erro': 'API Key é obrigatória'}), 400
        
        api_key = sanitizar_entrada(data['api_key'])
        model = sanitizar_entrada(data.get('model', 'gpt-3.5-turbo'))
        
        result = test_chatgpt_connection(api_key, model)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

