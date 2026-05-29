from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    print("\nAI:", response.choices[0].message.content) 