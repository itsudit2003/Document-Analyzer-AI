import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Generate logical question from given context
def generate_challenge_question(context: str) -> str:
    prompt = (
        "From the following document content, generate a logical comprehension question "
        "that checks the user's understanding:\n\n"
        f"{context}\n\n"
        "Question:"
    )
    response = model.generate_content(prompt)
    return response.text.strip()

# Evaluate user answer based on context
def evaluate_user_answer(context: str, question: str, user_answer: str) -> dict:
    prompt = (
        f"Document:\n{context}\n\n"
        f"Question: {question}\n"
        f"User's Answer: {user_answer}\n\n"
        "Evaluate the answer and reply in this format:\n"
        "Correct: Yes or No\nReason: Explain why the answer is right or wrong."
    )
    response = model.generate_content(prompt)
    
    lines = response.text.strip().split("\n")
    result = {"correct": "No", "reason": "Could not parse response"}
    
    for line in lines:
        if line.lower().startswith("correct:"):
            result["correct"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("reason:"):
            result["reason"] = line.split(":", 1)[1].strip()
    
    return result
