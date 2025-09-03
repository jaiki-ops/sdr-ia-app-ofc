# Configuração Portainer - SDR IA

Este guia explica como fazer deploy da aplicação SDR IA usando Portainer.

## 🚀 Deploy via Portainer

### Pré-requisitos

1. **Servidor com Docker e Portainer instalados**
2. **Repositório GitHub configurado** (veja GITHUB_SETUP.md)
3. **Domínio configurado** (ex: sdria.alveseco.com.br)

### 1. Configuração no Portainer

#### Acessar Portainer
1. Acesse seu painel Portainer
2. Vá em **Stacks** > **Add stack**

#### Configurar Stack
1. **Nome da Stack**: `sdr-ia-app`
2. **Build method**: Selecione **Git Repository**
3. **Repository URL**: `https://github.com/SEU_USUARIO/sdr-ia-app.git`
4. **Reference**: `refs/heads/main`
5. **Compose path**: `docker-compose.yml`

### 2. Variáveis de Ambiente

Configure as seguintes variáveis de ambiente no Portainer:

```bash
# Segurança
SECRET_KEY=sua-chave-secreta-super-segura-production

# OpenAI/ChatGPT
OPENAI_API_KEY=sk-sua-chave-openai-aqui

# N8N (opcional)
N8N_BASE_URL=https://n8n.exemplo.com
N8N_API_KEY=sua-api-key-n8n

# Aplicação
APP_BASE_URL=https://sdria.alveseco.com.br
FLASK_ENV=production
```

### 3. Docker Compose para Produção

O arquivo `docker-compose.yml` já está configurado para produção:

```yaml
version: '3.8'

services:
  sdr-ia-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: sdr_ia_app
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY:-sdr-ia-secret-key-production-change-me}
      - FLASK_ENV=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - N8N_BASE_URL=${N8N_BASE_URL}
      - N8N_API_KEY=${N8N_API_KEY}
      - APP_BASE_URL=${APP_BASE_URL}
    volumes:
      - sdr_ia_data:/app/src/database
      - sdr_ia_logs:/app/logs
    networks:
      - sdr_ia_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.sdr-ia.rule=Host(\`sdria.alveseco.com.br\`)"
      - "traefik.http.routers.sdr-ia.entrypoints=websecure"
      - "traefik.http.routers.sdr-ia.tls.certresolver=letsencrypt"
      - "traefik.http.services.sdr-ia.loadbalancer.server.port=5000"

volumes:
  sdr_ia_data:
  sdr_ia_logs:

networks:
  sdr_ia_network:
```

### 4. Configuração de Proxy Reverso

#### Com Traefik (Recomendado)

As labels do Traefik já estão configuradas no docker-compose.yml:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.sdr-ia.rule=Host(\`sdria.alveseco.com.br\`)"
  - "traefik.http.routers.sdr-ia.entrypoints=websecure"
  - "traefik.http.routers.sdr-ia.tls.certresolver=letsencrypt"
  - "traefik.http.services.sdr-ia.loadbalancer.server.port=5000"
```

#### Com Nginx

Se usar Nginx como proxy reverso:

```nginx
server {
    listen 80;
    server_name sdria.alveseco.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sdria.alveseco.com.br;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Configuração de DNS

Configure seu DNS para apontar para o servidor:

```
Tipo: A
Nome: sdria (ou @)
Valor: IP_DO_SEU_SERVIDOR
TTL: 300
```

### 6. Passos de Deploy

1. **Configurar variáveis de ambiente** no Portainer
2. **Clicar em "Deploy the stack"**
3. **Aguardar o build e deploy** (pode levar alguns minutos)
4. **Verificar logs** na aba "Logs" da stack
5. **Testar acesso** via https://sdria.alveseco.com.br

### 7. Monitoramento

#### Verificar Status da Stack
1. Vá em **Stacks** > **sdr-ia-app**
2. Verifique se o status está "running"
3. Clique em "Logs" para ver logs em tempo real

#### Verificar Container
1. Vá em **Containers**
2. Procure por "sdr_ia_app"
3. Verifique se está "running"
4. Clique no container para ver detalhes

#### Health Check
A aplicação tem health check configurado:
- **Endpoint**: `http://localhost:5000/`
- **Intervalo**: 30 segundos
- **Timeout**: 30 segundos
- **Retries**: 3

### 8. Backup e Manutenção

#### Backup do Banco de Dados
```bash
# Criar backup manual
docker exec sdr_ia_app tar -czf /tmp/backup.tar.gz -C /app/src/database .

# Copiar backup para host
docker cp sdr_ia_app:/tmp/backup.tar.gz ./backup_$(date +%Y%m%d).tar.gz
```

#### Backup Automático
O docker-compose inclui um serviço de backup:

```bash
# Executar backup
docker-compose --profile backup run backup
```

#### Atualização da Aplicação
1. **Push mudanças** para o repositório GitHub
2. **No Portainer**, vá na stack
3. **Clique em "Update the stack"**
4. **Selecione "Pull and redeploy"**
5. **Clique em "Update"**

### 9. Troubleshooting

#### Problemas Comuns

**1. Container não inicia**
- Verifique logs do container
- Confirme variáveis de ambiente
- Verifique se a porta 5000 está disponível

**2. Erro de build**
- Verifique se o repositório GitHub está acessível
- Confirme se o Dockerfile está correto
- Verifique logs de build

**3. Aplicação não responde**
- Verifique se o container está rodando
- Teste acesso direto via IP:5000
- Verifique configuração do proxy reverso

**4. Erro de banco de dados**
- Verifique se o volume está montado corretamente
- Confirme permissões do diretório
- Verifique logs da aplicação

#### Comandos Úteis

```bash
# Ver logs da aplicação
docker logs sdr_ia_app -f

# Acessar container
docker exec -it sdr_ia_app bash

# Reiniciar container
docker restart sdr_ia_app

# Ver status dos containers
docker ps

# Ver uso de recursos
docker stats sdr_ia_app
```

### 10. Configuração de SSL

#### Let's Encrypt com Traefik
Se usar Traefik, o SSL é automático com as labels configuradas.

#### Certificado Manual
Para certificado manual, monte os arquivos:

```yaml
volumes:
  - /path/to/ssl/cert.pem:/app/ssl/cert.pem:ro
  - /path/to/ssl/key.pem:/app/ssl/key.pem:ro
```

### 11. Escalabilidade

#### Múltiplas Instâncias
Para alta disponibilidade:

```yaml
deploy:
  replicas: 3
  update_config:
    parallelism: 1
    delay: 10s
  restart_policy:
    condition: on-failure
```

#### Load Balancer
Configure load balancer (Traefik, Nginx, HAProxy) para distribuir carga.

### 12. Segurança

#### Configurações Recomendadas
- **Firewall**: Apenas portas 80, 443 e SSH abertas
- **SSL**: Sempre usar HTTPS em produção
- **Secrets**: Usar Docker secrets para dados sensíveis
- **Updates**: Manter sistema e containers atualizados

#### Monitoramento de Segurança
- **Logs**: Monitorar logs de acesso e erro
- **Alerts**: Configurar alertas para falhas
- **Backup**: Backup regular do banco de dados

---

## 📞 Suporte

Para problemas de deploy:

1. **Verifique logs** do container e da stack
2. **Consulte documentação** do Portainer
3. **Teste localmente** antes do deploy
4. **Use issues** do GitHub para reportar problemas

**Deploy preparado pela equipe Manus AI** 🚀

