from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()
GEM_KEY = os.getenv("GOOGLE_API_KEY")

if not GEM_KEY:
    raise ValueError("GOOGLE_API_KEY not found!")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.4)

def summarize_text(text):
    prompt = f"Summarize this document in not more than 70 words:\n\n{text[:12000]}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
