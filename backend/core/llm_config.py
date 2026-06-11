from langchain_google_genai import GoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# get the gemini model 
def get_gemini_llm():
    return GoogleGenerativeAI(
        model = 'gemini-3.1-flash-lite',
        temperature = 0.5,
        google_api_key = os.getenv("GOOGLE_API_KEY"),
    )

# now generate the response 
def generate_answer(prompt: str) -> str:
    llm = get_gemini_llm()
    response = llm.invoke(prompt)
    return response.content


