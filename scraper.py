import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup

from utils.download import download
from utils.information_value import information_value

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
        found_url = urldefrag(found_url)[0] #defrag URL using urldefrag from urllib
        parsed = urlparse(found_url)
        if (len(found_url) != 0) and (parsed.scheme == ""): #check if found_url is a relative URL
            if re.match(r"^\/\/", found_url): # if url starts with // (shorthand to request reference url using protocol of current url)
                current_protocol = urlparse(url).scheme
                found_url = current_protocol + ":" + found_url
            else:
                found_url = urljoin(url,found_url) #if not, join urls using urljoin from urllib
        if len(found_url)!= 0:
            urls_list.append(found_url)

    return urls_list

def is_valid(url, config, logger):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # politeness -- need to do if using multithreading, otherwise already implemented when num threads = 1 using sleep
    # high textual content

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
        # TODO: robot.txt?
        if not re.match(r".*(\.ics|\.cs|\.informatics|\.stat)\.uci\.edu", parsed.hostname):  # check url is in valid domain
            return False
        
        resp = download(url, config, logger)
        if resp.error == None and resp.raw_response != None:
            soup = BeautifulSoup(resp.raw_response.content, "html.parser")
            info = information_value(soup)
            if info < 1: 
                logger.info(f"Skipped {url}: information value = {info} < 1")
                return False
        return True
        
    except TypeError:
        print ("TypeError for ", parsed)
        raise