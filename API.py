import json
from flask import Flask, jsonify, request
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="AIzaSyDLwwtwnky_btZCORbPTcbUkEnTjdnbpbQ")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

historico_conversas = {}

def inicializar_chatbot():
    # Histórico inicial do chatbot CliniBot
    return [
        {
            "enviado": 
                "A partir desse ponto você estará respondendo como se fosse o chatbot de um sistema de saúde.\n\n"+
                "Anote todo sintoma que o paciente falar e mantenha salvo em sua memória como informações de extrema importância.\n\n"+
                "Comece sempre o chat perguntando:\n\n"+
                "Nome, Telefone."+
                "O seu nome é CliniBot."
        },
        {
            "resposta": 
                "Olá! 👋 Meu nome é CliniBot, e estou aqui para te ajudar. 😄  \n\n"+
                "Para que eu possa te ajudar da melhor forma possível, poderia me dizer seu nome e telefone, por favor? \n"
        },
    ]

def formatar_historico_para_contexto(historico):
    contexto = []
    for mensagem in historico:
        if "enviado" in mensagem:
            contexto.append({"role": "user", "parts": [mensagem["enviado"]]})
        if "resposta" in mensagem:
            contexto.append({"role": "model", "parts": [mensagem["resposta"]]})
    return contexto

@app.route("/<int:id>", methods=["POST"])
def enviar_texto(id):
    data = request.get_json()
    texto = data.get("texto", "")

    if id not in historico_conversas:
        historico_conversas[id] = inicializar_chatbot()

    contexto = formatar_historico_para_contexto(historico_conversas[id])
    
    historico_conversas[id].append({"enviado": texto})

    chat_session = model.start_chat(history=contexto)

    response = chat_session.send_message(texto)

    historico_conversas[id].append({"resposta": response.text})

    return jsonify({
        "resposta": response.text,
        "historico": historico_conversas[id]
    })

@app.route("/finalizar/<int:id>", methods=["POST"])
def finalizar_conversa(id):
    
    if id not in historico_conversas:
        return jsonify({"erro": "Não há histórico para este ID."}), 400

    contexto = formatar_historico_para_contexto(historico_conversas[id])

    chat_session = model.start_chat(history=contexto)

    mensagem_final = (
        "A conversa com o paciente foi finalizada, me devolva em forma de JSON as seguintes informações conforme a estrutura: nome, telefone, sintomas(uma lista com os sintemas)"
    )

    response = chat_session.send_message(mensagem_final)

    resposta_string = response.text.replace("```json\n", "") \
                                    .replace("```", "") \
                                    .replace("\n", "") \
                                    .replace("'", "") \
                                    .strip()

    try:
        resposta_json = json.loads(resposta_string)
    except json.JSONDecodeError:
        return jsonify({"erro": "Resposta não está no formato JSON correto."}), 500
      
    return jsonify(resposta_json)

  

if __name__ == "__main__":
    app.run(port=8080, debug=True)
