# Workflows N8N - SDR IA

Este diretório contém os workflows do N8N para automação do sistema SDR IA.

## Workflows Disponíveis

### 1. SDR WHATSAPP IA - DINÂMICO
**Arquivo:** `SDRWHATSAPPIA_DINAMICO.json`

**Descrição:** Workflow principal para processamento de mensagens do WhatsApp com IA.

**Funcionalidades:**
- Recebe mensagens via webhook
- Busca configurações do cliente
- Processa mensagens com ChatGPT
- Integra com Kommo CRM
- Analisa áudio e imagens
- Gera respostas automáticas

**Webhook Path:** `sdr-webhook`
**Webhook ID:** `sdr-webhook-dinamico`

### 2. MUDA ETAPA IA TAG - DINÂMICO
**Arquivo:** `MUDAETAPAIATAG_DINAMICO.json`

**Descrição:** Workflow para mudança automática de etapas de leads baseada em tags IA.

**Funcionalidades:**
- Recebe eventos de mudança de etapa
- Busca configurações do cliente
- Aplica regras de negócio
- Atualiza status no Kommo CRM
- Registra logs de atividade

**Webhook Path:** `muda-etapa-webhook`
**Webhook ID:** `muda-etapa-webhook-dinamico`

## Configuração dos Workflows

### Pré-requisitos
1. Instância do N8N configurada
2. Aplicação SDR IA rodando
3. Credenciais do Kommo CRM
4. API Key do ChatGPT

### Importação dos Workflows

1. Acesse o painel do N8N
2. Vá em "Workflows" > "Import from file"
3. Selecione o arquivo JSON do workflow
4. Configure as credenciais necessárias
5. Ative o workflow

### Configuração de Webhooks

Os workflows esperam receber dados nos seguintes formatos:

#### SDR Webhook
```json
{
  "cliente_id": 123,
  "webhook_url": "https://sdria.alveseco.com.br/api/webhook/sdr",
  "message_data": {
    "from": "+5511999999999",
    "body": "Mensagem do cliente",
    "type": "text|audio|image",
    "media_url": "url_da_midia"
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "action": "process_message"
}
```

#### Muda Etapa Webhook
```json
{
  "cliente_id": 123,
  "webhook_url": "https://sdria.alveseco.com.br/api/webhook/sdr",
  "lead_data": {
    "lead_id": 456,
    "current_stage": "contato_inicial",
    "contact_info": {...}
  },
  "new_stage": "qualificacao",
  "timestamp": "2024-01-01T12:00:00Z",
  "action": "change_stage"
}
```

## URLs dos Webhooks

Para cada cliente, as URLs dos webhooks seguem o padrão:

- **Webhook Principal:** `https://sdria.alveseco.com.br/api/webhook/sdr?clienteId={CLIENTE_ID}`
- **Configurações:** `https://sdria.alveseco.com.br/api/webhook/config/{CLIENTE_ID}`
- **Teste:** `https://sdria.alveseco.com.br/api/webhook/test/{CLIENTE_ID}`

## Integração com a Aplicação

### Endpoints da API

#### Processar Mensagem
```
POST /api/n8n/process/message
```

#### Processar Áudio
```
POST /api/n8n/process/audio
```

#### Processar Imagem
```
POST /api/n8n/process/image
```

#### Mudar Etapa
```
POST /api/n8n/change-stage
```

#### Obter URLs de Webhook
```
GET /api/n8n/webhook-url/{cliente_id}
```

#### Status do N8N
```
GET /api/n8n/status/{cliente_id}
```

### Variáveis de Ambiente

Configure as seguintes variáveis de ambiente na aplicação:

```bash
N8N_BASE_URL=https://n8n.exemplo.com
N8N_API_KEY=sua_api_key_do_n8n
APP_BASE_URL=https://sdria.alveseco.com.br
```

## Fluxo de Dados

### 1. Recebimento de Mensagem
1. WhatsApp/Sistema externo envia dados para webhook do N8N
2. N8N processa dados iniciais
3. N8N faz requisição para aplicação SDR IA
4. Aplicação retorna configurações do cliente
5. N8N executa ações baseadas nas configurações

### 2. Processamento com IA
1. N8N envia conteúdo para ChatGPT
2. ChatGPT analisa e retorna resposta
3. N8N processa resposta da IA
4. N8N atualiza Kommo CRM se necessário

### 3. Mudança de Etapa
1. Sistema detecta necessidade de mudança
2. N8N recebe evento de mudança
3. N8N valida regras de negócio
4. N8N atualiza status no Kommo CRM
5. N8N registra log na aplicação

## Monitoramento

### Logs de Execução
- Acesse o painel do N8N
- Vá em "Executions" para ver histórico
- Filtre por workflow e data

### Logs da Aplicação
- Logs de webhook: `/api/webhook/sdr`
- Logs de segurança: tabela `log_atividade`
- Logs de controle: tabela `controle_requisicoes`

## Troubleshooting

### Problemas Comuns

1. **Webhook não recebe dados**
   - Verifique se o workflow está ativo
   - Confirme a URL do webhook
   - Verifique logs de execução

2. **Erro de autenticação**
   - Verifique credenciais do Kommo CRM
   - Confirme API Key do ChatGPT
   - Verifique configurações do cliente

3. **Timeout de execução**
   - Aumente timeout do N8N
   - Otimize prompts do ChatGPT
   - Verifique conectividade de rede

### Contato para Suporte
- Documentação: Este arquivo
- Logs: Painel do N8N e aplicação SDR IA
- Configurações: Painel administrativo da aplicação

