try:
    from urllib2 import urlopen, Request, HTTPError
except Exception:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
from configparser import ConfigParser
import requests
import os 
import re 
import ssl 
import anime1dl.config_controller as config_controller
import sys
import datetime
if not os.path.exists('/System/Library/AppleUSBDevice'):
    from anime1dl.database_controller import database
    import anime1dl.updator as updator


class Anime1_Downloader:
    def __init__(self, download_folder='./animes/'):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.app_config = config_controller.init_config('anime_downloader.ini')

    async def download_series(self, url):
        __VALID__URL__ = r"http://www.anime1.com/watch/*/"
        if re.match(__VALID__URL__, url) is None:
            print("ani-dl: Not a valid url")
            return 
        print("ani-dl: Donwloading webpage")
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        page = urlopen(req).read()

        print("ani-dl Getting series name and number of episode(s)", end="\n\n")
        YouAreHereIndex = page.find(b"You Are Here")
        if YouAreHereIndex == -1:
            print("\nani-dl Seriously... Wrong Link", end="\n\n")
            return

        TruncatedForName = page[YouAreHereIndex : ]
        NameIndex = TruncatedForName.find(b"</a></div>")
        Name = TruncatedForName[83 : NameIndex].decode()

        LatestEpIndex = page.find("Latest {} Episodes".format(Name).encode())
        if LatestEpIndex != -1:
            TruncatedForEpisode = page[LatestEpIndex + len("Latest {} Episodes".format(Name)) : ]
            EpIndex = TruncatedForEpisode.find("{} Episodes".format(Name).encode())
            TruncatedForEpisode = TruncatedForEpisode[EpIndex : ]
            EndOfEpisodes = TruncatedForEpisode.find(b"</ul>")
            TruncatedForEpisode = TruncatedForEpisode[ : EndOfEpisodes]
        else:
            TruncatedForEpisode = page[YouAreHereIndex : ]
            EndOfEpisodes = TruncatedForEpisode.find(bytes("</ul>", "utf-8"))
            TruncatedForEpisode = TruncatedForEpisode[ : EndOfEpisodes]

        URLs = re.findall(b"http://www.anime1.com/watch/[a-zA-Z0-9-]+/[a-z-]+-[0-9-]{1,8}", TruncatedForEpisode)

        print("ani-dl Name: {}".format(Name), end="\n\n")
        print("ani-dl Episodes Found: {}".format(len(URLs)), end="\n\n")

        for url in URLs:
            await self.download_episode(url.decode(), Name)

    async def download_episode(self, URL, tName):
        trys = 0
        Name = tName.replace(":", "").replace("/", " ")
        print("\nani-dl Download episode from {}...{}".format(URL[ : URL.find(".com/") + 5], URL[URL.find("/episode-") : ]))
        print("ani-dl Getting Info on the Episode")
        __FINAL__URL__, __FINAL__NAME__ = await self.get_info(URL)
        if __FINAL__URL__ == "" or __FINAL__NAME__ == "":
            print("ani-dl Video not Found")
            return
            
        if Name != "" and not os.path.exists(self.app_config.get('default', 'download_location') + Name):
            os.makedirs(self.app_config.get('default', 'download_location') + Name)
        try:
            Video = urlopen(__FINAL__URL__,context=self.ctx)
            File_Size = Video.info()["Content-Length"]
            File_Type = Video.info()["Content-Type"]
            __FINAL__NAME__ = self.app_config.get('default', 'download_location') + Name + "/" + __FINAL__NAME__.replace("/", " ") + "." + File_Type[File_Type.find("/") + 1 : ]

            if os.path.isfile(__FINAL__NAME__) and os.path.getsize(__FINAL__NAME__) == int(File_Size):
                    print("ani-dl File found and is of same size, skipping")
                    return

            File_Size_Text = self.BytesToPrefix(int(File_Size))
            f_Video = open(__FINAL__NAME__, "wb")
            print("\nani-dl Destination: {}\nani-dl Type: {}".format(__FINAL__NAME__[__FINAL__NAME__.find(self.app_config.get('default', 'download_location')) + 1 : ], File_Type))
            Downloaded = 0
            BlockSize = 8192

            while True:
                    Buffer = Video.read(BlockSize)
                    if not Buffer:
                            break

                    Downloaded += len(Buffer)
                    f_Video.write(Buffer)
                    bytess = self.BytesToPrefix(int(Downloaded))
                    Status_Text = "ani-dl: {:9s}/{:9s} [{:7.3f}%]".format(bytess, File_Size_Text, int(Downloaded)*100/int(File_Size))
                    print("{}    ".format(Status_Text), end="\r")

            f_Video.close()
            print()
        except Exception as e:
            trys += 1
            if trys >= 3:
                    print(f"Passed on episode: {__FINAL__NAME__}, Error code: {e}")
                    with open(f"{self.app_config.get('default', 'download_location') + Name + '/'}Skipped.txt", "a+") as skipped:
                            skipped.write(f"Passed on episode: {__FINAL__NAME__}, Error code: {e}\n")
                    pass
            else:
                    print(f"Retrying to download {__FINAL__NAME__}: ")
                    print(e)
                    await self.download_episode(URL, tName)

    async def get_info(self, URL):
        print("ani-dl Download webpage")
        req = Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        
        try:
            web = urlopen(req)
        except HTTPError:
            print("ani-dl Webpage not found, Error code: {}".HTTPError.code)
            return "", ""
        page = web.read()

        print("ani-dl Finding Video")
        v_URL = page.find(b'file: "') + 7
        f_URL = page.find(b'label: "') + 8
        if v_URL == -1 or f_URL == -1:
            return "", ""
        TruncatedForName = page[f_URL: ]
        TruncatedForName = TruncatedForName[: TruncatedForName.find(b'"')]
        TruncatedForVideo = page[v_URL: ]
        TruncatedForVideo = TruncatedForVideo[ : TruncatedForVideo.find(b'"')]
        TruncatedForVideo = TruncatedForVideo.replace(b" ", b"%20")
        return TruncatedForVideo.decode(), TruncatedForName.decode().replace(":", "").replace("Episode Episode", "Episode")

    def BytesToPrefix(self, Size):
        Prefix_N = 0
        Prefixes = ["B", "KiB", "MiB", "GiB", "TiB"]
        t_Size = Size
        l_Size = Size

        while t_Size > 0:
            t_Size = t_Size // 1024
            if t_Size:
                Prefix_N += 1

        l_Size = Size / (1024 ** Prefix_N)

        return "{:6.2f} {}".format(l_Size, Prefixes[Prefix_N])
        
    async def main(self):
        print('Anime downloader made by: AnimeDevOps', end='\n\n')
        if not os.path.exists('/System/Library/AppleUSBDevice'):
            try:
                if self.app_config.get('default', 'auto_update_anime_database') == 'true':
                    if  datetime.datetime.now().strftime("%Y%b%d") > self.app_config.get('default', 'next_update_time'):
                        print('Updating anime database')
                        update_now = updator.Updator()
                        await update_now.update()
                        print("finished relaunch app")
                        return
            except Exception:
                os.mkdir('config')
                os.mkdir('databases')
                config_code = requests.get('https://raw.githubusercontent.com/AnimeDevOps/ani-dl/main/config/anime_downloader.ini').text
                with open('./config/anime_downloader.ini', 'w') as config_file:
                    config_file.write(config_code)
                await updator.Updator().update()
                print('if you have any problems downloading animes, connect to a vpn, that should fix your problem')
                print("Setup finished, relaunch app, if you change folder the setup will run again, so it's better to stay with only one folder")
                return 
        else:
            try:
                self.app_config.get('default', 'download_location') 
            except Exception:
                print('You cannot search for anime on ios, sorry :(', end='\n\n')
                os.mkdir('config')
                os.mkdir('databases')
                config_code = requests.get('https://raw.githubusercontent.com/AnimeDevOps/ani-dl/main/config/anime_downloader.ini').text
                with open('./config/anime_downloader.ini', 'w') as config_file:
                    config_file.write(config_code)
                print('if you have any problems downloading animes, connect to a vpn, that should fix your problem')
                print("Setup finished, relaunch app, if you change folder the setup will run again, so it's better to stay with only one folder")
                return


        if len(sys.argv) == 1:
            print('usage: ani -s, exmaple search', end='\n')
            print('usage: ani -u, updates anime database', end='\n')
            print('usage: ani -d http://www.anime1.com/watch/black-clover-tv/, download from a url', end='\n')
            print('usage: ani --no-auto-update, turn off anime database auto update', end='\n')
            print('usage: ani --yes-auto-update, turn back on anime database auto update', end='\n')
            print('usage: ani -b file.txt, download a batch of anime, text file need to be filled with only anime1.com urls', end='\n')
        if len(sys.argv) == 2:
            if sys.argv[1] == '-s':
                if not os.path.exists('/System/Library/AppleUSBDevice'):
                    count = 0
                    found = []
                    found_url = []
                    search_query = input("What's the name of the anime you want to search for: ")
                    query = "SELECT * FROM Animes"
                    rows = await database.fetch_all(query=query)
                    for x in rows:
                        if search_query.title() in str(x[1]):
                            found.append(str(x[1]))
                            found_url.append(str(x[2]))
                        else:
                            pass
                    for animes in found:
                        print('%i: name: %s' % (count, str(animes)), end='\n\n')
                        count += 1
                    print('enter the number infront of the anime name, to start downloading.')
                    selected = input('')
                    if int(selected) > len(found):
                        print('Error, you entered to high of a number')
                        return 
                    else:
                        if 'anime1.com' not in found_url[int(selected)]:
                            print('Not a valid anime1.com url, sorry :(')
                            return
                        if 'watch/' in found_url[int(selected)]:
                            if 'episode-' in found_url[int(selected)]:
                                await self.download_episode(found_url[int(selected)], found_url[int(selected)])
                            else:
                                await self.download_series(found_url[int(selected)])
                else:
                    print('Search does not work on ios', end='\n\n')
                    return 
            elif sys.argv[1] == '-u':
                if not os.path.exists('/System/Library/AppleUSBDevice'):
                    update_now = updator.Updator()
                    await update_now.update()
                    return 
                else:
                    print('The database does not work on ios', end='\n\n')
                    return 
            elif sys.argv[1] == '--no-auto-update':
                if not os.path.exists('/System/Library/AppleUSBDevice'):
                    self.app_config.set('default', 'auto_update_anime_database', 'false')
                    config_controller.save(self.app_config)
                    print('Auto updates turned off', end='\n\n')
                    return
                else:
                    print('Database does not work on ios, so auto update is turned off automaticly')
            elif sys.argv[1] == '--yes-auto-update':
                if not os.path.exists('/System/Library/AppleUSBDevice'):
                    self.app_config.set('default', 'auto_update_anime_database', 'true')
                    config_controller.save(self.app_config)
                    return
                else:
                    print('Database does not work on ios, so auto update is turned off automaticly')

        elif len(sys.argv) == 3:
            if sys.argv[1] == '-d':
                if 'anime1.com' not in sys.argv[2]:
                    print('Error, you entered to high of a number')
                    return 
                if 'watch/' in sys.argv[2]:
                    if 'episode-' in sys.argv[2]:
                        await self.download_episode(sys.argv[2], '')
                    else:
                        await self.download_series(sys.argv[2])
            elif sys.argv[1] == '-b':
                with open(sys.argv[2], 'r+') as file:
                    for lines in file:
                        if 'anime1.com' not in lines:
                            print('Error, you entered to high of a number')
                            return
                        if 'watch/' in lines:
                            if 'episode-' in lines:
                                await self.download_episode(lines, '')
                            else:
                                await self.download_series(lines)

                            


                




 
