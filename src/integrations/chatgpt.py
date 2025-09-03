"""
Integração com ChatGPT/OpenAI
"""
import openai
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class ChatGPTClient:
    """Cliente para integração com ChatGPT/OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Inicializa o cliente ChatGPT
        
        Args:
            api_key: Chave da API OpenAI
            model: Modelo a ser usado (gpt-3.5-turbo, gpt-4, etc.)
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, 
                         max_tokens: int = 1000, temperature: float = 0.7) -> Dict:
        """
        Gera uma resposta usando ChatGPT
        
        Args:
            prompt: Prompt do usuário
            system_prompt: Prompt do sistema (opcional)
            max_tokens: Número máximo de tokens
            temperature: Temperatura para controlar criatividade
            
        Returns:
            Resposta do ChatGPT
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                'success': True,
                'response': response.choices[0].message.content,
                'usage': response.usage,
                'model': self.model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_audio_transcript(self, transcript: str, custom_prompt: Optional[str] = None) -> Dict:
        """
        Analisa transcrição de áudio
        
        Args:
            transcript: Transcrição do áudio
            custom_prompt: Prompt personalizado (opcional)
            
        Returns:
            Análise da transcrição
        """
        default_prompt = """
        Analise a seguinte transcrição de áudio de uma conversa de vendas/atendimento:
        
        {transcript}
        
        Forneça uma análise estruturada incluindo:
        1. Resumo da conversa
        2. Pontos principais discutidos
        3. Sentimento do cliente (positivo, neutro, negativo)
        4. Próximos passos sugeridos
        5. Classificação da qualidade do lead (quente, morno, frio)
        
        Responda em formato JSON estruturado.
        """
        
        prompt = custom_prompt or default_prompt
        formatted_prompt = prompt.format(transcript=transcript)
        
        system_prompt = "Você é um especialista em análise de conversas de vendas e atendimento ao cliente."
        
        return self.generate_response(formatted_prompt, system_prompt)
    
    def analyze_image_description(self, image_description: str, custom_prompt: Optional[str] = None) -> Dict:
        """
        Analisa descrição de imagem
        
        Args:
            image_description: Descrição da imagem
            custom_prompt: Prompt personalizado (opcional)
            
        Returns:
            Análise da imagem
        """
        default_prompt = """
        Analise a seguinte descrição de imagem recebida em uma conversa:
        
        {image_description}
        
        Forneça uma análise incluindo:
        1. Tipo de conteúdo identificado
        2. Relevância para vendas/negócios
        3. Possíveis ações a serem tomadas
        4. Classificação de prioridade (alta, média, baixa)
        
        Responda em formato JSON estruturado.
        """
        
        prompt = custom_prompt or default_prompt
        formatted_prompt = prompt.format(image_description=image_description)
        
        system_prompt = "Você é um especialista em análise de conteúdo visual para vendas e atendimento."
        
        return self.generate_response(formatted_prompt, system_prompt)
    
    def generate_sales_response(self, context: str, customer_message: str, 
                               custom_prompt: Optional[str] = None) -> Dict:
        """
        Gera resposta de vendas baseada no contexto
        
        Args:
            context: Contexto da conversa/cliente
            customer_message: Mensagem do cliente
            custom_prompt: Prompt personalizado (opcional)
            
        Returns:
            Resposta sugerida
        """
        default_prompt = """
        Contexto do cliente/conversa:
        {context}
        
        Mensagem do cliente:
        {customer_message}
        
        Gere uma resposta profissional e persuasiva que:
        1. Responda adequadamente à mensagem do cliente
        2. Mantenha o interesse na conversa
        3. Direcione para o próximo passo da venda
        4. Seja natural e não robótica
        
        Forneça apenas a resposta sugerida, sem explicações adicionais.
        """
        
        prompt = custom_prompt or default_prompt
        formatted_prompt = prompt.format(context=context, customer_message=customer_message)
        
        system_prompt = "Você é um especialista em vendas e comunicação persuasiva."
        
        return self.generate_response(formatted_prompt, system_prompt)
    
    def classify_lead_intent(self, message: str) -> Dict:
        """
        Classifica a intenção do lead baseada na mensagem
        
        Args:
            message: Mensagem do lead
            
        Returns:
            Classificação da intenção
        """
        prompt = f"""
        Classifique a intenção da seguinte mensagem de um lead:
        
        "{message}"
        
        Classifique em uma das categorias:
        - interesse_alto: Cliente demonstra forte interesse em comprar
        - interesse_medio: Cliente tem interesse mas precisa de mais informações
        - interesse_baixo: Cliente apenas explorando opções
        - duvida_tecnica: Cliente tem dúvidas técnicas sobre o produto/serviço
        - duvida_preco: Cliente tem dúvidas sobre preços/condições
        - reclamacao: Cliente tem alguma reclamação ou problema
        - agendamento: Cliente quer agendar reunião/demonstração
        - outros: Não se encaixa nas categorias acima
        
        Responda apenas com a categoria e um score de confiança de 0 a 100.
        Formato: categoria|score
        """
        
        system_prompt = "Você é um especialista em classificação de intenções de clientes."
        
        return self.generate_response(prompt, system_prompt, max_tokens=50)
    
    def extract_contact_info(self, message: str) -> Dict:
        """
        Extrai informações de contato de uma mensagem
        
        Args:
            message: Mensagem para extrair informações
            
        Returns:
            Informações de contato extraídas
        """
        prompt = f"""
        Extraia todas as informações de contato da seguinte mensagem:
        
        "{message}"
        
        Procure por:
        - Nome
        - Telefone
        - Email
        - Empresa
        - Cargo
        - Endereço
        
        Responda em formato JSON com as informações encontradas.
        Se não encontrar alguma informação, use null.
        """
        
        system_prompt = "Você é um especialista em extração de informações de contato."
        
        return self.generate_response(prompt, system_prompt)


def create_chatgpt_client(api_key: str, model: str = "gpt-3.5-turbo") -> ChatGPTClient:
    """
    Cria uma instância do cliente ChatGPT
    
    Args:
        api_key: Chave da API OpenAI
        model: Modelo a ser usado
        
    Returns:
        Instância do cliente ChatGPT
    """
    return ChatGPTClient(api_key, model)


def test_chatgpt_connection(api_key: str, model: str = "gpt-3.5-turbo") -> Dict:
    """
    Testa a conexão com ChatGPT
    
    Args:
        api_key: Chave da API OpenAI
        model: Modelo a ser usado
        
    Returns:
        Resultado do teste
    """
    try:
        client = create_chatgpt_client(api_key, model)
        response = client.generate_response(
            "Responda apenas 'OK' para confirmar que a conexão está funcionando.",
            max_tokens=10
        )
        
        if response['success']:
            return {
                'success': True,
                'message': 'Conexão com ChatGPT estabelecida com sucesso',
                'model': model,
                'response': response['response']
            }
        else:
            return {
                'success': False,
                'message': f'Erro ao conectar com ChatGPT: {response["error"]}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Erro ao conectar com ChatGPT: {str(e)}'
        }

