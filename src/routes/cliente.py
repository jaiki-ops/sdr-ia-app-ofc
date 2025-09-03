from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.cliente import Cliente, ConfiguracaoCliente, TagCliente
from src.models.administrador import ControleRequisicoes
from src.utils.security import cliente_required, login_required, validar_entrada_segura, sanitizar_entrada, log_atividade_seguranca
import json

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/perfil', methods=['GET'])
@cliente_required
def get_perfil():
    """Obter perfil do cliente logado"""
    try:
        cliente_id = session['usuario_id']
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        return jsonify({
            'cliente': cliente.to_dict(),
            'configuracoes': cliente.configuracoes.to_dict() if cliente.configuracoes else None,
            'tags': [tag.to_dict() for tag in cliente.tags],
            'webhook_url': f"/api/webhook/sdr?clienteId={cliente_id}"
        })
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@cliente_bp.route('/perfil', methods=['PUT'])
@cliente_required
def atualizar_perfil():
    """Atualizar perfil do cliente"""
    try:
        cliente_id = session['usuario_id']
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        data = request.get_json()
        
        # Validar entrada
        valido, mensagem = validar_entrada_segura(
            data,
            campos_obrigatorios=['nome', 'email'],
            tamanho_max={'nome': 100, 'email': 120, 'telefone': 20, 'empresa': 100, 'cnpj': 18, 'razao_social': 200}
        )
        
        if not valido:
            return jsonify({'erro': mensagem}), 400
        
        # Atualizar campos
        cliente.nome = sanitizar_entrada(data['nome'])
        cliente.telefone = sanitizar_entrada(data.get('telefone', ''))
        cliente.empresa = sanitizar_entrada(data.get('empresa', ''))
        cliente.cnpj = sanitizar_entrada(data.get('cnpj', ''))
        cliente.razao_social = sanitizar_entrada(data.get('razao_social', ''))
        
        # Verificar se email já existe (exceto o próprio)
        if data['email'] != cliente.email:
            email_existente = Cliente.query.filter(
                Cliente.email == data['email'],
                Cliente.id != cliente_id
            ).first()
            
            if email_existente:
                return jsonify({'erro': 'Email já está em uso'}), 409
            
            cliente.email = sanitizar_entrada(data['email'])
        
        db.session.commit()
        
        log_atividade_seguranca(cliente_id, 'cliente', 'perfil_atualizado')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Perfil atualizado com sucesso',
            'cliente': cliente.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@cliente_bp.route('/configuracoes', methods=['GET'])
