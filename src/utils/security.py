from functools import wraps
from flask import session, jsonify, request
from src.models.administrador import LogAtividade
from src.models.user import db
import hashlib
import hmac
import time
import secrets

# Chave master para segurança adicional (deve ser configurada via variável de ambiente)
MASTER_KEY = "sdr-ia-master-security-key-2025"

def gerar_token_seguranca():
    """Gera um token de segurança único"""
    return secrets.token_urlsafe(32)

def verificar_assinatura_master(data, signature, timestamp):
    """Verifica assinatura master para prevenir ataques"""
    try:
        # Verifica se o timestamp não é muito antigo (5 minutos)
        current_time = int(time.time())
        if abs(current_time - int(timestamp)) > 300:
            return False
        
        # Cria assinatura esperada
        message = f"{data}{timestamp}{MASTER_KEY}"
        expected_signature = hmac.new(
            MASTER_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compara assinaturas de forma segura
        return hmac.compare_digest(signature, expected_signature)
    
    except Exception:
        return False

def rate_limit_check(usuario_id, acao, limite=10, janela=60):
    """Verifica rate limiting básico"""
    try:
        # Conta tentativas na janela de tempo
        from datetime import datetime, timedelta
        inicio_janela = datetime.utcnow() - timedelta(seconds=janela)
        
        tentativas = LogAtividade.query.filter(
            LogAtividade.usuario_id == usuario_id,
            LogAtividade.acao == acao,
            LogAtividade.data_criacao >= inicio_janela
        ).count()
        
        return tentativas < limite
    
    except Exception:
        return True  # Em caso de erro, permite a ação

def log_atividade_seguranca(usuario_id, tipo_usuario, acao, detalhes=None):
    """Registra atividade de segurança"""
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
        print(f"Erro ao registrar log de segurança: {e}")

def login_required(f):
    """Decorator para exigir login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'erro': 'Login necessário'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para exigir login de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('tipo_usuario') != 'administrador':
            return jsonify({'erro': 'Acesso negado - Administrador necessário'}), 403
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Decorator para exigir super administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (session.get('tipo_usuario') != 'administrador' or 
            session.get('nivel_acesso') != 'super_admin'):
            return jsonify({'erro': 'Acesso negado - Super Administrador necessário'}), 403
        return f(*args, **kwargs)
    return decorated_function

def cliente_required(f):
    """Decorator para exigir login de cliente"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('tipo_usuario') != 'cliente':
            return jsonify({'erro': 'Acesso negado - Cliente necessário'}), 403
        return f(*args, **kwargs)
    return decorated_function

def validar_entrada_segura(data, campos_obrigatorios=None, tamanho_max=None):
    """Valida entrada de dados de forma segura"""
    if not data:
        return False, "Dados não fornecidos"
    
    if campos_obrigatorios:
        for campo in campos_obrigatorios:
            if campo not in data or not data[campo]:
                return False, f"Campo {campo} é obrigatório"
    
    if tamanho_max:
        for campo, valor in data.items():
            if isinstance(valor, str) and len(valor) > tamanho_max.get(campo, 1000):
                return False, f"Campo {campo} excede tamanho máximo"
    
    return True, "Válido"

def sanitizar_entrada(texto):
    """Sanitiza entrada de texto"""
    if not isinstance(texto, str):
        return texto
    
    # Remove caracteres perigosos
    caracteres_perigosos = ['<', '>', '"', "'", '&', '\x00']
    for char in caracteres_perigosos:
        texto = texto.replace(char, '')
    
    return texto.strip()

def verificar_ip_suspeito(ip_address):
    """Verifica se o IP é suspeito (implementação básica)"""
    # Lista de IPs bloqueados (pode ser expandida)
    ips_bloqueados = []
    
    return ip_address in ips_bloqueados

def middleware_seguranca():
    """Middleware de segurança para todas as requisições"""
    # Verifica IP suspeito
    if verificar_ip_suspeito(request.remote_addr):
        log_atividade_seguranca(None, 'sistema', 'ip_bloqueado', request.remote_addr)
        return jsonify({'erro': 'Acesso negado'}), 403

# Adiciona headers de segurança (registrado diretamente no app no main.py)
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response