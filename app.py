import os
import pandas as pd
from ddgs import DDGS
from groq import Groq

# 1. Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
NICHE_KEYWORD = "SaaS growth"

def find_target_questions(niche):
    print(f"Searching web for top Quora & Reddit threads on: {niche}...")
    results = []
    
    try:
        ddgs = DDGS()
        for site in ["quora.com", "reddit.com"]:
            query = f"site:{site} {niche}"
            try:
                search_results = ddgs.text(query, max_results=3)
                if search_results:
                    for item in search_results:
                        results.append({
                            "Platform": "Quora" if "quora.com" in item.get('href', '') else "Reddit",
                            "Title": item.get('title', 'No Title'),
                            "URL": item.get('href', ''),
                            "Snippet": item.get('body', '')
                        })
            except Exception as e:
                print(f"Error searching {site}: {e}")
    except Exception as e:
        print(f"DDGS Initialization Error: {e}")
                
    return results

def generate_ai_answer(question_title, platform):
    if not GROQ_API_KEY:
        return "Groq API Key not found. Please set it in GitHub Secrets."
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
        Write an expert, high-value {platform} answer responding to the question: "{question_title}"
        
        CRITICAL STRUCTURE RULES FOR AI & SEARCH OPTIMIZATION:
        1. Direct Answer: Start with 1-2 conclusive, clear opening sentences.
        2. Framework: Provide a 3-bullet point breakdown of the core strategy.
        3. E-E-A-T Signal: Include first-person language ("In my experience testing X...").
        4. Call-to-Action: End with a professional closing note.
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq Generation Error: {e}"

if __name__ == "__main__":
    threads = find_target_questions(NICHE_KEYWORD)
    print(f"Found {len(threads)} target threads.")
    
    if len(threads) == 0:
        print("No threads found. Attempting generic query...")
        try:
            ddgs = DDGS()
            fallback = ddgs.text("SaaS marketing strategy reddit", max_results=2)
            if fallback:
                for item in fallback:
                    threads.append({
                        "Platform": "Reddit",
                        "Title": item.get('title', 'SaaS Growth Strategy'),
                        "URL": item.get('href', ''),
                        "Snippet": item.get('body', '')
                    })
        except Exception as e:
            print(f"Fallback search error: {e}")

    if not threads:
        # Guarantee execution even if search is completely blocked/throttled
        threads = [{
            "Platform": "Reddit",
            "Title": "What are the best SaaS growth strategies for 2026?",
            "URL": "https://reddit.com/r/SaaS",
            "Snippet": "Looking for scalable SaaS growth channels."
        }]

    for i, thread in enumerate(threads[:2]):
        print(f"\n--- Processing Thread {i+1}: {thread['Title']} ---")
        print(f"URL: {thread['URL']}")
        draft = generate_ai_answer(thread['Title'], thread['Platform'])
        print("\nAI Generated Draft:\n", draft)
