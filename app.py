
import os
import gradio as gr
from groq import Groq

MODEL = "openai/gpt-oss-20b"

def responder(mensaje, historial):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return "Falta configurar GROQ_API_KEY en el alojamiento."

    try:
        cliente = Groq(api_key=api_key)

        mensajes = [{
            "role": "system",
            "content": (
                "Eres ZephAI, una inteligencia artificial creada por Joahn. "
                "Responde en español, de forma clara, natural y útil."
            )
        }]

        for item in (historial or [])[-10:]:
            if isinstance(item, dict) and item.get("role") in ("user", "assistant"):
                mensajes.append({
                    "role": item["role"],
                    "content": str(item.get("content", ""))
                })

        mensajes.append({"role": "user", "content": mensaje})

        resultado = cliente.chat.completions.create(
            model=MODEL,
            messages=mensajes,
            max_completion_tokens=500
        )

        return resultado.choices[0].message.content or "No pude generar una respuesta."

    except Exception:
        return "No pude responder. Revisa la configuración del servicio."

app = gr.ChatInterface(
    fn=responder,
    title="ZephAI",
    description="Tu inteligencia artificial personal, creada por Joahn.",
    analytics_enabled=False
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
app.launch(server_name="0.0.0.0", server_port=port)
