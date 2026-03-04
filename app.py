import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, session, redirect, url_for
from utils import nettoyer_email
from gemini import classifier_email, generer_reponse
from lecteur_mail import recuperer_emails_nouveaux
from database import db, Email

app = Flask(__name__)
app.secret_key = "revival2024"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/projet_email"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

UTILISATEURS = {
    "admin": "1234"
}

def envoyer_email(destinataire, sujet, corps):
    try:
        msg = MIMEMultipart()
        msg["From"] = "testentreprises1@gmail.com"
        msg["To"] = destinataire
        msg["Subject"] = "Re: " + sujet
        msg.attach(MIMEText(corps, "plain"))
        serveur = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        serveur.login("testentreprises1@gmail.com", "aqdf mhid gjrc aqzm")
        serveur.sendmail("testentreprises1@gmail.com", destinataire, msg.as_string())
        serveur.quit()
        return True
    except Exception as e:
        print(f"Erreur envoi: {e}")
        return False

@app.route("/", methods=["GET", "POST"])
def accueil():
    erreur = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in UTILISATEURS and UTILISATEURS[username] == password:
            session["connecte"] = True
            session["username"] = username
            return redirect(url_for("index"))
        else:
            erreur = "Identifiant ou mot de passe incorrect."
    return render_template("accueil.html", erreur=erreur)

@app.route("/emails", methods=["GET", "POST"])
def index():
    if not session.get("connecte"):
        return redirect(url_for("accueil"))

    resultat = None
    onglet_actif = "emails"
    message = session.pop("message", None)

    # Récupérer nouveaux emails IMAP et les sauvegarder en base
    emails_bruts = recuperer_emails_nouveaux()
    for e in emails_bruts:
        try:
            contenu_propre = nettoyer_email(e["contenu"])
            categorie = classifier_email(contenu_propre)
        except:
            categorie = "AUTRE"

        # Sauvegarder uniquement si pas déjà en base
        existant = Email.query.filter_by(expediteur=e["expediteur"], sujet=e["sujet"]).first()
        if not existant:
            nouvel_email = Email(
                expediteur=e["expediteur"],
                sujet=e["sujet"],
                contenu=e["contenu"],
                categorie=categorie,
                reponse="",
                statut="non_traite"
            )
            db.session.add(nouvel_email)
            db.session.commit()
        time.sleep(1)

    # Afficher uniquement les emails non traités
    emails = Email.query.filter_by(statut="non_traite").order_by(Email.date_traitement.desc()).all()

    if request.method == "POST":
        email_recu = request.form["email"]
        onglet_actif = request.form.get("onglet", "emails")
        email_id = request.form.get("email_id")
        expediteur = request.form.get("expediteur", "Manuel")
        sujet = request.form.get("sujet", "Analyse manuelle")

        email_propre = nettoyer_email(email_recu)
        categorie = classifier_email(email_propre)
        reponse = generer_reponse(email_propre, categorie)

        # Si analyse manuelle sauvegarder en base
        if not email_id:
            existant = Email.query.filter_by(expediteur=expediteur, sujet=sujet).first()
            if not existant:
                nouvel = Email(
                    expediteur=expediteur,
                    sujet=sujet,
                    contenu=email_recu,
                    categorie=categorie,
                    reponse=reponse,
                    statut="non_traite"
                )
                db.session.add(nouvel)
                db.session.commit()
                email_id = nouvel.id

        resultat = {
            "email_original": email_recu,
            "categorie": categorie,
            "reponse_suggeree": reponse,
            "expediteur": expediteur,
            "sujet": sujet,
            "email_id": email_id
        }

    emails_traites = Email.query.order_by(Email.date_traitement.desc()).all()
    return render_template("index.html", resultat=resultat, emails=emails, onglet_actif=onglet_actif, emails_traites=emails_traites, message=message)

@app.route("/marquer_lu/<int:email_id>")
def marquer_lu(email_id):
    if not session.get("connecte"):
        return redirect(url_for("accueil"))
    email = Email.query.get(email_id)
    if email:
        email.statut = "lu"
        db.session.commit()
    session["message"] = "✅ Email marqué comme lu."
    return redirect(url_for("index"))

@app.route("/envoyer", methods=["POST"])
def envoyer():
    if not session.get("connecte"):
        return redirect(url_for("accueil"))

    destinataire = request.form.get("destinataire")
    sujet = request.form.get("sujet")
    corps = request.form.get("corps")
    email_id = request.form.get("email_id")

    succes = envoyer_email(destinataire, sujet, corps)

    if succes:
        if email_id:
            email = Email.query.get(int(email_id))
            if email:
                email.statut = "repondu"
                email.reponse = corps
                db.session.commit()
        session["message"] = "✅ Email envoyé avec succès !"
    else:
        session["message"] = "❌ Erreur lors de l'envoi."

    return redirect(url_for("index"))

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("accueil"))

if __name__ == "__main__":
    app.run(debug=True)