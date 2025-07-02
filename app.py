import os
import json
from flask import Flask, render_template, request, jsonify 
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)


try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"Erreur lors de l'initialisation du client OpenAI : {e}")
    client = None


ANALYZE_PROMPT = """
Tu es un assistant d'analyse de communication pour freelances. Analyse le message suivant et extrais les informations clés en respectant STRICTEMENT le format JSON demandé.

Message à analyser :
\"\"\"
{user_message}
\"\"\"

Identifie les éléments suivants et retourne-les dans un objet JSON avec les clés suivantes :
- "intent": Quelle est l'intention principale ? Choisis une seule valeur parmi : "demande_devis", "question_simple", "suivi_projet", "negociation", "plainte", "prise_de_contact", "remerciement", "autre".
- "sentiment": Le ton général du message. Choisis une seule valeur parmi : "positif", "neutre", "negatif", "urgent".
- "summary": Un résumé très court de la demande en une phrase (en français).
"""

GENERATE_REPLY_PROMPT = """
Tu es un assistant de communication expert pour les freelances, nommé Stratext. Ta mission est de rédiger des brouillons de réponses claires, professionnelles et efficaces.

Contexte de la demande :
- Intention détectée : {intent}
- Résumé de la demande initiale : {summary}
- Informations complémentaires fournies par le freelance : {details}

Instructions pour la réponse :
- Rédige un message adapté au canal "{channel}".
- Adopte un ton "{tone}".
- Le message doit être concis, aller droit au but tout en restant courtois.
- Termine toujours par une question ouverte ou une proposition d'action claire pour encourager une réponse.
- Ne signe pas le message. Le freelance ajoutera sa propre signature.

Rédige maintenant le message de réponse.
"""




@app.route('/')
def index():
    """ Affiche la page principale. """
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_message():
    """ Reçoit le message de l'utilisateur, l'analyse via GPT et renvoie l'analyse. """
    if not client:
        return jsonify({"error": "Client OpenAI non configuré. Vérifiez votre clé API."}), 500

    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Le message ne peut pas être vide."}), 400

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini", 
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ANALYZE_PROMPT.format(user_message=user_message)}
            ]
        )
        analysis = json.loads(completion.choices[0].message.content)
        return jsonify(analysis)

    except Exception as e:
        print(f"Erreur API OpenAI (analyse): {e}")
        return jsonify({"error": "Une erreur est survenue lors de l'analyse."}), 500


@app.route('/generate_reply', methods=['POST'])
def generate_reply():
    """ Reçoit l'analyse et les détails, et génère la réponse finale. """
    if not client:
        return jsonify({"error": "Client OpenAI non configuré."}), 500

    data = request.get_json()
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o", # On utilise le meilleur modèle pour la rédaction
            messages=[
                {"role": "system", "content": GENERATE_REPLY_PROMPT.format(
                    intent=data.get('intent'),
                    summary=data.get('summary'),
                    details=data.get('details'),
                    channel=data.get('channel'),
                    tone=data.get('tone')
                )}
            ]
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Erreur API OpenAI (génération): {e}")
        return jsonify({"error": "Une erreur est survenue lors de la génération de la réponse."}), 500

# Pour lancer l'application
if __name__ == '__main__':
    app.run(debug=True)