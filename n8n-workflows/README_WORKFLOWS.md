# Workflows N8N Dinâmicos - SDR IA

Este diretório contém os workflows do N8N modificados para integração dinâmica com o sistema SDR IA.

## Arquivos

### 1. SDRWHATSAPPIA_DINAMICO.json
Workflow principal para processamento de mensagens WhatsApp com IA.

**Principais modificações:**
- Busca configurações dinamicamente via webhook da aplicação
- Utiliza credenciais do cliente (Kommo, ChatGPT) obtidas da API
- Processa diferentes tipos de mídia (texto, áudio, imagem)
- Executa ações baseadas em tags configuradas pelo cliente
- Suporte a múltiplos clientes com configurações independentes

**Fluxo:**
1. Recebe webhook inicial
2. Busca configurações do cliente via API
3. Verifica se N8N está habilitado para o cliente
4. Processa mensagem com IA usando prompts personalizados
5. Executa ações baseadas em tags (transferir vendedor, suporte, etc.)
6. Atualiza lead no Kommo
7. Envia resposta

### 2. MUDAETAPAIATAG_DINAMICO.json
Workflow para mudança automática de etapas no Kommo baseada em tags.

**Principais modificações:**
- Busca configurações do cliente dinamicamente
- Identifica tag acionada automaticamente
- Utiliza funil_id e pipeline_id específicos do cliente
- Adiciona nota explicativa no lead
- Notifica sucesso/erro via webhook

**Fluxo:**
1. Recebe webhook de mudança de etapa
2. Busca configurações do cliente
3. Processa qual tag foi acionada
4. Valida dados necessários
5. Busca lead atual no Kommo
6. Atualiza etapa do lead
7. Adiciona nota explicativa
8. Notifica resultado

## Configuração no N8N

### 1. Importar Workflows
```bash
# No N8N, vá em Workflows > Import from File
# Selecione os arquivos JSON deste diretório
```

### 2. Configurar Credenciais Dinâmicas
Os workflows agora buscam credenciais dinamicamente da aplicação, mas você ainda precisa configurar:

**ChatGPT Dinâmico:**
- Nome: `chatgpt-dinamico`
- Tipo: OpenAI
- API Key: Será obtida dinamicamente do cliente

**Kommo Dinâmico:**
- Nome: `kommo-dinamico`
- Tipo: Kommo CRM
- Token: Será obtido dinamicamente do cliente

### 3. Configurar Webhooks
Os workflows usam webhooks específicos:

**SDR WhatsApp IA:**
- Path: `sdr-webhook`
- URL: `https://seu-n8n.com/webhook/sdr-webhook`

**Muda Etapa IA Tag:**
- Path: `muda-etapa-webhook`
- URL: `https://seu-n8n.com/webhook/muda-etapa-webhook`

### 4. Variáveis de Ambiente
Configure no N8N:
```
SDR_IA_API_URL=https://sdria.alveseco.com.br
```

## Integração com a Aplicação

### Webhook Principal
A aplicação fornece o endpoint principal:
```
POST https://sdria.alveseco.com.br/api/webhook/sdr?clienteId={ID}
```

**Resposta esperada:**
```json
{
  "cliente_id": "123",
  "configuracoes": {
    "kommo_token": "token_do_cliente",
    "kommo_domain": "https://cliente.kommo.com",
    "chatgpt_api_key": "sk-...",
    "chatgpt_model": "gpt-4",
    "pipeline_id": "12345",
    "funil_ids": ["67890", "67891"],
    "prompt_agente_ia": "Você é um assistente...",
    "prompt_audio": "Transcreva este áudio...",
    "prompt_imagem": "Descreva esta imagem...",
    "usar_n8n": true
  },
  "tags_permitidas": ["transfere_vendedor", "transfere_suporte"],
  "webhook_data": {...}
}
```

### Configuração de Tags
Cada cliente pode configurar tags personalizadas:
- `transfere_vendedor`: Move para funil de vendas
- `transfere_suporte`: Move para funil de suporte
- `transfere_ligacao`: Move para funil de ligações
- Tags customizadas com funil_id específico

## Vantagens da Versão Dinâmica

1. **Multi-tenant**: Suporte a múltiplos clientes
2. **Configuração flexível**: Cada cliente tem suas próprias configurações
3. **Segurança**: Credenciais isoladas por cliente
4. **Escalabilidade**: Fácil adição de novos clientes
5. **Manutenção**: Workflows centralizados, configurações distribuídas
6. **Auditoria**: Logs de atividade por cliente

## Troubleshooting

### Erro: "Cliente não encontrado"
- Verifique se o clienteId está correto na URL
- Confirme se o cliente está ativo e aprovado

### Erro: "N8N não habilitado"
- Verifique a configuração `usar_n8n` do cliente
- Confirme se o cliente tem permissão para usar N8N

### Erro: "Credenciais inválidas"
- Verifique se as credenciais do Kommo/ChatGPT estão corretas
- Confirme se os tokens não expiraram

### Erro: "Tag não encontrada"
- Verifique se a tag está cadastrada para o cliente
- Confirme se a tag está ativa
- Verifique se funil_id e pipeline_id estão configurados

## Monitoramento

Use os endpoints da aplicação para monitorar:
- `/api/cliente/estatisticas` - Estatísticas do cliente
- `/api/admin/logs` - Logs de atividade (admin)
- `/api/webhook/test/{cliente_id}` - Teste de webhook

