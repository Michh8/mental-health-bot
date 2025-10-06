import requests
import time

# ======================================
# CONFIGURACIÓN
# ======================================
CHECK_URL = "https://mental-health-bot-2-g9ke.onrender.com"   # tu endpoint principal
RENDER_DEPLOY_HOOK = "https://api.render.com/deploy/srv-d3cqmb6mcj7s73dr33pg?key=L-VjJV7IvSA"  # tu hook de Render
CHECK_INTERVAL = 300  # segundos entre verificaciones (300 = 5 minutos)

def is_down():
    try:
        response = requests.get(CHECK_URL, timeout=10)
        return response.status_code != 200
    except requests.RequestException:
        return True

def trigger_redeploy():
    try:
        r = requests.post(RENDER_DEPLOY_HOOK)
        if r.status_code == 200:
            print("✅ Redeploy ejecutado correctamente.")
        else:
            print(f"⚠️ Error al hacer redeploy: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Error enviando deploy hook: {e}")

if __name__ == "__main__":
    print("🚀 Monitor de servicio iniciado...")
    while True:
        if is_down():
            print("🔴 Servicio caído. Ejecutando redeploy...")
            trigger_redeploy()
        else:
            print("🟢 Servicio funcionando correctamente.")
        time.sleep(CHECK_INTERVAL)
