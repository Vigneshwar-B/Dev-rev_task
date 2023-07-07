from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "vigneshwar"  # Set your secret key for session management

# Configure PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vigneshwar:OlmCvOoTmhP2IUruhWNgib9chYC1BsQQ@dpg-cijs4ltph6euh7hqi7g0-a.oregon-postgres.render.com/demo_35ax'
db = SQLAlchemy(app)

from routes import *

if __name__ == '__main__':
    app.run(host="0.0.0.0")
 
