import hid
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

# ============================
# CONFIGURAÇÕES DO DISPOSITIVO
# ============================
VID = 0x1A86
PID = 0xE010

def connect_device():
    """Tenta conectar ao dispositivo HID repetidamente."""
    while True:
        try:
            print(f"Tentando abrir dispositivo (VID: {VID:04X}, PID: {PID:04X})...")
            h = hid.device()
            h.open(VID, PID)
            h.set_nonblocking(1)
            print("✅ Dispositivo conectado com sucesso!")
            print("📡 Aproxime uma TAG RFID...\n")
            return h
        except IOError as e:
            print(f"⚠️ Erro ao abrir: {e}")
            print("Verifique se o dispositivo está plugado ou se você tem permissão (sudo).")
            time.sleep(2)
        except Exception as e:
            print(f"Erro inesperado: {e}")
            time.sleep(2)

# Inicia conexão
device = connect_device()

while True:
    try:
        # Tenta ler 64 bytes
        data = device.read(64)
        
        if data:
            # Converte bytes para lista HEX
            hex_list = [f"{b:02X}" for b in data]

            # 🔹 Remove zeros do final (Padding)
            while hex_list and hex_list[-1] == "00":
                hex_list.pop()

            if not hex_list:
                continue

            # ========================================================
            # ATENÇÃO: Ajuste de Offset Linux vs Windows
            # No Linux, às vezes o primeiro byte é o Report ID.
            # Se o código ficar estranho, tente mudar de [18:] para [19:] ou [17:]
            # ========================================================
            
            # 🔹 Lógica original de corte
            if len(hex_list) > 20:
                # Mantive o original, mas monitore o print "Recebido"
                id_real = hex_list[18:] 
            else:
                id_real = hex_list

            # 🔥 TAG sem espaços
            id_string = "".join(id_real)

            # 🔹 Remove os últimos 4 dígitos da TAG
            if len(id_string) > 4:
                id_string = id_string[:-4]

            print(f"🔹 Recebido Bruto: {hex_list}") # Debug extra para ajudar no ajuste
            print(f"🏷️  Processado: {id_string}")

            # 2️⃣ Envia para API
            payload = { "code": id_string }

            print("📤 Enviando para API...")

            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=5 # Timeout para não travar se a net cair
                )

                print(f"Status: {response.status_code}")
                try:
                    print("Resposta:", response.json())
                except:
                    print("Resposta texto:", response.text)

            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão com a API: {e}")

            print("-" * 30)

        time.sleep(0.05)

    except IOError:
        print("❌ Dispositivo desconectado ou erro de leitura. Tentando reconectar...")
        device.close()
        time.sleep(1)
        device = connect_device()
    except KeyboardInterrupt:
        print("\nEncerrando...")
        device.close()
        sys.exit()