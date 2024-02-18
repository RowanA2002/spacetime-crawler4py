import csv
import re
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from utils.download import download
from utils.get_parents import get_parents_set
from utils.information_value import information_value
from utils.tokenize_string import tokenize
from utils.calendar_trap import calendar_trap_check
from utils import normalize

def scraper(url, resp, config, logger, frontier):
    links = extract_next_links(url, resp, frontier, logger)
    return [link for link in links if is_valid(link, config, logger)]

def extract_next_links(url, resp, frontier, logger):

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
    if resp.status != 200:
        if resp.status == 404:
            logger.info(f"{url} returned 404 not found")
        elif (resp.error != None):
            logger.info(resp.error)
        return urls_list
    if (resp.raw_response.content == "" or resp.raw_response.content == None): # Check for dead pages
        logger.info("Page has no data")
        return urls_list

    unique_urls = set() # keeps track of unique urls on page
    unique_urls.add(url) # add parent url to set

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    # Report processing
    page_token_count = 0

    # Record all tokens in page
    with open(frontier.config.word_file, 'at') as words:
        for strings in soup.stripped_strings:
            tokens = tokenize(strings)
            page_token_count += len(tokens)
            if len(tokens) > 0:
                words.write(' '.join(tokens) + '\n')

    # Record url and token count
    with open(frontier.config.url_file, 'a', newline='') as urlcount:
        urlwriter = csv.writer(urlcount)
        urlwriter.writerow([url, page_token_count])

    for link in soup.find_all(href=True):
        found_url = link['href']
        found_url = urldefrag(found_url)[0] # defrag URL using urldefrag from urllib
        parsed = urlparse(found_url)
        if (len(found_url) != 0) and (parsed.scheme == ""): # check if found_url is a relative URL
            if (re.match(r"^\/{3}", found_url)): #if 3 slashes, it is a file URL, don't add
                logger.info(f"SKIPPING {found_url}: Most likely a file")
                continue
            if re.match(r"^(\/\/)", found_url): # if url starts with // (shorthand to request reference url using protocol of current url)
                current_protocol = urlparse(url).scheme
                found_url = current_protocol + ":" + found_url
            else:
                found_url = urljoin(url, found_url) # if not, join urls using urljoin from urllib

        if len(found_url) == 0: #Check URL is not empty string
            logger.info(f"SKIPPING {found_url}: Empty URL")
            continue
        
        #check for repeating directories
        if (re.search(r'\/([^\/]+)\/(.+\/)?\1\/(.+\/)?\1', found_url)): #check if directory is repeated 3 or more times
            logger.info(f"SKIPPING {found_url}: Repeated path")
            continue

        #check for calendar traps
        pattern = r'\/?([0-9]{0,2})\/([0-9]{0,2})\/([0-9]{4})($|\/)$'

        if (re.search(pattern, url) and re.search(pattern, found_url)):
            if(re.sub(pattern, "", url) == re.sub(pattern, "", found_url)):
                logger.info(f"SKIPPING {found_url}: Found common calendar format")
                continue

        #Check for dynamic urls
        if "?" in (found_url):
            found_url = found_url.split("?")[0]
            if (found_url) == url: #don't add if url without query parameters is same as parent url
                logger.info(f"SKIPPING {found_url}: Same as parent ({url}) without query")
                continue 
        found_url = normalize(found_url)
        # trap check
        parents = get_parents_set(url, frontier, 50) # number should be changed based on trap check implementation
        logger.info(f"{found_url} had parents {parents}")
        if (found_url) in parents:
            logger.info(f"SKIPPING {found_url}: Existed in parents")
            continue
        if calendar_trap_check(found_url, parents) > 10:
            logger.info(f"SKIPPING {found_url}: Repeated number pattern found (Calendar)")
            continue

        if found_url not in unique_urls:
            urls_list.append(found_url)
            unique_urls.add(found_url)
        else:
            logger.info(f"SKIPPING {found_url}: Already found on page")

    return urls_list

def is_valid(url, config, logger):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpe?g|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|json|java|apk|img|war|xml"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|txt|vmdk|php|ppsx)$|.*(json|xmlrpc|mailto|\.php)", parsed.path.lower()):
            return False

        # check for valid domain
        if parsed.netloc is not None and not re.match(r".*(\.ics|\.cs|\.informatics|\.stat)\.uci\.edu", parsed.netloc):
            return False

        resp = download(url, config, logger)
        if resp.error == None and resp.raw_response != None:
            soup = BeautifulSoup(resp.raw_response.content, "html.parser")
            info = information_value(soup)
            if info < 0.33: 
                logger.info(f"Skipped {url}: information value = {info} < 1/3")
                return False
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise