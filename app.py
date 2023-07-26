from flask import Flask, request, redirect
from flask import render_template, jsonify, flash
from flask import send_from_directory, url_for
from flaskext.mysql import MySQL
from logging import exception
from datetime import datetime
import os


# conexion a flask
app = Flask(__name__)

mysql = MySQL()

# conexion a la base de datos
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "sistema"

# conexion a la app de sql
mysql.init_app(app)

# Guarar el nombre de la carpeta en con config de python para utilizarlo en /uploas
CARPETA = os.path.join(app.root_path, "uploas")
app.config["CARPETA"] = CARPETA


# ruta para traer imagen y poder mostrarla con flask
@app.route("/uploas/<nombreFoto>")
def uploas(nombreFoto):
    return send_from_directory(app.config["CARPETA"], nombreFoto)


# para hacer una validacion en /stre
app.secret_key = "Develoteca"

# ////////////////////////////////////////////////////////////////////////////
# ruta de inicio


@app.route("/")
def index():

    sql = "SELECT *FROM empleados"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()

    conn.commit()

    return render_template("empleados/index.html", empleados=empleados)


# ruta para crear un empleado y se envia a /store
@app.route("/create", methods=["GET"])
def create():

    return render_template("empleados/create.html")


# aqui se envia la informacion de /creat y se guarda
@app.route("/store", methods=["POST"])
def store():

    try:
        nombre = request.form["txtnombre"]
        correo = request.form["txtcorreo"]
        foto = request.files["txtfoto"]

        if nombre == "" or correo == "" or foto == "":
            flash("Recuerda que es obligatorio llebar los campos")
            return redirect(url_for('create'))

        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")

        if foto.filename != "":
            nuevoNombreFoto = tiempo+foto.filename
            foto.save("uploas/"+nuevoNombreFoto)

        sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s)"

        data = (nombre, correo, tiempo+foto.filename)

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()

        return redirect("/")

    except Exception:
        exception("SERVER ERROR-")
        return jsonify({"msg": "algo salio mal"})


# ruta para eliminar de la base de datos un empleado por id
@app.route("/destroy/<int:id>", methods=["GET"])
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    # remover la foto de la carpeta uploas
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config["CARPETA"], fila[0][0]))

    cursor.execute("DELETE FROM empleados WHERE id =%s", id)
    conn.commit()

    return redirect("/")


# ruta para trar los empleados y luego enviarlos a /update
@app.route("/edit/<int:id>", methods=["GET"])
def edit(id):

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT *FROM empleados WHERE id=%s ", (id))

    empleados = cursor.fetchall()

    return render_template("empleados/edit.html", empleados=empleados)


@app.route("/update", methods=["POST"])
def update():

    try:
        nombre = request.form["txtnombre"]
        correo = request.form["txtcorreo"]
        foto = request.files["txtfoto"]
        id = request.form["txtid"]

        conn = mysql.connect()
        cursor = conn.cursor()

        # actualiar foto
        now = datetime.now()
        hoy = now.strftime("%Y%H%M%S")

        if foto.filename != "":
            nuevaFoto = hoy+foto.filename
            foto.save(os.path.join(app.config["CARPETA"], nuevaFoto))

        # buscar la foto en la base con el id

            cursor.execute("SELECT foto  FROM empleados WHERE id=%s ", id)
            fila = cursor.fetchall()
            print("-------", fila[0][0])

            # remover la foto con el nombre en la carpeta

            os.remove(os.path.join(app.config["CARPETA"], fila[0][0]))

            cursor.execute(
                "UPDATE empleados SET foto=%s WHERE id=%s", (nuevaFoto, id))
            conn.commit()

        datos = (nombre, correo, id)
        sql = "UPDATE empleados SET nombre=%s,correo=%s WHERE id=%s"

        cursor.execute(sql, datos)

        conn.commit()

        return redirect("/")
    except Exception as e:
        exception("SERVER ERROR --> ", str(e))

        return jsonify({"msg": "Algo salio mal en la actulizacion de empleados"})


"""conn = mysql.connect()
cursor = conn.cursor()

cursor.execute("SELECT foto FROM empleados WHERE id=%s", 28)
fila = cursor.fetchall()

ruta = os.path.join(app.config["CARPETA"], fila[0][0])

archivo = os.listdir(ruta)

print(ruta)"""


if __name__ == "__main__":
    app.run(debug=True, port=3000)


"""def prueba():

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT foto  FROM empleados WHERE id=%s", 41)
    fila = cursor.fetchall()

    os.remove(os.path.join(app.config["CARPETA"], fila[0][0]))


prueba()"""
