import feedparser
import pandas as pd
from textblob import TextBlob
import os
import time

# 1. LIVE COMPREHENSIVE ENDPOINTS
rss_feeds = [
    {"field": "Technology", "source": "Google Tech", "url": "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en"},
    {"field": "Business", "source": "Google Biz", "url": "https://news.google.com/rss/search?q=business&hl=en-US&gl=US&ceid=US:en"},
    {"field": "Politics", "source": "Google Politics", "url": "https://news.google.com/rss/search?q=politics&hl=en-US&gl=US&ceid=US:en"},
    {"field": "World", "source": "CNN World", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"field": "Science", "source": "Google Science", "url": "https://news.google.com/rss/search?q=science&hl=en-US&gl=US&ceid=US:en"}
]

# Path to your dataset file inside PythonAnywhere
csv_filename = "live_news_dataset.csv"

def fetch_and_update_news():
    print(f"⚡ [{time.strftime('%Y-%m-%d %H:%M:%S')}] Executing Scheduled AI News Collection...")
    
    # Load existing file if it exists, otherwise start fresh
    if os.path.exists(csv_filename):
        try:
            existing_df = pd.read_csv(csv_filename)
            existing_headlines = set(existing_df["Headline"].astype(str).tolist())
        except Exception:
            existing_df = pd.DataFrame(columns=["Headline", "Summary", "Field", "Source", "Sentiment", "Timestamp"])
            existing_headlines = set()
    else:
        existing_df = pd.DataFrame(columns=["Headline", "Summary", "Field", "Source", "Sentiment", "Timestamp"])
        existing_headlines = set()

    new_rows = []

    # Loop through RSS channels
    for target in rss_feeds:
        field = target["field"]
        source = target["source"]
        url = target["url"]
        
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                headline = entry.get('title', '').strip()
                summary = entry.get('summary', '').strip()
                published = entry.get('published', time.strftime('%Y-%m-%d %H:%M:%S'))
                
                # Check for duplicates
                if headline not in existing_headlines and headline != '':
                    
                    # Sentiment Analysis Engine
                    analysis = TextBlob(headline)
                    polarity = analysis.sentiment.polarity
                    
                    if polarity > 0.0:
                        sentiment = "Good"
                    elif polarity < 0.0:
                        sentiment = "Bad"
                    else:
                        sentiment = "Neutral"
                    
                    new_rows.append({
                        "Headline": headline,
                        "Summary": summary,
                        "Field": field,
                        "Source": source,
                        "Sentiment": sentiment,
                        "Timestamp": published
                    })
                    existing_headlines.add(headline)
                    
        except Exception as e:
            print(f"⚠️ Error reading {source}: {e}")
            continue

    # Append and save updates
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        updated_df.to_csv(csv_filename, index=False)
        print(f"🎉 Success! Added {len(new_rows)} brand new stories.")
        print(f"📊 Total Dataset Volume: {len(updated_df)} rows.")
    else:
        print("💤 Scan complete. No new articles posted since last run.")

# Run the collection function exactly once
if __name__ == "__main__":
    fetch_and_update_news()