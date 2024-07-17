import pandas as pd
import os


class PostedManager:
    def __init__(self, posted_file):
        self.posted_file = posted_file
        self.posted_ids = self.load_posted_ids()

    def load_posted_ids(self):
        try:
            if os.path.exists(self.posted_file):
                df = pd.read_csv(self.posted_file)
                if 'post_id' in df.columns:
                    return df['post_id'].tolist()
                else:
                    return []
            else:
                return []
        except pd.errors.EmptyDataError:
            print(f"Warning: {self.posted_file} is empty. Initializing with an empty list.")
            return []
        except Exception as e:
            print(f"Error loading {self.posted_file}: {str(e)}")
            return []

    def is_posted(self, post_id):
        return post_id in self.posted_ids

    def add_posted_id(self, post_id):
        if post_id not in self.posted_ids:
            try:
                with open(self.posted_file, 'a') as f:
                    f.write(f"{post_id}\n")
                self.posted_ids.append(post_id)
                print(f"Added {post_id} to {self.posted_file}")
            except Exception as e:
                print(f"Error adding {post_id} to {self.posted_file}: {str(e)}")

