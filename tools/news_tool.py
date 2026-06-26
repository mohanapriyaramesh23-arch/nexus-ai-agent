import os
import requests
from typing import Dict, Any

def fetch_live_news(query: str) -> Dict[str, Any]:
    """
    Queries NewsAPI for current live global events regarding a target topic string.
    Returns data matching the unified tool interface schema.
    """
    print(f"\n[NEWS_TOOL] Searching active news wires for: '{query}'")
    api_key = os.getenv("NEWS_API_KEY")
    
    if not api_key:
        print("[NEWS_TOOL_ERROR] Missing 'NEWS_API_KEY' in environment variables.")
        return {
            "source_type": "news",
            "results": [{"content": "Error: News API Key is missing from system configurations.", "source_info": "Config Failure"}]
        }
        
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "pageSize": 3,  # Return the top 3 snapshot matches
        "apiKey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get("message", "Unknown API Error")
            print(f"[NEWS_TOOL_ERROR] NewsAPI returned fault: {error_msg}")
            return {
                "source_type": "news",
                "results": [{"content": f"NewsAPI Fault: {error_msg}", "source_info": "API Response Error"}]
            }
            
        articles = data.get("articles", [])
        if not articles:
            return {
                "source_type": "news",
                "results": [{"content": f"No recent news articles found matching target query: '{query}'", "source_info": "Zero Matches"}]
            }
            
        formatted_news = []
        for index, art in enumerate(articles, start=1):
            title = art.get("title", "No Title")
            source_name = art.get("source", {}).get("name", "Unknown Source")
            description = art.get("description") or art.get("content") or "No description provided."
            art_url = art.get("url", "")
            
            payload_text = f"Headline: {title}\nSource: {source_name}\nSummary: {description}\nLink: {art_url}"
            formatted_news.append({
                "content": payload_text.strip(),
                "source_info": f"Live News Feed Entry #{index}"
            })
            
        return {
            "source_type": "news",
            "results": formatted_news
        }
        
    except Exception as e:
        print(f"[NEWS_TOOL_ERROR] Network extraction failure: {e}")
        return {
            "source_type": "news",
            "results": [{"content": f"News service failed: {str(e)}", "source_info": "System Fault"}]
        }