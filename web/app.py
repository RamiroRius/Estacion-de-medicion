import os
from flask import Flask, render_template
from flask_socketio import SocketIO
import serial

app = Flask(__name__)

PUERTO_SERIAL = os.environ.get("PUERTO_SERIAL", "/dev/ttyACM0")
BAUD_RATE = 9600

try:
    ser = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
    ser = None

socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")


def mostrar_datos():
    while True:
        if ser is None:
            socketio.sleep(2)
            continue
        try:
            linea = ser.readline().decode("utf-8", errors="ignore").strip()
            if linea:
                print(f"Enviando dato: {linea}")
                socketio.emit("actualizar_sensor", {"valor": linea})
        except serial.SerialException as e:
            print(f"Error de conexión serial: {e}")
            socketio.emit("error_sensor", {"mensaje": "Sensor desconectado"})
            socketio.sleep(2)


if __name__ == "__main__":
    socketio.start_background_task(mostrar_datos)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)