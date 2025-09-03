# Guia de Deployment - SDR IA

**Versão:** 1.0.0  
**Autor:** Manus AI  
**Data:** Janeiro 2025

## Passo a Passo Completo para Deployment

Este guia fornece instruções detalhadas para fazer o deployment completo do sistema SDR IA, desde a configuração inicial até a disponibilização em produção com o domínio `sdria.alveseco.com.br`.

## Fase 1: Preparação do Ambiente

### 1.1 Configuração do Servidor

Antes de iniciar o deployment, certifique-se de que seu servidor atende aos requisitos mínimos:

**Especificações Mínimas:**
- CPU: 2 cores
- RAM: 4GB
- Armazenamento: 20GB SSD
- Sistema Operacional: Ubuntu 20.04 LTS ou superior
- Conexão de Internet estável

**Instalação de Dependências:**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar Nginx
sudo apt install nginx -y

# Instalar Certbot para SSL
sudo apt install certbot python3-certbot-nginx -y

# Reiniciar para aplicar mudanças do Docker
sudo reboot
```

### 1.2 Configuração do Portainer

Se ainda não tiver o Portainer instalado:

```bash
# Criar volume para dados do Portainer
docker volume create portainer_data

# Executar Portainer
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```

Acesse o Portainer em `https://seu-servidor:9443` e configure a conta administrativa.

## Fase 2: Configuração do Repositório GitHub

### 2.1 Preparação do Código no Visual Studio

1. **Abrir Visual Studio Code**
2. **Criar novo workspace ou abrir pasta existente**
3. **Copiar todos os arquivos do projeto** para o diretório de trabalho

Estrutura esperada:
```
sdr-ia-app/
├── src/
├── n8n-workflows/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### 2.2 Inicialização do Repositório Git

No terminal integrado do VS Code:

```bash
# Inicializar repositório
git init

# Configurar usuário (se necessário)
git config user.name "Seu Nome"
git config user.email "seu.email@exemplo.com"

# Adicionar arquivos
git add .

# Primeiro commit
git commit -m "feat: initial commit - SDR IA application"
```

### 2.3 Criação do Repositório no GitHub

1. **Acessar GitHub.com**
2. **Clicar em "New repository"**
3. **Configurar repositório:**
   - Nome: `sdr-ia-app`
   - Descrição: `Sistema de Automação Inteligente SDR com N8N`
   - Visibilidade: Private (recomendado para produção)
   - Não inicializar com README, .gitignore ou licença

4. **Conectar repositório local:**
```bash
git remote add origin https://github.com/SEU_USUARIO/sdr-ia-app.git
git branch -M main
git push -u origin main
```

### 2.4 Configuração de Secrets no GitHub

Para deployment automático futuro, configure os seguintes secrets:

1. **Acessar Settings > Secrets and variables > Actions**
2. **Adicionar secrets:**
   - `SECRET_KEY`: Chave secreta forte para produção
   - `MASTER_SECURITY_KEY`: Chave master de segurança
   - `SERVER_HOST`: IP ou hostname do servidor
   - `SERVER_USER`: Usuário SSH do servidor
   - `SERVER_SSH_KEY`: Chave SSH privada (opcional)

## Fase 3: Deployment no Portainer

### 3.1 Preparação das Variáveis de Ambiente

Antes do deployment, prepare as variáveis de ambiente de produção:

```env
SECRET_KEY=sua-chave-secreta-super-forte-para-producao-min-32-chars
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=sqlite:///src/database/app.db
MASTER_SECURITY_KEY=sua-chave-master-de-seguranca-super-forte
CORS_ORIGINS=https://sdria.alveseco.com.br
```

### 3.2 Criação da Stack no Portainer

1. **Acessar Portainer** (`https://seu-servidor:9443`)
2. **Navegar para Stacks**
3. **Clicar em "Add stack"**
4. **Configurar stack:**
   - **Name:** `sdr-ia-app`
   - **Build method:** Git Repository
   - **Repository URL:** `https://github.com/SEU_USUARIO/sdr-ia-app.git`
   - **Reference:** `refs/heads/main`
   - **Compose path:** `docker-compose.yml`

5. **Configurar Environment variables:**
```
SECRET_KEY=sua-chave-secreta-super-forte-para-producao-min-32-chars
FLASK_ENV=production
FLASK_DEBUG=False
```

6. **Clicar em "Deploy the stack"**

### 3.3 Verificação do Deployment

Após o deployment:

1. **Verificar containers:**
   - Vá em "Containers"
   - Confirme que `sdr_ia_app` está rodando
   - Status deve ser "running"

2. **Verificar logs:**
   - Clique no container `sdr_ia_app`
   - Vá em "Logs"
   - Procure por mensagens de erro

