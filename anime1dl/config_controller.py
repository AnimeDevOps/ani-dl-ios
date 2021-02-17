from configparser import ConfigParser

config_location = "./config/"

def init_config(filename=None):
    if filename == None:
        config = ConfigParser(default_section="default")
        config.read(config_location + 'anime_downloader.ini')
        return config
    else:
        config = ConfigParser(default_section="default")
        config.read(config_location + filename)
        return config
def save(config,filename=None):
    if filename == None:
        with open(config_location + 'anime_downloader.ini', 'w') as config_file:
                config.write(config_file)
    else:
        with open(config_location + filename, 'w') as config_file:
            config.write(config_file)
