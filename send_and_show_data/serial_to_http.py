import serial
import requests
import time
import re

PORT = "COM5"
BAUD = 115200
ENDPOINT = "http://127.0.0.1:5000/state"

# Ejemplo: "Prediction: lie_down  score=0.9994"
pred_re = re.compile(r"^Prediction:\s*([A-Za-z_]+)\s*score=([0-9]*\.?[0-9]+)")

def parse_line(line: str):
    m = pred_re.search(line.strip())
    if not m:
        return None
    state = m.group(1)
    score = float(m.group(2))
    return state, score

def main():
    # opcional: check rápido del server
    try:
        r = requests.get("http://127.0.0.1:5000/last", timeout=2)
        print("Servidor OK ->", r.status_code, flush=True)
    except Exception as e:
        print("❌ Flask no responde. Lánzalo primero. Error:", e, flush=True)
        return

    print(f"Abriendo puerto {PORT} a {BAUD}...", flush=True)
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(1.5)

    print("Escuchando Serial...\n", flush=True)

    while True:
        raw = ser.readline().decode(errors="ignore").strip()
        if not raw:
            continue

        # 👀 ves lo que llega
        print("RAW <-", raw, flush=True)

        parsed = parse_line(raw)
        if not parsed:
            # si quieres ver qué líneas no matchean:
            # print("NO MATCH", flush=True)
            continue

        state, score = parsed

        # ✅ imprimir ANTES del POST
        print(f"PARSED -> state={state}, score={score:.4f}", flush=True)

        payload = {"state": state, "score": score}

        try:
            resp = requests.post(ENDPOINT, json=payload, timeout=2)
            print("HTTP ->", resp.status_code, resp.text, "\n", flush=True)
        except Exception as e:
            print("HTTP error:", e, "\n", flush=True)

if __name__ == "__main__":
    main()