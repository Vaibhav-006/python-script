from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import sys
import json
import requests
from urllib.parse import urlparse, parse_qs
import re

def get_video_id(url):
    try:
        # More comprehensive URL pattern matching
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',
            r'youtube\.com\/embed\/([^&\n?]+)',
            r'youtube\.com\/v\/([^&\n?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    except Exception:
        return None

def is_video_available(video_id):
    try:
        # Try to access video info through YouTube's oEmbed API
        response = requests.get(f'https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json')
        return response.status_code == 200
    except Exception:
        return False

def get_transcript(url, language='en'):
    try:
        # Validate URL format
        if not url or not isinstance(url, str):
            return {"success": False, "error": "Invalid URL format"}

        # Extract video ID
        video_id = get_video_id(url)
        if not video_id:
            return {"success": False, "error": "Invalid YouTube URL format"}

        # Check if video is available
        if not is_video_available(video_id):
            return {"success": False, "error": "Video is unavailable or restricted"}

        # Get available transcripts
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except TranscriptsDisabled:
            return {"success": False, "error": "Transcripts are disabled for this video"}
        except NoTranscriptFound:
            return {"success": False, "error": "No transcript found for this video"}
        except Exception as e:
            return {"success": False, "error": f"Could not access video transcripts: {str(e)}"}

        # Try to get transcript in requested language
        try:
            transcript = transcript_list.find_transcript([language])
            return {
                "success": True,
                "transcript": transcript.fetch(),
                "language": language,
                "video_id": video_id
            }
        except:
            # If requested language not available, try to get English transcript
            try:
                transcript = transcript_list.find_transcript(['en'])
                return {
                    "success": True,
                    "transcript": transcript.fetch(),
                    "language": "en",
                    "video_id": video_id
                }
            except:
                # If no English transcript, get the first available transcript
                try:
                    transcript = transcript_list.find_transcript()
                    return {
                        "success": True,
                        "transcript": transcript.fetch(),
                        "language": transcript.language_code,
                        "video_id": video_id
                    }
                except:
                    return {"success": False, "error": "No transcripts available for this video"}

    except Exception as e:
        return {"success": False, "error": f"Error fetching transcript: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Please provide a YouTube URL"}))
        sys.exit(1)
    
    url = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'en'
    result = get_transcript(url, language)
    print(json.dumps(result)) 