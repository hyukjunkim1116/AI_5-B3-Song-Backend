import openai
import my_settings

# GPT-4 API 키 설정
openai.api_key = my_settings.OPENAI_API_KEY


# GPT에게 질문하기 위한 요청 생성
def generate_gpt_input(content):
    return f"음악 추천: {content}"


# GPT-4에서 반환된 응답을 파싱하여 음악 추천 가져오기
def parse_gpt_response(response):
    return response.choices[0].text.strip()


# GPT-4를 사용하여 음악 추천 받기
def get_music_recommendation(content):
    gpt_input = generate_gpt_input(content)
    prompt = gpt_input

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    recommendation = parse_gpt_response(response)
    return recommendation
