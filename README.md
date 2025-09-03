# SDR IA - Sistema de Automação Inteligente

**Versão:** 1.0.0  
**Autor:** Manus AI  
**Data:** Janeiro 2025

## Visão Geral

O SDR IA é um sistema completo de automação inteligente para vendas e atendimento, desenvolvido para integrar com N8N, Kommo CRM e ChatGPT. O sistema permite que múltiplos clientes utilizem a mesma infraestrutura de automação com configurações personalizadas e isoladas.

### Principais Funcionalidades

- **Sistema Multi-tenant**: Suporte a múltiplos clientes com configurações isoladas
- **Integração N8N**: Workflows dinâmicos que se adaptam às configurações de cada cliente
- **Integração Kommo CRM**: Gestão automática de leads e pipeline de vendas
- **Integração ChatGPT**: Processamento inteligente de mensagens com prompts personalizados
- **Webhook Dinâmico**: URL única por cliente para integração com sistemas externos
- **Painel Administrativo**: Controle completo de clientes, permissões e estatísticas
- **Painel do Cliente**: Interface para configuração de credenciais, tags e prompts
- **Sistema de Segurança**: Autenticação robusta com middleware de segurança

### Arquitetura do Sistema

O sistema é construído com uma arquitetura moderna e escalável:

- **Backend**: Flask (Python) com SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript responsivo
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Containerização**: Docker e Docker Compose
- **Orquestração**: Portainer
- **Integração**: N8N para automação de workflows

## Estrutura do Projeto

```
sdr-ia-app/
├── src/                          # Código fonte da aplicação
│   ├── models/                   # Modelos de dados
│   │   ├── user.py              # Modelo base de usuário
│   │   ├── cliente.py           # Modelos relacionados a clientes
│   │   └── administrador.py     # Modelos administrativos
│   ├── routes/                   # Rotas da API
│   │   ├── auth.py              # Autenticação
│   │   ├── cliente.py           # Endpoints do cliente
│   │   ├── admin.py             # Endpoints administrativos
│   │   └── webhook.py           # Webhooks para N8N
│   ├── utils/                    # Utilitários
│   │   └── security.py          # Funções de segurança
│   ├── static/                   # Arquivos estáticos
│   │   └── index.html           # Interface web
│   └── main.py                   # Aplicação principal
├── n8n-workflows/                # Workflows do N8N
│   ├── SDRWHATSAPPIA_DINAMICO.json
│   ├── MUDAETAPAIATAG_DINAMICO.json
│   └── README_WORKFLOWS.md
├── Dockerfile                    # Configuração Docker
├── docker-compose.yml           # Orquestração de containers
├── requirements.txt             # Dependências Python
├── .env.example                 # Exemplo de variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo Git
└── README.md                    # Esta documentação
```

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- **Visual Studio Code** (versão mais recente)
- **Git** (versão 2.30 ou superior)
- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 1.29 ou superior)
- **Portainer** (configurado no servidor)
- **Conta GitHub** (para versionamento)

### Extensões Recomendadas para VS Code

- Python
- Docker
- GitLens
- REST Client
- SQLite Viewer

## Configuração Inicial

### 1. Preparação do Ambiente de Desenvolvimento

Primeiro, clone ou baixe o projeto para sua máquina local. Se você ainda não tem o código, pode começar criando um novo diretório:

```bash
mkdir sdr-ia-app
cd sdr-ia-app
```

### 2. Configuração de Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
SECRET_KEY=sua-chave-secreta-super-forte-aqui
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///src/database/app.db
MASTER_SECURITY_KEY=sua-chave-master-de-seguranca
```

### 3. Teste Local

Para testar a aplicação localmente:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python src/main.py
```

A aplicação estará disponível em `http://localhost:5000`.

## Integração com Visual Studio Code

### Configuração do Workspace

1. **Abrir o Projeto no VS Code**:
   ```bash
   code .
   ```

