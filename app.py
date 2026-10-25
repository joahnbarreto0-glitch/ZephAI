
import os
import logging

import gradio as gr
from groq import Groq


# =====================================================
# ZEPHAI - CONFIGURACION
# =====================================================

APP_NAME = "ZephAI"
MODEL = "openai/gpt-oss-20b"
MAX_HISTORY_MESSAGES = 12
MAX_COMPLETION_TOKENS = 1200

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("zephai")


SYSTEM_PROMPT = """
Eres ZephAI, una inteligencia artificial creada por Joahn.

Tu objetivo es ayudar de forma clara, natural, precisa y util.

REGLAS:
- Responde en el idioma del usuario.
- Explica paso a paso cuando sea necesario.
- Usa Markdown para organizar las respuestas.
- Ayuda con programacion, estudios, creatividad y tecnologia.
- No inventes datos cuando no conozcas la respuesta.
- No afirmes haber realizado acciones que no has realizado.
- No reveles claves API ni informacion secreta.
- Tu nombre es ZephAI y eres un proyecto independiente.
- No afirmes ser ChatGPT ni otra inteligencia artificial.
"""


# =====================================================
# PREPARAR EL HISTORIAL
# =====================================================

def texto_mensaje(contenido):
    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        partes = []

        for parte in contenido:
            if isinstance(parte, str):
                partes.append(parte)

            elif isinstance(parte, dict):
                texto = parte.get("text")

                if isinstance(texto, str):
                    partes.append(texto)

        return "\n".join(partes)

    return ""


def construir_mensajes(mensaje, historial):
    mensajes = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    for elemento in (historial or [])[-MAX_HISTORY_MESSAGES:]:

        if not isinstance(elemento, dict):
            continue

        rol = elemento.get("role")
        contenido = texto_mensaje(
            elemento.get("content", "")
        )

        if rol in ("user", "assistant") and contenido.strip():
            mensajes.append({
                "role": rol,
                "content": contenido
            })

    mensajes.append({
        "role": "user",
        "content": mensaje
    })

    return mensajes


# =====================================================
# MOTOR DE RESPUESTAS GROQ
# =====================================================

def responder(mensaje, historial):
    if not isinstance(mensaje, str) or not mensaje.strip():
        yield "Escribe un mensaje para comenzar."
        return

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        yield (
            "Falta configurar GROQ_API_KEY en las variables "
            "de entorno de Render."
        )
        return

    try:
        cliente = Groq(api_key=api_key)

        mensajes = construir_mensajes(
            mensaje.strip(),
            historial
        )

        flujo = cliente.chat.completions.create(
            model=MODEL,
            messages=mensajes,
            max_completion_tokens=MAX_COMPLETION_TOKENS,
            stream=True
        )

        respuesta = ""

        for fragmento in flujo:
            if not fragmento.choices:
                continue

            contenido = fragmento.choices[0].delta.content

            if isinstance(contenido, str) and contenido:
                respuesta += contenido
                yield respuesta

        if not respuesta:
            yield "No recibí una respuesta. Inténtalo otra vez."

    except Exception as error:
        # Registrar el tipo de error, nunca la clave API
        logger.error(
            "Error Groq: %s",
            type(error).__name__
        )

        yield (
            "No pude generar la respuesta. Inténtalo de nuevo. "
            "Si el problema continúa, revisa los registros de "
            "Render y el estado de tu servicio de Groq."
        )


# =====================================================
# DISENO VISUAL
# =====================================================

