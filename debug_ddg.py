
from duckduckgo_search import DDGS

def test_ddg(topic):
    print(f"Searching for: {topic} news india sports")
    search_context = ""
    try:
        with DDGS() as ddgs:
            # Search for news related to the topic
            results = list(ddgs.text(f"{topic} news india sports", max_results=5))
            if results:
                print("FOUND RESULTS:", len(results))
                search_context = "HERE ARE THE LATEST REAL-WORLD SEARCH RESULTS (USE THESE FACTS ONLY):\n\n"
                for i, res in enumerate(results):
                    search_context += f"Source {i+1}: {res.get('title')}\nSummary: {res.get('body')}\nLink: {res.get('href')}\n\n"
                print(search_context)
            else:
                print("No direct search results found.")
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")

test_ddg('Kohli Playing Domestic Cricket')
