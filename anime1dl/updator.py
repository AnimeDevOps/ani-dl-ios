import re
import requests 
import datetime 
from bs4 import BeautifulSoup as BS 
import anime1dl.config_controller as config_controller
import os
if not os.path.exists('/System/Library/AppleUSBDevice'):
    from anime1dl.database_controller import database, connect

class Updator:
    def __init__(self):
        self.app_config = config_controller.init_config('anime_downloader.ini')
    if not os.path.exists('/System/Library/AppleUSBDevice'):
        def get_html(self):
            return requests.get(self.app_config.get('updates', 'update_url')).text
        def get_info(self, url):
            name = url.replace('watch/', '').split('/')[-1].replace('-', ' ').title()
            return name
        def delete_database(self):
            try:
                os.remove('./databases/anime_databse.db')
            except Exception:
                pass
        async def create_table(self, database):
            query = """CREATE TABLE Animes (id INTEGER PRIMARY KEY, name VARCHAR(500), url VARCHAR(500))"""
            await database.execute(query=query)
        async def update(self):
            self.delete_database()
            await connect()
            html = self.get_html()
            for animes in BS(html, 'lxml').findAll('a'):
                valid_url = r'http://www.anime1.com/watch/*/'
                if re.match(valid_url, str(animes.get('href'))) is None:
                    pass
                else:
                    if 'episode-' in str(animes.get('href')):
                        pass
                    else:
                        try:
                            query = """INSERT INTO Animes(name, url) VALUES (:name, :url)"""
                            values = [{"name": self.get_info(str(animes.get('href'))), "url": str(animes.get('href'))}]
                            await database.execute_many(query=query, values=values)
                        except Exception: 
                            await self.create_table(database)
            will_update_in = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y%b%d")
            self.app_config.set('default', 'next_update_time', will_update_in)
            config_controller.save(self.app_config)
