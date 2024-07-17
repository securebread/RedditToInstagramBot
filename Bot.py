import threading

import InstagramPoster
import RedditPostChecker

subreddit_names = ['your', 'subreddits', 'here']
data_file = 'downloaded_posts.csv'
posted_file = 'posted.csv'

instagram_username = 'insta username'
instagram_password = 'insta password'

client_id = 'reddit bot client id'
client_secret = 'reddit client secret'
user_agent = 'reddit user agent'

threads = []

instagram_poster = InstagramPoster.main(instagram_username, instagram_password)
thread_instagram_post = threading.Thread(target=instagram_poster.main)
threads.append(thread_instagram_post)

reddit_post_checkers = []
for subreddit_name in subreddit_names:
    reddit_post_checker = RedditPostChecker.postChecker(data_file, subreddit_name, client_id, client_secret, user_agent)
    reddit_post_checkers.append(reddit_post_checker)

for reddit_post_checker in reddit_post_checkers:
    thread_reddit_scrape = threading.Thread(target=reddit_post_checker.scrape_subreddit())
    thread_reddit_download_new = threading.Thread(target=reddit_post_checker.start_periodic_check())
    threads.append(thread_reddit_scrape)
    threads.append(thread_reddit_download_new)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
