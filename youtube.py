import re

from googleapiclient.discovery import build

api_key = "AIzaSyCvkVurZfm9j_FV-J2laLJAl02g-2nJFr8"
youtube_api = build("youtube", "v3", developerKey=api_key)


# Extract video ID from URL within text
def extract_video_id(text):
    # Enhanced regex that matches URLs embedded in a longer text
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\s*[^\/\n\s]+\/|(?:v|e(?:mbed)?)\/|\S*?[^\/\n\s]\/)?|youtu\.be\/)([a-zA-Z0-9_-]{11})"
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
