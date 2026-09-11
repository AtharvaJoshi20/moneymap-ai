import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = "gemini-3.5-flash-lite"      # Everyday chat
ADVANCED_MODEL = "gemini-3.5-flash"          # Deep analysis


if not API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY not found. Create a .env file in the project root."
    )

# Create one reusable client for the whole application.
_client = genai.Client(api_key=API_KEY)


def get_gemini_client():
    """
    Return the initialized Gemini client.
    """
    return _client


def get_model_name():
    """
    Return the default Gemini model used by MoneyMap AI.
    """
    return DEFAULT_MODEL

def get_advanced_model():
    """
    Return the advanced Gemini model used by MoneyMap AI.
    """
    return ADVANCED_MODEL