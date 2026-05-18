import serial
import time
import os
from datetime import datetime

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(
    LOG_DIR,
    f"sensor_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
)

def parse_line(line: str):
    try:
        parts = line.split(",")

        temp = float(parts[0].split(":")[1])
        time_ms = int(parts[1].split(":")[1])
        minutes = float(parts[2].split(":")[1])

        return temp, time_ms, minutes
    except:
        return None

def main():
    print("🔌 Iniciando sensor PCM Logger...")

    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)

    print(f"📁 Salvando log em: {log_file}\n")

    temps = []

    with open(log_file, "w") as f:
        f.write("temp,time_ms,minutes,temp_simulada_10pct\n")

        while True:
            try:
                raw = ser.readline().decode("utf-8", errors="ignore").strip()

                if not raw:
                    continue

                parsed = parse_line(raw)

                if parsed:
                    temp, time_ms, minutes = parsed

                    # média simples
                    temps.append(temp)
                    if len(temps) > 50:
                        temps.pop(0)

                    avg_temp = sum(temps) / len(temps)

                    # simulação +10%
                    temp_simulada = temp * 1.10

                    # print no terminal
                    print(
                        f"[PCM LOG] "
                        f"T:{temp:.2f}°C | "
                        f"AVG:{avg_temp:.2f}°C | "
                        f"SIM:{temp_simulada:.2f}°C | "
                        f"TIME:{time_ms}"
                    )

                    # salva CSV
                    f.write(
                        f"{temp},{time_ms},{minutes},{temp_simulada}\n"
                    )
                    f.flush()

                else:
                    print(f"[RAW] {raw}")

            except KeyboardInterrupt:
                print("\n🛑 Encerrado")
                break

if __name__ == "__main__":
    main()