import re
from typing import Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi

def _extract_video_id(url: str) -> str:
    """
    Helper function using regular expressions to safely extract the 11-character 
    YouTube video ID from standard URLs, shared shorts, or embed links.
    """
    patterns = [
        r"(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/shorts\/|^)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""

def get_youtube_transcript(url: str) -> Dict[str, Any]:
    """
    Extracts the transcript of a target YouTube video link and returns 
    the parsed output matching our unified tool interface schema.
    """
    print(f"\n[YOUTUBE_TOOL] Processing target URL: '{url}'")
    video_id = _extract_video_id(url)
    
    if not video_id:
        print("[YOUTUBE_TOOL] Refused: Failed to parse a valid 11-character Video ID.")
        return {
            "source_type": "youtube",
            "results": [{"content": "Error: Invalid or malformed YouTube link format.", "source_info": "URL Parser"}]
        }
        
    try:
        print(f"[YOUTUBE_TOOL] Fetching active transcript tracks for ID: {video_id}...")
        
        # Instantiate the client explicitly
        client = YouTubeTranscriptApi()
        
        # Fetch the transcript object records
        transcript_list = client.fetch(video_id)
        
        # Collate subtitle records using direct object attributes instead of dictionary getters
        full_transcript_text = ""
        for entry in transcript_list:
            start_seconds = int(getattr(entry, 'start', 0))
            minutes = start_seconds // 60
            seconds = start_seconds % 60
            timestamp_label = f"[{minutes:02d}:{seconds:02d}]"
            
            text_snippet = getattr(entry, 'text', '')
            full_transcript_text += f"{timestamp_label} {text_snippet} "
            
        return {
            "source_type": "youtube",
            "results": [{
                "content": full_transcript_text.strip(),
                "source_info": f"YouTube Video Stream - ID: {video_id}"
            }]
        }
        
    except Exception as e:
        print(f"[YOUTUBE_TOOL_ERROR] Transcript extraction dropped: {e}")
        return {
            "source_type": "youtube",
            "results": [{
                "content": f"Could not retrieve video transcript. Reason: {str(e)}",
                "source_info": f"YouTube Error Log - ID: {video_id}"
            }]
        }