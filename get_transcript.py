from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import sys
import json
import requests
from urllib.parse import urlparse, parse_qs
import re
from typing import Dict, Any, Optional

class TranscriptError(Exception):
    """Base exception for transcript-related errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class InvalidURLError(TranscriptError):
    """Raised when the YouTube URL is invalid"""
    def __init__(self, message: str = "Invalid YouTube URL format"):
        super().__init__(message, 400)

class VideoUnavailableError(TranscriptError):
    """Raised when the video is unavailable"""
    def __init__(self, message: str = "Video is unavailable or restricted"):
        super().__init__(message, 404)

class TranscriptsDisabledError(TranscriptError):
    """Raised when transcripts are disabled for the video"""
    def __init__(self, message: str = "Transcripts are disabled for this video"):
        super().__init__(message, 403)

class NoTranscriptFoundError(TranscriptError):
    """Raised when no transcript is found"""
    def __init__(self, message: str = "No transcript found for this video"):
        super().__init__(message, 404)

def get_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats
    """
    try:
        if not url or not isinstance(url, str):
            raise InvalidURLError("URL must be a non-empty string")

        # More comprehensive URL pattern matching
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',
            r'youtube\.com\/embed\/([^&\n?]+)',
            r'youtube\.com\/v\/([^&\n?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                if not video_id or len(video_id) != 11:  # YouTube video IDs are 11 characters
                    raise InvalidURLError("Invalid YouTube video ID format")
                return video_id
                
        raise InvalidURLError("Could not extract video ID from URL")
    except TranscriptError:
        raise
    except Exception as e:
        raise InvalidURLError(f"Error processing URL: {str(e)}")

def is_video_available(video_id):
    try:
        # Try to access video info through YouTube's oEmbed API
        response = requests.get(f'https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json')
        return response.status_code == 200
    except Exception:
        return False

def get_transcript(url: str, language: str = 'en') -> Dict[str, Any]:
    """
    Get transcript for a YouTube video
    """
    try:
        # Extract video ID
        video_id = get_video_id(url)
        
        # Get available transcripts
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except TranscriptsDisabled:
            raise TranscriptsDisabledError()
        except NoTranscriptFound:
            raise NoTranscriptFoundError()
        except Exception as e:
            raise TranscriptError(f"Could not access video transcripts: {str(e)}", 500)

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
                    raise NoTranscriptFoundError("No transcripts available for this video")

    except TranscriptError:
        raise
    except Exception as e:
        raise TranscriptError(f"Unexpected error: {str(e)}", 500)

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise InvalidURLError("Please provide a YouTube URL")
        
        url = sys.argv[1]
        language = sys.argv[2] if len(sys.argv) > 2 else 'en'
        result = get_transcript(url, language)
        print(json.dumps(result))
    except TranscriptError as e:
        print(json.dumps({
            "success": False,
            "error": e.message,
            "status_code": e.status_code
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "status_code": 500
        }))
        sys.exit(1) 