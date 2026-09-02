from flask import Flask, request
from database import conectar_bd
app = Flask(__name__)

@app.route("/probar")
def probar_data():
    conec = conectar_bd()
    if conec.is_connected():
        conec.close()

        return{
            "mensaje":"conexion ok"
        }

@app.route("/api/registrohv", methods =["POST"])
def registrohvida():
    conec = conectar_bd()
    cursor = conec.cursor()
    datos = request.json

    sql_consulta = "SELECT id FROM hojas_vida WHERE correo = %s"
    cursor.execute(sql_consulta, (datos["correo"],))
    usuario_existente = cursor.fetchone()

    if usuario_existente:

        cursor.close()
        conec.close()

        return {
            "mensaje": "El usuario ya está registrado",
        }

    sql = """INSERT INTO hojas_vida(nombre,edad,ciudad,correo,fotografia,programa,ficha,jornada)VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
    valor =(datos["nombre"],
            datos["edad"],
            datos["ciudad"],
            datos["correo"],
            datos.get("fotografia"),
            datos["programa"],
            datos["ficha"],
            datos["jornada"])
    cursor.execute(sql,valor)
    conec.commit()
    #manejo del id de la hoja de vida
    id_generado = cursor.lastrowid

    cursor.close()
    conec.close()

    return{"mensaje":"Hoja de vida creada","id":id_generado}

@app.route("/")
def inicio():
    return "Api hoja de vida funcionando"

@app.route("/api/hojas-vida/<int:id>")
def obtener_hojasvidaid(id):
    return{
        "mensaje":"hoja de vida encontrada","id":id
    }

@app.route("/api/hojas-vida")
def obtener_hojasvida():
    conec = conectar_bd()
    cursor = conec.cursor()

    sql = "SELECT * FROM hojas_vida"
    cursor.execute(sql)

    hojas_vida = cursor.fetchall()

    cursor.close()
    conec.close()

    return hojas_vida

if __name__=="__main__":
    app.run(debug=True)