import mysql.connector

def connect_mysql():
    mydb=mysql.connector.connect(
        host="itpmysql.usc.edu",
        port=3306,
        user="forishua",
        password="3680289662",
        database="largeco"
    )
    return mydb





