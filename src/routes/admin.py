from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.cliente import Cliente, ConfiguracaoCliente, TagCliente
from src.models.administrador import Administrador, ControleRequisicoes, LogAtividade
from src.utils.security import admin_required, super_admin_required, validar_entrada_segura, sanitizar_entrada, log_atividade_seguranca
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """Dashboard do administrador"""
    try:
        # Estatísticas gerais
        total_clientes = Cliente.query.count()
        clientes_ativos = Cliente.query.filter_by(ativo=True).count()
        clientes_aprovados = Cliente.query.filter_by(aprovado=True).count()
        clientes_pendentes = Cliente.query.filter_by(aprovado=False, ativo=True).count()
        
        # Estatísticas de eventos
        total_eventos = db.session.query(func.sum(ControleRequisicoes.eventos_utilizados)).scalar() or 0
        
        # Atividades recentes (últimas 24h)
        ontem = datetime.utcnow() - timedelta(days=1)
        atividades_recentes = LogAtividade.query.filter(
            LogAtividade.data_criacao >= ontem
        ).order_by(LogAtividade.data_criacao.desc()).limit(10).all()
        
        dashboard = {
            'clientes': {
                'total': total_clientes,
                'ativos': clientes_ativos,
                'aprovados': clientes_aprovados,
                'pendentes': clientes_pendentes
            },
            'eventos': {
                'total_utilizados': total_eventos
            },
            'atividades_recentes': [atividade.to_dict() for atividade in atividades_recentes]
        }
        
        return jsonify(dashboard)
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/clientes', methods=['GET'])
@admin_required
def get_clientes():
    """Listar todos os clientes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')  # 'ativo', 'inativo', 'aprovado', 'pendente'
        
        query = Cliente.query
        
        # Filtros
        if status == 'ativo':
            query = query.filter_by(ativo=True)
        elif status == 'inativo':
            query = query.filter_by(ativo=False)
        elif status == 'aprovado':
            query = query.filter_by(aprovado=True)
        elif status == 'pendente':
            query = query.filter_by(aprovado=False)
        
        clientes = query.order_by(Cliente.data_criacao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'clientes': [cliente.to_dict() for cliente in clientes.items],
            'total': clientes.total,
            'pages': clientes.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/clientes/<int:cliente_id>', methods=['GET'])
@admin_required
def get_cliente_detalhes(cliente_id):
    """Obter detalhes de um cliente específico"""
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        # Buscar configurações e controle de requisições
        configuracoes = ConfiguracaoCliente.query.filter_by(cliente_id=cliente_id).first()
        controle = ControleRequisicoes.query.filter_by(cliente_id=cliente_id).first()
        tags = TagCliente.query.filter_by(cliente_id=cliente_id).all()
        
        # Atividades recentes do cliente
        atividades = LogAtividade.query.filter_by(
            usuario_id=cliente_id,
            tipo_usuario='cliente'
        ).order_by(LogAtividade.data_criacao.desc()).limit(20).all()
        
        detalhes = {
            'cliente': cliente.to_dict(),
            'configuracoes': configuracoes.to_dict() if configuracoes else None,
            'controle_requisicoes': controle.to_dict() if controle else None,
            'tags': [tag.to_dict() for tag in tags],
            'atividades_recentes': [atividade.to_dict() for atividade in atividades]
        }
        
        return jsonify(detalhes)
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/clientes/<int:cliente_id>/aprovar', methods=['POST'])
@admin_required
def aprovar_cliente(cliente_id):
    """Aprovar cliente"""
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        cliente.aprovado = True
        
        # Criar controle de requisições se não existir
        controle = ControleRequisicoes.query.filter_by(cliente_id=cliente_id).first()
        if not controle:
            controle = ControleRequisicoes(
                cliente_id=cliente_id,
                limite_eventos=900  # Padrão
            )
            db.session.add(controle)
        
        db.session.commit()
        
        admin_id = session['usuario_id']
        log_atividade_seguranca(admin_id, 'administrador', 'cliente_aprovado', f'Cliente ID: {cliente_id}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Cliente aprovado com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/clientes/<int:cliente_id>/desativar', methods=['POST'])
@admin_required
def desativar_cliente(cliente_id):
    """Desativar cliente"""
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        cliente.ativo = False
        db.session.commit()
        
        admin_id = session['usuario_id']
        log_atividade_seguranca(admin_id, 'administrador', 'cliente_desativado', f'Cliente ID: {cliente_id}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Cliente desativado com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/clientes/<int:cliente_id>/reativar', methods=['POST'])
@admin_required
def reativar_cliente(cliente_id):
    """Reativar cliente"""
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        cliente.ativo = True
        db.session.commit()
        
        admin_id = session['usuario_id']
        log_atividade_seguranca(admin_id, 'administrador', 'cliente_reativado', f'Cliente ID: {cliente_id}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Cliente reativado com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/clientes/<int:cliente_id>/limite-eventos', methods=['PUT'])
@admin_required
def atualizar_limite_eventos(cliente_id):
    """Atualizar limite de eventos do cliente"""
    try:
        data = request.get_json()
        
        if 'limite_eventos' not in data:
            return jsonify({'erro': 'limite_eventos é obrigatório'}), 400
        
        limite = data['limite_eventos']
        
        # -1 para ilimitado, ou número positivo
        if limite != -1 and (not isinstance(limite, int) or limite < 0):
            return jsonify({'erro': 'Limite deve ser -1 (ilimitado) ou número positivo'}), 400
        
        controle = ControleRequisicoes.query.filter_by(cliente_id=cliente_id).first()
        
        if not controle:
            controle = ControleRequisicoes(cliente_id=cliente_id)
            db.session.add(controle)
        
        controle.limite_eventos = limite
        db.session.commit()
        
        admin_id = session['usuario_id']
        log_atividade_seguranca(admin_id, 'administrador', 'limite_eventos_atualizado', 
                               f'Cliente ID: {cliente_id}, Novo limite: {limite}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Limite de eventos atualizado com sucesso',
            'controle': controle.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/administradores', methods=['GET'])
@super_admin_required
def get_administradores():
    """Listar administradores (apenas super admin)"""
    try:
        admins = Administrador.query.order_by(Administrador.data_criacao.desc()).all()
        
        return jsonify([admin.to_dict() for admin in admins])
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/administradores', methods=['POST'])
@super_admin_required
def criar_administrador():
    """Criar novo administrador (apenas super admin)"""
    try:
        data = request.get_json()
        
        # Validar entrada
        valido, mensagem = validar_entrada_segura(
            data,
            campos_obrigatorios=['nome', 'email', 'senha'],
            tamanho_max={'nome': 100, 'email': 120}
        )
        
        if not valido:
            return jsonify({'erro': mensagem}), 400
        
        # Verificar se email já existe
        if Administrador.query.filter_by(email=data['email']).first():
            return jsonify({'erro': 'Email já cadastrado'}), 409
        
        # Criar administrador
        admin = Administrador(
            nome=sanitizar_entrada(data['nome']),
            email=sanitizar_entrada(data['email']),
            nivel_acesso=data.get('nivel_acesso', 'admin')
        )
        admin.set_senha(data['senha'])
        
        db.session.add(admin)
        db.session.commit()
        
        super_admin_id = session['usuario_id']
        log_atividade_seguranca(super_admin_id, 'administrador', 'admin_criado', f'Admin: {admin.email}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Administrador criado com sucesso',
            'administrador': admin.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_logs():
    """Obter logs de atividade"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        tipo_usuario = request.args.get('tipo_usuario')
        acao = request.args.get('acao')
        
        query = LogAtividade.query
        
        # Filtros
        if tipo_usuario:
            query = query.filter_by(tipo_usuario=tipo_usuario)
        
        if acao:
            query = query.filter(LogAtividade.acao.contains(acao))
        
        logs = query.order_by(LogAtividade.data_criacao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@admin_bp.route('/estatisticas', methods=['GET'])
@admin_required
def get_estatisticas_admin():
    """Estatísticas detalhadas para administrador"""
    try:
        # Estatísticas por período
        hoje = datetime.utcnow().date()
        ontem = hoje - timedelta(days=1)
        semana_passada = hoje - timedelta(days=7)
        mes_passado = hoje - timedelta(days=30)
        
        # Novos clientes por período
        novos_hoje = Cliente.query.filter(func.date(Cliente.data_criacao) == hoje).count()
        novos_ontem = Cliente.query.filter(func.date(Cliente.data_criacao) == ontem).count()
        novos_semana = Cliente.query.filter(Cliente.data_criacao >= semana_passada).count()
        novos_mes = Cliente.query.filter(Cliente.data_criacao >= mes_passado).count()
        
        # Eventos por período
        eventos_hoje = db.session.query(func.sum(ControleRequisicoes.eventos_utilizados)).filter(
            func.date(ControleRequisicoes.periodo_inicio) == hoje
        ).scalar() or 0
        
        estatisticas = {
            'clientes': {
                'total': Cliente.query.count(),
                'ativos': Cliente.query.filter_by(ativo=True).count(),
                'aprovados': Cliente.query.filter_by(aprovado=True).count(),
                'pendentes': Cliente.query.filter_by(aprovado=False, ativo=True).count(),
                'novos': {
                    'hoje': novos_hoje,
                    'ontem': novos_ontem,
                    'semana': novos_semana,
                    'mes': novos_mes
                }
            },
            'eventos': {
                'total': db.session.query(func.sum(ControleRequisicoes.eventos_utilizados)).scalar() or 0,
                'hoje': eventos_hoje
            },
            'tags': {
                'total': TagCliente.query.count(),
                'ativas': TagCliente.query.filter_by(ativa=True).count()
            }
        }
        
        return jsonify(estatisticas)
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

