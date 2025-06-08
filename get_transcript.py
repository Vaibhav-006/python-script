import requests
import random
import json
import re
# get_transcript.py
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

class TranscriptError(Exception):
    pass

def get_transcript(video_url: str, language='en') -> dict:
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return {"transcript": transcript}
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        raise TranscriptError(str(e))

# Proxy list (example)
proxies = [
    "http://87.248.129.32:80",
"http://78.28.152.113:80",
"http://85.132.37.9:1313",
"http://4.149.210.210:3128",
"http://139.59.1.14:80",
"http://159.203.61.169:3128",
"http://158.255.77.169:80",
"http://143.198.42.182:31280",
"http://65.108.203.37:18080",
"http://198.199.86.11:8080",
"http://91.103.120.39:80",
"http://57.129.81.201:8080",
"http://51.81.245.3:17981",
"http://47.236.224.32:8080",
"http://34.102.48.89:8080",
"http://67.43.228.250:7015",
"http://86.98.20.177:8080",
"http://66.191.31.158:80",
"http://138.68.60.8:80",
"http://98.191.238.177:80",
"http://103.154.87.12:80",
"http://91.103.120.37:80",
"http://41.59.90.175:80",
"http://4.156.78.45:80",
"http://171.237.236.104:1004",
"http://91.99.125.212:80",
"http://46.29.162.222:80",
"http://185.234.65.66:1080",
"http://91.103.120.40:80",
"http://91.92.136.132:8889",
"http://123.141.181.49:5031",
"http://158.255.77.166:80",
"http://45.12.150.82:8080",
"http://23.247.136.248:80",
"http://185.88.101.207:8085",
"http://5.59.249.92:8118",
"http://109.191.154.140:8081",
"http://45.81.149.155:6587",
"http://31.57.42.217:6487",
"http://166.88.169.241:6848",
"http://64.79.234.246:6770",
"http://166.88.224.225:6123",
"http://67.227.119.188:6517",
"http://216.246.106.128:5657",
"http://23.27.78.101:5681",
"http://193.233.228.56:8085",
"http://84.46.204.253:6556",
"http://146.103.44.248:6800",
"http://31.59.15.218:6485",
"http://104.239.42.226:6251",
"http://45.38.45.19:5958",
"http://31.58.29.207:6173",
"http://45.39.5.54:6492",
"http://185.94.34.223:8085",
"http://27.79.194.117:16000",
"http://104.143.224.127:5988",
"http://212.119.41.25:8085",
"http://198.23.147.34:5049",
"http://154.6.59.224:6692",
"http://198.46.241.5:6540",
"http://38.153.152.124:9474",
"http://154.30.250.72:5584",
"http://104.249.55.114:6482",
"http://104.238.8.82:5940",
"http://198.23.128.223:5851",
"http://154.6.8.119:5586",
"http://193.31.127.57:8085",
"http://64.49.39.56:8085",
"http://198.37.118.194:5653",
"http://83.171.225.14:8085",
"http://157.20.98.89:1111",
"http://203.95.198.160:8080",
"http://140.235.3.64:8085",
"http://198.23.143.74:80",
"http://123.140.146.21:5031",
"http://190.103.177.131:80",
"http://23.247.136.254:80",
"http://91.103.120.57:80",
"http://37.60.230.56:8888",
"http://37.60.230.27:8888",
"http://77.237.76.83:80",
"http://82.190.190.98:80",
"http://123.140.146.20:5031",
"http://200.250.131.218:80",
"http://27.71.129.117:16000",
"http://141.94.196.80:8989",
"http://27.79.195.199:16000",
"http://165.22.48.81:3128",
"http://27.79.160.227:16000",
"http://37.60.230.30:8888",
"http://82.102.10.253:80",
"http://65.108.203.35:28080",
"http://201.222.50.218:80",
"http://95.111.229.159:8080",
"http://91.103.120.48:80",
"http://139.59.34.209:8080",
"http://195.114.209.50:80",
"http://66.201.7.151:3128",
"http://149.200.200.44:80",
"http://68.183.63.141:8080",
"http://103.75.119.185:80",
"http://164.68.101.70:8888",
"http://193.30.122.197:80",
"http://103.79.131.70:13001",
"http://168.138.50.91:80",
"http://160.251.142.232:80",
"http://198.49.68.80:80",
"http://47.56.110.204:8989",
"http://47.251.43.115:33333",
"http://8.210.88.48:13128",
"http://91.103.120.55:80",
"http://138.199.233.152:80",
"http://159.69.57.20:8880",
"http://186.65.109.21:81",
"http://37.60.230.40:8888",
"http://97.74.87.226:80",
"http://8.219.97.248:80",
"http://46.101.115.59:80",
"http://204.199.68.201:53281",
"http://91.65.103.34:80",
"http://209.97.150.167:8080",
"http://161.35.70.249:8080",
"http://133.18.234.13:80",
"http://167.99.124.118:80",
"http://91.107.154.214:80",
"http://181.65.169.37:999",
"http://47.90.205.231:33333",
"http://179.60.53.28:999",
"http://154.65.39.7:80",
"http://197.243.20.178:80",
"http://13.80.134.180:80",
"http://87.255.196.143:80",
"http://174.138.54.65:80",
"http://146.59.202.70:80",
"http://197.44.247.35:3128",
"http://154.90.48.76:80",
"http://192.73.244.36:80",
"http://103.123.25.65:80",
"http://209.135.168.41:80",
"http://103.109.237.18:8080"
    # Add more proxies here
]

def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if match:
        return match.group(1)
    else:
        return None

def fetch_transcript_with_proxy(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    # Random proxy pick
    proxy = random.choice(proxies)
    proxies_dict = {
        'http': proxy,
        'https': proxy,
    }

    # YouTube transcript API endpoint (unofficial)
    transcript_api_url = f'https://youtube.com/api/timedtext?lang=en&v={video_id}'

    try:
        response = requests.get(transcript_api_url, proxies=proxies_dict, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch transcript, status code: {response.status_code}")

        # Response is XML, so parse accordingly
        from xml.etree import ElementTree
        root = ElementTree.fromstring(response.text)

        transcript = []
        for child in root.findall('text'):
            start = float(child.attrib['start'])
            dur = float(child.attrib.get('dur', 0))
            text = child.text or ''
            transcript.append({'start': start, 'duration': dur, 'text': text})

        return transcript

    except Exception as e:
        print("Error fetching transcript:", e)
        return None

if __name__ == "__main__":
    url = input("Enter YouTube URL: ")
    result = fetch_transcript_with_proxy(url)
    if result:
        print("Transcript:")
        for item in result:
            print(f"{item['start']:.2f} --> {item['text']}")
    else:
        print("Transcript fetch failed.")