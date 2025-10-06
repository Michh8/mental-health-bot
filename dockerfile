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



# Ejecuta el bot y el monitor al mismo tiempo
CMD ["sh", "-c", "python bot/main.py & python auto_redeploy.py"]
