from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from dbManager import connect_to_db, close_db_connection
from datetime import datetime
import hashlib
import json

app = FastAPI()

dict_flag={
    1:'test_flag',
    2:'hallo_flag'
}

# 로깅 정보 모델 정의
class LogInfo(BaseModel):
    container_id: str
    concat_flag: str
    challenge_id: str
    user_id: str
    user_ip: str
    created_at: str

# 비동기 로깅 함수
async def log_container_info(log_data: LogInfo):
    conn = connect_to_db()
    cursor = conn.cursor()
    print("로깅 시작...")
    try:
        # 컬럼을 명시적으로 지정 (no는 AUTO_INCREMENT로 설정되어 있으므로 제외)
        logging_sql = """
        INSERT INTO container_log 
        (container_id, concat_flag, challenge_id, user_id, user_ip, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # DATE 타입에 맞는 형식으로 변환
        created_date = datetime.now().strftime("%Y-%m-%d")
        
        values = (
            log_data.container_id,
            log_data.concat_flag,
            log_data.challenge_id,
            log_data.user_id,
            log_data.user_ip,
            created_date
        )
        
        print(f"SQL 실행: {logging_sql}")
        print(f"값: {values}")
        
        cursor.execute(logging_sql, values)
        conn.commit()
        print("로깅 성공!")
    except Exception as e:
        print(f"로깅 중 오류 발생: {e}")
        conn.rollback()
    finally:
        cursor.close()
        close_db_connection(conn)

@app.get("/")
async def root():
    return {"message": "Anti-Cheat Logging API"}

@app.post("/api/container_logging")
async def container_logging(background_tasks: BackgroundTasks):
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        get_info_sql = "SELECT * FROM container_info_model ORDER BY timestamp desc LIMIT 1"
        cursor.execute(get_info_sql)
        row = cursor.fetchone()
        if not row:
            return {"status": "error", "message": "컨테이너 정보를 찾을 수 없습니다."}
        
        container_id = row[0]  # container_id 컬럼 인덱스
        challenge_id = row[1]  # challenge_id 컬럼 인덱스
        user_id = row[3]       # user_id 컬럼 인덱스
        
        print(f"데이터 조회 결과: {row}")
        print(f"사용자 ID: {user_id}")
        
        user_ip = "127.0.0.1"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        concat_str = str(container_id) + str(dict_flag[challenge_id])
        hashing_flag = hashlib.sha256(concat_str.encode()).hexdigest()
        
        log_data = LogInfo(
            container_id=container_id,
            concat_flag=hashing_flag,
            challenge_id=str(challenge_id),  # 문자열로 변환
            user_id=str(user_id),            # 문자열로 변환
            user_ip=user_ip,
            created_at=created_at
        )
        
        print(f"로깅 데이터: {log_data}")
        
        # 디버깅을 위해 직접 호출
        #await log_container_info(log_data)
        # 나중에 다시 백그라운드로 변경
        background_tasks.add_task(log_container_info, log_data)
        
        return {"status": "success", "message": "컨테이너 로깅이 처리되었습니다."}
    
    except Exception as e:
        print(f"전체 프로세스 오류: {str(e)}")
        return {"status": "error", "message": f"오류 발생: {str(e)}"}
    
    finally:
        cursor.close()
        close_db_connection(conn)