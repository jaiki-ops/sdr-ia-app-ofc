print("DEBUG: Iniciando main.py")
import os
import sys
# DON\"T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.extensions import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.webhook import webhook_bp
from src.routes.cliente import cliente_bp
from src.routes.admin import admin_bp
from src.routes.integrations import integrations_bp
from src.routes.n8n import n8n_bp
from src.utils.security import middleware_seguranca, add_security_headers

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações de segurança
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sdr-ia-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # True em produção com HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configurar CORS para permitir requisições externas
CORS(app, supports_credentials=True, origins=['*'])

# Aplicar middleware de segurança
app.before_request(middleware_seguranca)
app.after_request(add_security_headers)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(webhook_bp, url_prefix='/api/webhook')
app.register_blueprint(cliente_bp, url_prefix='/api/cliente')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(integrations_bp, url_prefix='/api/integrations')
app.register_blueprint(n8n_bp, url_prefix='/api/n8n')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar tabelas
with app.app_context():
    db.create_all()
    
    # Criar administrador padrão se não existir
    from src.models.administrador import Administrador
    admin_default = Administrador.query.filter_by(email='admin@sdria.com').first()
    if admin_default:
        db.session.delete(admin_default)
        db.session.commit()
        print("Administrador padrão existente deletado.")

    admin = Administrador(
        nome='Administrador',
        email='admin@sdria.com',
        nivel_acesso='super_admin'
    )
    admin.set_senha('admin123')
    db.session.add(admin)
    db.session.commit()
    print("Administrador padrão criado: admin@sdria.com / admin123")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """Servir arquivos estáticos e SPA"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health_check():
    """Endpoint de verificação de saúde"""
    return {'status': 'healthy', 'service': 'SDR IA App'}, 200

if __name__ == '__main__':
    # Configurações para desenvolvimento e produção
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )




