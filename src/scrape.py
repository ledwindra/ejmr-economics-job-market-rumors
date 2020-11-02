import glob
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from random import randint

class StatsTable:

    def max_page(self):
        url = 'https://www.econjobrumors.com'
        status_code = None
        while status_code != 200:
            res = requests.get(url)
            status_code = res.status_code
            content = BeautifulSoup(res.content, features='html.parser')
            page = content.find('div', {'class': 'nav'})
            page = [x.get_text() for x in page.find_all('a')]
            page = [''.join([j for j in i if j.isnumeric() == True]) for i in page]
            page = max([int(i) for i in page if i != ''])
        
        return page

    def stats_table(self, page):
        if page == 1:
            url = f'https://www.econjobrumors.com/'
        else:
            url = f'https://www.econjobrumors.com/page/{page}'
        status_code = None
        while status_code != 200:
            res = requests.get(url)
            status_code = res.status_code
            content = BeautifulSoup(res.content, features='html.parser')
            table = content.find('table', {'id': 'latest'})
            table = table.find_all('tr')
            title = pd.DataFrame([x.find('a').attrs['href'] for x in table[1:]], columns=['url'])
            stats =  pd.DataFrame([[j.get_text() for j in i.find_all('td', {'class': 'num'})] for i in table[1:]], columns=['posts', 'views', 'votes', 'freshness'])
            df = pd.merge(title, stats, how='inner', left_index=True, right_index=True)
            df['updated_at_utc'] = datetime.utcnow()
        
        return df
    
    def read_data(self):
        stats_table = glob.glob(f'data/stats-table/stats-table-*.csv')
        data = []
        for s in stats_table:
            df = pd.read_csv(s)
            data.append(df)
        df = pd.concat(data, sort=False)
        
        return df

class Post:

    def content(self, url):
        status_code = None
        while status_code != 200:
            res = requests.get(url)
            status_code = res.status_code
            content = BeautifulSoup(res.content, features='html.parser')

        return content

    def max_page(self, url):
        content = self.content(url)
        try:
            page = [x.get_text() for x in content.find('div', {'class': 'nav'}).find_all('a')]
            page = [''.join([j for j in i if j.isnumeric() == True]) for i in page]
            page = max([int(i) for i in page if i != ''])
        except AttributeError:
            page = 1

        return page
    
    def dataframe(self, url):
        content = self.content(url)
        poststuff = content.find_all('div', {'class': 'poststuff'})
        post = content.find_all('div', {'class': 'post'})
        df = pd.DataFrame([{
            'url': url,
            'post': post[x].text,
            'posted_at': poststuff[x].contents[0],
            'good': int(poststuff[x].contents[5].text.replace(' ', '')),
            'no_good': int(poststuff[x].contents[8].text.replace(' ', '')),
            'updated_at_utc': datetime.utcnow()
        } for x in range(len(post))])

        return df

    def get_post(self, url):
        max_page = self.max_page(url)
        df = self.dataframe(url)
        if max_page > 1:
            i = 2
            while i <= max_page:
                df = df.append(self.dataframe(f'{url}/page/{i}'))
                i += 1
            df = df.reset_index(drop=True)

        return df

    def read_data(self, data):
        post = glob.glob(f'data/{data}/{data}-*.csv')
        data = []
        for p in post:
            df = pd.read_csv(p)
            data.append(df)
        df = pd.concat(data, sort=False)
        
        return df
