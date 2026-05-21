import serial
import time
import os
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(
    LOG_DIR,
    f"sensor_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
)

# ─────────────────────────────────────────────
# CALIBRAÇÃO SENSOR IR
# ─────────────────────────────────────────────

# Sensor IR mede ~5°C abaixo
TEMP_OFFSET = 5.0

# ganho térmico experimental
TEMP_GAIN = 1.10

# suavização
MEDIA_MOVEL = 15

# ─────────────────────────────────────────────

def parse_line(line: str):

    try:
        parts = line.split(",")

        temp = float(parts[0].split(":")[1])
        time_ms = int(parts[1].split(":")[1])
        minutes = float(parts[2].split(":")[1])

        return temp, time_ms, minutes

    except:
        return None


def calibrar_temperatura(temp: float) -> float:
    """
    Corrige erro típico do sensor IR.
    """

    return (
        (temp + TEMP_OFFSET)
        * TEMP_GAIN
    )


def main():

    print("🔌 Iniciando sensor PCM Logger...")

    ser = serial.Serial(
        PORT,
        BAUDRATE,
        timeout=1
    )

    time.sleep(2)

    print(f"📁 Salvando log em: {log_file}\n")

    temps_reais = []
    temps_corrigidas = []

    with open(log_file, "w") as f:

        f.write(
            "temp,time_ms,minutes,temp_corrigida,temp_suavizada\n"
        )

        while True:

            try:

                raw = (
                    ser.readline()
                    .decode("utf-8", errors="ignore")
                    .strip()
                )

                if not raw:
                    continue

                parsed = parse_line(raw)

                if parsed:

                    temp, time_ms, minutes = parsed

                    # ─────────────────────────
                    # temperatura corrigida
                    # ─────────────────────────

                    temp_corrigida = calibrar_temperatura(
                        temp
                    )

                    # ─────────────────────────
                    # suavização
                    # ─────────────────────────

                    temps_corrigidas.append(
                        temp_corrigida
                    )

                    if len(temps_corrigidas) > MEDIA_MOVEL:
                        temps_corrigidas.pop(0)

                    temp_suavizada = (
                        sum(temps_corrigidas)
                        / len(temps_corrigidas)
                    )

                    # ─────────────────────────
                    # média temperatura real
                    # ─────────────────────────

                    temps_reais.append(temp)

                    if len(temps_reais) > MEDIA_MOVEL:
                        temps_reais.pop(0)

                    avg_temp = (
                        sum(temps_reais)
                        / len(temps_reais)
                    )

                    # ─────────────────────────
                    # terminal
                    # ─────────────────────────

                    print(
                        f"[PCM LOG] "
                        f"REAL:{temp:.2f}°C | "
                        f"AVG:{avg_temp:.2f}°C | "
                        f"CORR:{temp_corrigida:.2f}°C | "
                        f"SUAVE:{temp_suavizada:.2f}°C | "
                        f"TIME:{time_ms}"
                    )

                    # ─────────────────────────
                    # CSV
                    # ─────────────────────────

                    f.write(
                        f"{temp},"
                        f"{time_ms},"
                        f"{minutes},"
                        f"{temp_corrigida},"
                        f"{temp_suavizada}\n"
                    )

                    f.flush()

                else:
                    print(f"[RAW] {raw}")

            except KeyboardInterrupt:

                print("\n🛑 Encerrado")
                break
            
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

        while True:
            try:
                linha = ser.readline().decode().strip()

                if linha:
                    print(linha)

            except serial.SerialException as e:
                print("Erro serial:", e)
                break

    except Exception as e:
        print("Erro geral:", e)


if __name__ == "__main__":
    main()