import argparse
import os
import numpy as np
import pandas as pd
from random import randint
from scrape import Post

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--post',
        type=int,
        default=1000,
        help='Total posts that will be scraped (default is 100)',
        metavar=''
    )
    args = parser.parse_args()
    post = Post()
    urls = post.read_data('stats-table')
    urls = urls.url.to_list()
    if os.path.exists('data/post/post-0.csv'): # first data start from *-0.csv
        existing = post.read_data('post')
    i = 0
    df = pd.DataFrame([])
    while i < args.post:
        u = randint(0, len(urls))
        df = df.append(post.get_post(urls[u]))
        i += 1
    try:
        df = pd.concat([df, existing], sort=False)
        df = df.drop_duplicates()
        total_df = int(len(df) / 50000)
        dfs = np.array_split(df, total_df)
        [dfs[i].to_csv(f'data/post/post-{i}.csv', index=False) for i in range(len(dfs))]
    except UnboundLocalError:
        df = df.drop_duplicates()
        df.to_csv('data/post/post-0.csv', index=False)

if __name__ == "__main__":
    main()
