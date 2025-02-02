import os
import shelve
from queue import Empty, Queue
from threading import RLock, Thread

from scraper import is_valid
from utils import get_logger, get_urlhash, normalize


class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url, None)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url, None)

        if not os.path.exists(self.config.url_file) and not restart:
            # Url file does not exist, but request to load save.
            self.logger.info(
                f"Did not find url file {self.config.url_file}, "
                f"Creating a new one.")
            open(self.config.url_file, 'x').close()
        elif os.path.exists(self.config.url_file) and restart:
            # Url file does exists, but request to start from seed.
            self.logger.info(
                f"Found url file {self.config.url_file}, deleting it.")
            os.remove(self.config.url_file)
            # Create one if it does not exist.
            open(self.config.url_file, 'x').close()

        if not os.path.exists(self.config.word_file) and not restart:
            # Word file does not exist, but request to load save.
            self.logger.info(
                f"Did not find word file {self.config.word_file}, "
                f"Creating a new one.")
            open(self.config.word_file, 'x').close()
        elif os.path.exists(self.config.word_file) and restart:
            # Word file does exists, but request to start from seed.
            self.logger.info(
                f"Found word file {self.config.word_file}, deleting it.")
            os.remove(self.config.word_file)
            # Create one if it does not exist.
            open(self.config.word_file, 'x').close()
            

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save) 
        tbd_count = 0
        for url, completed, _ in self.save.values():
            if not completed and is_valid(url, self.config, self.logger):
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        try:
            return self.to_be_downloaded.pop()
        except IndexError:
            return None

    def add_url(self, url, parent_url=None):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            self.save[urlhash] = (url, False, parent_url)
            self.save.sync()
            self.to_be_downloaded.append(url)
    
    def get_parent(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            raise
        return self.save[urlhash][2]
    
    def exists_in_shelf(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        return urlhash in self.save

    def mark_url_complete(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.save[urlhash] = (url, True, self.save[urlhash][2])
        self.save.sync()
