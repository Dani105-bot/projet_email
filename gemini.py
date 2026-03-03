from groq import Groq

API_KEY = "TA_CLE_GROQ_ICI"
client = Groq(api_key=API_KEY)

def classifier_email(texte_email):
    prompt = "Classe cet email dans UNE SEULE categorie parmi : DEVIS, SUPPORT, RECLAMATION, INFORMATION, CANDIDATURE, AUTRE. Reponds uniquement avec le nom. Email : " + texte_email
    reponse = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return reponse.choices[0].message.content.strip()

def generer_reponse(texte_email, categorie):
    prompt = "Tu es un assistant de Revival Technologies. Redige une reponse professionnelle pour cet email de categorie " + categorie + ". Email : " + texte_email
    reponse = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return reponse.choices[0].message.content.strip()