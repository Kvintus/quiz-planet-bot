from flask import Flask, request, jsonify
from typing import List
from bs4 import BeautifulSoup as Soup
from urllib.parse import quote_plus, parse_qs, urlparse
import requests
from collections import defaultdict

app = Flask(__name__)

def generateGoogleUrl(phrase: str) -> str:
    return f"https://www.google.sk/search?q={quote_plus(phrase)}"

def extractPageUrl(url: str) -> str:
    qs = parse_qs(urlparse(url).query)
    return qs['q'][0] if 'q' in qs else url

def extractUrlsFromGoogleBlocks(blocks: List[Soup], n = None) -> List[str]:
    urls: List[str] = []
    for block in blocks:
        urls.append(extractPageUrl(block.find('h3', {'class' : 'r'}).find('a')['href']))
    return urls[:n]

def getGoogleBlocks(question: str) -> List[Soup]:
    google_source = requests.get(generateGoogleUrl(question)).text
    google_soup = Soup(google_source, 'html.parser')
    return google_soup.find_all('div', {'class': "g"})

def countTheKeywords(urls: List[str], answers: List[str]) -> defaultdict:
    keyword_count: defaultdict = defaultdict(int)
    for url in urls:
        source = requests.get(url).text
        for answer in answers:
            keyword_count[answer] += source.count(answer)
    return keyword_count

@app.route('/', methods=["POST"])
def index():
    rejson = request.get_json() 
    urls = extractUrlsFromGoogleBlocks(getGoogleBlocks(rejson['question']), n=3)
    return jsonify(answer=sorted(countTheKeywords(urls, rejson['answers']).items(), key=lambda x: x[1], reverse=True)[0][0])

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")