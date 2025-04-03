import pymysql
import pymysql

# 데이터베이스 연결 설정
def connect_to_db():
    try:
        connection = pymysql.connect(
            host='localhost', 
            user='ctfd', 
            password='ctfd', 
            db='ctfd', 
            charset='utf8',
            port=3306
            #cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리 형태로 반환
        )
        print("DB connecton")
        return connection
    except pymysql.MySQLError as e:
        print(f"connection fail: {e}")
        return None

def close_db_connection(connect):
    if connect:
        connect.close()
        print("DB closed")