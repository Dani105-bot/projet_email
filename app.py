import time
from flask import Flask, render_template, request, session, redirect, url_for
from utils import nettoyer_email
from gemini import classifier_email, generer_reponse
from lecteur_mail import recuperer_emails_nouveaux
from database import db, Email

app = Flask(__name__)
app.secret_key = "revival2024"

# Configuration MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1470@localhost/projet_email"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

UTILISATEURS = {
    "admin": "1234"
}

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

    emails_bruts = recuperer_emails_nouveaux()
    emails = []
    for e in emails_bruts:
        try:
            contenu_propre = nettoyer_email(e["contenu"])
            categorie = classifier_email(contenu_propre)
            e["categorie"] = categorie
        except:
            e["categorie"] = "AUTRE"
        emails.append(e)
        time.sleep(1)

    if request.method == "POST":
        email_recu = request.form["email"]
        onglet_actif = request.form.get("onglet", "emails")
        email_propre = nettoyer_email(email_recu)
        categorie = classifier_email(email_propre)
        reponse = generer_reponse(email_propre, categorie)

        expediteur = request.form.get("expediteur", "Manuel")
        sujet = request.form.get("sujet", "Analyse manuelle")

        nouvel_email = Email(
            expediteur=expediteur,
            sujet=sujet,
            contenu=email_recu,
            categorie=categorie,
            reponse=reponse
        )
        db.session.add(nouvel_email)
        db.session.commit()

        resultat = {
            "email_original": email_recu,
            "categorie": categorie,
            "reponse_suggeree": reponse
        }

    return render_template("index.html", resultat=resultat, emails=emails, onglet_actif=onglet_actif)

@app.route("/historique")
def historique():
    if not session.get("connecte"):
        return redirect(url_for("accueil"))
    emails_traites = Email.query.order_by(Email.date_traitement.desc()).all()
    return render_template("historique.html", emails=emails_traites)

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("accueil"))

if __name__ == "__main__":
    app.run(debug=True)