@cliente_required
def get_configuracoes():
    """Obter configurações do cliente"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config:
            # Criar configuração padrão
            config = ConfiguracaoCliente(cliente_id=cliente_id)
            db.session.add(config)
            db.session.commit()
        
        return jsonify(config.to_dict())
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@cliente_bp.route('/configuracoes', methods=['PUT'])
@cliente_required
def atualizar_configuracoes():
    """Atualizar configurações do cliente"""
    try:
        cliente_id = session['usuario_id']
        config = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        
        if not config:
            config = ConfiguracaoCliente(cliente_id=cliente_id)
            db.session.add(config)
        
        data = request.get_json()
        
        # Atualizar configurações
        if 'kommo_token' in data:
            config.kommo_token = sanitizar_entrada(data['kommo_token'])
        
        if 'kommo_domain' in data:
            config.kommo_domain = sanitizar_entrada(data['kommo_domain'])
        
        if 'chatgpt_api_key' in data:
            config.chatgpt_api_key = sanitizar_entrada(data['chatgpt_api_key'])
        
        if 'chatgpt_model' in data:
            config.chatgpt_model = sanitizar_entrada(data['chatgpt_model'])
        
        if 'pipeline_id' in data:
            config.pipeline_id = sanitizar_entrada(data['pipeline_id'])
        
        if 'funil_ids' in data:
            config.set_funil_ids_list(data['funil_ids'])
        
        if 'prompt_agente_ia' in data:
            config.prompt_agente_ia = sanitizar_entrada(data['prompt_agente_ia'])
        
        if 'prompt_audio' in data:
            config.prompt_audio = sanitizar_entrada(data['prompt_audio'])
        
        if 'prompt_imagem' in data:
            config.prompt_imagem = sanitizar_entrada(data['prompt_imagem'])
        
        if 'aprovacao_automatica' in data:
            config.aprovacao_automatica = bool(data['aprovacao_automatica'])
        
        if 'usar_n8n' in data:
            config.usar_n8n = bool(data['usar_n8n'])
        
        db.session.commit()
        
        log_atividade_seguranca(cliente_id, 'cliente', 'configuracoes_atualizadas')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Configurações atualizadas com sucesso',
            'configuracoes': config.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@cliente_bp.route('/tags', methods=['GET'])
@cliente_required
def get_tags():
    """Obter tags do cliente"""
    try:
        cliente_id = session['usuario_id']
        tags = TagCliente.query.filter_by(cliente_id=cliente_id).all()
        
        return jsonify([tag.to_dict() for tag in tags])
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@cliente_bp.route('/tags', methods=['POST'])
@cliente_required
def criar_tag():
    """Criar nova tag"""
    try:
        cliente_id = session['usuario_id']
        data = request.get_json()
        
        # Validar entrada
        valido, mensagem = validar_entrada_segura(
            data,
            campos_obrigatorios=['nome', 'funil_id', 'pipeline_id'],
            tamanho_max={'nome': 100, 'funil_id': 50, 'pipeline_id': 50}
        )
        
        if not valido:
            return jsonify({'erro': mensagem}), 400
        
        # Verificar se tag já existe
        tag_existente = TagCliente.query.filter_by(
            cliente_id=cliente_id,
            nome=data['nome']
        ).first()
        
        if tag_existente:
            return jsonify({'erro': 'Tag já existe'}), 409
        
        # Criar nova tag
        tag = TagCliente(
            cliente_id=cliente_id,
            nome=sanitizar_entrada(data['nome']),
            funil_id=sanitizar_entrada(data['funil_id']),
            pipeline_id=sanitizar_entrada(data['pipeline_id']),
            ativa=data.get('ativa', True)
        )
        
        db.session.add(tag)
        db.session.commit()
        
        log_atividade_seguranca(cliente_id, 'cliente', 'tag_criada', f'Tag: {tag.nome}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Tag criada com sucesso',
            'tag': tag.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@cliente_bp.route('/tags/<int:tag_id>', methods=['PUT'])
@cliente_required
def atualizar_tag(tag_id):
    """Atualizar tag"""
    try:
        cliente_id = session['usuario_id']
        tag = TagCliente.query.filter_by(id=tag_id, cliente_id=cliente_id).first()
        
        if not tag:
            return jsonify({'erro': 'Tag não encontrada'}), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'nome' in data:
            tag.nome = sanitizar_entrada(data['nome'])
        
        if 'funil_id' in data:
            tag.funil_id = sanitizar_entrada(data['funil_id'])
        
        if 'pipeline_id' in data:
            tag.pipeline_id = sanitizar_entrada(data['pipeline_id'])
        
        if 'ativa' in data:
            tag.ativa = bool(data['ativa'])
        
        db.session.commit()
        
        log_atividade_seguranca(cliente_id, 'cliente', 'tag_atualizada', f'Tag: {tag.nome}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Tag atualizada com sucesso',
            'tag': tag.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@cliente_bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@cliente_required
def deletar_tag(tag_id):
    """Deletar tag"""
    try:
        cliente_id = session['usuario_id']
        tag = TagCliente.query.filter_by(id=tag_id, cliente_id=cliente_id).first()
        
        if not tag:
            return jsonify({'erro': 'Tag não encontrada'}), 404
        
        nome_tag = tag.nome
        db.session.delete(tag)
        db.session.commit()
        
        log_atividade_seguranca(cliente_id, 'cliente', 'tag_deletada', f'Tag: {nome_tag}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Tag deletada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@cliente_bp.route('/estatisticas', methods=['GET'])
@cliente_required
def get_estatisticas():
    """Obter estatísticas do cliente"""
    try:
        cliente_id = session['usuario_id']
        
        # Buscar controle de requisições
        controle = ControleRequisicoes.query.filter_by(cliente_id=cliente_id, ativo=True).first()
        
        # Contar tags
        total_tags = TagCliente.query.filter_by(cliente_id=cliente_id).count()
        tags_ativas = TagCliente.query.filter_by(cliente_id=cliente_id, ativa=True).count()
        
        estatisticas = {
            'eventos': {
                'limite_total': controle.limite_eventos if controle else 0,
                'utilizados': controle.eventos_utilizados if controle else 0,
                'restantes': controle.eventos_restantes() if controle else 0
            },
            'tags': {
                'total': total_tags,
                'ativas': tags_ativas,
                'inativas': total_tags - tags_ativas
            },
            'webhook_url': f"https://webhook.com/sdr?clienteId={cliente_id}"
        }
        
        return jsonify(estatisticas)
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

