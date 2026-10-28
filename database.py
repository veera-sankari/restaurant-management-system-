import pymysql

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="Reera07&19",
    database="dineflow_db",
    cursorclass=pymysql.cursors.DictCursor
)