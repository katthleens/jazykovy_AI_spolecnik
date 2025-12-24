import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

LANGUAGES = {
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "pl": "Polish",
    "tr": "Turkish",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}

def ask_ai(user_message: str,
           mode: str = "dialog",
           language: str = "en",
           history=None) -> str:
    """
    Отправляет запрос к модели и возвращает ответ.
    history — список сообщений [{role: "user"/"assistant", content: "..."}],
    чтобы ИИ помнил контекст.
    """
    lang_name = LANGUAGES.get(language, "English")

    if mode == "dialog":
        system_prompt = (
            f"You are a friendly {lang_name} teacher for a Czech-speaking student. "
            "The student is practicing the target language. "
            "Your answer should follow this format:\n"
            "1) First, answer in the target language (2–5 short sentences).\n"
            "2) Then, in Czech, briefly explain mistakes and give 1–2 tips.\n"
            "Use simple vocabulary, A2–B1 level."
        )
    elif mode == "explain":
        system_prompt = (
            f"You are a {lang_name} teacher for a Czech-speaking student. "
            "Explain the requested words or grammar in Czech with examples. "
            "Give several short example sentences in the target language with Czech translation."
        )
    else:
        system_prompt = "You are a helpful assistant."

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for m in history:
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant") and isinstance(content, str):
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    message = data.get("message", "").strip()
    mode = data.get("mode", "dialog")
    language = data.get("language", "en")

    if not message:
        return jsonify({"error": "Prázdný dotaz"}), 400

    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({"error": "Proměnná OPENAI_API_KEY nebyla nalezena v prostředí"}), 500

    try:
        answer = ask_ai(message, mode, language)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
