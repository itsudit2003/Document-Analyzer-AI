from flask import Blueprint, render_template, request, redirect, session, url_for
from db.database import register_user, validate_user
from modules.chat_engine import initialize_user_memory

# Registering the blueprint with name 'auth'
auth_bp = Blueprint('auth', __name__)

# ---------- LOGIN ----------
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        passwd = request.form['password']
        if validate_user(uname, passwd):
            session['user'] = uname
            initialize_user_memory(uname)
            return redirect(url_for('chat_bp.chat_home'))  # correct endpoint
        else:
            return render_template('login.html', error="❌ Invalid credentials.")
    return render_template('login.html')

# ---------- REGISTER PAGE ----------
@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# ---------- REGISTER SUBMISSION ----------
@auth_bp.route('/register', methods=['POST'])
def register():
    uname = request.form['username']
    passwd = request.form['password']
    success = register_user(uname, passwd)
    
    if success:
        session['user'] = uname
        initialize_user_memory(uname)
        return redirect(url_for('chat_bp.chat_home'))  # ✅ Go to chat directly on success
    else:
        # ❌ Don't render missing template — show error on login page instead
        return render_template('login.html', error="Username already taken. Please try another.")
