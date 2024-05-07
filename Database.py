import mysql.connector

# 数据库连接配置
config = {
    'user': 'root',      
    'password': 'rcdatabase', 
    'host': '127.0.0.1',           
    'port': 3306,                 
    'database': 'rc_card',   
    'raise_on_warnings': True
}


# try:
#     # 连接到数据库
#     cnx = mysql.connector.connect(**config)
#     cursor = cnx.cursor()

#     # 插入数据
#     # Try to insert, if fail, just select
#     try:
#         insert_query = ("INSERT INTO students (name, student_id, hold) "
#                         "VALUES (%s, %s, %s)")
#         data = ('Xiaoyang', 3200112429, True)
#         cursor.execute(insert_query, data)
#     except mysql.connector.Error as err:
#         print(f"Insert failed: {err}")

#     # 提交修改
#     cnx.commit()

#     # 查询并打印所有数据
#     query = "SELECT name, student_id, hold FROM students"
#     cursor.execute(query)

#     print("Students table contents:")
#     for (name, student_id, hold) in cursor:
#         print(f"{name}, {student_id}, {hold}")

# except mysql.connector.Error as err:
#     print(f"Something went wrong: {err}")

# finally:
#     # 关闭连接
#     cursor.close()
#     cnx.close()


def select(cnx, cursor, database, table, columns, condition=None):
    query = f"SELECT {columns} FROM {database}.{table}"
    if condition:
        query += f" WHERE {condition}"
        
    cursor.execute(query)
    return cursor.fetchall()

def insert(cnx, cursor, database, table, columns, data):
    query = f"INSERT INTO {database}.{table} ({columns}) VALUES ({data})"
    print(query)
    cursor.execute(query)
    try:
        cnx.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Insert failed: {err}")
        return False
