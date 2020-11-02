import argparse
import os
import numpy as np
import pandas as pd
import requests
from random import randint
from scrape import StatsTable

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--page',
        type=int,
        default=1000,
        help='Total pages that will be scraped (default number is 100)',
        metavar=''
    )
    args = parser.parse_args()
    st = StatsTable()
    max_page = st.max_page()
    if os.path.exists('data/stats-table/stats-table-0.csv'): # first data start from *-0.csv
        existing = st.read_data()
    i = 0
    df = pd.DataFrame([])
    while i < args.page:
        page = randint(1, max_page)
        df = df.append(st.stats_table(page))
        i += 1
    try:
        df = pd.concat([df, existing], sort=False)
        df = df.drop_duplicates(subset=['url'])
        total_df = int(len(df) / 50000)
        dfs = np.array_split(df, total_df)
        [dfs[i].to_csv(f'data/stats-table/stats-table-{i}.csv', index=False) for i in range(len(dfs))]
    except UnboundLocalError:
        df = df.drop_duplicates(subset=['url'])
        df.to_csv('data/stats-table/stats-table-0.csv', index=False)

if __name__ == "__main__":
    main()
