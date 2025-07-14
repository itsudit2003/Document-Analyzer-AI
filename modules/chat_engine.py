from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from db.database import save_chat_history, load_chat_memory_for_user
from dotenv import load_dotenv
import os

load_dotenv()
GEM_KEY = os.getenv("GOOGLE_API_KEY")

if not GEM_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env!")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.4,
    max_output_tokens=500,
)

chat_memory = {}

#  Used after new file upload to reset + load fresh context
def reset_user_memory(username, context):
    system_instruction = (
        "You are a friendly natured helpful assistant. "
        "Only answer based on the following document context. "
        "Respond concisely (within 2–2 lines) also with a brief justification "
        "(e.g., Reference to paragraph 3 of section 1...). Avoid unrelated details "
        "and also keep yourself updated with the latest document context uploaded.\n\n"
        f"Context:\n{context}"
    )
    chat_memory[username] = [SystemMessage(content=system_instruction)]

# Used during login/register to load DB chat history
def initialize_user_memory(username):
    history = load_chat_memory_for_user(username)
    memory = []
    for q, a in history:
        memory.append(HumanMessage(content=q))
        memory.append(AIMessage(content=a))
    chat_memory[username] = memory

# After question from user
def generate_answer(username, user_question, context):
    if username not in chat_memory:
        chat_memory[username] = []

    memory = chat_memory[username]

    # ✅ If no system context present (failsafe)
    if not any(isinstance(m, SystemMessage) for m in memory):
        reset_user_memory(username, context)
        memory = chat_memory[username]

    memory.append(HumanMessage(content=user_question))

    if len(memory) > 21:
        memory = [memory[0]] + memory[-20:]

    response = llm.invoke(memory)
    reply = response.content.strip()

    memory.append(AIMessage(content=reply))
    chat_memory[username] = memory

    return reply
