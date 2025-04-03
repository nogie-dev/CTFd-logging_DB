from fastapi import FastAPI
from pydantic import BaseModel
from dbManager import connect_to_db,close_db_connection
app=FastAPI()
curs=connect_to_db().cursor()

@app.get("/")
async def root():
    return{"message":"Anti-Cheat Logging API"}

# class logInfo(BaseModel):
#     container_id: str
#     challenge_name: str
#     user_name: str
#     user_ip: str
#     created_at: str
    
@app.post("/api/container_logging")
async def test():
    get_info_sql="SELECT * FROM container_info_model  ORDER BY timestamp desc LIMIT 1"
    curs.execute(get_info_sql)
    row=curs.fetchone()
    print(row)
    logging_sql="INSERT INTO container_logging_db VALUES(%s, %s, %s, %s, %s)"
    # curs.execute(sql,log[])
    # rows=curs.fetchall()
    # for row in rows:
   
    # print(log.container_id)
    