3. **Teste de conectividade:**
```bash
curl -f http://localhost:5000/health
```

Resposta esperada:
```json
{"status": "healthy", "service": "SDR IA App"}
```

## Fase 4: Configuração do Nginx e Proxy Reverso

### 4.1 Configuração do Site no Nginx

Criar arquivo de configuração:

```bash
sudo nano /etc/nginx/sites-available/sdria.alveseco.com.br
```

Conteúdo do arquivo:

```nginx
# Configuração inicial (HTTP apenas)
server {
    listen 80;
    server_name sdria.alveseco.com.br;
    
    # Logs
    access_log /var/log/nginx/sdria_access.log;
    error_log /var/log/nginx/sdria_error.log;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    
    # Main proxy configuration
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Login endpoints with stricter rate limiting
    location /api/auth/login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000;
        access_log off;
    }
    
    # Static files caching
    location /static/ {
        proxy_pass http://127.0.0.1:5000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4.2 Ativação do Site

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/sdria.alveseco.com.br /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx

# Verificar status
sudo systemctl status nginx
```

### 4.3 Teste Inicial

```bash
# Teste local
curl -H "Host: sdria.alveseco.com.br" http://localhost/health

# Teste externo (se DNS já estiver configurado)
curl http://sdria.alveseco.com.br/health
```

## Fase 5: Configuração de DNS e Domínio

### 5.1 Configuração de DNS

No painel de controle do seu provedor de domínio (onde `alveseco.com.br` está registrado):

1. **Acessar gerenciamento de DNS**
2. **Criar registro A:**
   ```
   Tipo: A
   Nome: sdria
   Valor: IP_PUBLICO_DO_SEU_SERVIDOR
   TTL: 3600 (1 hora)
   ```

3. **Criar registro AAAA (se IPv6 disponível):**
   ```
   Tipo: AAAA
   Nome: sdria
   Valor: IPv6_DO_SEU_SERVIDOR
   TTL: 3600
   ```

### 5.2 Verificação de Propagação DNS

```bash
# Verificar resolução DNS
nslookup sdria.alveseco.com.br

# Verificar com dig
dig sdria.alveseco.com.br

# Verificar de diferentes locais
dig @8.8.8.8 sdria.alveseco.com.br
dig @1.1.1.1 sdria.alveseco.com.br
```

### 5.3 Teste de Conectividade

```bash
# Ping para verificar conectividade
ping sdria.alveseco.com.br

# Teste HTTP
curl -I http://sdria.alveseco.com.br

# Teste de resposta da aplicação
curl http://sdria.alveseco.com.br/health
```

## Fase 6: Configuração de SSL/TLS

### 6.1 Obtenção de Certificado SSL

```bash
# Obter certificado Let's Encrypt
sudo certbot --nginx -d sdria.alveseco.com.br

# Seguir prompts interativos:
# - Fornecer email para notificações
# - Aceitar termos de serviço
# - Escolher redirecionamento HTTPS (recomendado: Yes)
```

### 6.2 Verificação do Certificado

```bash
# Verificar certificado
sudo certbot certificates

# Testar renovação
sudo certbot renew --dry-run

# Verificar configuração SSL
curl -I https://sdria.alveseco.com.br
```

### 6.3 Configuração de Renovação Automática

```bash
# Editar crontab
sudo crontab -e

# Adicionar linha para renovação automática (2x por dia)
0 12 * * * /usr/bin/certbot renew --quiet
0 0 * * * /usr/bin/certbot renew --quiet
```

### 6.4 Configuração Final do Nginx

Após o Certbot, o arquivo de configuração será atualizado automaticamente. Verificar:

```bash
sudo nano /etc/nginx/sites-available/sdria.alveseco.com.br
```

Deve conter configuração HTTPS similar a:

```nginx
server {
    listen 443 ssl http2;
    server_name sdria.alveseco.com.br;
    
    ssl_certificate /etc/letsencrypt/live/sdria.alveseco.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sdria.alveseco.com.br/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Resto da configuração...
}

server {
    listen 80;
    server_name sdria.alveseco.com.br;
    return 301 https://$server_name$request_uri;
}
```

## Fase 7: Configuração de Segurança

### 7.1 Configuração de Firewall

```bash
# Verificar status do UFW
sudo ufw status

# Configurar regras básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH (ajustar porta se necessário)
sudo ufw allow 22/tcp

# Permitir HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir Portainer (apenas se necessário externamente)
sudo ufw allow 9443/tcp

# Ativar firewall
sudo ufw enable
```

### 7.2 Configuração de Fail2Ban

```bash
# Instalar Fail2Ban
sudo apt install fail2ban -y

# Criar configuração personalizada
sudo nano /etc/fail2ban/jail.local
```

