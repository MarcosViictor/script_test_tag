import time
import requests
import sys

# ============================
# CONFIGURAÇÕES DA API
# ============================
url = "http://sitiobarreiras.app.br:55432/api/gate/check"

headers = {
    "Authorization": "sbs",
    "Content-Type": "application/json"
}

print("=== MODO SIMULAÇÃO (SEM LEITOR USB) ===")
print("O sistema vai pedir para você digitar um código manualmente.")
print("Para sair, pressione Ctrl+C\n")

while True:
    try:
        # EM VEZ DE LER O USB, PEDE PARA DIGITAR
        id_string = input("📝 Digite o código da TAG e dê Enter: ")

        # Se digitou algo vazio, ignora
        if not id_string.strip():
            continue

        print(f"🔹 Processando TAG simulada: {id_string}")

        # 2️⃣ Envia para API
        payload = { "code": id_string }

        print("📤 Enviando para API...")

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=5
            )

            print(f"Status: {response.status_code}")
            try:
                print("Resposta JSON:", response.json())
            except:
                print("Resposta Texto:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão com a API: {e}")

        print("-" * 30)

    except KeyboardInterrupt:
        print("\nEncerrando simulação...")
        sys.exit()
    except Exception as e:
        print(f"Erro: {e}")