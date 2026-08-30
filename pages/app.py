from flask import Flask, render_template
from flask_socketio import SocketIO
import serial

app = Flask(__name__)

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)

socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*", logger=True, engineio_logger=True)


@app.route("/")
def index():
    return render_template("index.html")

def mostrar_datos():
    contador = 0
    while True:
        linea = ser.readline().decode("utf-8").strip()
        if linea :
            print(f"Enviando dato: {linea}")
            socketio.emit("actualizar_sensor", {"valor": linea})

if __name__ == "__main__":
    socketio.start_background_task(mostrar_datos)

    socketio.run(app, debug=True, use_reloader=False)
