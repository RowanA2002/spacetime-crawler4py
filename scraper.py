import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup

from utils.download import download

def scraper(url, resp, config, logger):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link, config, logger)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    urls_list = []
    if (resp.error != None):
        print(resp.error)
        return urls_list

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    for link in soup.find_all(href=True):
        found_url = link['href']
        found_url = urldefrag(found_url)[0] #defrag URL using urlparse
        parsed = urlparse(found_url) #parse URL using urldefrag from urllib.parse
        if (parsed.scheme not in set(["http", "https"])): #check if found_url is a relative URL
            found_url = url + found_url #if not, concatenate url to found_url create absolute url
        urls_list.append(found_url)

    return urls_list

def is_valid(url, config, logger):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # politeness -- need to do if using multithreading, otherwise already implemented when num threads = 1 using sleep
    # high textual content
    # domain

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        # check for valid domain
        # TODO: robot.txt?
        if not re.match(r".*(\.ics|\.cs|\.informatics|\.stat)\.uci\.edu", parsed.hostname):
            return False
        
        resp = download(url, config, logger)
        if resp.error == None and resp.raw_response != None:
            soup = BeautifulSoup(resp.raw_response.content, "html.parser")
            # TODO: check for textual content
        return True
        
    except TypeError:
        print ("TypeError for ", parsed)
        raise