2. **Configurar Python Interpreter**:
   - Pressione `Ctrl+Shift+P`
   - Digite "Python: Select Interpreter"
   - Selecione o interpretador Python apropriado

3. **Configurar Debugging**:
   Crie o arquivo `.vscode/launch.json`:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Flask",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/src/main.py",
               "env": {
                   "FLASK_ENV": "development",
                   "FLASK_DEBUG": "1"
               },
               "args": [],
               "jinja": true,
               "justMyCode": true
           }
       ]
   }
   ```

4. **Configurar Tasks**:
   Crie o arquivo `.vscode/tasks.json`:
   ```json
   {
       "version": "2.0.0",
       "tasks": [
           {
               "label": "Run Flask App",
               "type": "shell",
               "command": "python",
               "args": ["src/main.py"],
               "group": "build",
               "presentation": {
                   "echo": true,
                   "reveal": "always",
                   "focus": false,
                   "panel": "new"
               }
           },
           {
               "label": "Build Docker Image",
               "type": "shell",
               "command": "docker",
               "args": ["build", "-t", "sdr-ia-app", "."],
               "group": "build"
           }
       ]
   }
   ```

### Desenvolvimento com VS Code

1. **Terminal Integrado**: Use `Ctrl+`` para abrir o terminal
2. **Explorer**: Navegue pelos arquivos no painel lateral
3. **Source Control**: Use `Ctrl+Shift+G` para acessar controle de versão
4. **Debug**: Use `F5` para iniciar debugging
5. **Extensions**: Instale extensões recomendadas para Python e Docker

## Integração com GitHub

### Configuração Inicial do Repositório

1. **Inicializar Repositório Git**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: SDR IA Application"
   ```

2. **Criar Repositório no GitHub**:
   - Acesse [GitHub](https://github.com)
   - Clique em "New repository"
   - Nome: `sdr-ia-app`
   - Descrição: "Sistema de Automação Inteligente SDR com N8N"
   - Visibilidade: Private (recomendado)
   - Não inicialize com README (já temos um)

3. **Conectar Repositório Local ao GitHub**:
   ```bash
   git remote add origin https://github.com/SEU_USUARIO/sdr-ia-app.git
   git branch -M main
   git push -u origin main
   ```

### Workflow de Desenvolvimento

1. **Criar Branch para Nova Feature**:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. **Fazer Commits Regulares**:
   ```bash
   git add .
   git commit -m "feat: adicionar nova funcionalidade X"
   ```

3. **Push para GitHub**:
   ```bash
   git push origin feature/nova-funcionalidade
   ```

4. **Criar Pull Request**:
   - No GitHub, clique em "Compare & pull request"
   - Adicione descrição detalhada
   - Solicite review se necessário
   - Merge após aprovação

### Configuração de Secrets

Para deployment automático, configure secrets no GitHub:

1. Vá em Settings > Secrets and variables > Actions
2. Adicione os seguintes secrets:
   - `SECRET_KEY`: Chave secreta da aplicação
   - `DOCKER_USERNAME`: Usuário Docker Hub (opcional)
   - `DOCKER_PASSWORD`: Senha Docker Hub (opcional)

## Deployment com Portainer

### Preparação do Servidor

Antes de fazer o deployment, certifique-se de que seu servidor tem:

- Docker instalado e funcionando
- Portainer instalado e acessível
- Acesso SSH ao servidor
- Domínio configurado (sdria.alveseco.com.br)

### Configuração no Portainer

1. **Acessar Portainer**:
   - Abra seu Portainer (ex: `https://portainer.seuservidor.com`)
   - Faça login com suas credenciais

2. **Criar Nova Stack**:
   - Vá em "Stacks" no menu lateral
   - Clique em "Add stack"
   - Nome: `sdr-ia-app`

