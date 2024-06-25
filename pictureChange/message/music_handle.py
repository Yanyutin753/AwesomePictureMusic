# 此类用于存放音乐回复处理操作
import json
import re
import time

import requests

from plugins.pictureChange.message import message_reply


class music_handle:
    def __init__(self):
        super().__init__()

    def text_to_music(url: str, key: str, prompt: str, model: str, max_retries: int = 1, backoff_factor: float = 1.0):
        headers = {
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": model,
            "stream": True,
            "messages": [
                {
                    "content": prompt,
                    "role": "user"
                }
            ]
        }

        content = ""

        retries = 0
        music_link_counter = 0
        video_counter = 0
        song_counter = 0
        result = {
            "song_name": None,
            "genre": None,
            "full_lyrics": None,
            "song_image": None,
            "music_link1": None,
            "music_link2": "",
            "video1": "",
            "video2": "",
            "song1": "",
            "song2": "",
        }

        while retries < max_retries:
            try:
                with requests.post(url, headers=headers, json=payload, stream=True) as response:
                    response.raise_for_status()  # Check HTTP status code
                    print(response.status_code)

                    for i, line in enumerate(response.iter_lines()):
                        line = line.decode('utf-8')

                        if line.startswith("data:") and "[DONE]" not in line:
                            try:
                                # 将UTF-8字符串重新编码为GBK并处理可能的编码错误
                                line_gbk = line.encode('gbk', errors='ignore').decode('gbk', errors='ignore')
                                line_gbk = line_gbk.replace("data: ", "")
                                json_data = json.loads(line_gbk)
                                # print(f"第{i}条信息为：{json_data}")
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    message_content = delta.get('content', "")

                                    if "歌名" in message_content:
                                        song_name_match = re.search(r'歌名\*\*：(.+?)\n', message_content)
                                        if song_name_match:
                                            result["song_name"] = song_name_match.group(1).strip()
                                        print(result["song_name"])
                                    elif "类型" in message_content:
                                        genre_match = re.search(r'类型\*\*：(.+)', message_content)
                                        if genre_match:
                                            result["genre"] = genre_match.group(1).strip()
                                        print(result["genre"])
                                    elif "完整歌词" in message_content:
                                        lyrics_start_index = message_content.find("## 🎼 完整歌词\n```")
                                        if lyrics_start_index != -1:
                                            lyrics_start_index += len("## 🎼 完整歌词\n```")
                                            lyrics_end_index = message_content.find("```", lyrics_start_index)
                                            if lyrics_end_index != -1:
                                                lyrics_content = message_content[lyrics_start_index:lyrics_end_index]
                                                result["full_lyrics"] += lyrics_content
                                                message_reply.reply_Text_Message(lyrics_content)
                                                print(result["full_lyrics"])
                                    elif "封面图片_大" in message_content:
                                        url_match = re.search(r'https?://.*?\)', message_content)
                                        if url_match:
                                            result["song_image"] = url_match.group(0).rstrip(')')
                                        print(result["song_image"])
                                        message_reply.reply_ImageUrl_Message(result["song_image"])
                                    elif "永久音乐链接" in message_content and "歌曲" in message_content:
                                        url_matches = re.findall(r'https?://\S+\.mp3', message_content)
                                        for idx, match in enumerate(url_matches):
                                            if idx == 0:
                                                result["song1"] = match
                                            elif idx == 1:
                                                result["song2"] = match
                                        print(result["song1"])
                                        print(result["song2"])
                                        message_reply.reply_VideoUrl_Message(result["song1"])
                                    elif "音乐链接" in message_content:
                                        url_match = re.search(r'https?://\S+', message_content)
                                        if url_match:
                                            music_link_counter += 1
                                            if music_link_counter == 1:
                                                result["music_link1"] = url_match.group(0)
                                                print(result["music_link1"])
                                            elif music_link_counter == 2:
                                                result["music_link2"] = url_match.group(0)
                                                print(result["music_link2"])
                                    elif "永久视频链接" in message_content:
                                        url_matches = re.findall(r'https?://\S+\.mp4', message_content)
                                        for idx, match in enumerate(url_matches):
                                            if idx == 0:
                                                result["video1"] = match
                                            elif idx == 1:
                                                result["video2"] = match
                                        print(result["video1"])
                                        print(result["video2"])
                                        message_reply.reply_VideoUrl_Message(result["video1"])

                                    # if message_content:
                                    #     content += message_content
                            except json.JSONDecodeError:
                                continue

                return result

            except requests.exceptions.RequestException as e:
                if hasattr(response, 'status_code') and response.status_code == 503:
                    retries += 1
                    wait = backoff_factor * (2 ** (retries - 1))
                    print(f"503 Error: Retrying in {wait} seconds...")
                    time.sleep(wait)
                else:
                    return f"An error occurred: {e}"

        return f"Failed to retrieve content after {max_retries} attempts due to 503 errors."
