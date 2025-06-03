import requests
import time
import os

# File to store last tweet ID
LAST_ID_FILE = "last_id.txt"

def load_last_tweet_id():
	if os.path.exists(LAST_ID_FILE):
		with open(LAST_ID_FILE, 'r') as f:
			return f.read().strip()
	return None

def save_last_tweet_id(tweet_id):
	with open(LAST_ID_FILE, 'w') as f:
		f.write(str(tweet_id))

# === CONFIG ===
TWITTER_USERNAME = 'coinheadline' # Change to the Twitter user you want to track
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAGPU2AEAAAAAfgPPdwvqyxJ9%2BfcpC0YkbbFBQ1w%3DiMDIArVobqpFwnTFzguHHqjgDRjk1s7v0BhJRekQo4ZRXz5EWX'
TELEGRAM_BOT_TOKEN = '7616941891:AAHR_S8OV8AY7T1GalADHy1LJIYus9s0kh0'
TELEGRAM_CHAT_ID = '@coinheadlines' # Or numeric chat ID
LAST_TWEET_ID = load_last_tweet_id()

def get_latest_tweet():
	url = f"https://api.twitter.com/2/users/by/username/{TWITTER_USERNAME}"
	headers = {
	"Authorization": f"Bearer {BEARER_TOKEN}"
	}

	# Step 1: Get user ID from username
	response = requests.get(url, headers=headers)
	user_data = response.json()
	if 'data' not in user_data:
		print("Failed to get user data:", response.text)
		return None
	user_id = user_data['data']['id']

	# Step 2: Get recent tweets by user ID
	tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5"
	response = requests.get(tweets_url, headers=headers)
	print("Twitter API status:", response.status_code)
	print("Twitter response body:", response.text)

	if response.status_code == 429:
		print("Rate limit hit. Waiting 5 minutes before retrying...")
		time.sleep(300)
		return None

	tweets = response.json().get('data', [])
	if tweets:
		return tweets[0]
	return None

def send_to_telegram(message):
	url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
	payload = {
	"chat_id": TELEGRAM_CHAT_ID,
	"text": message,
	"parse_mode": "HTML"
	}
	requests.post(url, json=payload)

# === MAIN LOOP ===
print("Bot is running...")
while True:
	try:
		tweet = get_latest_tweet()
		if tweet:
			tweet_id = tweet['id']
			tweet_text = tweet['text']
			tweet_url = f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet_id}"
			if tweet_id != LAST_TWEET_ID:
				send_to_telegram(f"New tweet by @{TWITTER_USERNAME}:\n{tweet_text}\n\n{tweet_url}")
				save_last_tweet_id(tweet_id)
			LAST_TWEET_ID = tweet_id
		time.sleep(60) # Check every 60 seconds
	except Exception as e:
		print(f"Error: {e}")
		time.sleep(60)