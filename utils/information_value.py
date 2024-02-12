from bs4 import BeautifulSoup
from utils.tokenize_string import tokenize

def information_value(soup: BeautifulSoup):
    """Computes a percentage of text (token_count/(tag_count+token_count)) representing information value"""
    tag_count = len(soup.find_all(True))
    token_count = 0
    for s in soup.stripped_strings:
        token_count += len(tokenize(s))
    return token_count/(tag_count+token_count) if (tag_count + token_count) > 0 else token_count