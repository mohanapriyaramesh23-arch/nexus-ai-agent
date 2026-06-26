import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def scrape_web_page(url: str) -> Dict[str, Any]:
    """
    Fetches a web page and parses its main text contents using BeautifulSoup.
    Returns data matching the unified tool interface schema.
    """
    print(f"\n[WEB_SCRAPER] Targeting URL: '{url}'")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[WEB_SCRAPER_ERROR] Received non-200 status code: {response.status_code}")
            return {
                "source_type": "web",
                "results": [{"content": f"Error: Unable to reach page. HTTP Status {response.status_code}", "source_info": url}]
            }
            
        # Verify content is actually HTML text
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            print(f"[WEB_SCRAPER_ERROR] Rejected non-HTML content type: {content_type}")
            return {
                "source_type": "web",
                "results": [{"content": "Error: Target URL did not return HTML text content.", "source_info": url}]
            }
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Strip script, style, and navigation tags to keep clean text
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.extract()
            
        # Extract paragraph text strings
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip()]
        cleaned_text = "\n\n".join(paragraphs)
        
        if not cleaned_text:
            # Fallback to general body text if no paragraph tags were used
            cleaned_text = soup.get_text(separator="\n", strip=True)
            
        return {
            "source_type": "web",
            "results": [{
                "content": cleaned_text[:4000],  # Protect window context size from massive dumps
                "source_info": f"Live Web Scrape - {url}"
            }]
        }
        
    except Exception as e:
        print(f"[WEB_SCRAPER_ERROR] Connection failed: {e}")
        return {
            "source_type": "web",
            "results": [{"content": f"Scraper execution error: {str(e)}", "source_info": url}]
        }