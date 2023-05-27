import openai
import googleapiclient.discovery
import googleapiclient.errors
import re
from my_settings import OPENAI_API_KEY, YOUTUBE_API_KEY

# GPT API 키 설정
openai.api_key = OPENAI_API_KEY

import requests
from bs4 import BeautifulSoup


def is_artist_first(text):
    if re.match(r"^[a-zA-Z가-힣\s]+[-]\s*", text):
        return True
    else:
        return False


def extract_song_title(text):
    if is_artist_first(text):
        pattern = r"^[a-zA-Z가-힣\s]+[-]\s*"
    else:
        pattern = r"[-]\s*[a-zA-Z가-힣\s]+"

    without_artist = re.sub(pattern, "", text)
    return without_artist.strip()


def gpt_music_recommendation(content):
    gpt_input = (
        f"이 내용 분위기에 어울리는 완벽한 팝송 추천 한곡만 부탁드립니다: {content}. 제목만 알려주세요. 가수 이름과 링크는 필요없어요. "
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=gpt_input,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.3,
    )

    recommendation = response.choices[0].text.strip()
    song_title = extract_song_title(recommendation)
    return song_title


def get_youtube_music_link(song):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=YOUTUBE_API_KEY
    )

    request = youtube.search().list(
        part="id,snippet",
        type="video",
        videoCategoryId="10",  # 추가 - 음악 카테고리만 해당
        q=song,
        videoDefinition="high",
        maxResults=1,
        fields="items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description))",
    )

    response = request.execute()

    if response["items"]:
        video_url = (
            f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
        )

        html_doc = requests.get(video_url)
        soup = BeautifulSoup(html_doc.text, "html.parser")
        meta_tags = soup.find_all("meta")

        og_title = None
        og_url = None
        for tag in meta_tags:
            if "property" not in tag.attrs:
                continue
            if tag.attrs["property"] == "og:title":
                og_title = tag.attrs["content"]
            if tag.attrs["property"] == "og:url":
                og_url = tag.attrs["content"]
            if og_title is not None and og_url is not None:
                break

        return og_title, og_url
    else:
        return "찾을 수 없습니다."


def recommend_music_and_link(content):
    recommendation = gpt_music_recommendation(content)
    youtube_link = get_youtube_music_link(recommendation)
    return recommendation, youtube_link
