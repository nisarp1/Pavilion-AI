
import requests
import feedparser
from urllib.parse import quote_plus

def test_rss(topic):
    print(f"Testing topic: {topic}")
    
    encoded_topic = quote_plus(topic)
    url = f"https://news.google.com/rss/search?q={encoded_topic}+sports+when:24h&hl=en&gl=IN&ceid=IN:en"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, */*',
        'Referer': 'https://news.google.com/'
    }
    
    print(f"URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to get 200 OK")
            print(response.text[:200])
            return

        # Check if it looks like XML
        content_preview = response.content[:100]
        print(f"Content Start: {content_preview}")
        
        feed = feedparser.parse(response.content)
        print(f"Entries found: {len(feed.entries)}")
        
        if len(feed.entries) > 0:
            print("First Entry Title:", feed.entries[0].title)
            print("First Entry Link:", feed.entries[0].link)
        else:
            print("NO ENTRIES found.")
            if b'<!DOCTYPE html>' in response.content:
                print("It looks like HTML (probably a block/consent page)")
                
    except Exception as e:
        print(f"Exception: {e}")

test_rss("India Cricket")