3. **Configurar Stack via Git Repository**:
   - Selecione "Git Repository"
   - Repository URL: `https://github.com/SEU_USUARIO/sdr-ia-app.git`
   - Reference: `refs/heads/main`
   - Compose path: `docker-compose.yml`

4. **Configurar Variáveis de Ambiente**:
   ```env
   SECRET_KEY=sua-chave-secreta-super-forte-para-producao
   FLASK_ENV=production
   FLASK_DEBUG=False
   DATABASE_URL=sqlite:///src/database/app.db
   ```

5. **Deploy da Stack**:
   - Clique em "Deploy the stack"
   - Aguarde o build e deployment
   - Verifique logs em caso de erro

### Configuração de Proxy Reverso

Para usar o domínio `sdria.alveseco.com.br`, configure um proxy reverso:

#### Opção 1: Nginx (Recomendado)

1. **Instalar Nginx** (se não estiver instalado):
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Criar Configuração do Site**:
   ```bash
   sudo nano /etc/nginx/sites-available/sdria.alveseco.com.br
   ```

   Conteúdo do arquivo:
   ```nginx
   server {
       listen 80;
       server_name sdria.alveseco.com.br;
       
       # Redirect HTTP to HTTPS
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl http2;
       server_name sdria.alveseco.com.br;
       
       # SSL Configuration
       ssl_certificate /path/to/your/certificate.crt;
       ssl_certificate_key /path/to/your/private.key;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;
       
       # Security Headers
       add_header X-Frame-Options "SAMEORIGIN" always;
       add_header X-XSS-Protection "1; mode=block" always;
       add_header X-Content-Type-Options "nosniff" always;
       add_header Referrer-Policy "no-referrer-when-downgrade" always;
       add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
       
       # Proxy to Flask App
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_buffering off;
           proxy_request_buffering off;
       }
       
       # API endpoints with increased timeout
       location /api/ {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 300;
           proxy_connect_timeout 300;
           proxy_send_timeout 300;
       }
   }
   ```

3. **Ativar Site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/sdria.alveseco.com.br /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

#### Opção 2: Traefik (via Docker)

Se preferir usar Traefik, adicione as labels no `docker-compose.yml`:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.sdr-ia.rule=Host(`sdria.alveseco.com.br`)"
  - "traefik.http.routers.sdr-ia.entrypoints=websecure"
  - "traefik.http.routers.sdr-ia.tls.certresolver=letsencrypt"
  - "traefik.http.services.sdr-ia.loadbalancer.server.port=5000"
```

### Configuração de SSL/TLS

#### Usando Certbot (Let's Encrypt)

1. **Instalar Certbot**:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obter Certificado**:
   ```bash
   sudo certbot --nginx -d sdria.alveseco.com.br
   ```

3. **Configurar Renovação Automática**:
   ```bash
   sudo crontab -e
   ```
   
   Adicione a linha:
   ```
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Monitoramento e Logs

1. **Verificar Status da Aplicação**:
   ```bash
   curl -f http://localhost:5000/health
   ```

2. **Visualizar Logs no Portainer**:
   - Vá em "Containers"
   - Clique no container `sdr_ia_app`
   - Clique em "Logs"

3. **Logs via Docker CLI**:
   ```bash
   docker logs sdr_ia_app -f
   ```

## Configuração do N8N

### Importação dos Workflows

1. **Acessar N8N**:
   - Abra sua instância do N8N
   - Faça login com suas credenciais

2. **Importar Workflows**:
   - Vá em "Workflows"
   - Clique em "Import from File"
   - Selecione `n8n-workflows/SDRWHATSAPPIA_DINAMICO.json`
   - Repita para `MUDAETAPAIATAG_DINAMICO.json`

3. **Configurar Credenciais**:
   - Vá em "Credentials"
   - Crie credencial "OpenAI" com nome `chatgpt-dinamico`
   - Crie credencial "Kommo CRM" com nome `kommo-dinamico`
   - Use tokens temporários (serão substituídos dinamicamente)

