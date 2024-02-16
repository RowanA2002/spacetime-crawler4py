import csv
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from urllib.parse import urldefrag, urlparse

from utils.tokenize_string import tokenize


# O(n) for n tokens
def compute_word_frequencies(tokens: List[str]) -> Dict[str, int]:
    """
    Counts the number of occurrences of each token in the token list
    """
    freq_dict = defaultdict(int)
    for token in tokens: 
        freq_dict[token] += 1
    return freq_dict

# O(nlogn) where n is the numner of keys in the dictionary
def get_n_frequencies(frequencies: Dict[str, int], n: int, stopwords: Set) -> List[Tuple[str, int]]:
    items = [(k, v) for k, v in frequencies.items()]  # O(n)
    items.sort(key=lambda i : (-i[1], i[0]))  # O(nlogn)
    n_frequencies = []
    for token, freq in items:  # O(n)
        if token in stopwords or len(token) < 2 or re.match(r"\d+", token):
            continue
        n_frequencies.append((token, freq))
        if len(n_frequencies) == n:
            break


    return n_frequencies

def generate_report(url_file: str, word_file: str, stopwordfile: str):
    """Generate crawling statistics from logs"""
    if not os.path.exists("reports"):
        os.mkdir("reports")
    report_num = -1
    for filename in os.listdir("reports"):
        match = re.match(r"report([0-9]+)\.txt", filename)
        if match is not None:
            num = int(match.group(1))
            report_num = max(report_num, num)
    report_num += 1
    report_file = os.path.join("reports", f"report{report_num}.txt")
    # Number of Unique pages
    # Longest page
    # Number of Subdomains in ics.uci.edu and their page count
    unique_page_count = 0
    longest_page = (None, 0)
    ics_subs = dict() # domain -> set(pages in domain)
    unique_urls = set()
    if os.path.exists(url_file):
        with open(url_file, 'r', newline='') as urls:
            urlreader = csv.reader(urls)
            row = next(urlreader)
            while row is not None:
                url, token_count = row
                token_count = int(token_count)
                defrag = urldefrag(url)[0]
                if defrag not in unique_urls:
                    unique_page_count +=1
                    unique_urls.add(defrag)
                if token_count >= longest_page[1]:
                    longest_page = (defrag, token_count)
                parsedurl = urlparse(defrag)
                if re.match(r".*\.ics\.uci\.edu.*", parsedurl.netloc):
                    domain = "/".join([parsedurl.scheme, parsedurl.netloc])
                    if domain not in ics_subs:
                        ics_subs[domain] = set()
                    ics_subs[domain].add(defrag)
                try:
                    row = next(urlreader)
                except StopIteration:
                    break
    ics_sub_counts = [(k, len(v)) for k, v in ics_subs.items()]
    ics_sub_counts.sort()
    # Common words
    top_freqs = []
    if os.path.exists(word_file):
        if not os.path.exists(stopwordfile):
            stopwordfile="stopwords.txt"
        stopwords = set()
        with open(stopwordfile, 'r') as f:
            stopwords = set(f.read().split())
        with open(word_file, 'r') as words:
            tokens = words.read().split()
            freqs = compute_word_frequencies(tokens)
            top_freqs = get_n_frequencies(freqs, 50, stopwords)
    
    # Generate Report
    with open(report_file, 'x') as r:
        r.write(f"Report Number {report_num} on Crawl of ics\n\n")
        r.write(f"Number of unique pages: {unique_page_count}\n\n")
        r.write(f"Longest Page: {longest_page[0]} at {longest_page[1]} words\n\n")
        r.write("50 Most Common Words:\n\n")
        for word, count in top_freqs:
            r.write(f"\t{word} -> {count}\n")
        r.write("\n")
        r.write("Subdomains Under ics:\n")
        for url, pages in ics_sub_counts:
            r.write(f"{url}, {pages}\n")

if __name__ == "__main__":
    try:
        url_file, word_file, stopwordfile = sys.argv[1:4]
    except:
        raise Exception("Not enough args")
    generate_report(url_file, word_file, stopwordfile)