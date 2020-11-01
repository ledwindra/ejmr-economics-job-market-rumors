import glob
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
import seaborn as sns
import statistics
import string
import warnings
from datetime import datetime, timedelta
from nltk.corpus import stopwords

font_manager._rebuild()
plt.xkcd()
nltk.download('stopwords', quiet=True)
warnings.filterwarnings('ignore')

def read_data(data):
    list_data = glob.glob(f'data/{data}/{data}-*.csv')
    data = []
    for l in list_data:
        df = pd.read_csv(l)
        data.append(df)
    df = pd.concat(data, sort=False)
    
    return df

def tokenize_word():
    df = read_data('stats-table')
    remove = 'https://www.econjobrumors.com/topic/'
    df['url'] = df.apply(lambda x: x['url'].replace(remove, ''), axis=1)
    word = df.url.to_list()
    word = [x.replace('-', ' ') for x in word]
    word = [x.split(' ') for x in word]
    data = []
    for i in word:
        for j in i:
            data.append(j)
    sw = stopwords.words('english')
    sw = sw + [x for x in string.digits]
    word = [x for x in data if x not in sw]

    return word

def top_five_word(word):
    df = pd.DataFrame(tokenize_word(), columns=['word'])
    df = df.groupby('word').size().to_frame().reset_index()
    df = df.sort_values(by=0, ascending=False)
    df = df.iloc[:5, :].reset_index(drop=True)
    df = df.rename(columns={0: 'count'})

    return df

def top_five_numeric(column):
    df = read_data('stats-table')
    df = df.sort_values(by=column, ascending=False)
    df = df.iloc[:5, :].reset_index(drop=True)
    
    return df

def bar_chart(df, height, label, title, column, img_title='', save=False):
    fig, ax = plt.subplots(figsize=(15, 5))
    opacity = 0.9
    ax.bar(
        df.index,
        height=height,
        width=0.5,
        data=df,
        alpha=opacity,
        color='black',
        label=label
    )
    plt.title(title)
    caption = lambda df, column: ' \n'.join([f'{df.index[x]}: {df[column][x]}' for x in range(len(df))])
    plt.xlabel(caption(df, column), loc='left')
    plt.ylabel('')
    plt.xticks(df.index)
    plt.yticks()
    ax.legend()
    if save:
        plt.savefig(f'img/{img_title}.png', bbox_inches = 'tight')
    plt.show()
    
def distributions(img_title='', save=False):
    # transform
    df = read_data('stats-table')
    df['log_posts'] = df.apply(lambda x: np.log(x['posts']), axis=1)
    df['log_views'] = df.apply(lambda x: np.log(x['views']), axis=1)
    
    # visualize
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))
    
    # must be > 0 otherwise error appears
    dist_data = lambda column: df[df[column] > 0][column]
    dist_plot = lambda data, color, rug_color, ax_loc: sns.distplot(
        data,
        hist=False,
        kde=True,
        rug=True,
        color=color,
        kde_kws={'shade': True, 'bw': 0.3},
        rug_kws={'color': rug_color},
        ax=ax_loc
    )
    dist_plot(dist_data('log_posts'), 'red', 'darkred', ax[0])
    dist_plot(dist_data('log_views'), 'blue', 'darkblue', ax[1])
    fig.suptitle('Distributions of threads\' posts and views')

    # show median values
    ax[0].axvline(statistics.median(df['log_posts']), color='red')
    ax[1].axvline(statistics.median(df['log_views']), color='blue')

    if save:
        plt.savefig(f'img/{img_title}.png', bbox_inches = 'tight')
    plt.show()
    
def relationship(img_title='', save=False):
    # transform
    df = read_data('stats-table')
    df['log_posts'] = df.apply(lambda x: np.log(x['posts'], where=x['posts'] > 0), axis=1)
    df['log_views'] = df.apply(lambda x: np.log(x['views'], where=x['views'] > 0), axis=1)
    
    # visualize
    fig, ax = plt.subplots(figsize=(15, 5))
    hb = ax.hexbin(x='log_views', y='log_posts', data=df, bins='log', gridsize=50, edgecolors='grey', cmap='inferno', mincnt=1)
    plt.title('Relationship between numbers of posts and views (no causality implied)')
    plt.xlabel('Log views')
    plt.ylabel('Log posts')
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('log10 of n')
    if save:
        plt.savefig(f'img/{img_title}.png', bbox_inches = 'tight')
    plt.show
    
def post_per_year(img_title='', save=False):
    # transform
    df = read_data('post')
    df['updated_at_utc'] = pd.to_datetime(df.updated_at_utc)
    df['posted_at'] = df.apply(lambda x: x['posted_at'].split(' '), axis=1)
    def posted_at_utc(x):
        if 'second' in x['posted_at'][1]:
            return x['updated_at_utc'] - timedelta(seconds=int(x['posted_at'][0]))
        elif 'minute' in x['posted_at'][1]:
            return x['updated_at_utc'] - timedelta(minutes=int(x['posted_at'][0]))
        elif 'hour' in x['posted_at'][1]:
            return x['updated_at_utc'] - timedelta(hours=int(x['posted_at'][0]))
        elif 'day' in x['posted_at'][1]:
            return x['updated_at_utc'] - timedelta(days=int(x['posted_at'][0]))
        elif 'week' in x['posted_at'][1]:
            return x['updated_at_utc'] - timedelta(days=7 * int(x['posted_at'][0]))
        elif 'month' in x['posted_at'][1]:
            return x['updated_at_utc'] - timedelta(days=30 * int(x['posted_at'][0]))
        elif 'year' in x['posted_at'][1]:
            return x['updated_at_utc'] - timedelta(days=360 * int(x['posted_at'][0]))
        else:
            pass
    df['posted_at_utc'] = df.apply(posted_at_utc, axis=1)
    df['posted_year'] = df.apply(lambda x: x['posted_at_utc'].strftime('%Y'), axis=1)
    df = df.groupby('posted_year').size().to_frame().reset_index()
    df = df.rename(columns={0: 'count'})
    
    #visualize
    min_year = int(min(df['posted_year']))
    max_year = int(max(df['posted_year']))
    fig, ax = plt.subplots(figsize=(15, 5))
    plt.plot('posted_year', 'count', data=df, color='black')
    plt.title(f'Numbers of posts per year')
    plt.xlabel('Year')
    plt.ylabel('Total posts')
    if save:
        plt.savefig(f'img/{img_title}.png', bbox_inches = 'tight')
    plt.show
