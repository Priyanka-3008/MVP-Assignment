from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error: {e}")
        return None

def format_transcript(transcript):
    formatter = SRTFormatter()
    return formatter.format_transcript(transcript)

# Example usage
video_url = 'https://www.youtube.com/watch?v=2lAe1cqCOXo'
video_id = video_url.split('v=')[-1].split('&')[0]  # Extract video ID from the URL
transcript = get_transcript(video_id)
if transcript:
    formatted_transcript = format_transcript(transcript)
    print("Transcript:\n", formatted_transcript)
else:
    print("Transcript not available.")
