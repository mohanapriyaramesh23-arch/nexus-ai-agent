import os
import re
import requests
from typing import Dict, Any

def scrape_web_page(query: str) -> Dict[str, Any]:
    """
    Extracts a valid target HTTP/HTTPS URL from conversational input strings
    and returns parsed text context.
    """
    print(f"[WEB_SCRAPER] Targeting input string: '{query}'")
    
    # Extract the actual URL from the query string using a regex pattern match
    url_match = re.search(r'(https?://[^\s]+)', query)
    if not url_match:
        print("[WEB_SCRAPER_ERROR] No valid URL found inside the query string.")
        return {
            "source_type": "web",
            "results": [{"content": "Error: A valid URL starting with http:// or https:// must be provided.", "source_info": "Input Validation Fault"}]
        }
        
    target_url = url_match.group(1).strip(")'\",.")
    print(f"[WEB_SCRAPER] Isolated target URL: '{target_url}'")
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(target_url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # Pull text context from the page response (lean fallback variant)
        text_content = response.text[:1500]  
        
        return {
            "source_type": "web",
            "results": [{
                "content": text_content.strip(),
                "source_info": f"Live Web Link Extraction: {target_url}"
            }]
        }
    except Exception as e:
        print(f"[WEB_SCRAPER_ERROR] Connection failed: {e}")
        return {
            "source_type": "web",
            "results": [{"content": f"Failed to connect or download page data from link source: {str(e)}", "source_info": "Network Fault"}]
        }