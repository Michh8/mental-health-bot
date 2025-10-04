# 🤖 Bot de Salud Mental con Gemini AI

Este proyecto implementa un **bot de Telegram** que integra **Google Gemini AI** con **LangChain** y varias herramientas personalizadas.  
El bot está enfocado en **bienestar emocional**, ofreciendo mensajes motivacionales, chequeo de estado de ánimo, clima y búsqueda de centros psicológicos/hospitales en El Salvador.

---

## 📌 Funcionalidades disponibles

- `/start` → Mensaje de bienvenida
- `/help` → Lista de comandos
- `/fecha` → Muestra la fecha y hora actual en El Salvador
- `/clima [ciudad]` → Consulta el clima actual de una ciudad
- `/motivacion` → Envía un mensaje motivacional generado con IA
- `/mood [estado]` → Analiza tu estado de ánimo y da un consejo breve
- `/centros [ciudad]` → Busca psicólogos y hospitales en una ciudad usando OpenStreetMap

Además, si escribes cualquier otro mensaje libremente, el bot responde con **Gemini AI**.

---

## ⚙️ Tecnologías usadas

- **Python 3.10+**
- [python-telegram-bot](https://docs.python-telegram-bot.org/)
- [LangChain](https://www.langchain.com/)
- [langchain-google-genai](https://pypi.org/project/langchain-google-genai/)
- [Google Gemini API](https://ai.google.dev/)
- [OpenWeather API](https://openweathermap.org/) → Clima
- [Overpass API](https://overpass-turbo.eu/) → Búsqueda de lugares (psicólogos/hospitales)
- [aiohttp](https://docs.aiohttp.org/) → Servidor para despliegue en la nube
- [dotenv](https://pypi.org/project/python-dotenv/) → Variables de entorno

---

## 🚀 Instalación local

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu_usuario/telegram-mental-health-bot.git
cd telegram-mental-health-bot
