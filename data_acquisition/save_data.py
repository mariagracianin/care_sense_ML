import serial
import csv
import keyboard
from datetime import datetime

PORT = "COM6"
BAUD = 115200
MAX_EVENTS = 50

ser = serial.Serial(PORT, BAUD, timeout=1)

print("Esperando Arduino LISTO...")

# esperar mensaje LISTO del Arduino
while True:
    line = ser.readline().decode(errors="ignore").strip()
    if line:
        print(line)
    if line == "LISTO":
        break

print("Arduino listo")

filename = f"sit_{datetime.now().strftime('%H%M%S')}.csv"
f = open(filename, "w", newline="")
writer = csv.writer(f)
writer.writerow(["event","aX","aY","aZ","gX","gY","gZ"])

events = 0

while events < MAX_EVENTS:

    print(f"\n👉 Presiona ESPACIO para capturar evento {events+1}")
    keyboard.wait("space")
    keyboard.release("space")  # evita doble disparo

    print("Trigger enviado")
    ser.write(b'T')

    # leer hasta fin de evento
    while True:
        line = ser.readline().decode(errors="ignore").strip()

        if not line:
            continue

        print(line)

        if line == "EVENT_START":
            continue

        if line == "EVENT_END":
            events += 1
            print(f"✅ Evento {events} completo")
            break

        if "," in line:
            writer.writerow([events+1] + line.split(","))

f.close()

print("\n✅ Guardados", MAX_EVENTS, "eventos")
print("Archivo creado:", filename)