Conteúdo do arquivo:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = systemd

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
```

```bash
# Reiniciar Fail2Ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Verificar status
sudo fail2ban-client status
```

### 7.3 Configuração de Monitoramento

```bash
# Instalar htop para monitoramento
sudo apt install htop -y

# Configurar logrotate para logs do Nginx
sudo nano /etc/logrotate.d/nginx-sdria
```

Conteúdo:

```
/var/log/nginx/sdria_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
```

## Fase 8: Configuração da Aplicação

### 8.1 Primeiro Acesso

1. **Acessar aplicação:**
   ```
   https://sdria.alveseco.com.br
   ```

2. **Login inicial:**
   - Email: `admin@sdria.com`
   - Senha: `admin123`
   - **IMPORTANTE:** Alterar senha imediatamente

### 8.2 Configuração Inicial do Administrador

1. **Alterar senha do administrador**
2. **Criar usuários administrativos adicionais** (se necessário)
3. **Configurar limites padrão** para novos clientes
4. **Revisar configurações de segurança**

### 8.3 Teste de Funcionalidades

1. **Teste de cadastro de cliente:**
   - Criar conta de teste
   - Verificar processo de aprovação
   - Testar login do cliente

2. **Teste de webhook:**
   ```bash
   curl -X POST https://sdria.alveseco.com.br/api/webhook/test/1 \
     -H "Content-Type: application/json" \
     -d '{"message": "teste", "phone": "+5511999999999"}'
   ```

3. **Teste de APIs:**
   ```bash
   # Health check
   curl https://sdria.alveseco.com.br/health
   
   # Verificar resposta da aplicação
   curl https://sdria.alveseco.com.br/
   ```

## Fase 9: Configuração do N8N

### 9.1 Preparação dos Workflows

1. **Acessar instância do N8N**
2. **Importar workflows:**
   - `n8n-workflows/SDRWHATSAPPIA_DINAMICO.json`
   - `n8n-workflows/MUDAETAPAIATAG_DINAMICO.json`

### 9.2 Configuração de Credenciais

1. **Criar credencial OpenAI:**
   - Nome: `chatgpt-dinamico`
   - Tipo: OpenAI
   - API Key: Temporária (será substituída dinamicamente)

2. **Criar credencial Kommo:**
   - Nome: `kommo-dinamico`
   - Tipo: Kommo CRM
   - Token: Temporário (será substituído dinamicamente)

### 9.3 Configuração de Webhooks

1. **Ativar webhooks nos workflows**
2. **Anotar URLs geradas:**
   - SDR WhatsApp: `https://seu-n8n.com/webhook/sdr-webhook`
   - Muda Etapa: `https://seu-n8n.com/webhook/muda-etapa-webhook`

### 9.4 Teste de Integração

```bash
# Teste direto do webhook N8N
curl -X POST https://seu-n8n.com/webhook/sdr-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "1",
    "message": "Olá, preciso de ajuda",
    "phone": "+5511999999999",
    "webhook_url": "https://sdria.alveseco.com.br/api/webhook/sdr"
  }'
```

## Fase 10: Monitoramento e Manutenção

### 10.1 Configuração de Monitoramento

1. **Script de monitoramento:**

```bash
sudo nano /usr/local/bin/monitor-sdria.sh
```

Conteúdo:

```bash
#!/bin/bash

# Verificar se aplicação está respondendo
if ! curl -f -s https://sdria.alveseco.com.br/health > /dev/null; then
    echo "$(date): SDR IA não está respondendo" >> /var/log/sdria-monitor.log
    # Reiniciar container se necessário
    docker restart sdr_ia_app
fi

# Verificar uso de disco
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Uso de disco alto: ${DISK_USAGE}%" >> /var/log/sdria-monitor.log
fi

# Verificar logs de erro
ERROR_COUNT=$(tail -100 /var/log/nginx/sdria_error.log | grep -c "$(date +%Y/%m/%d)")
if [ $ERROR_COUNT -gt 10 ]; then
    echo "$(date): Muitos erros detectados: ${ERROR_COUNT}" >> /var/log/sdria-monitor.log
fi
```

```bash
# Tornar executável
sudo chmod +x /usr/local/bin/monitor-sdria.sh

# Adicionar ao cron
sudo crontab -e
```

Adicionar linha:
```
*/5 * * * * /usr/local/bin/monitor-sdria.sh
```

### 10.2 Backup Automático

```bash
sudo nano /usr/local/bin/backup-sdria.sh
```

Conteúdo:

