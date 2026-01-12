from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import datetime
import logging
from typing import Any

from ...domain.ports.agent_port import AIAgentPort
from ...config import AGENDA_FILENAME, SYSTEM_PROMPT_PATH

logger = logging.getLogger(__name__)

class LangChainAgentAdapter(AIAgentPort):
    """Adaptador de infraestructura para el agente de LangChain."""
    
    def __init__(self, openai_api_key: str, tools: list, model_name: str = "gpt-3.5-turbo"):
        self.openai_api_key = openai_api_key
        self.tools = tools
        self.model_name = model_name
        self.executor = self._initialize_executor()

    def _initialize_executor(self) -> AgentExecutor:
        # Lógica de temperatura ya implementada previamente
        if self.model_name.startswith("gpt-5") or self.model_name.startswith("o1"):
            temp = 1.0
        else:
            temp = 0.0
            
        llm = ChatOpenAI(
            model_name=self.model_name, 
            openai_api_key=self.openai_api_key, 
            temperature=temp
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        try:
            with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
                system_prompt_raw = f.read()
            system_prompt = system_prompt_raw.format(today=today, AGENDA_FILENAME=AGENDA_FILENAME)
        except Exception as e:
            logger.error(f"Error cargando prompt: {e}")
            system_prompt = f"Eres un asistente de agenda. Hoy es {today}. Gestionas {AGENDA_FILENAME}."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )

    def get_response(self, user_input: str, chat_history: Any = None) -> str:
        # El historial se maneja dentro de la memoria del executor
        response_dict = self.executor.invoke({"input": user_input})
        return response_dict["output"]
