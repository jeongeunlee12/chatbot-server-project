import os
from dotenv import load_dotenv
import json
import openai
import mysql.connector
from analysis import summary

# .env 파일에서 API 키 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# AI의 시스템 메시지 설정
#systemMessages = "using korean,너는 5~7세 전용 콘텐츠 제공 ai야 다음의 기능을 포함해줘. 0.질문을 답을 하되 아동용에 맞게 수위를 조절하고 검열하며 유기적으로 대답 해야한다. 다만 관심사에대해서는 최대한 이어나가야한다., 1.처음에 기분을 물어본다. 1의 예시: 안녕! 오늘 하루는 어땠어? 특별히 재미있거나 신난 일이 있었어? 2.감정을 색으로 물어보기 2의 예시: 오늘 네 기분을 색깔로 표현하면 어떤 색일까? 2-1. 이때 색깔을 감정으로 분석하고 연결하는 질문을 한며, 색깔과 연관된 감정을 확대하여 놀이를 추천한다(에: 그림그리기, 음악듣기).이때 감정을 표현하기 어려워 하면 예시를 제공한다."

# MySQL DB 연결 설정
db = mysql.connector.connect(
    host="monorail.proxy.rlwy.net",  # Railway에서 제공된 호스트 주소
    port=33050,
    user="root",                      # Railway에서 제공된 사용자명
    password="OzQePaejTXglCantEWdrLvcuXGXVUchR",  # Railway 비밀번호
    database="railway"                # 데이터베이스 이름
)

def load_prompt_from_json():
    with open('prompt.json','r',encoding="utf-8") as file:
        data = json.load(file)

    # 전체 시스템 메시지 생성    
    system_message = f"""
        {data["content"]["descroption"]}
        언어: {data["content"]["lang"]}
        규칙: {data["content"]["rule"]}
        """
    
    # 콘텐츠별 세부 설명 추가
    instructions = ""
    for key, value in data["content"]["instructions"].items():
        instructions += f"\n\n{value[key + '_Name']}\n"
        instructions += f"{value['descroption']}\n"
        instructions += f"언어: {value['lang']}\n"
        instructions += f"규칙: {value['rule']}\n"
        instructions += f"지침: {value['instructions']}\n"

        # 예시 질문 추가
        for i in range(1, 4):
            example_key = f"example{i}"
            if example_key in value:
                instructions += f"예시 질문 {i}: {value[example_key]}\n"
    
    return {"role": "system", "content": system_message + instructions}

#프롬프트 호출 테스트
#print(load_prompt_from_json())

#프롬프트 호출
system_prompt = load_prompt_from_json()

# 대화 이력을 저장할 리스트
messages = [load_prompt_from_json()]

def ai_connect(user_input):
    # 사용자 입력을 대화 목록에 추가
    messages.append({"role": "user", "content": user_input})
    
    # OpenAI API 호출
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=1
    )
    
    # AI 응답 가져오기
    result = response.choices[0].message.content
    print("AI:", result)
    
    # AI의 응답을 대화 이력에 추가
    messages.append({"role": "assistant", "content": result})

    #대화 내용 DB에 저장
    put_conversation(user_input, result)
    #분석내용 DB에 저장
    put_analysis(user_input, result)

#대화내용 DB에 저장
def put_conversation(user_input, result): #추후에는 child_id도 파라미터로 받아서 실행해야함.
    sql = "insert into conversation(child_id, input_text, response_text) values (%s, %s, %s)"
    values = (1, user_input, result)
    cursor = db.cursor()
    cursor.execute(sql, values)
    db.commit()

# 분석 내용 DB에저장
def put_analysis(user_input, result): #추후에는 child_id도 파라미터로 받아서 실행해야함.
    json_data = summary.summary(user_input,result)

    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    emotion_analysis = json.dumps({"감정분석": json_data["감정분석"]}, ensure_ascii=False)
    language_analysis = json.dumps(json_data["언어발달"], ensure_ascii=False)
    social_interaction = json.dumps(json_data["사회성발달"], ensure_ascii=False)

    cursor = db.cursor()

    sql = "INSERT INTO analysis (child_id, emotion_analysis, language_analysis, social_interaction) VALUES (%s, %s, %s, %s)"
    values = (1, emotion_analysis, language_analysis, social_interaction)

    cursor.execute(sql, values)
    db.commit()

# 메인 루프: 사용자 입력을 계속 받음
print("AI와 대화를 시작합니다. '종료'를 입력하면 끝납니다.")
while True:
    user_input = input("You: ")
    
    if user_input.lower() == "종료":
        print("대화를 종료합니다.")
        break
    
    ai_connect(user_input)