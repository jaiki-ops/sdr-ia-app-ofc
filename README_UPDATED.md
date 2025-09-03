# SDR IA - Sistema de Automação Inteligente

**Versão:** 2.0.0  
**Autor:** Manus AI  
**Data:** Setembro 2025

## 🚀 Visão Geral

O SDR IA é um sistema completo de automação inteligente para vendas e atendimento, desenvolvido para integrar com N8N, Kommo CRM e ChatGPT. O sistema permite que múltiplos clientes utilizem a mesma infraestrutura de automação com configurações personalizadas e isoladas.

### ✨ Principais Funcionalidades

- **🏢 Sistema Multi-tenant**: Suporte a múltiplos clientes com configurações isoladas
- **🔄 Integração N8N**: Workflows dinâmicos que se adaptam às configurações de cada cliente
- **📊 Integração Kommo CRM**: Gestão automática de leads e pipeline de vendas
- **🤖 Integração ChatGPT**: Processamento inteligente de mensagens com prompts personalizados
- **🔗 Webhook Dinâmico**: URL única por cliente para integração com sistemas externos
- **👨‍💼 Painel Administrativo**: Controle completo de clientes, permissões e estatísticas
- **👤 Painel do Cliente**: Interface para configuração de credenciais, tags e prompts
- **🔒 Sistema de Segurança**: Autenticação robusta com middleware de segurança
- **📱 Interface Responsiva**: Design adaptável para desktop e mobile
- **📈 Monitoramento**: Logs de atividade e controle de requisições

### 🏗️ Arquitetura do Sistema

O sistema é construído com uma arquitetura moderna e escalável:

- **Backend**: Flask (Python) com SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript responsivo
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Containerização**: Docker e Docker Compose
- **Orquestração**: Portainer
- **Integração**: N8N para automação de workflows
- **IA**: OpenAI GPT para processamento inteligente

## 📁 Estrutura do Projeto

```
sdr-ia-app/
├── src/                          # Código fonte da aplicação
│   ├── models/                   # Modelos de dados
│   │   ├── __init__.py          # Inicialização dos modelos
│   │   ├── user.py              # Modelo base de usuário
│   │   ├── cliente.py           # Modelos relacionados a clientes
│   │   └── administrador.py     # Modelos administrativos
│   ├── routes/                   # Rotas da API
│   │   ├── auth.py              # Autenticação
│   │   ├── cliente.py           # Endpoints do cliente
│   │   ├── admin.py             # Endpoints administrativos
│   │   ├── webhook.py           # Webhooks para N8N
│   │   ├── integrations.py      # Integrações (Kommo/ChatGPT)
│   │   └── n8n.py               # Gerenciamento N8N
│   ├── integrations/             # Módulos de integração
│   │   ├── __init__.py          # Inicialização
│   │   ├── kommo_crm.py         # Cliente Kommo CRM
│   │   ├── chatgpt.py           # Cliente ChatGPT
│   │   └── n8n_workflows.py     # Gerenciador N8N
│   ├── utils/                    # Utilitários
│   │   └── security.py          # Funções de segurança
│   ├── static/                   # Arquivos estáticos
│   │   └── index.html           # Interface web
│   ├── database/                 # Banco de dados
│   │   └── app.db               # SQLite database
│   ├── extensions.py             # Extensões Flask
│   └── main.py                   # Aplicação principal
├── n8n-workflows/                # Workflows N8N
│   ├── SDRWHATSAPPIA_DINAMICO.json
│   ├── MUDAETAPAIATAG_DINAMICO.json
│   ├── README_WORKFLOWS.md
│   └── README_WORKFLOWS_UPDATED.md
├── requirements.txt              # Dependências Python
├── Dockerfile                    # Configuração Docker
├── docker-compose.yml            # Docker Compose
├── .env.example                  # Exemplo de variáveis de ambiente
├── .gitignore                    # Arquivos ignorados pelo Git
├── DEPLOYMENT_GUIDE.md           # Guia de deploy
└── README.md                     # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-CORS**: Suporte a CORS
- **Bcrypt**: Hash de senhas
- **OpenAI**: Integração com ChatGPT
- **Requests**: Cliente HTTP

### Frontend
- **HTML5/CSS3**: Estrutura e estilo
- **JavaScript ES6+**: Lógica do frontend
- **Responsive Design**: Design adaptável

### Integrações
- **Kommo CRM**: Gestão de leads e vendas
- **OpenAI GPT**: Processamento de linguagem natural
- **N8N**: Automação de workflows
- **WhatsApp Business API**: Comunicação

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração local
- **Portainer**: Gerenciamento de containers
- **Git**: Controle de versão

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.9+
- Docker e Docker Compose
- Git
- Conta OpenAI (para ChatGPT)
- Conta Kommo CRM
- Instância N8N (opcional)

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/sdr-ia-app.git
cd sdr-ia-app
```

### 2. Configuração Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de ambiente
cp .env.example .env

