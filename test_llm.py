import os
from dotenv import load_dotenv
from groq import Groq

# Load the .env file so we can access GROQ_API_KEY
load_dotenv()

# Create a client using our API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Send a simple test message
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "Say hello and tell me one fun fact about Python the programming language."}
    ]
)

print(response.choices[0].message.content)