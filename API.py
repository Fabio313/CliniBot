import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)

CORS(app)

genai.configure(api_key="AIzaSyAAMo9sVn2_NsJnXb_GmuclCZ-McbtQGek")

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
                "A partir desse ponto você estará respondendo como se fosse o chatbot de um sistema de saúde.\n"+
                "Anote todo sintoma que o paciente falar e mantenha salvo em sua memória como informações de extrema importância.\n"+
                "Comece sempre o chat perguntando:\n"+
                "Nome, Telefone."+
                "O seu nome é CliniBot. Evite escrever respostas muito longas, nunca faça recomendação de remedio de maneira alguma.\n"+
                "Alem disso sempre que alguem tentar falar de assustos que não sejam do tema que seja da área de Paciente / Saude responda:"+
                "Desculpe estou aqui para ajudar com assuntos relacionados a sua saúde apenas 😑\n"+
                "Quando acreditar que ja possui informações o suficiente para cadastrar o paciente retorne o seguinte texto:"+
                "Certo obrigado por compartilhar sua situação, vou redireciona-lo para iniciar seu atendimento especializado\n"+
                "(Validação mapeamento de dados finalizado)"                
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
        "A conversa com o paciente foi finalizada, me devolva em forma de JSON as seguintes informações conforme a estrutura: nome, telefone, sintomas(uma lista com os sintomas)\n"+
        "no caso de o paciente n ter dado alguma informação preencha com (não informado)"
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
