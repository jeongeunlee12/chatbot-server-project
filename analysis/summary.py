import openai

#해당 키들 다른곳에서 보관해야함 ex).env
def getApiKey():
    return ""

def getOrganization():
    return ""

openai.organization = getOrganization()
openai.api_key = getApiKey()

#테스트용 input
kid = "하늘은 왜 파란색이야?"
gpt = "햇빛이 공기랑 만나면서 파란색이 더 많이 퍼져서 그래! 낮에는 파란색이 많이 보이고, 해 질 때는 빨간색이 더 보이는 거야. 신기하지?"

def summary(kid, gpt):
    prompt = "아래의 대화가 교육(과학), 교육(수학), 언어발달, 사회성발달 중 어떤 카테고리에 속하는지 알려주고 카테고리|요약 의 형태로 요약해줘 "

    stream = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt+ f"아이:{kid} gpt: {gpt}"}],
        stream=True,
    )

    return stream

def res_to_str(res):
    result = ""
    for chunk in res:
        if chunk.choices[0].delta.content is not None:
            result += chunk.choices[0].delta.content

    return result

#테스트용
if __name__ == '__main__':
    res = summary(kid, gpt)
    result = res_to_str(res)
    print(result)