# Usar Python 3.12
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements y proyecto
COPY requirements.txt .
COPY . .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Variables de entorno (opcional)
ENV TELEGRAM_TOKEN=tu_token
ENV GEMINI_API_KEY=tu_api_key

# Comando para iniciar el bot
CMD ["python", "bot.py"]