CSS_ZEPHAI = """
:root {
    color-scheme: dark;
}

html,
body {
    background: #212121 !important;
    color: #ececec !important;
}

.gradio-container {
    background: #212121 !important;
    color: #ececec !important;
    max-width: 100% !important;
    min-height: 100vh !important;
    padding: 10px 12px !important;
}

.main {
    max-width: 900px !important;
    margin: 0 auto !important;
}

/* Titulo */

h1 {
    color: #f5f5f5 !important;
    text-align: center !important;
    font-size: 30px !important;
    font-weight: 750 !important;
    letter-spacing: -1px !important;
}

h1::before {
    content: "✦ ";
    color: #b4a0ff;
}

/* Descripcion */

.prose,
p {
    color: #b8b8b8;
}

/* Conversacion */

#zephai-chatbot {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

#zephai-chatbot .message {
    border-radius: 18px !important;
    padding: 12px 16px !important;
    line-height: 1.65 !important;
    font-size: 15px !important;
}

/* Mensajes del usuario */

#zephai-chatbot .message.user {
    background: #303030 !important;
    border: 1px solid #414141 !important;
    color: #f5f5f5 !important;
}

/* Respuestas de ZephAI */

#zephai-chatbot .message.bot {
    background: transparent !important;
    color: #ececec !important;
}

/* Bloques de codigo */

#zephai-chatbot pre {
    background: #171717 !important;
    border: 1px solid #404040 !important;
    border-radius: 12px !important;
    overflow-x: auto !important;
}

#zephai-chatbot code {
    border-radius: 5px;
}

/* Entrada de texto */

#zephai-input {
    background: #303030 !important;
    border: 1px solid #454545 !important;
    border-radius: 25px !important;
    padding: 7px 12px !important;
    box-shadow: 0 3px 14px rgba(0, 0, 0, 0.12) !important;
}

#zephai-input:focus-within {
    border-color: #777777 !important;
}

#zephai-input textarea {
    background: transparent !important;
    color: #f5f5f5 !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 15px !important;
}

#zephai-input textarea::placeholder {
    color: #a6a6a6 !important;
}

/* Botones */

button {
    border-radius: 18px !important;
    transition: background 0.15s ease !important;
}

button.primary {
    background: #f0f0f0 !important;
    color: #202020 !important;
    border: none !important;
    font-weight: 650 !important;
}

button.primary:hover {
    background: #d7d7d7 !important;
}

button.secondary {
    background: #303030 !important;
    color: #eeeeee !important;
    border: 1px solid #454545 !important;
}

/* Sugerencias */

.examples,
.example {
    border-color: #454545 !important;
    border-radius: 14px !important;
}

.example {
    background: #292929 !important;
    color: #e4e4e4 !important;
}

.example:hover {
    background: #363636 !important;
}

/* Tablas */

#zephai-chatbot th,
#zephai-chatbot td {
    border-color: #454545 !important;
    padding: 8px !important;
}

/* Scrollbar */

* {
    scrollbar-color: #555555 #212121;
    scrollbar-width: thin;
}

/* Ocultar creditos */

footer,
.built-with {
    display: none !important;
}

/* Adaptacion a telefonos */

@media (max-width: 600px) {
    .gradio-container {
        padding: 6px 7px !important;
    }

    h1 {
        font-size: 27px !important;
    }

    #zephai-chatbot .message {
        padding: 10px 12px !important;
        font-size: 14px !important;
    }

    #zephai-input {
        border-radius: 22px !important;
        padding: 5px 8px !important;
    }
}
"""


# =====================================================
# INTERFAZ PRINCIPAL
# =====================================================

app = gr.ChatInterface(
    fn=responder,

    chatbot=gr.Chatbot(
        elem_id="zephai-chatbot",
        height=600,
        layout="bubble",
        buttons=["copy", "copy_all"],
        render_markdown=True,
        autoscroll=True,
        placeholder=(
            "<strong>¿Que hacemos hoy?</strong><br>"
            "Pregunta, aprende, programa o crea algo nuevo."
        )
    ),

    textbox=gr.Textbox(
        elem_id="zephai-input",
        placeholder="Escribe un mensaje a ZephAI...",
        container=False,
        lines=1,
        max_lines=6,
        scale=7
    ),

    title=APP_NAME,
    description="Tu inteligencia artificial personal.",

    examples=[
        "Explicame un tema dificil con ejemplos.",
        "Ayudame a programar en Python.",
        "Dame ideas para un proyecto creativo."
    ],

    run_examples_on_click=False,

    css=CSS_ZEPHAI,
    analytics_enabled=False,
    autofocus=False,
    fill_height=True,
    save_history=True,
    submit_btn=True,
    stop_btn=True,
    flagging_mode="never"
)


# =====================================================
# ARRANQUE EN RENDER
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))

    app.launch(
        server_name="0.0.0.0",
        server_port=port
    )
