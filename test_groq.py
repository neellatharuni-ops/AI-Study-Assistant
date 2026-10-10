import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY not found.")
    exit()

client = Groq(api_key=api_key)

response = client.chat.completions.create(
model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "Explain B-tree in simple words for a first-year CSE student."
        }
    ]
)

print("\n===== AI RESPONSE =====\n")
print(response.choices[0].message.content)