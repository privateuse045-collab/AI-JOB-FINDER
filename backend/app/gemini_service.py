import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def ask_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    answer = ask_gemini(
        "Hello Gemini! Tell me in one sentence what you can do."
    )

    print("\nGemini Response:")
    print(answer)