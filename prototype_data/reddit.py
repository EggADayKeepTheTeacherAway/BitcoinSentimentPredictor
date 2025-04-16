import praw
import datetime
import csv

from dotenv import load_dotenv
import os

load_dotenv()

# Reddit API credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

subreddit_name = "bitcoin"  # Change this to any subreddit
num_posts = 10_000  # Target number of posts

data = []
count = 0

# Fetch posts from the subreddit (newest first)
subreddit = reddit.subreddit(subreddit_name)

for submission in subreddit.new(limit=None):  # limit=None fetches as many as possible
    if count >= num_posts:
        break  # Stop once we reach 10,000 posts

    data.append([
        submission.id,
        datetime.datetime.utcfromtimestamp(submission.created_utc),
        submission.url,
        submission.title,
        submission.score,
        submission.num_comments,
        submission.selftext,
        submission.upvote_ratio if hasattr(submission, 'upvote_ratio') else None,
    ])
    count += 1

# Save to CSV
with open("left_reddit_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ID", "Timestamp", "URL", "Title", "Score", "Comments", "Text", "Upvote Ratio"])
    writer.writerows(data)

print(f"Data written to reddit_data.csv with {count} posts.")
