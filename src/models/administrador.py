from src.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Administrador(db.Model):
    __tablename__ = 'administradores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nivel_acesso = db.Column(db.String(20), default='admin')  # admin, super_admin
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_ultimo_login = db.Column(db.DateTime, nullable=True)
    
    def set_senha(self, senha):
        """Define a senha do administrador com hash"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'nivel_acesso': self.nivel_acesso,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_ultimo_login': self.data_ultimo_login.isoformat() if self.data_ultimo_login else None
        }
    
    def __repr__(self):
        return f'<Administrador {self.nome} - {self.email}>'


class ControleRequisicoes(db.Model):
    __tablename__ = 'controle_requisicoes'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    limite_eventos = db.Column(db.Integer, default=900)  # 900 eventos ou -1 para ilimitado
    eventos_utilizados = db.Column(db.Integer, default=0)
    periodo_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    periodo_fim = db.Column(db.DateTime, nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com cliente
    cliente = db.relationship('Cliente', backref='controle_requisicoes')
    
    def eventos_restantes(self):
        """Retorna o número de eventos restantes"""
        if self.limite_eventos == -1:  # Ilimitado
            return -1
        return max(0, self.limite_eventos - self.eventos_utilizados)
    
    def pode_usar_evento(self):
        """Verifica se ainda pode usar eventos"""
        if not self.ativo:
            return False
        if self.limite_eventos == -1:  # Ilimitado
            return True
        return self.eventos_utilizados < self.limite_eventos
    
    def usar_evento(self):
        """Incrementa o contador de eventos utilizados"""
        if self.pode_usar_evento() and self.limite_eventos != -1:
            self.eventos_utilizados += 1
            return True
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'limite_eventos': self.limite_eventos,
            'eventos_utilizados': self.eventos_utilizados,
            'eventos_restantes': self.eventos_restantes(),
            'periodo_inicio': self.periodo_inicio.isoformat() if self.periodo_inicio else None,
            'periodo_fim': self.periodo_fim.isoformat() if self.periodo_fim else None,
            'ativo': self.ativo
        }
    
    def __repr__(self):
        return f'<ControleRequisicoes Cliente {self.cliente_id} - {self.eventos_utilizados}/{self.limite_eventos}>'


class LogAtividade(db.Model):
    __tablename__ = 'log_atividades'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=True)  # ID do usuário (cliente ou admin)
    tipo_usuario = db.Column(db.String(20), nullable=False)  # 'cliente' ou 'administrador'
    acao = db.Column(db.String(100), nullable=False)
    detalhes = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'tipo_usuario': self.tipo_usuario,
            'acao': self.acao,
            'detalhes': self.detalhes,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
    
    def __repr__(self):
        return f'<LogAtividade {self.tipo_usuario} {self.usuario_id} - {self.acao}>'

