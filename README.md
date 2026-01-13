# Information-to-Action Calendar-Integrated Agent

This agent summarizes articles or YouTube videos into key points, extracts actionable tasks, and schedules them on your Google Calendar.

## Prerequisites

- Python 3.9+
- A Google Cloud account

## Setup Instructions

### 1. Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a new API key.
3. In this project, create a `.env` file from the `.env.example`:
   ```bash
   cp .env.example .env
   ```
4. Paste your API key into `.env`: `GOOGLE_API_KEY=your_key_here`.

### 2. Google Calendar API (OAuth)
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named **Info-to-Action**.
3. **Enable API**: Go to "APIs & Services" > "Library" and search for/enable **Google Calendar API**.
4. **OAuth Consent Screen**:
   - Go to "APIs & Services" > "OAuth consent screen".
   - Choose **External**.
   - Fill in the required app information.
   - **IMPORTANT**: Scroll to "Test users" and add your own Google email address. (Required while the app is in "Testing" mode).
5. **Create Credentials**:
   - Go to "APIs & Services" > "Credentials".
   - Click **Create Credentials** > **OAuth client ID**.
   - Select **Application type**: **Desktop app**.
   - Click **Create** and download the JSON file.
6. **Rename and Move**: Move the downloaded JSON into this project folder and rename it exactly to `credentials.json`.

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv google-genai beautifulsoup4 requests youtube-transcript-api
   ```

## Running the Agent

```bash
python modular_agent.py
```

- When prompted, provide a text snippet, an article URL, or a YouTube URL.
- On the first run, a browser window will open for Google Calendar authorization. After authorizing, a `token.json` file will be created locally.
