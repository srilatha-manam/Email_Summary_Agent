from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def add_to_memory(email_id, subject, summary):
    memory.chat_memory.add_message(HumanMessage(content=f"Email ID: {email_id}, Subject: {subject}"))
    memory.chat_memory.add_message(AIMessage(content=f"Summary: {summary}"))

def get_memory():
    return memory.load_memory_variables({})["chat_history"]