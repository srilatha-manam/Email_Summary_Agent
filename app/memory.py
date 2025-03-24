import logging
from langchain.memory import ConversationBufferMemory

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('memory.log')  # Logs to a file
    ]
)
logger = logging.getLogger(__name__)

try:
    memory = ConversationBufferMemory(memory_key="chat_history")
    logger.info("ConversationBufferMemory initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ConversationBufferMemory: {str(e)}")
    raise RuntimeError(f"Memory initialization failed: {str(e)}")

def add_to_memory(email_id, subject, priority, summary):
    """Add email context to memory."""
    try:
        memory.save_context(
            {"input": f"Email ID: {email_id}, Subject: {subject}"},
            {"output": f"Priority: {priority}, Summary: {summary}"}
        )
        logger.info(f"Added context to memory for email ID={email_id}, Subject={subject}")
    except Exception as e:
        logger.error(f"Error adding context to memory for email ID={email_id}: {str(e)}")
        raise ValueError(f"Failed to add context to memory for email ID={email_id}: {str(e)}")

def get_memory():
    """Retrieve the current memory history."""
    try:
        memory_history = memory.load_memory_variables({})["chat_history"]
        logger.info(f"Retrieved memory history with {len(memory_history)} entries")
        return memory_history
    except Exception as e:
        logger.error(f"Error retrieving memory history: {str(e)}")
        raise RuntimeError(f"Failed to retrieve memory history: {str(e)}")