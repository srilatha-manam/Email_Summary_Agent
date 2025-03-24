import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('prioritizer.log')  # Logs to a file
    ]
)
logger = logging.getLogger(__name__)

PRIORITY_KEYWORDS = {
    "urgent": 10, "immediately": 10, "important": 8, "meeting": 6, "schedule": 6
}

def prioritize_email(subject, body):
    """Prioritize an email based on keywords in subject and body."""
    try:
        # Validate inputs
        if not isinstance(subject, str) or not isinstance(body, str):
            raise ValueError("Subject and body must be strings")
        
        score = 0
        text = (subject + " " + body).lower()
        logger.debug(f"Processing text for prioritization: {text[:50]}...")

        for keyword, value in PRIORITY_KEYWORDS.items():
            if keyword in text:
                score = max(score, value)
                logger.debug(f"Found keyword '{keyword}' with value {value}, new score: {score}")
        
        logger.info(f"Prioritized email with score: {score}")
        return scor