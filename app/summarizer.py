import logging
from transformers import pipeline
from transformers import PipelineException

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('summarizer.log')  # Logs to a file
    ]
)
logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self):
        """Initialize the summarization model."""
        try:
            self.model = pipeline("summarization", model="facebook/bart-large-cnn")
            logger.info("Summarization model 'facebook/bart-large-cnn' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize summarization model: {str(e)}")
            raise RuntimeError(f"Failed to initialize summarizer: {str(e)}")

    def summarize(self, text):
        """Summarize the given text using the model."""
        try:
            if not isinstance(text, str):
                raise ValueError("Input text must be a string")
            if not text.strip():
                raise ValueError("Input text cannot be empty")

            logger.debug(f"Summarizing text: {text[:50]}...")
            summary = self.model(text[:1024], max_length=50, mi