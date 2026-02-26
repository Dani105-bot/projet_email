import imaplib
import email
from email.header import decode_header

ADRESSE_MAIL = "testentreprises1@gmail.com"
MOT_DE_PASSE = ""

def recuperer_emails(nombre=5):
    connexion = imaplib.IMAP4_SSL("imap.gmail.com")
    connexion.login(ADRESSE_MAIL, MOT_DE_PASSE)
    connexion.select("inbox")

    _, messages = connexion.search(None, "ALL")
    ids_emails = messages[0].split()
    derniers_ids = ids_emails[-nombre:]

    emails_recuperes = []

    for id_email in reversed(derniers_ids):
        _, data = connexion.fetch(id_email, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        expediteur = msg["From"]

        sujet, encoding = decode_header(msg["Subject"])[0]
        if isinstance(sujet, bytes):
            sujet = sujet.decode(encoding or "utf-8")

        contenu = ""
        if msg.is_multipart():
            for partie in msg.walk():
                type_contenu = partie.get_content_type()
                disposition = str(partie.get("Content-Disposition"))
                if type_contenu == "text/plain" and "attachment" not in disposition:
                    try:
                        contenu = partie.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
                    except:
                        pass
        else:
            try:
                contenu = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            except:
                contenu = str(msg.get_payload())

        if not contenu.strip():
            contenu = sujet

        emails_recuperes.append({
            "expediteur": expediteur,
            "sujet": sujet,
            "contenu": contenu
        })

    connexion.close()
    connexion.logout()

    return emails_recuperes

if __name__ == "__main__":
    emails = recuperer_emails(3)
    for e in emails:
        print(f"De : {e['expediteur']}")
        print(f"Sujet : {e['sujet']}")
        print(f"Contenu : {e['contenu'][:100]}...")
        print("---")
        
def recuperer_emails_nouveaux():
    try:
        with open("dernier_id.txt", "r") as f:
            dernier_id = int(f.read().strip())
    except:
        dernier_id = 0

    connexion = imaplib.IMAP4_SSL("imap.gmail.com")
    connexion.login(ADRESSE_MAIL, MOT_DE_PASSE)
    connexion.select("inbox")

    _, messages = connexion.search(None, "ALL")
    ids_emails = messages[0].split()

    nouveaux_ids = [i for i in ids_emails if int(i) > dernier_id]

    if not nouveaux_ids:
        connexion.close()
        connexion.logout()
        return []

    emails_recuperes = []

    for id_email in nouveaux_ids:
        _, data = connexion.fetch(id_email, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        expediteur = msg["From"]

        sujet, encoding = decode_header(msg["Subject"])[0]
        if isinstance(sujet, bytes):
            sujet = sujet.decode(encoding or "utf-8")

        contenu = ""
        if msg.is_multipart():
            for partie in msg.walk():
                type_contenu = partie.get_content_type()
                disposition = str(partie.get("Content-Disposition"))
                if type_contenu == "text/plain" and "attachment" not in disposition:
                    try:
                        contenu = partie.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
                    except:
                        pass
        else:
            try:
                contenu = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            except:
                contenu = str(msg.get_payload())

        if not contenu.strip():
            contenu = sujet

        emails_recuperes.append({
            "expediteur": expediteur,
            "sujet": sujet,
            "contenu": contenu
        })

    if nouveaux_ids:
        with open("dernier_id.txt", "w") as f:
            f.write(str(int(nouveaux_ids[-1])))

    connexion.close()
    connexion.logout()

    return emails_recuperes 