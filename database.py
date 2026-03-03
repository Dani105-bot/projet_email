from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Email(db.Model):
    __tablename__ = "emails_traites"

    id = db.Column(db.Integer, primary_key=True)
    expediteur = db.Column(db.String(255), nullable=False)
    sujet = db.Column(db.String(255), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    categorie = db.Column(db.String(50), nullable=False)
    reponse = db.Column(db.Text, nullable=False)
    date_traitement = db.Column(db.DateTime, default=datetime.utcnow)