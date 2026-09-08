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

#actualizar hv de vida por medio del id
@app.route("/api/actualizarhv/<int:id>",methods=["PUT"])
def actualizarhv(id):

    #recibir los datos enviados
    datos = request.json
    conec = conectar_bd()
    cursor = conec.cursor()

    #verificar que la hv existe
    buscar = """SELECT id FROM hojas_vida WHERE id=%s"""
    cursor.execute(buscar,(id,))
    resul = cursor.fetchone()

    if resul is None:
        cursor.close()
        conec.close()
        return{"mensaje":"No se encontro la hoja de vida"}, 404

    sqlcorreo = """SELECT id FROM hojas_vida WHERE correo = %s and id !=%s"""
    cursor.execute(sqlcorreo,(datos["correo"], id))
    resul = cursor.fetchone()
    if resul is not None:
            cursor.close()
            conec.close()
            return{
            "mensaje":"el correo esta asociado a otra hoja de vida"
            },409

    sqlactualizar = """UPDATE hojas_vida SET nombre=%s,edad=%s,ciudad=%s,correo=%s,fotografia=%s,programa=%s,ficha=%s,jornada=%s WHERE id=%s"""
    valor =(
            datos["nombre"],
            datos["edad"],
            datos["ciudad"],
            datos["correo"],
            datos.get("fotografia"),
            datos["programa"],
            datos["ficha"],
            datos["jornada"],
            id
        )
    cursor.execute(sqlactualizar,valor)
    conec.commit()
    cursor.close()
    conec.close()

    return{
        "Mensaje":"Hoja de vida actualizada",
        "id":id}

#eliminar hv por id
@app.route("/api/eliminarhv/<int:id>",methods=["DELETE"])
def eliminar_hv(id):
    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute("SELECT id FROM hojas_vida WHERE id = %s",(id,))

    existe = cursor.fetchone()

    if existe is None:
        cursor.close()
        conec.close()
        return{"mensaje": "No se encotro la hoja de vida"}, 404

    sql = """DELETE FROM hojas_vida WHERE id=%s"""

    cursor.execute(sql,(id,))
    conec.commit()
    cursor.close()
    conec.close()
    return {"mensaje":"Hoja de vida eliminada"}

#consultar hv por id
@app.route("/api/consultahv/<int:id>", methods=["GET"])
def obtener_hvida(id):
    #conecion a la base de datos
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT * FROM hojas_vida WHERE id = %s"""
    cursor.execute(sql,(id,))

    datos = cursor.fetchone()

    cursor.close()
    conec.close()
    #que pasa cuando es nulo
    if datos is None:
        return{"mensaje":"No se encotro la hoja de vida"}, 404

    return datos

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

        return {"mensaje": "El usuario ya está registrado"}, 409

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

@app.route("/api/hojas-vida/<int:id>", methods=["GET"])
def obtener_hojasvidaid(id):
    return{"mensaje":"hoja de vida encontrada","id":id}

@app.route("/api/hojas-vida", methods=["GET"])
def obtener_hojasvida():
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True) 

    sql = "SELECT * FROM hojas_vida"
    cursor.execute(sql)

    hojas_vida = cursor.fetchall()

    cursor.close()
    conec.close()

    return hojas_vida

if __name__=="__main__":
    app.run(debug=True)