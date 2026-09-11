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

#consultar los estudios asociados a una hoja de vida
@app.route("/api/hojas-vida/int:id/estudios", methods=["GET"])
def obtener_estudios(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    # Verificar que la hoja de vida exista
    sql_verificar = "SELECT id FROM hojas_vida WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    hoja = cursor.fetchone()

    if hoja is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la hoja de vida"}, 404

    # Consultar los estudios
    sql = """SELECT id, hoja_vida_id, nivel, institucion, titulo, anio_graduacion
            FROM estudios
            WHERE hoja_vida_id = %s"""

    cursor.execute(sql, (id,))
    estudios = cursor.fetchall()

    cursor.close()
    conec.close()

    return estudios

#registrar un nuevo estudio
@app.route("/api/hojas-vida/int:id/estudios", methods=["POST"])
def registrar_estudio(id):
    datos = request.json

    conec = conectar_bd()
    cursor = conec.cursor()

    # Verificar que la hoja de vida exista
    sql_verificar = "SELECT id FROM hojas_vida WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    hoja = cursor.fetchone()

    if hoja is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la hoja de vida"}, 404

    # Registrar el estudio
    sql = """INSERT INTO estudios
            (hoja_vida_id, nivel, institucion, titulo, anio_graduacion)
            VALUES (%s, %s, %s, %s, %s)"""

    valores = (
        id,
        datos["nivel"],
        datos["institucion"],
        datos["titulo"],
        datos["anio_graduacion"]
    )

    cursor.execute(sql, valores)
    conec.commit()

    id_generado = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio registrado",
        "id": id_generado,
        "hoja_vida_id": id
    }, 201

