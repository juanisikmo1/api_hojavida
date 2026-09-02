import mysql.connector

def conectar_bd():
    conexion = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="",
        database="hojas_vida"
    )
    return conexion