# run.py
from flask import Flask
from flask_login import LoginManager
from authValid.routes import auth_valid

app = Flask(__name__)

# Load configuration from the config.py file
app.config.from_pyfile('config.py', silent=True)

login_manager = LoginManager(app)
login_manager.login_view = 'auth_valid.login'  # Use the blueprint name in login_view

# Register Blueprints
app.register_blueprint(auth_valid, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)