#Consultar un estudio específico
@app.route("/api/estudios/int:id", methods=["GET"])
def obtener_estudio(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT id, hoja_vida_id, nivel, institucion, titulo, anio_graduacion
            FROM estudios
            WHERE id = %s"""

    cursor.execute(sql, (id,))
    estudio = cursor.fetchone()

    cursor.close()
    conec.close()

    if estudio is None:
        return {"mensaje": "No se encontro el estudio"}, 404

    return estudio

#Actualizar un estudio
@app.route("/api/estudios/int:id", methods=["PUT"])
def actualizar_estudio(id):

    datos = request.json

    conec = conectar_bd()
    cursor = conec.cursor()

    # Verificar que el estudio exista
    sql_verificar = "SELECT id FROM estudios WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    estudio = cursor.fetchone()

    if estudio is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro el estudio"}, 404

    # Actualizar estudio
    sql = """UPDATE estudios
            SET nivel = %s,
                institucion = %s,
                titulo = %s,
                anio_graduacion = %s
            WHERE id = %s"""

    valores = (
        datos["nivel"],
        datos["institucion"],
        datos["titulo"],
        datos["anio_graduacion"],
        id
    )

    cursor.execute(sql, valores)
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio actualizado",
        "id": id
    }

#Eliminar un estudio
@app.route("/api/estudios/int:id", methods=["DELETE"])
def eliminar_estudio(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    # Verificar que el estudio exista
    sql_verificar = "SELECT id FROM estudios WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    estudio = cursor.fetchone()

    if estudio is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro el estudio"}, 404

    # Eliminar estudio
    sql = "DELETE FROM estudios WHERE id = %s"
    cursor.execute(sql, (id,))
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio eliminado"
    }

#Consultar las experiencias laborales
@app.route("/api/hojas-vida/<int:id>/experiencias", methods=["GET"])
def obtener_experiencias(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    # Verificar que la hoja de vida exista
    sql_verificar = "SELECT id FROM hojas_vida WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    hoja = cursor.fetchone()

    if hoja is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la hoja de vida"}, 404

    # Consultar las experiencias
    sql = """SELECT id, hoja_vida_id, empresa, cargo, tiempo, funciones
             FROM experiencias
             WHERE hoja_vida_id = %s"""

    cursor.execute(sql, (id,))
    experiencias = cursor.fetchall()

    cursor.close()
    conec.close()

    return experiencias


#Registrar una nueva experiencia
@app.route("/api/hojas-vida/<int:id>/experiencias", methods=["POST"])
def registrar_experiencia(id):

    datos = request.json

    conec = conectar_bd()
    cursor = conec.cursor()

    #Verificar que la hoja de vida exista
    sql_verificar = "SELECT id FROM hojas_vida WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    hoja = cursor.fetchone()

    if hoja is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la hoja de vida"}, 404

    #Registrar la experiencia
    sql = """INSERT INTO experiencias
             (hoja_vida_id, empresa, cargo, tiempo, funciones)
             VALUES (%s, %s, %s, %s, %s)"""

    valores = (
        id,
        datos["empresa"],
        datos["cargo"],
        datos["tiempo"],
        datos["funciones"]
    )

    cursor.execute(sql, valores)
    conec.commit()

    id_generado = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia registrada",
        "id": id_generado,
        "hoja_vida_id": id
    }, 201


#Consultar una experiencia
@app.route("/api/experiencias/<int:id>", methods=["GET"])
def obtener_experiencia(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """SELECT id, hoja_vida_id, empresa, cargo, tiempo, funciones
             FROM experiencias
             WHERE id = %s"""

    cursor.execute(sql, (id,))
    experiencia = cursor.fetchone()

    cursor.close()
    conec.close()

    if experiencia is None:
        return {"mensaje": "No se encontro la experiencia"}, 404

    return experiencia


#Actualizar una experiencia
@app.route("/api/experiencias/<int:id>", methods=["PUT"])
def actualizar_experiencia(id):

    datos = request.json

    conec = conectar_bd()
    cursor = conec.cursor()

    #Verificar que la experiencia exista
    sql_verificar = "SELECT id FROM experiencias WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    experiencia = cursor.fetchone()

    if experiencia is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la experiencia"}, 404

    #Actualizar experiencia
    sql = """UPDATE experiencias
             SET empresa = %s,
                 cargo = %s,
                 tiempo = %s,
                 funciones = %s
             WHERE id = %s"""

    valores = (
        datos["empresa"],
        datos["cargo"],
        datos["tiempo"],
        datos["funciones"],
        id
    )

    cursor.execute(sql, valores)
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia actualizada",
        "id": id
    }


#Eliminar una experiencia
@app.route("/api/experiencias/<int:id>", methods=["DELETE"])
def eliminar_experiencia(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    #Verificar que la experiencia exista
    sql_verificar = "SELECT id FROM experiencias WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    experiencia = cursor.fetchone()

    if experiencia is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la experiencia"}, 404

    #Eliminar experiencia
    sql = "DELETE FROM experiencias WHERE id = %s"
    cursor.execute(sql, (id,))
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia eliminada"
    }

# Consultar las habilidades de una experiencia
@app.route("/api/experiencias/<int:id>/habilidades", methods=["GET"])
def obtener_habilidades(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    # Verificar que la experiencia exista
    sql_verificar = "SELECT id FROM experiencias WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    experiencia = cursor.fetchone()

    if experiencia is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la experiencia"}, 404

    # Consultar las habilidades
    sql = """SELECT id, experiencia_id, nombre
             FROM habilidades
             WHERE experiencia_id = %s"""

    cursor.execute(sql, (id,))
    habilidades = cursor.fetchall()

    cursor.close()
    conec.close()

    return habilidades


# Registrar una habilidad
@app.route("/api/experiencias/<int:id>/habilidades", methods=["POST"])
def registrar_habilidad(id):

    datos = request.json

    conec = conectar_bd()
    cursor = conec.cursor()

    # Verificar que la experiencia exista
    sql_verificar = "SELECT id FROM experiencias WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    experiencia = cursor.fetchone()

    if experiencia is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la experiencia"}, 404

    # Registrar la habilidad
    sql = """INSERT INTO habilidades
             (experiencia_id, nombre)
             VALUES (%s, %s)"""

    valores = (
        id,
        datos["nombre"]
    )

    cursor.execute(sql, valores)
    conec.commit()

    id_generado = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad registrada",
        "id": id_generado,
        "experiencia_id": id
    }, 201


# Actualizar una habilidad
@app.route("/api/habilidades/<int:id>", methods=["PUT"])
def actualizar_habilidad(id):

    datos = request.json

    conec = conectar_bd()
    cursor = conec.cursor()

    # Verificar que la habilidad exista
    sql_verificar = "SELECT id FROM habilidades WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    habilidad = cursor.fetchone()

    if habilidad is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la habilidad"}, 404

    # Actualizar habilidad
    sql = """UPDATE habilidades
             SET nombre = %s
             WHERE id = %s"""

    valores = (
        datos["nombre"],
        id
    )

    cursor.execute(sql, valores)
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad actualizada",
        "id": id
    }


# Eliminar una habilidad
@app.route("/api/habilidades/<int:id>", methods=["DELETE"])
def eliminar_habilidad(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    # Verificar que la habilidad exista
    sql_verificar = "SELECT id FROM habilidades WHERE id = %s"
    cursor.execute(sql_verificar, (id,))
    habilidad = cursor.fetchone()

    if habilidad is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontro la habilidad"}, 404

    # Eliminar habilidad
    sql = "DELETE FROM habilidades WHERE id = %s"
    cursor.execute(sql, (id,))
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Habilidad eliminada"
    }


if __name__=="__main__":
    app.run(debug=True)