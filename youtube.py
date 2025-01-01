import re
from googleapiclient.discovery import build

# Read the API key from the credentials file
with open("credentials/youtube.key", "r") as key_file:
    api_key = key_file.read().strip()

youtube_api = build("youtube", "v3", developerKey=api_key)


# Extract video ID from URL within text
def extract_video_id(text):
    # Enhanced regex that matches URLs embedded in a longer text
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|\S*?[^\/\n\s]\/)?|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, text)
    return match.group(1) if match else None


# Get video duration from API
def get_video_duration(text):
    video_id = extract_video_id(text)

    if not video_id:
        return "Invalid or missing YouTube URL"

    response = youtube_api.videos().list(part="contentDetails", id=video_id).execute()

    if not response["items"]:
        return "Video not found"

    duration = response["items"][0]["contentDetails"]["duration"]
    return duration


def parse_youtube_duration(duration_str):
    """
    Convert a YouTube duration string (e.g. 'PT1H25M7S') into a human-readable format (e.g. '1:25:07').
    """
    import re

    hours, minutes, seconds = 0, 0, 0
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if match:
        h, m, s = match.groups()
        hours = int(h) if h else 0
        minutes = int(m) if m else 0
        seconds = int(s) if s else 0

    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes}:{seconds:02}"


def get_youtube_video_info(text):
    """
    Extract video ID from the provided text and fetch additional details from the YouTube API.
    Returns a dictionary with keys: 'video_id', 'title', 'channel', 'duration', and 'thumbnail'.
    If no valid video is found, returns None.
    """
    video_id = extract_video_id(text)
    if not video_id:
        return None

    response = (
        youtube_api.videos().list(part="snippet,contentDetails", id=video_id).execute()
    )
    items = response.get("items", [])
    if not items:
        return None

    video_data = items[0]
    snippet = video_data.get("snippet", {})
    content_details = video_data.get("contentDetails", {})
    thumbnails = snippet.get("thumbnails", {})
    default_thumb = thumbnails.get("medium") or thumbnails.get("default") or {}

    return {
        "video_id": video_id,
        "title": snippet.get("title", ""),
        "channel": snippet.get("channelTitle", ""),
        "duration": parse_youtube_duration(content_details.get("duration", "")),
        "thumbnail": default_thumb.get("url", ""),
    }
