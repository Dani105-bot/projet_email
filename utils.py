import re

def nettoyer_email(texte_brut):
    # Supprimer les balises HTML
    texte = re.sub(r'<.*?>', '', texte_brut)
    
    # Supprimer les espaces multiples
    texte = re.sub(r'\s+', ' ', texte)
    
    # Supprimer les espaces en début et fin
    texte = texte.strip()
    
    return texte

# Test pour vérifier que ça marche
if __name__ == "__main__":
 email_test = "  Bonjour,   je voudrais un devis   pour votre service.  "
 email_propre = nettoyer_email(email_test)
 print(f"Résultat : {email_propre}")