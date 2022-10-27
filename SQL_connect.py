# import mysql.connector
# db = mysql.connector.connect(host='remotemysql.com', user='YAhxezPhBh', passwd="TSP5zmOVD3",
#                              database='YAhxezPhBh')
# mycursor = db.cursor()
# mycursor.execute("SELECT * FROM Users")
command = {"name": "test", "type": 1, "description": "For testing purposes", "options": [
    {"name": "required", "description": "required", "type": 3, "required": True,
     "choices": [{"name": "Uno", "value": "1"}, {"name": "Dos", "value": 2}]}
    ]}
