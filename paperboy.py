import sys
from enum import Enum
from bs4 import BeautifulSoup as bs
import requests
import json
from datetime import datetime


ExamPeriod = Enum('ExamPeriod', ['January', 'Summer', 'Autumn'])

now = datetime.now()

cookies={}
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
    cookies = config_data['cookies']


def get_papers(module:str, min_year:int=2000, max_year:int=now.year, 
               periods:list=['January','Summer','Autumn']):
    if max_year <= min_year:
        raise Exception('Invalid year range')
    soup = _get_page_soup(module)
    papers = _extract_links(soup)
    for year in range(min_year, max_year):
        year = f"{year}"
        if year not in papers.keys():
            continue
        for period in periods:
            if period not in papers[year].keys():
                continue
            paper = papers[year][period]
            _download_pdf(paper['url'], paper['filename'])
            print("Saved file:", paper['filename'])


def _get_page_soup(module: str) -> bs:
    url = f"https://www.maynoothuniversity.ie/library/exam-papers?code_value_1={module}"
    response = requests.get(url, cookies=cookies)
    if response.ok:
        data = response.content.decode(encoding='ansi')
        soup = bs(data, "html.parser")
        return soup
    else:
        raise Exception('HTTP request failed: {response}', response)


def _extract_links(soup: bs) -> dict:
    d = {}
    links = soup.find_all("span", {'class': "file"})
    links = [link.a for link in links]
    for link in links:
        filename = link.text.strip()
        year, module, period = filename.rstrip('.pdf').split('-')
        url = link['href']
        if year not in d.keys():
            d[year] = {}
        d[year][period] = {'filename': filename, 'url': url}
    return d
    

def _download_pdf(url, filename):
    response = requests.get(url, cookies=cookies)
    with open(filename, mode='wb') as file:
        file.write(response.content)


def _prettyprint_dict(d: dict):
    print(json.dumps(d, indent=2))


def main():
    module=""
    min_year=2000
    max_year=now.year
    if len(sys.argv) > 1:
        module = sys.argv[1]
    else:
        print("You must provide atleast the module code")
    if len(sys.argv) > 2:
        min_year = int(sys.argv[2])
    if len(sys.argv) > 3:
        max_year = int(sys.argv[3])
    get_papers(module, min_year, max_year)

if __name__ == "__main__":
    main()