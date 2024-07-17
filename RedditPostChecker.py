import os
import random
import threading
import time
import pandas as pd
import praw
import requests
import schedule

import PostIf


class postChecker:
    def __init__(self, data_file, subreddits, client_id, client_secret, user_agent):
        self.reddit = self.authenticate(client_id, client_secret, user_agent)
        self.subreddit_name = subreddits
        self.data_file = data_file
        self.downloaded_manager = PostIf.PostedManager(data_file)
        self.downloaded_posts = self.load_downloaded_posts()
        self.downloaded_ids = self.load_downloaded_ids()
        print("initialized post checker")

    @staticmethod
    def authenticate(client_id, client_secret, user_agent):
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                             user_agent=user_agent)
        return reddit

    def load_downloaded_posts(self):
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            return pd.DataFrame(columns=['post_id', 'title', 'url'])

        try:
            return pd.read_csv(self.data_file)
        except pd.errors.EmptyDataError:
            print(f"Warning: {self.data_file} is empty or has no columns to parse.")
            return pd.DataFrame(columns=['post_id', 'title', 'url'])

    def load_downloaded_ids(self):
        try:
            if os.path.exists(self.data_file) and os.stat(self.data_file).st_size > 0:
                df = pd.read_csv(self.data_file)
                if 'post_id' in df.columns:
                    return df['post_id'].tolist()
                else:
                    print(
                        f"Warning: 'post_id' column not found in {self.data_file}. Initializing with an empty list.")
                    return []
            else:
                print(f"Warning: {self.data_file} is empty or does not exist. Initializing with an empty list.")
                return []
        except pd.errors.EmptyDataError:
            print(f"Warning: {self.data_file} is empty. Initializing with an empty list.")
            return []
        except Exception as e:
            print(f"Error loading {self.data_file}: {str(e)}")
            return []

    def scrape_subreddit(self):
        print("Scraping subreddit")
        subreddit = self.reddit.subreddit(self.subreddit_name)
        for submission in subreddit.top('all', limit=100):
            if submission.id not in self.downloaded_posts['post_id'].values:
                if not self.is_downloaded(submission.id):
                    self.download_post(submission)

    def check_and_download_new_posts(self):
        print("Checking and downloading posts")
        subreddit = self.reddit.subreddit(self.subreddit_name)
        for submission in subreddit.hot(limit=10):
            if submission.id not in self.downloaded_posts['post_id'].values:
                if not self.is_downloaded(submission.id):
                    self.download_post(submission)

    def download_post(self, submission):
        try:
            if submission.url.endswith(('jpg', 'jpeg')):
                image_url = submission.url
                image_data = requests.get(image_url).content

                image_path = f"images/{submission.id}.jpg"
                with open(image_path, 'wb') as f:
                    f.write(image_data)

                new_entry = pd.DataFrame({
                    'post_id': [submission.id],
                    'title': [submission.title],
                    'url': [submission.url],
                    'image_path': [image_path]
                })
                self.downloaded_posts = pd.concat([self.downloaded_posts, new_entry], ignore_index=True)
                self.downloaded_posts.to_csv(self.data_file, index=False)

                print(f"Downloaded post {submission.id}: {submission.title}")
            else:
                print(f"Post {submission.id} is not an image. Skipping.")

        except Exception as e:
            print(f"Error downloading post {submission.id}: {str(e)}")

    def start_periodic_check(self):
        print("Starting periodic check")
        times = 12 * 60 * 60 + random.uniform(-4312, 1232)
        times2 = times / 60 / 60
        times3 = times % 60 % 60
        print("started timer for" + str(times2) + " hours" + str(times3) + " min")
        schedule.every(int(times)).minutes.do(self.check_and_download_new_posts)
        time.sleep(times)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def is_downloaded(self, post_id):
        return post_id in self.downloaded_ids

    def mark_downloaded(self, post_id):
        self.downloaded_ids.append(post_id)
        pd.DataFrame({'post_id': self.downloaded_ids}).to_csv(self.data_file, index=False)
        print(f"Marked post {post_id} as downloaded.")

    