### Configuração de Webhooks

1. **Ativar Webhooks**:
   - Nos workflows importados, ative os nós de webhook
   - Anote as URLs geradas

2. **Configurar URLs no Sistema**:
   - As URLs dos webhooks devem ser configuradas no sistema
   - Exemplo: `https://seu-n8n.com/webhook/sdr-webhook`

### Teste de Integração

1. **Teste Manual**:
   ```bash
   curl -X POST https://sdria.alveseco.com.br/api/webhook/test/1 \
     -H "Content-Type: application/json" \
     -d '{"message": "teste", "phone": "+5511999999999"}'
   ```

2. **Verificar Logs**:
   - No N8N, verifique execuções dos workflows
   - No Portainer, verifique logs da aplicação

## Configuração de Subdomínio

### DNS Configuration

1. **Acessar Painel de DNS**:
   - Entre no painel do seu provedor de domínio
   - Vá na seção de gerenciamento de DNS

2. **Criar Registro A**:
   ```
   Tipo: A
   Nome: sdria
   Valor: IP_DO_SEU_SERVIDOR
   TTL: 3600
   ```

3. **Criar Registro CNAME (Alternativo)**:
   ```
   Tipo: CNAME
   Nome: sdria
   Valor: seuservidor.com
   TTL: 3600
   ```

### Verificação de DNS

1. **Teste de Resolução**:
   ```bash
   nslookup sdria.alveseco.com.br
   dig sdria.alveseco.com.br
   ```

2. **Teste de Conectividade**:
   ```bash
   curl -I https://sdria.alveseco.com.br
   ```

### Configuração de Firewall

Certifique-se de que as portas estão abertas:

```bash
# Verificar portas abertas
sudo ufw status

# Abrir portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp  # Apenas se necessário para acesso direto
```

## Uso do Sistema

### Acesso Inicial

1. **Administrador Padrão**:
   - Email: `admin@sdria.com`
   - Senha: `admin123`
   - **IMPORTANTE**: Altere a senha após primeiro login

2. **Primeiro Acesso**:
   - Acesse `https://sdria.alveseco.com.br`
   - Faça login como administrador
   - Configure o sistema conforme necessário

### Cadastro de Clientes

1. **Via Interface Web**:
   - Clique em "Cadastre-se"
   - Preencha todos os campos obrigatórios
   - Aguarde aprovação do administrador

2. **Via Painel Administrativo**:
   - Login como administrador
   - Vá em "Clientes"
   - Aprove clientes pendentes

### Configuração de Cliente

1. **Credenciais Kommo**:
   - Token de acesso do Kommo CRM
   - Domínio da conta (ex: `https://cliente.kommo.com`)
   - Pipeline ID e Funil IDs

2. **Credenciais ChatGPT**:
   - API Key do OpenAI
   - Modelo preferido (gpt-4, gpt-3.5-turbo)

3. **Prompts Personalizados**:
   - Prompt para agente de IA
   - Prompt para processamento de áudio
   - Prompt para análise de imagens

4. **Tags Dinâmicas**:
   - Criar tags personalizadas
   - Associar com funis específicos
   - Configurar ações automáticas

### Integração com WhatsApp

1. **Obter URL do Webhook**:
   - No painel do cliente, copie a URL do webhook
   - Formato: `https://sdria.alveseco.com.br/api/webhook/sdr?clienteId=123`

2. **Configurar no Sistema de WhatsApp**:
   - Use a URL no seu sistema de WhatsApp Business
   - Configure para enviar dados no formato JSON

3. **Formato de Dados Esperado**:
   ```json
   {
     "phone": "+5511999999999",
     "message": "Texto da mensagem",
     "message_type": "text|audio|image",
     "audio_url": "https://...",
     "image_url": "https://..."
   }
   ```

## Manutenção e Monitoramento

### Backup do Banco de Dados

