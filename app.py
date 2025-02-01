from flask import Flask, request, jsonify
import mysql.connector

# Flask 앱 초기화
app = Flask(__name__)

# MySQL DB 연결 설정
db = mysql.connector.connect(
    host="monorail.proxy.rlwy.net",  # Railway에서 제공된 호스트 주소
    port=33050,
    user="root",                      # Railway에서 제공된 사용자명
    password="OzQePaejTXglCantEWdrLvcuXGXVUchR",  # Railway 비밀번호
    database="railway"                # 데이터베이스 이름
)

# API 엔드포인트 정의
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')

    # DB에서 메시지에 대한 응답 조회
    cursor = db.cursor()
    cursor.execute("SELECT response FROM chatbot_responses WHERE message = %s", (user_message,))
    result = cursor.fetchone()

    if result:
        response = {"reply": result[0]}
    else:
        response = {"reply": "저장된 응답이 없습니다."}

    return jsonify(response)

# Flask 앱 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

