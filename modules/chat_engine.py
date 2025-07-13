from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from db.database import save_chat_history, load_chat_memory_for_user
from dotenv import load_dotenv
import os

load_dotenv()
GEM_KEY = os.getenv("GOOGLE_API_KEY")

if not GEM_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env!")

# Initialize Gemini with concise answer settings
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.4,
    max_output_tokens=500,
)

# In-memory user context memory
chat_memory = {}

# 1️⃣ Load existing history from DB and store in-memory
def initialize_user_memory(username):
    history = load_chat_memory_for_user(username)
    memory = []
    for q, a in history:
        memory.append(HumanMessage(content=q))
        memory.append(AIMessage(content=a))
    chat_memory[username] = memory

# 2️⃣ Main generate_answer function
def generate_answer(username, user_question, context):
    if username not in chat_memory:
        chat_memory[username] = []

    memory = chat_memory[username]

    # 3️⃣ Add context only once (or reset if user uploads new doc)
    if not any(isinstance(m, SystemMessage) for m in memory):
        system_instruction = (
            "You are a helpful assistant. "
            "Only answer based on the following document context. "
            "Respond concisely (within 2–5 lines). Avoid unrelated details.\n\n"
            f"Context:\n{context}"
        )
        memory.insert(0, SystemMessage(content=system_instruction))

    # 4️⃣ Add user question to memory
    memory.append(HumanMessage(content=user_question))

    # 5️⃣ Keep only last 10 turns + context
    if len(memory) > 21:
        memory = [memory[0]] + memory[-20:]

    # 6️⃣ Get response from Gemini
    response = llm.invoke(memory)
    reply = response.content.strip()

    # 7️⃣ Store response
    memory.append(AIMessage(content=reply))
    chat_memory[username] = memory

    # 8️⃣ Save to DB
    save_chat_history(username, user_question, reply)

    return reply
