from flask import Flask
from routes.auth import auth_bp
from routes.chat import chat_bp
from db.database import create_user_table

app = Flask(__name__)
app.secret_key = 'secret'
create_user_table()

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

if __name__ == "__main__":
    app.run(debug=True)
