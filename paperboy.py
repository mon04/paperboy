import requests
import json
import os.path
from bs4 import BeautifulSoup as bs
from argparse import ArgumentParser, ArgumentError
from enum import Enum


ExamPeriod = Enum('ExamPeriod', ['January', 'Summer', 'Autumn', 'Unknown'])

class ExamPaper():
    def __init__(self, module : str, year : int, exam_period : ExamPeriod, url : str):
        self.module = module
        self.year = year
        self.exam_period = exam_period
        self.url = url
    
    def __str__(self):
        return f"{{ 'module': '{self.module}', 'year': '{self.year}', 'exam_period': '{self.exam_period}' }}"


def _get_page_soup(module: str, cookie: dict) -> bs:
    url = f"https://www.maynoothuniversity.ie/library/exam-papers?code_value_1={module}"
    response = requests.get(url, cookies=cookie)
    if response.ok:
        data = response.content.decode(encoding='ansi')
        soup = bs(data, "html.parser")
        return soup
    else:
        raise Exception('HTTP request failed: {response}', response)


def _extract_papers(soup: bs) -> dict:
    links = [div.a for div in soup.find_all("span", {'class': "file"})]
    extracted = []
    for link in links:
        url = link['href']
        filename = link.text.strip()
        year, module, exam_period = filename.rstrip('.pdf').split('-')
        year = int(year)
        _, exam_period = _validate_exam_period(exam_period)
        extracted.append(ExamPaper(module, year, exam_period, url))
    return extracted


def _validate_exam_period(exam_period : str) -> (bool, ExamPeriod):
    exam_period = exam_period.lower()
    if exam_period == 'january':
        return (True, 'January')
    if exam_period == 'summer':
        return (True, 'Summer')
    if exam_period == 'autumn' or exam_period == 'repeat':
        return (True, 'Autumn')
    return (False, 'Unknown')


def _generate_filename(paper: ExamPaper):
    return f"{paper.module}-{paper.year}-{paper.exam_period}.pdf"


def _download_pdf(url, filename, cookie):
    response = requests.get(url, cookies=cookie)
    with open(filename, mode='wb') as file:
        file.write(response.content)


def main():
    parser = ArgumentParser(
        description="Get Maynooth University exam papers.")
    
    parser.add_argument('module', type=str,
                        help="the code of the module you want papers for "
                        "e.g. 'CS211'")
    parser.add_argument('cookie', type=str,
                        help="your session cookie in the format 'NAME=VALUE' "
                        "OR path to a JSON file of your session cookie")
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
    
    papers = _extract_papers(soup)

    if args.minyear :
        papers = filter(lambda p: p.year >= args.minyear, papers)
    
    if args.maxyear:
        papers = filter(lambda p: p.year < args.maxyear, papers)
    
    if args.noresits:
        papers = filter(lambda p: p.exam_period != 'Autumn')
    
    for paper in papers:
        if args.save:
            filename = _generate_filename(paper)
            _download_pdf(paper.url, filename, cookie=cookie)
            print(f"Saved: {filename}")
        else:
            print(paper.url)


if __name__ == "__main__":
    main()
