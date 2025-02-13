import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#테스트용 input
kid = "하늘은 왜 파란색이야?"
gpt = "햇빛이 공기랑 만나면서 파란색이 더 많이 퍼져서 그래! 낮에는 파란색이 많이 보이고, 해 질 때는 빨간색이 더 보이는 거야. 신기하지?"

def summary(kid, gpt):#분석 프롬프트 json 문자열 으로 반환
    prompt = "아래의 대화를 감정분석(긍정/부정), 언어발달(어휘 다양성, 평균 문장 길이, 문법 복잡성), 사회성발달(감정적 반응 점수, 응답 상호작용) 카테고리에 맞게 수치화해서 json으로 답변해줘"

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt+ f"아이:{kid} gpt: {gpt}"}],
        stream=True,
    )

    result = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            result += chunk.choices[0].delta.content

    return result

# 테스트 실행
if __name__ == '__main__':
    res = summary(kid, gpt)
    print(res)
