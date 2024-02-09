import shelve

from utils import get_urlhash
from typing import List


def get_parents(url, save: shelve.Shelf, n_parents) -> List:
    """Gets n parent urls (url it was scraped from) of url"""
    urlhash = get_urlhash(url)
    if urlhash not in save:
        raise
    parents = []
    parent = save[urlhash][2]
    i = 0
    while parent and i < n_parents:
        urlhash = get_urlhash(parent)
        parents.append(parent)
        parent = save[urlhash][2]
        i+=1
    return parents