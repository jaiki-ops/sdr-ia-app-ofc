from src.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    empresa = db.Column(db.String(100), nullable=True)
    cnpj = db.Column(db.String(18), nullable=True)
    razao_social = db.Column(db.String(200), nullable=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    aprovado = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configurações do cliente
    configuracoes = db.relationship('ConfiguracaoCliente', backref='cliente', uselist=False, cascade='all, delete-orphan')
    tags = db.relationship('TagCliente', backref='cliente', cascade='all, delete-orphan')
    
    def set_senha(self, senha):
        """Define a senha do cliente com hash"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'empresa': self.empresa,
            'cnpj': self.cnpj,
            'razao_social': self.razao_social,
            'ativo': self.ativo,
            'aprovado': self.aprovado,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }


class ConfiguracaoCliente(db.Model):
    __tablename__ = 'configuracoes_cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    # Configurações do Kommo CRM
    kommo_token = db.Column(db.Text, nullable=True)
    kommo_domain = db.Column(db.String(255), nullable=True)
    
    # Configurações do ChatGPT
    chatgpt_api_key = db.Column(db.Text, nullable=True)
    chatgpt_model = db.Column(db.String(50), default='gpt-4o-mini')
    
    # Configurações de funis e pipelines
    pipeline_id = db.Column(db.String(50), nullable=True)
    funil_ids = db.Column(db.Text, nullable=True)  # JSON string com IDs dos funis
    
    # Prompts personalizados
    prompt_agente_ia = db.Column(db.Text, nullable=True)
    prompt_audio = db.Column(db.Text, nullable=True)
    prompt_imagem = db.Column(db.Text, nullable=True)
    
    # Configurações de aprovação
    aprovacao_automatica = db.Column(db.Boolean, default=False)
    
    # Switch N8N
    usar_n8n = db.Column(db.Boolean, default=True)
    
    # Webhook personalizado
    webhook_url = db.Column(db.String(500), nullable=True)
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_funil_ids_list(self):
        """Retorna a lista de IDs dos funis"""
        if self.funil_ids:
            try:
                return json.loads(self.funil_ids)
            except:
                return []
        return []
    
    def set_funil_ids_list(self, ids_list):
        """Define a lista de IDs dos funis"""
        self.funil_ids = json.dumps(ids_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'kommo_token': self.kommo_token,
            'kommo_domain': self.kommo_domain,
            'chatgpt_api_key': self.chatgpt_api_key,
            'chatgpt_model': self.chatgpt_model,
            'pipeline_id': self.pipeline_id,
            'funil_ids': self.funil_ids,
            'prompt_agente_ia': self.prompt_agente_ia,
            'prompt_audio': self.prompt_audio,
            'prompt_imagem': self.prompt_imagem,
            'aprovacao_automatica': self.aprovacao_automatica,
            'usar_n8n': self.usar_n8n,
            'webhook_url': self.webhook_url,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }


class TagCliente(db.Model):
    __tablename__ = 'tags_cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    funil_id = db.Column(db.String(50), nullable=False)
    pipeline_id = db.Column(db.String(50), nullable=False)
    ativa = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'kommo_token': self.kommo_token,
            'kommo_domain': self.kommo_domain,
            'chatgpt_api_key': self.chatgpt_api_key,
            'chatgpt_model': self.chatgpt_model,
            'pipeline_id': self.pipeline_id,
            'funil_ids': self.funil_ids,
            'prompt_agente_ia': self.prompt_agente_ia,
            'prompt_audio': self.prompt_audio,
            'prompt_imagem': self.prompt_imagem,
            'aprovacao_automatica': self.aprovacao_automatica,
            'usar_n8n': self.usar_n8n,
            'webhook_url': self.webhook_url,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }





