from youtube_transcript_api import YouTubeTranscriptApi
import sys
import json
import io

# Force stdout to use UTF-8 encoding (fixes Windows console 'charmap' errors)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def get_video_id(url):
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com' in url and 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    return None


def serialize_transcript(raw_transcript):
    return [
        {
            "text": item.text,
            "start": item.start,
            "duration": item.duration
        }
        for item in raw_transcript
    ]


def get_transcript(url, language='en'):
    try:
        video_id = get_video_id(url)
        if not video_id:
            return {"error": "Invalid YouTube URL"}

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception as e:
            return {"error": f"Could not fetch transcripts: {str(e)}"}

        for lang in [language, 'en']:
            try:
                transcript = transcript_list.find_transcript([lang])
                return {"transcript": serialize_transcript(transcript.fetch())}
            except Exception:
                continue

        try:
            transcript = next(iter(transcript_list), None)
            if transcript:
                return {"transcript": serialize_transcript(transcript.fetch())}
            else:
                return {"error": "No transcripts available for this video."}
        except Exception as e:
            return {"error": f"No transcripts available: {str(e)}"}

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print(json.dumps({"error": "Please provide a YouTube URL"}))
            sys.exit(1)

        url = sys.argv[1]
        language = sys.argv[2] if len(sys.argv) > 2 else 'en'

        result = get_transcript(url, language)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"error": f"Fatal error: {str(e)}"}))