# Editar variáveis de ambiente
nano .env
```

### 3. Variáveis de Ambiente

```bash
# .env
SECRET_KEY=sua-chave-secreta-super-segura
OPENAI_API_KEY=sk-sua-chave-openai
N8N_BASE_URL=https://n8n.exemplo.com
N8N_API_KEY=sua-api-key-n8n
APP_BASE_URL=https://sdria.alveseco.com.br
```

### 4. Executar Localmente

```bash
# Executar aplicação
python src/main.py

# Ou usando Flask CLI
FLASK_APP=src/main.py flask run --host=0.0.0.0 --port=5000
```

### 5. Deploy com Docker

```bash
# Build e execução
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

## 📋 API Endpoints

### Autenticação
- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/logout` - Logout
- `GET /api/auth/verificar-sessao` - Verificar sessão

### Administração
- `GET /api/admin/clientes` - Listar clientes
- `POST /api/admin/cliente/{id}/aprovar` - Aprovar cliente
- `POST /api/admin/cliente/{id}/desativar` - Desativar cliente

### Cliente
- `POST /api/cliente/cadastro` - Cadastro de cliente
- `GET /api/cliente/configuracoes` - Obter configurações
- `PUT /api/cliente/configuracoes` - Atualizar configurações

### Webhooks
- `POST /api/webhook/sdr?clienteId={id}` - Webhook principal
- `GET /api/webhook/config/{id}` - Configurações do cliente
- `POST /api/webhook/test/{id}` - Teste de webhook

### Integrações
- `POST /api/integrations/test/kommo` - Testar Kommo CRM
- `POST /api/integrations/test/chatgpt` - Testar ChatGPT
- `GET /api/integrations/kommo/pipelines` - Obter pipelines
- `POST /api/integrations/chatgpt/analyze` - Análise com IA

### N8N
- `POST /api/n8n/process/message` - Processar mensagem
- `POST /api/n8n/process/audio` - Processar áudio
- `POST /api/n8n/process/image` - Processar imagem
- `POST /api/n8n/change-stage` - Mudar etapa de lead

## 🔧 Configuração de Integrações

### Kommo CRM

1. Obtenha suas credenciais no painel do Kommo
2. Configure no painel administrativo:
   - Token de acesso
   - Domínio da conta
   - Pipeline ID

### ChatGPT/OpenAI

1. Crie uma conta na OpenAI
2. Gere uma API Key
3. Configure no painel:
   - API Key
   - Modelo (gpt-3.5-turbo, gpt-4, etc.)
   - Prompts personalizados

### N8N Workflows

1. Importe os workflows do diretório `n8n-workflows/`
2. Configure as credenciais necessárias
3. Ative os workflows
4. Configure as URLs de webhook na aplicação

## 🔒 Segurança

### Funcionalidades de Segurança

- **Autenticação robusta** com hash bcrypt
- **Middleware de segurança** em todas as rotas
- **Sanitização de entrada** para prevenir XSS
- **Logs de atividade** para auditoria
- **Controle de requisições** por cliente
- **Headers de segurança** (CSP, HSTS, etc.)

### Boas Práticas

- Senhas hasheadas com bcrypt
- Sessões seguras com cookies HttpOnly
- Validação de entrada em todos os endpoints
- Rate limiting por cliente
- Logs detalhados de segurança

## 📊 Monitoramento

### Logs de Sistema

- **Logs de autenticação**: Login/logout de usuários
- **Logs de webhook**: Execuções de webhook
- **Logs de segurança**: Tentativas de acesso
- **Logs de integração**: Chamadas para APIs externas

### Métricas

- **Requisições por cliente**: Controle de uso
- **Taxa de sucesso**: Webhooks e integrações
- **Tempo de resposta**: Performance da API
- **Erros**: Monitoramento de falhas

## 🚀 Deploy em Produção

### Portainer

1. Configure o repositório Git
2. Crie uma nova Stack no Portainer
3. Use o arquivo `docker-compose.yml`
4. Configure as variáveis de ambiente
5. Deploy da aplicação

### Configurações de Produção

```yaml
# docker-compose.yml para produção
version: '3.8'
services:
  sdr-ia-app:
    build: .
    ports:
      - "80:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - N8N_BASE_URL=${N8N_BASE_URL}
    restart: always
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas:

- **Email**: suporte@sdria.com
- **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/sdr-ia-app/wiki)
- **Issues**: [GitHub Issues](https://github.com/seu-usuario/sdr-ia-app/issues)

## 🎯 Roadmap

### Versão 2.1
- [ ] Interface de usuário aprimorada
- [ ] Dashboard com métricas em tempo real
- [ ] Integração com mais CRMs
- [ ] API REST completa

### Versão 2.2
- [ ] Suporte a PostgreSQL
- [ ] Cache com Redis
- [ ] Autenticação OAuth2
- [ ] Webhooks bidirecionais

### Versão 3.0
- [ ] Microserviços
- [ ] Kubernetes
- [ ] Machine Learning avançado
- [ ] Interface mobile nativa

---

**Desenvolvido com ❤️ pela equipe Manus AI**

