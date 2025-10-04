# 🤖 Telegram Bot de Salud Mental

Este proyecto implementa un **bot de Telegram** con integración a **LangChain** y Gemini.  
El bot ofrece **apoyo emocional básico**, búsqueda de **centros psicológicos/hospitales** usando OpenStreetMap (Overpass API), y funcionalidades adicionales como clima, motivación y chequeo de estado de ánimo.

---

## 📦 Características

- ✅ Integración con **LangChain + Gemini** para respuestas inteligentes.
- ✅ Comandos de Telegram personalizados.
- ✅ Búsqueda de psicólogos y hospitales en **OpenStreetMap (Overpass API)**.
- ✅ Generación de mensajes motivacionales y análisis de ánimo.
- ✅ Información meteorológica con **OpenWeatherMap**.
- ✅ Arquitectura modular con carpetas:
  - `bot.py` → Punto de entrada principal.
  - `config.py` → Configuración centralizada del bot.
  - `handlers/commands.py` → Manejo de comandos de Telegram.
  - `handlers/messages.py` → Manejo de mensajes generales.
  - `utils/tools.py` → Herramientas externas (OSM, clima, motivación, ánimo).
  - `utils/gemini_client.py` → Cliente para interactuar con Gemini AI.
  - `.env` → Configuración de variables de entorno.
  - `dockerfile` → Configuración para contenedor Docker.
  - `runtime.txt` → Especifica la versión de Python para deployment.

---

## 📂 Estructura del Proyecto

```
TELEGRAM_BOT_PROYECTO/
├── .godo/
├── handlers/
│   ├── __init__.py
│   ├── commands.py
│   └── messages.py
├── utils/
│   ├── __init__.py
│   ├── gemini_client.py
│   └── tools.py
├── bot.py
├── bot_env
├── config.py
├── dockerfile
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── runtime.txt
```

---

## ⚙️ Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
   ```

2. **Crea y activa un entorno virtual:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno en el archivo `.env`:**

   ```ini
   TELEGRAM_TOKEN=tu_token_de_telegram
   GEMINI_API_KEY=tu_api_key_de_google
   WEATHER_API_KEY=tu_api_key_de_openweathermap
   ```

---

## ▶️ Ejecución

Ejecuta el bot con:

```bash
python bot.py
```

Si está en Render o Railway, el servidor web ya está configurado en `bot.py` para mantenerse activo.

---

## 💬 Uso del Bot

### 🟢 Comandos disponibles

- `/start` → Mensaje de bienvenida.
- `/help` → Muestra la lista de funcionalidades.
- `/fecha` → Devuelve la fecha y hora actual (zona horaria de El Salvador).
- `/clima [ciudad]` → Información meteorológica de una ciudad.
- `/motivacion` → Mensaje motivacional y consejo breve.
- `/mood [estado]` → Analiza tu estado de ánimo y da un consejo práctico.
- `/centros [ciudad]` → Busca psicólogos y hospitales cercanos en la ciudad indicada.

### ✨ Chat libre con Gemini

Puedes enviar cualquier mensaje y el bot responderá usando Gemini (Google Generative AI).

---

## 🔗 Demo

Puedes probar el bot aquí:

👉 [@mental_health_guy_bot](https://t.me/mental_health_guy_bot)

---

## 📘 Documentación del Código

### `bot.py`
Punto de entrada del bot.
- Inicializa la aplicación de Telegram.
- Configura el modelo Gemini.
- Ejecuta el polling y servidor web (para Render/Railway).

### `config.py`
Configuración centralizada del proyecto.
- Carga variables de entorno.
- Define constantes globales.

### `handlers/commands.py`
Define los comandos principales:
- `/start`, `/help`, `/fecha`, `/clima`, `/motivacion`, `/mood`, `/centros`.

### `handlers/messages.py`
Maneja los mensajes generales del usuario que no son comandos.

### `utils/gemini_client.py`
Cliente personalizado para interactuar con la API de Gemini.

### `utils/tools.py`
Contiene las herramientas externas:
- **`psych_tool`** → Consulta OpenStreetMap (Overpass API) para buscar psicólogos y hospitales.
- **`motivation_tool`** → Genera mensajes motivacionales con Gemini.
- **`mood_tool`** → Analiza el estado de ánimo con Gemini.
- **`weather_tool`** → Obtiene información meteorológica desde OpenWeatherMap.

### `.env`
Variables de entorno necesarias:

```
TELEGRAM_TOKEN
GEMINI_API_KEY
WEATHER_API_KEY
```

---

## 🛠️ Tecnologías

- Python
- LangChain + Gemini
- python-telegram-bot
- OpenStreetMap (Overpass API)
- OpenWeatherMap API

---

## 👤 Autor

Proyecto desarrollado por **Michelle Flamenco**  
📧 Contacto: michelleflamenko@yahoo.com  
🐙 GitHub: [@Michh8](https://github.com/Michh8)