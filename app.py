from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from sqlalchemy import desc, text
from sqlalchemy.dialects import mysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///craze.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/")
def home():
    return "<h1>It works!</h1>"

if __name__ == "__main__":
    app.run(debug=True)