```bash
#!/bin/bash

BACKUP_DIR="/backup/sdria"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
docker exec sdr_ia_app cp /app/src/database/app.db /app/backup_${DATE}.db
docker cp sdr_ia_app:/app/backup_${DATE}.db $BACKUP_DIR/

# Backup da configuração do Nginx
cp /etc/nginx/sites-available/sdria.alveseco.com.br $BACKUP_DIR/nginx_${DATE}.conf

# Remover backups antigos (manter 30 dias)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.conf" -mtime +30 -delete

echo "$(date): Backup realizado com sucesso" >> /var/log/sdria-backup.log
```

```bash
# Tornar executável
sudo chmod +x /usr/local/bin/backup-sdria.sh

# Adicionar ao cron (backup diário às 2h)
sudo crontab -e
```

Adicionar linha:
```
0 2 * * * /usr/local/bin/backup-sdria.sh
```

### 10.3 Logs e Alertas

1. **Configurar rotação de logs:**

```bash
sudo nano /etc/logrotate.d/sdria-app
```

Conteúdo:

```
/var/log/sdria-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

2. **Script de alertas:**

```bash
sudo nano /usr/local/bin/alert-sdria.sh
```

Conteúdo:

```bash
#!/bin/bash

# Configurar email (ajustar conforme necessário)
EMAIL="admin@alveseco.com.br"

# Verificar se há erros críticos
CRITICAL_ERRORS=$(docker logs sdr_ia_app --since="1h" | grep -i "critical\|fatal\|error" | wc -l)

if [ $CRITICAL_ERRORS -gt 5 ]; then
    echo "Detectados $CRITICAL_ERRORS erros críticos na última hora no SDR IA" | \
    mail -s "ALERTA: Erros críticos no SDR IA" $EMAIL
fi

# Verificar se container está rodando
if ! docker ps | grep -q sdr_ia_app; then
    echo "Container SDR IA não está rodando!" | \
    mail -s "ALERTA: SDR IA fora do ar" $EMAIL
fi
```

## Fase 11: Testes Finais e Validação

### 11.1 Checklist de Validação

- [ ] Aplicação acessível via HTTPS
- [ ] Certificado SSL válido
- [ ] Login administrativo funcionando
- [ ] Cadastro de cliente funcionando
- [ ] Webhook respondendo corretamente
- [ ] Integração N8N funcionando
- [ ] Logs sendo gerados corretamente
- [ ] Backup automático configurado
- [ ] Monitoramento ativo
- [ ] Firewall configurado
- [ ] DNS resolvendo corretamente

### 11.2 Testes de Performance

```bash
# Teste de carga básico
ab -n 100 -c 10 https://sdria.alveseco.com.br/

# Teste de webhook
for i in {1..10}; do
  curl -X POST https://sdria.alveseco.com.br/api/webhook/test/1 \
    -H "Content-Type: application/json" \
    -d '{"message": "teste '$i'", "phone": "+5511999999999"}' &
done
wait
```

### 11.3 Testes de Segurança

```bash
# Verificar headers de segurança
curl -I https://sdria.alveseco.com.br/

# Teste de rate limiting
for i in {1..20}; do
  curl -X POST https://sdria.alveseco.com.br/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test", "senha": "test", "tipo": "cliente"}'
done
```

## Troubleshooting Comum

### Problema: Container não inicia

**Sintomas:**
- Container para imediatamente após iniciar
- Logs mostram erro de dependências

**Solução:**
```bash
# Verificar logs detalhados
docker logs sdr_ia_app --details

# Reconstruir imagem
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problema: SSL não funciona

**Sintomas:**
- Erro de certificado no navegador
- Certbot falha ao obter certificado

**Solução:**
```bash
# Verificar se domínio resolve corretamente
nslookup sdria.alveseco.com.br

# Verificar se porta 80 está acessível
curl -I http://sdria.alveseco.com.br

# Tentar obter certificado novamente
sudo certbot delete --cert-name sdria.alveseco.com.br
sudo certbot --nginx -d sdria.alveseco.com.br
```

### Problema: Webhook não responde

**Sintomas:**
- Timeout ao chamar webhook
- Erro 502 Bad Gateway

**Solução:**
```bash
# Verificar se aplicação está rodando
curl http://localhost:5000/health

# Verificar logs do Nginx
sudo tail -f /var/log/nginx/sdria_error.log

# Verificar configuração do proxy
sudo nginx -t
```

## Conclusão

Após seguir todos os passos deste guia, você terá:

1. **Sistema SDR IA** rodando em produção
2. **Domínio HTTPS** configurado e funcionando
3. **Integração N8N** pronta para uso
4. **Monitoramento** e backup automático
5. **Segurança** adequada para ambiente de produção

O sistema estará acessível em `https://sdria.alveseco.com.br` e pronto para receber clientes e processar automações de vendas.

Para suporte contínuo, mantenha este guia como referência e monitore regularmente os logs e métricas do sistema.

---

**Desenvolvido por Manus AI**  
**Janeiro 2025**

