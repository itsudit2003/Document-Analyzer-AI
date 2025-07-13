from flask import Blueprint, render_template, request, session, redirect, url_for
from modules.document_reader import read_pdf, read_txt
from flask import jsonify, render_template_string
from modules.text_cleaner import clean_text
from modules.summarizer import summarize_text
from modules.chat_engine import initialize_user_memory, generate_answer
from modules.challenge_engine import generate_challenge_question, evaluate_user_answer
import os
import tempfile
from werkzeug.utils import secure_filename

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/chat', methods=['GET', 'POST'])
def chat_home():
    summary = ""
    answer = ""
    if request.method == 'POST':
        file = request.files['file']
        if not file or file.filename == "":
            return render_template('chat.html', summary="❌ No file uploaded.", answer="")

        filename = secure_filename(file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(temp_path)

        if filename.endswith('.pdf'):
            text = read_pdf(temp_path)
        elif filename.endswith('.txt'):
            text = read_txt(temp_path)
        else:
            return render_template('chat.html', summary="❌ Only .pdf or .txt files are supported.", answer="")

        try:
            os.remove(temp_path)
        except:
            pass

        clean = clean_text(text)
        summary = summarize_text(clean)
        session['context'] = clean
        session['user'] = session.get('user', 'guest')
        session['score'] = 0  # initialize score
        initialize_user_memory(session['user'])

        return render_template('chat.html', summary=summary, answer="")

    return render_template('chat.html', summary="", answer="")

@chat_bp.route('/ask', methods=['POST'])
def ask_question():
    q = request.form.get('question', '').strip()
    context = session.get('context', '')
    username = session.get('user', 'guest')

    if not context:
        return jsonify({'chat_html': '<div class="chat-bubble bot">❌ Please upload a document first.</div>'})

    answer = generate_answer(username, q, context)

    if 'history' not in session:
        session['history'] = []

    session['history'].append({
        "question": q,
        "answer": answer
    })
    session.modified = True

    rendered_html = render_template('chat_history.html', history=session['history'])
    return jsonify({'chat_html': rendered_html})



# ------------------- Challenge Mode ----------------------

@chat_bp.route('/challenge', methods=['GET'])
def challenge_me():
    context = session.get('context', '')
    if not context:
        return redirect(url_for('chat_bp.chat_home'))

    question = generate_challenge_question(context)
    session['challenge_question'] = question
    return render_template('challenge.html', question=question, feedback=None, score=session.get('score', 0))

@chat_bp.route('/submit_challenge', methods=['POST'])
def submit_challenge():
    user_answer = request.form.get('answer', '').strip()
    context = session.get('context', '')
    question = session.get('challenge_question', '')
    feedback = "Something went wrong."

    if not context or not question:
        return redirect(url_for('chat_bp.chat_home'))

    result = evaluate_user_answer(context, question, user_answer)
    correct = result['correct'].lower() == 'yes'
    reason = result['reason']

    if correct:
        session['score'] += 1

    feedback = f"{'✅ Correct!' if correct else '❌ Incorrect.'} Reason: {reason}"
    return render_template('challenge.html', question=question, feedback=feedback, score=session['score'])
