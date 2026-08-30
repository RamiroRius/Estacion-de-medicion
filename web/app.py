import os
from flask import Flask, render_template
from flask_socketio import SocketIO
import serial
import sqlite3

app = Flask(__name__)

PUERTO_SERIAL = os.environ.get("PUERTO_SERIAL", "/dev/ttyACM0")
BAUD_RATE = 9600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
DB_PATH = os.path.join(DATA_DIR, "mediciones.db")


conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS datos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lectura INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)
conexion.commit()
conexion.close()


try:
    ser = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
    ser = None

socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")
@app.route("/")
def index():
    return render_template("index.html")

def insertDataBase(valor):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO datos (lectura) VALUES (?)", (valor,)
    )
    conexion.commit()
    conexion.close()

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
                insertDataBase(linea)
        except serial.SerialException as e:
            print(f"Error de conexión serial: {e}")
            socketio.emit("error_sensor", {"mensaje": "Sensor desconectado"})
            socketio.sleep(2)


if __name__ == "__main__":
    socketio.start_background_task(mostrar_datos)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)