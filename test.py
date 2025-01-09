from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now you can access the variables
api_key = os.getenv('OPENAI_API_KEY')
print(f"OPENAI_API_KEY: {api_key}")

