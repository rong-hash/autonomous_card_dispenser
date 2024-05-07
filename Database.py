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


def select(cnx, cursor, database, table, columns, condition=None):
    query = f"SELECT {columns} FROM {database}.{table}"
    if condition:
        query += f" WHERE {condition}"
        
    try:
        cursor.execute(query)
    except mysql.connector.Error as err:
        print(f"Select failed: {err}")
        return None
    return cursor.fetchall()

def insert(cnx, cursor, database, table, columns, data):
    query = f"INSERT INTO {database}.{table} ({columns}) VALUES ({data})"
    
    try:
        cursor.execute(query)
        cnx.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Insert failed: {err}")
        return False


def update(cnx, cursor, database, table, columns, data, condition):
    query = f"UPDATE {database}.{table}"
    columns = columns.replace(" ", "").split(',')
    data = data.replace(" ", "").split(',')
    if columns and data and len(columns) == len(data):
        query += f" SET "
        for i in range(len(columns)):
            query += f"{columns[i]} = {data[i]}"
            if i < len(columns) - 1:
                query += ", "
    if condition:
        query += f" WHERE {condition}"
    try:
        cursor.execute(query)
        cnx.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Update failed: {err}")
        return False