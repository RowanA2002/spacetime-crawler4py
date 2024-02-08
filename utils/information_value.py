from bs4 import BeautifulSoup
from utils.tokenize_string import tokenize

def information_value(soup: BeautifulSoup):
    """Computes a ration of tags to string text representing information value"""
    # find ration of tags to tokens
    # tokenize
    tag_count = len(soup.find_all(True))
    token_count = 0
    for s in soup.stripped_strings:
        token_count += len(tokenize(s))
    return token_count/tag_count if tag_count > 0 else token_count