1. **Backup Manual**:
   ```bash
   docker exec sdr_ia_app cp /app/src/database/app.db /app/backup_$(date +%Y%m%d).db
   docker cp sdr_ia_app:/app/backup_$(date +%Y%m%d).db ./
   ```

2. **Backup Automático**:
   - Use o serviço de backup no docker-compose
   - Configure cron job para execução regular

### Monitoramento de Performance

1. **Métricas da Aplicação**:
   - Endpoint: `/health`
   - Logs de acesso e erro
   - Tempo de resposta das APIs

2. **Métricas do Sistema**:
   - Uso de CPU e memória
   - Espaço em disco
   - Conectividade de rede

### Atualizações

1. **Atualização de Código**:
   ```bash
   git pull origin main
   docker-compose down
   docker-compose up --build -d
   ```

2. **Atualização de Dependências**:
   ```bash
   pip freeze > requirements.txt
   docker-compose build --no-cache
   ```

## Troubleshooting

### Problemas Comuns

1. **Aplicação não inicia**:
   - Verificar logs: `docker logs sdr_ia_app`
   - Verificar variáveis de ambiente
   - Verificar permissões de arquivo

2. **Erro de conexão com banco**:
   - Verificar se diretório database existe
   - Verificar permissões de escrita
   - Verificar se SQLite está instalado

3. **Webhook não funciona**:
   - Verificar URL do webhook
   - Verificar se cliente está ativo e aprovado
   - Verificar logs de segurança

4. **Erro de SSL/TLS**:
   - Verificar certificado
   - Verificar configuração do Nginx
   - Verificar firewall

### Logs e Debugging

1. **Logs da Aplicação**:
   ```bash
   docker logs sdr_ia_app -f --tail 100
   ```

2. **Logs do Nginx**:
   ```bash
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Debug Mode**:
   - Altere `FLASK_DEBUG=True` no .env
   - Reinicie a aplicação
   - **ATENÇÃO**: Não use em produção

### Suporte

Para suporte técnico:

1. **Documentação**: Consulte este README
2. **Logs**: Colete logs relevantes antes de reportar
3. **GitHub Issues**: Crie issue no repositório
4. **Email**: Entre em contato com a equipe de desenvolvimento

## Segurança

### Boas Práticas

1. **Senhas Fortes**:
   - Use senhas complexas para todos os usuários
   - Altere senhas padrão imediatamente
   - Implemente rotação regular de senhas

2. **HTTPS Obrigatório**:
   - Configure SSL/TLS corretamente
   - Use certificados válidos
   - Redirecione HTTP para HTTPS

3. **Firewall**:
   - Abra apenas portas necessárias
   - Use fail2ban para proteção contra ataques
   - Configure rate limiting

4. **Atualizações**:
   - Mantenha sistema operacional atualizado
   - Atualize dependências regularmente
   - Monitore vulnerabilidades conhecidas

### Auditoria

1. **Logs de Segurança**:
   - Todos os logins são registrados
   - Tentativas de acesso inválido são logadas
   - Ações administrativas são auditadas

2. **Monitoramento**:
   - Configure alertas para atividades suspeitas
   - Monitore uso de recursos
   - Verifique integridade dos dados

## Conclusão

Este sistema SDR IA fornece uma solução completa e escalável para automação de vendas e atendimento. Com a integração entre Flask, N8N, Kommo CRM e ChatGPT, oferece flexibilidade e poder para atender múltiplos clientes com configurações personalizadas.

A arquitetura containerizada facilita deployment e manutenção, enquanto o sistema de segurança robusto garante proteção adequada dos dados. O painel administrativo permite controle total do sistema, e o painel do cliente oferece autonomia para configurações específicas.

Para dúvidas ou suporte, consulte a documentação adicional nos diretórios específicos ou entre em contato com a equipe de desenvolvimento.

---

**Desenvolvido por Manus AI**  
**Janeiro 2025**

