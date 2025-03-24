import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('gmail_client.log')  # Logs to a file
    ]
)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Initialize and return the Gmail API service."""
    try:
        creds = None
        if os.path.exists('token.json'):
            try:
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                logger.info("Loaded credentials from token.json")
            except ValueError as e:
                logger.error(f"Invalid token.json file: {str(e)}")
                raise ValueError(f"Failed to load credentials from token.json: {str(e)}")

        if not creds or not creds.valid:
            if not os.path.exists('credentials.json'):
                logger.error("credentials.json file not found")
                raise FileNotFoundError("credentials.json file is missing")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                logger.info("OAuth flow completed and token.json generated")
            except Exception as e:
                logger.error(f"Error during OAuth flow: {str(e)}")
                raise RuntimeError(f"Failed to complete OAuth authentication: {str(e)}")

        service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API service initialized successfully")
        return service

    except Exception as e:
        logger.error(f"Unexpected error initializing Gmail service: {str(e)}")
        raise RuntimeError(f"Unexpected error initializing Gmail service: {str(e)}")

def fetch_emails(max_results=10):
    """Fetch a specified number of recent emails from Gmail."""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        logger.info(f"Fetched {len(messages)} email messages from Gmail")

        emails = []
        for msg in messages:
            try:
                email = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = {h['name']: h['value'] for h in email['payload']['headers']}
                subject = headers.get('Subject', 'No Subject')
                body = email.get('snippet', '')
                emails.append({'id': msg['id'], 'subject': subject, 'body': body})
                logger.debug(f"Processed email ID={msg['id']}, Subject={subject}")
            except HttpError as e:
                logger.error(f"HttpError fetching email ID={msg['id']}: {str(e)}")
                continue  # Skip this email and continue with others
            except Exception as e:
                logger.error(f"Unexpected error fetching email ID={msg['id']}: {str(e)}")
                continue  # Skip this email and continue with others

        logger.info(f"Successfully processed {len(emails)} emails")
        return emails

    except HttpError as e:
        logger.error(f"HttpError fetching email list: {str(e)}")
        raise ValueError(f"Failed to fetch emails due to API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching emails: {str(e)}")
        raise RuntimeError(f"Unexpected error fetching emails: {str(e)}")