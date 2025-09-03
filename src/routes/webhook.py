from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.cliente import Cliente, ConfiguracaoCliente
from src.models.administrador import ControleRequisicoes
from src.utils.security import log_atividade_seguranca
import json

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/sdr', methods=['POST'])
def webhook_sdr():
    """Webhook principal para receber dados do N8N"""
    try:
        # Obter clienteId dos parâmetros da query
        cliente_id = request.args.get('clienteId')
        
        if not cliente_id:
            log_atividade_seguranca(None, 'sistema', 'webhook_sem_cliente_id', request.remote_addr)
            return jsonify({'erro': 'clienteId é obrigatório'}), 400
        
        # Buscar cliente
        cliente = Cliente.query.filter_by(id=cliente_id, ativo=True, aprovado=True).first()
        if not cliente:
            log_atividade_seguranca(None, 'sistema', 'webhook_cliente_invalido', f'Cliente ID: {cliente_id}')
            return jsonify({'erro': 'Cliente não encontrado ou inativo'}), 404
        
        # Verificar controle de requisições
        controle = ControleRequisicoes.query.filter_by(cliente_id=cliente_id, ativo=True).first()
        if controle and not controle.pode_usar_evento():
            log_atividade_seguranca(cliente_id, 'cliente', 'webhook_limite_excedido')
            return jsonify({'erro': 'Limite de eventos excedido'}), 429
        
        # Obter configurações do cliente
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        if not config:
            return jsonify({'erro': 'Configurações do cliente não encontradas'}), 404
        
        # Obter dados do webhook
        webhook_data = request.get_json() or request.form.to_dict()
        
        # Incrementar contador de eventos
        if controle:
            controle.usar_evento()
            db.session.commit()
        
        # Preparar resposta com configurações do cliente
        response_data = {
            'cliente_id': cliente_id,
            'configuracoes': {
                'kommo_token': config.kommo_token,
                'kommo_domain': config.kommo_domain,
                'chatgpt_api_key': config.chatgpt_api_key,
                'chatgpt_model': config.chatgpt_model,
                'pipeline_id': config.pipeline_id,
                'funil_ids': config.get_funil_ids_list(),
                'prompt_agente_ia': config.prompt_agente_ia,
                'prompt_audio': config.prompt_audio,
                'prompt_imagem': config.prompt_imagem,
                'usar_n8n': config.usar_n8n
            },
            'tags_permitidas': [tag.nome for tag in cliente.tags if tag.ativa],
            'webhook_data': webhook_data
        }
        
        log_atividade_seguranca(cliente_id, 'cliente', 'webhook_executado')
        
        return jsonify(response_data), 200
    
    except Exception as e:
        log_atividade_seguranca(None, 'sistema', 'webhook_erro', str(e))
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@webhook_bp.route('/config/<int:cliente_id>', methods=['GET'])
def get_config_cliente(cliente_id):
    """Endpoint para obter configurações de um cliente específico"""
    try:
        # Buscar cliente
        cliente = Cliente.query.filter_by(id=cliente_id, ativo=True, aprovado=True).first()
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        # Obter configurações
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        if not config:
            return jsonify({'erro': 'Configurações não encontradas'}), 404
        
        # Preparar resposta (sem dados sensíveis)
        response_data = {
            'cliente_id': cliente_id,
            'cliente_nome': cliente.nome,
            'configuracoes': {
                'chatgpt_model': config.chatgpt_model,
                'pipeline_id': config.pipeline_id,
                'funil_ids': config.get_funil_ids_list(),
                'usar_n8n': config.usar_n8n,
                'webhook_url': f"/api/webhook/sdr?clienteId={cliente_id}"
            },
            'tags_permitidas': [tag.nome for tag in cliente.tags if tag.ativa]
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@webhook_bp.route('/test/<int:cliente_id>', methods=['POST'])
def test_webhook(cliente_id):
    """Endpoint para testar webhook de um cliente"""
    try:
        # Buscar cliente
        cliente = Cliente.query.filter_by(id=cliente_id, ativo=True, aprovado=True).first()
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        # Dados de teste
        test_data = {
            'test': True,
            'timestamp': request.json.get('timestamp') if request.json else None,
            'message': 'Teste de webhook'
        }
        
        log_atividade_seguranca(cliente_id, 'cliente', 'webhook_teste')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Webhook testado com sucesso',
            'cliente_id': cliente_id,
            'data_teste': test_data
        }), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

