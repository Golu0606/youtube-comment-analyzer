import re
import requests
import os
from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from textblob import TextBlob
from collections import Counter

app = Flask(__name__)

# Load YouTube API key from environment variable
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

def extract_video_id(youtube_url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None

def get_video_comments(video_id, max_results=100):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=max_results
    )
    response = request.execute()

    for item in response.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)

    return comments

def analyze_sentiment(comments):
    sentiments = []
    for comment in comments:
        analysis = TextBlob(comment)
        sentiment_score = analysis.sentiment.polarity
        sentiment = "Neutral"
        if sentiment_score > 0:
            sentiment = "Positive"
        elif sentiment_score < 0:
            sentiment = "Negative"
        sentiments.append(sentiment)

    sentiment_summary = Counter(sentiments)
    return sentiment_summary

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    youtube_url = data.get("youtube_url")
    if not youtube_url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    comments = get_video_comments(video_id)
    if not comments:
        return jsonify({"message": "No comments found"}), 200

    sentiment_summary = analyze_sentiment(comments)
    return jsonify({
        "Total Comments": len(comments),
        "Sentiment Summary": sentiment_summary
    })

@app.route('/')
def home():
    return "Flask YouTube Comment Analyzer is Running!"

if __name__ == '__main__':
    app.run(debug=True)
