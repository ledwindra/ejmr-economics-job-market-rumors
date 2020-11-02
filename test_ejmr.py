import bs4
import os
import pandas as pd
import pytest
import sys
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{path}/../')
from random import randint
from scrape import StatsTable, Post

class TestStatsTable(StatsTable):

    def test_stats_table_max_page(self):
        assert type(self.max_page()) == int

    def test_stats_table_page_one(self):
        one = self.stats_table(1)
        assert type(one) == pd.core.frame.DataFrame

    def test_stats_table_page_last(self):
        max_page = self.max_page()
        last = self.stats_table(max_page)
        assert type(last) == pd.core.frame.DataFrame

    def test_stats_table_page_random(self):
        max_page = self.max_page()
        page = randint(1, max_page)
        random = self.stats_table(page)
        assert type(random) == pd.core.frame.DataFrame

    def test_stats_table_read_data(self):
        assert type(self.read_data()) == pd.core.frame.DataFrame

    def test_stats_table_page_exception(self):
        with pytest.raises(AttributeError):
            assert self.stats_table('1')

class TestPost(Post):

    def test_post_content(self):
        urls = self.read_data('stats-table')
        urls = urls.url.to_list()
        u = randint(0, len(urls))
        content = self.content(urls[u])
        assert type(content) == bs4.BeautifulSoup
    
    def test_post_max_page(self):
        urls = self.read_data('stats-table')
        urls = urls.url.to_list()
        u = randint(0, len(urls))
        max_page = self.max_page(urls[u])
        assert type(max_page) == int

    def test_post_dataframe(self):
        urls = self.read_data('stats-table')
        urls = urls.url.to_list()
        u = randint(0, len(urls))
        df = self.dataframe(urls[u])
        assert type(df) == pd.core.frame.DataFrame

    def test_post_get_post(self):
        urls = self.read_data('stats-table')
        urls = urls.url.to_list()
        u = randint(0, len(urls))
        post = self.get_post(urls[u])
        assert type(post) == pd.core.frame.DataFrame

    def test_post_read_data(self):
        df = self.read_data('stats-table')
        assert type(df) == pd.core.frame.DataFrame

    def test_post_read_data(self):
        df = self.read_data('post')
        assert type(df) == pd.core.frame.DataFrame
