
from typing import List


def get_parents(url, frontier, n_parents) -> List:
    """Gets n parent urls (url it was scraped from) of url"""
    if not frontier.exists_in_shelf(url):
        raise
    parents = [url,]
    parent = frontier.get_parent(url)
    i = 0
    while parent and i < n_parents-1:
        parents.append(parent)
        parent = frontier.get_parent(parent)
        i+=1
    return parents