from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.cliente import Cliente, ConfiguracaoCliente
from src.models.administrador import Administrador, LogAtividade
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def validar_email(email):
    """Valida formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_cnpj(cnpj):
    """Validação básica de CNPJ (apenas formato)"""
    if not cnpj:
        return True  # CNPJ é opcional
    
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verifica se tem 14 dígitos
    return len(cnpj) == 14

def log_atividade(usuario_id, tipo_usuario, acao, detalhes=None):
    """Registra atividade no log"""
    try:
        log = LogAtividade(
            usuario_id=usuario_id,
            tipo_usuario=tipo_usuario,
            acao=acao,
            detalhes=detalhes,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao registrar log: {e}")

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login para cliente ou administrador"""
    try:
        data = request.get_json()
        
        if not data or not data.get("email") or not data.get("senha"):
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400
        
        email = data["email"].lower().strip()
        senha = data["senha"]
        tipo_usuario = data.get("tipo", "cliente")  # "cliente" ou "administrador"
        print(f"DEBUG: Tentativa de login iniciada. Email: {email}, Tipo: {tipo_usuario}")
        
        if not validar_email(email):
            return jsonify({"erro": "Email inválido"}), 400
        
        if tipo_usuario == "administrador":
            # Login de administrador
            admin = Administrador.query.filter_by(email=email, ativo=True).first()
            
            if not admin or not admin.check_senha(senha):
                log_atividade(None, 'administrador', 'login_falhou', f'Email: {email}')
                return jsonify({'erro': 'Credenciais inválidas'}), 401
            
            # Se chegou aqui, admin foi encontrado e a senha está correta
            admin.data_ultimo_login = datetime.utcnow()
            db.session.commit()
            
            # Cria sessão
            session['usuario_id'] = admin.id
            session['tipo_usuario'] = 'administrador'
            session['nivel_acesso'] = admin.nivel_acesso
            
            log_atividade(admin.id, 'administrador', 'login_sucesso')
            
            return jsonify({
                'sucesso': True,
                'usuario': admin.to_dict(),
                'tipo': 'administrador'
            })
        
        else:
            # Login de cliente
            cliente = Cliente.query.filter_by(email=email, ativo=True).first()
            
            if not cliente or not cliente.check_senha(senha):
                log_atividade(None, 'cliente', 'login_falhou', f'Email: {email}')
                return jsonify({'erro': 'Credenciais inválidas'}), 401
            
            if not cliente.aprovado:
                log_atividade(cliente.id, 'cliente', 'login_negado', 'Cliente não aprovado')
                return jsonify({'erro': 'Cadastro ainda não foi aprovado pelo administrador'}), 403
            
            # Cria sessão
            session['usuario_id'] = cliente.id
            session['tipo_usuario'] = 'cliente'
            
            log_atividade(cliente.id, 'cliente', 'login_sucesso')
            
            return jsonify({
                'sucesso': True,
                'usuario': cliente.to_dict(),
                'tipo': 'cliente'
            })
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    """Cadastro de novo cliente"""
    try:
        data = request.get_json()
        
        # Validações obrigatórias
        campos_obrigatorios = ['nome', 'email', 'senha']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({'erro': f'Campo {campo} é obrigatório'}), 400
        
        nome = data['nome'].strip()
        email = data['email'].lower().strip()
        senha = data['senha']
        telefone = data.get('telefone', '').strip()
        empresa = data.get('empresa', '').strip()
        cnpj = data.get('cnpj', '').strip()
        razao_social = data.get('razao_social', '').strip()
        
        # Validações
        if len(nome) < 2:
            return jsonify({'erro': 'Nome deve ter pelo menos 2 caracteres'}), 400
        
        if not validar_email(email):
            return jsonify({'erro': 'Email inválido'}), 400
        
        if len(senha) < 6:
            return jsonify({'erro': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        if cnpj and not validar_cnpj(cnpj):
            return jsonify({'erro': 'CNPJ inválido'}), 400
        
        # Verifica se email já existe
        if Cliente.query.filter_by(email=email).first():
            return jsonify({'erro': 'Email já cadastrado'}), 409
        
        # Cria novo cliente
        cliente = Cliente(
            nome=nome,
            email=email,
            telefone=telefone,
            empresa=empresa,
            cnpj=cnpj,
            razao_social=razao_social
        )
        cliente.set_senha(senha)
        
        db.session.add(cliente)
        db.session.flush()  # Para obter o ID
        
        # Cria configuração padrão
        config = ConfiguracaoCliente(cliente_id=cliente.id)
        db.session.add(config)
        
        db.session.commit()
        
        log_atividade(cliente.id, 'cliente', 'cadastro_realizado')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Cadastro realizado com sucesso. Aguarde aprovação do administrador.',
            'cliente_id': cliente.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout do usuário"""
    try:
        usuario_id = session.get('usuario_id')
        tipo_usuario = session.get('tipo_usuario')
        
        if usuario_id and tipo_usuario:
            log_atividade(usuario_id, tipo_usuario, 'logout')
        
        session.clear()
        
        return jsonify({'sucesso': True, 'mensagem': 'Logout realizado com sucesso'})
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@auth_bp.route('/verificar-sessao', methods=['GET'])
def verificar_sessao():
    """Verifica se o usuário está logado"""
    try:
        usuario_id = session.get('usuario_id')
        tipo_usuario = session.get('tipo_usuario')
        
        if not usuario_id or not tipo_usuario:
            return jsonify({'logado': False}), 401
        
        if tipo_usuario == 'administrador':
            admin = Administrador.query.filter_by(id=usuario_id, ativo=True).first()
            if not admin:
                session.clear()
                return jsonify({'logado': False}), 401
            
            return jsonify({
                'logado': True,
                'usuario': admin.to_dict(),
                'tipo': 'administrador'
            })
        
        else:
            cliente = Cliente.query.filter_by(id=usuario_id, ativo=True, aprovado=True).first()
            if not cliente:
                session.clear()
                return jsonify({'logado': False}), 401
            
            return jsonify({
                'logado': True,
                'usuario': cliente.to_dict(),
                'tipo': 'cliente'
            })
    
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500


