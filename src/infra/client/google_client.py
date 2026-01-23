"""Google API clients (GenAI and Calendar)."""
import logging
import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google import genai
from src.core.settings import settings

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_genai_client() -> genai.Client:
    """Returns a Gemini API client."""
    return genai.Client(api_key=settings.GOOGLE_API_KEY)


def get_calendar_service():
    """Gets authenticated Google Calendar service."""
    # Build paths relative to the project root
    base_dir = Path(__file__).parent.parent.parent.parent
    tokens_dir = base_dir / 'storage' / 'tokens'
    tokens_dir.mkdir(parents=True, exist_ok=True)
    token_path = tokens_dir / 'token.json'
    creds_path = base_dir / 'credentials.json'

    creds = None
    if os.path.exists(token_path):
        try:
            logger.debug("Loading existing token from file")
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except ValueError as e:
            # If token is corrupted or missing refresh_token, delete it
            if "missing fields" in str(e).lower() or "refresh_token" in str(e).lower():
                logger.warning("Invalid token file detected, deleting and requesting new authorization")
                token_path.unlink()  # Delete invalid token
                creds = None
            else:
                logger.error(f"Error loading token: {e}", exc_info=True)
                raise
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired token")
            creds.refresh(Request())
            logger.info("Token refreshed successfully")
        else:
            if not os.path.exists(creds_path):
                logger.error(f"credentials.json not found at {creds_path}")
                raise FileNotFoundError(
                    f"Could not find credentials.json at {creds_path}. "
                    "Please ensure it is present."
                )
            logger.info("Starting OAuth flow for calendar access")
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=8080)
            logger.info("OAuth authorization completed")
            
            # Check if we got refresh_token, if not, we need to force re-consent
            if not creds.refresh_token:
                # Delete the token file to force fresh authorization
                if token_path.exists():
                    token_path.unlink()
                # Force consent screen by using authorization_url with prompt=consent
                auth_url, _ = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true',
                    prompt='consent'  # Force consent to get refresh_token
                )
                print(f"\nPlease visit this URL to re-authorize (this will ensure refresh_token):")
                print(auth_url)
                print("\nAfter authorization, copy the full redirect URL from your browser.")
                redirect_response = input("Enter the full redirect URL: ").strip()
                
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(redirect_response)
                query_params = parse_qs(parsed.query)
                
                if 'code' not in query_params:
                    raise ValueError("Authorization code not found in redirect URL")
                
                code = query_params['code'][0]
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                if not creds.refresh_token:
                    raise ValueError(
                        "Still no refresh_token. Please revoke app access in your Google account "
                        "(https://myaccount.google.com/permissions) and try again."
                    )
        
        # Save token only if it has refresh_token
        if creds.refresh_token:
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            logger.info("Token saved successfully")
        else:
            logger.error("Cannot save token without refresh_token")
            raise ValueError("Cannot save token without refresh_token")
    
    logger.debug("Calendar service initialized")
    return build('calendar', 'v3', credentials=creds)
