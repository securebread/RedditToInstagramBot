import csv
import random
import time
from instagrapi import Client
import pandas as pd
import os


def read_posts_from_csv(csv_file):
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)


def read_posted_ids(csv_file):
    print("reading id's to post")
    try:
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            if 'post_id' in df.columns:
                return df['post_id'].tolist()
            else:
                return []
        else:
            return []
    except pd.errors.EmptyDataError:
        print(f"Warning: {csv_file} is empty. Initializing with an empty list.")
        return []
    except Exception as e:
        print(f"Error loading {csv_file}: {str(e)}")
        return []


def write_posted_id(csv_file, post_id):
    if post_id not in csv_file:
        try:
            with open(csv_file, 'a') as f:
                f.write(f"\n{post_id}")
            print(f"Added {post_id} to {csv_file}")
        except Exception as e:
            print(f"Error adding {post_id} to {csv_file}: {str(e)}")


def get_hashtags(csv_file, min_count=7, max_count=12):
    print("reading # to post")
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            hashtags = [row[0].strip() for row in reader if row]  # Assuming hashtags are in the first column
    except FileNotFoundError:
        print(f"Error: File {csv_file} not found.")
        return []
    except Exception as e:
        print(f"Error reading {csv_file}: {str(e)}")
        return []

    if len(hashtags) < min_count:
        print(f"Warning: Insufficient hashtags found in {csv_file}. Need at least {min_count}.")
        return []

    num_hashtags = random.randint(min_count, max_count)
    selected_hashtags = random.sample(hashtags, num_hashtags)

    return selected_hashtags


def hashTagsToString(cvs_hashtags):
    hashtags = ""
    for hashtag in get_hashtags(cvs_hashtags):
        hashtags += hashtag

    return hashtags


def main(username, password):

    client = Client()
    client.login(username, password)

    posts_file = 'downloaded_posts.csv'
    posted_file = 'posted.csv'

    posts = read_posts_from_csv(posts_file)
    posted_ids = read_posted_ids(posted_file)

    for post in posts:
        post_id = post['post_id']
        if post_id in posted_ids:
            continue

        title = post['title']
        description = post['url']
        image_path = post['image_path']
        hashtags = hashTagsToString('hashtags.csv')
        try:
            client.photo_upload(image_path, caption=title + '\n\n' + hashtags + "\n\n" + description)
            write_posted_id(posted_file, post_id)
            print(f"Posted: {title}")
            times = 12 * 60 * 60 + random.uniform(-4312, 1232)
            times2 = times / 60 / 60
            times3 = times % 60 % 60
            print("started timer for" + str(times2) + " hours" + str(times3) + " min")
            time.sleep(times)
        except Exception as e:
            print(f"Error posting {title}: {str(e)}")
            continue
