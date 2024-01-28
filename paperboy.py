import requests
import json
import os.path
from bs4 import BeautifulSoup as bs
from argparse import ArgumentParser, ArgumentError


def _get_page_soup(module: str, cookie: dict) -> bs:
    url = f"https://www.maynoothuniversity.ie/library/exam-papers?code_value_1={module}"
    response = requests.get(url, cookies=cookie)
    if response.ok:
        data = response.content.decode(encoding='ansi')
        soup = bs(data, "html.parser")
        return soup
    else:
        raise Exception('HTTP request failed: {response}', response)


def _extract_papers_details(soup: bs) -> dict:
    d = {}
    links = soup.find_all("span", {'class': "file"})
    links = [link.a for link in links]
    for link in links:
        filename = link.text.strip()
        year, module, period = filename.rstrip('.pdf').split('-')
        year = int(year)
        url = link['href']
        if year not in d.keys():
            d[year] = {}
        d[year][period] = {'filename': filename, 'url': url}
    return d
    

def _download_pdf(url, filename, cookie):
    response = requests.get(url, cookies=cookie)
    with open(filename, mode='wb') as file:
        file.write(response.content)


def _prettyprint_dict(d: dict):
    print(json.dumps(d, indent=2))


def main():
    parser = ArgumentParser(
        description="Get Maynooth University exam papers.")
    
    parser.add_argument('module', type=str,
                        help="the code of the module you want papers for "
                        "e.g. 'CS211'")
    parser.add_argument('cookie', type=str,
                        help="a JSON file with the key and value of your "
                        "session cookie OR the key and value as separated by '='")
    parser.add_argument('-l', '--minyear', type=int,
                        help="the inclusive lower bound of the range of years you "
                        "want papers for")
    parser.add_argument('-u', '--maxyear', type=int,
                        help="the non-inclusive upper bound of the "
                        "range of years you want papers for")
    parser.add_argument('-r', '--noresits', action='store_true',
                        help="exclude papers from Autumn exam periods")
    parser.add_argument('-s', '--save', action='store_true',
                        help="save the exam papers to current working directory "
                        "instead of printing links to stdout")
    
    args = parser.parse_args()
    
    if os.path.isfile(args.cookie):
        with open(args.cookie, 'r') as cookiefile:
            cookie = json.load(cookiefile)
    else:
        parts = args.cookie.split('=')
        if len(parts) == 2:
            name, value = parts
            cookie = { name: value }
        else:
            raise ArgumentError('inavlid session cookie', 
            argument=args.cookie, parser=parser)
        
    try:
        soup = _get_page_soup(args.module, cookie)
    except Exception:
        print('error: failed to scrape webpage')
        exit(1)
    
    papers = _extract_papers_details(soup)

    if args.minyear or args.maxyear:
        def year_filter(pair):
            year = pair[0]
            if args.minyear and year < args.minyear:
                return False
            if args.maxyear and year >= args.maxyear:
                return False
            return True
        papers = dict(filter(year_filter, papers.items()))
    
    if args.noresits:
        def period_filter(pair):
            period = pair[0]
            return period != 'Autumn' and period != 'Repeat'
        for pair in papers.items():
            year, value = pair
            papers[year] = dict(filter(period_filter, papers[year].items()))
    
    for year in papers.keys():
        for period in papers[year].keys():
            url = papers[year][period]['url']
            filename = papers[year][period]['filename']
            if args.save:
                _download_pdf(url, filename, cookie=cookie)
                print(f"saved {filename}")
            else:
                print(url)


if __name__ == "__main__":
    main()
