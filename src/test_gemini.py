

import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Clé API introuvable dans .env")

client = genai.Client(api_key=api_key)

questions = [
    "Quelles sont les conditions nécessaires pour s'inscrire au PFE et quelle est sa durée ?",
    "Quelles sont les parties obligatoires du rapport de PFE et dans quel ordre doivent-elles apparaître ?",
    "Comment se déroule la soutenance du PFE et quelle est la durée consacrée à chaque partie ?",
    "Quelles sont les principales obligations de l'étudiant pendant son stage en entreprise ?",
    "Quel est le montant mensuel de la bourse d'excellence accordée aux étudiants pendant leur PFE ?"
]

# Fichier pour sauvegarder les réponses
fichier = "resultats_llm_seul.txt"

with open(fichier, "w", encoding="utf-8") as f:
    f.write("RESULTATS DU TEST LLM SEUL\n")
    f.write("Aucune consultation des documents PDF.\n\n")

for i, question in enumerate(questions, start=1):

    print("\n" + "=" * 70)
    print(f"QUESTION {i}")
    print("=" * 70)
    print(question)

    for tentative in range(1, 3):
        try:
            print("\nGemini est en train de réfléchir...", flush=True)

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=question
            )

            reponse = response.text or "Aucune réponse textuelle reçue."

            print("\nRéponse du LLM seul :")
            print(reponse)

            # Sauvegarder immédiatement la réponse
            with open(fichier, "a", encoding="utf-8") as f:
                f.write(f"\nQUESTION {i}\n{question}\n")
                f.write(f"\nREPONSE :\n{reponse}\n")
                f.write("\n" + "-" * 70 + "\n")

            break

        except Exception as e:
            print(f"\nErreur lors de la tentative {tentative} : {e}")

            if tentative < 2:
                print("Nouvelle tentative dans 10 secondes...")
                time.sleep(10)
            else:
                print("Question non traitée. Nous pourrons la réessayer plus tard.")

                with open(fichier, "a", encoding="utf-8") as f:
                    f.write(f"\nQUESTION {i}\n{question}\n")
                    f.write(f"ERREUR : {e}\n")
                    f.write("\n" + "-" * 70 + "\n")

print("\nTest terminé !")
print(f"Résultats enregistrés dans : {fichier}")
