import os
import datetime
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google import genai
from google.genai import types
import requests
from bs4 import BeautifulSoup
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_genai_client():
    """Returns a Gemini API client."""
    return genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

def fetch_article_text(url: str) -> str:
    """Fetches the main text from an online article URL."""
    try:
        print(f"--- Fetching content from: {url} ---")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script_or_style.decompose()

        # Try to find common article tags
        article = soup.find('article')
        if not article:
            # Fallback to main or specific containers if article tag is missing
            article = soup.find('main') or soup.find('div', class_=re.compile(r'article|post|content|entry', re.I))
        
        # If still not found, use body
        if not article:
            article = soup.body
            
        if not article:
            return ""

        # Get text from paragraphs
        paragraphs = article.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
        
        return text.strip()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return ""

def is_url(input_str: str) -> bool:
    """Simple check if a string is a URL."""
    return input_str.strip().startswith(('http://', 'https://'))

def is_youtube_url(url: str) -> bool:
    """Detects if a URL is a YouTube link."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return bool(re.match(youtube_regex, url))

def fetch_video_transcript(url: str) -> str:
    """Extracts the transcript text from a YouTube video URL."""
    try:
        print(f"--- Fetching transcript from: {url} ---")
        # Extract video ID from URL
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if not video_id_match:
            print("Could not extract YouTube video ID.")
            return ""
        
        video_id = video_id_match.group(1)
        api = YouTubeTranscriptApi()
        
        # Try to get English transcripts first
        try:
            transcript_data = api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
        except Exception:
            # Fallback: list all and take the first one available
            try:
                transcript_list = api.list(video_id)
                transcript = next(iter(transcript_list))
                transcript_data = transcript.fetch()
            except Exception as e2:
                print(f"No transcripts found for this video: {e2}")
                return ""
        
        # Join transcript parts into a single string
        text = ' '.join([item.text for item in transcript_data])
        return text.strip()
    except Exception as e:
        print(f"Error fetching YouTube transcript: {e}")
        return ""

def summarize_text(text: str) -> str:
    """Summarizes text into 5 key bullet points using Gemini API."""
    client = get_genai_client()
    print("\n--- Summarizing Text ---")
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='Summarize the following text into exactly 5 concise bullet points:\n\n' + text
    )
    return response.text

def extract_actions(summary: str) -> list[str]:
    """Extracts 3-5 concrete actionable tasks from summary points."""
    client = get_genai_client()
    print("--- Extracting Actions ---")
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents='Given these summary points, extract 3 to 5 concrete, actionable tasks for a calendar. Return ONLY a simple list, one per line:\n\n' + summary
    )
    # Basic parsing: split by lines and filter empty/index markers
    actions = [line.strip().lstrip('- 12345. ') for line in response.text.split('\n') if line.strip()]
    return actions[:5]

def ask_user(actions: list[str]) -> list[tuple[str, datetime.datetime]]:
    """Asks user if they want to schedule each action and gets time."""
    confirmed_actions = []
    print("\n--- Scheduling Actions ---")
    for action in actions:
        choice = input(f"\nDo you want to schedule: '{action}'? (y/n): ").lower()
        if choice == 'y':
            time_str = input("Enter start time (YYYY-MM-DD HH:MM) or press Enter for today 10:00: ")
            if not time_str:
                now = datetime.datetime.now()
                start_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
            else:
                try:
                    start_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    print("Invalid format. Defaulting to today 10:00.")
                    now = datetime.datetime.now()
                    start_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
            confirmed_actions.append((action, start_time))
    return confirmed_actions

def get_calendar_service():
    """Gets authenticated Google Calendar service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def add_to_calendar(action: str, start_time: datetime.datetime):
    """Adds action as an event to Google Calendar."""
    try:
        service = get_calendar_service()
        end_time = start_time + datetime.timedelta(hours=1)
        
        event = {
            'summary': action,
            'description': 'Generated by Calendar-Integrated Agent',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC', # Adjust to user timezone if needed
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")

    except HttpError as error:
        print(f"An error occurred: {error}")

def run_agent():
    """Main function to integrate all steps."""
    print("Welcome to the Information-to-Action Agent!")
    user_input = input("Enter one of the following:\n"
    "1. Direct text you want summarized\n"
    "2. URL to an online article\n"
    "3. URL to a YouTube video\n"
    "The agent will summarize the content, generate actions, and offer to add them to your Google Calendar.\n"
    "Your input: ").strip()
    if not user_input:
        print("Empty input. Exiting.")
        return

    if is_url(user_input):
        if is_youtube_url(user_input):
            text_input = fetch_video_transcript(user_input)
            source_type = "video transcript"
        else:
            text_input = fetch_article_text(user_input)
            source_type = "article"
            
        if not text_input:
            print(f"Could not extract text from the {source_type}. Please provide direct text.")
            return
        print(f"\nExtracted {len(text_input)} characters from {source_type}.")
    else:
        text_input = user_input

    # Step 1: Summarize
    summary = summarize_text(text_input)
    print("\nSummary Points:")
    print(summary)

    # Step 2: Extract Actions
    actions = extract_actions(summary)
    print("\nExtracted Actionable Tasks:")
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action}")

    # Step 3 & 4: Ask User and Add to Calendar
    confirmed = ask_user(actions)
    for action, start_time in confirmed:
        add_to_calendar(action, start_time)

    print("\nProcessing complete. Thank you!")

if __name__ == '__main__':
    run_agent()
