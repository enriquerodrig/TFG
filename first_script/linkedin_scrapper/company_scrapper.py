import sys
import os
from bs4 import BeautifulSoup
import regex as re

# Obtain the parent directory path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    # Add parent directory to path
    sys.path.append(path)

from json_handler import handler
from dependencies.crosslinked.search import get_agent, get_statuscode, web_request, extract_links
from dependencies.crosslinked.logger import Log

def scrap_company(target):
    """
    Scrap company page to obtain its description, address and phone number
    :param target: String with the name of the target company
    :returns: Title, description and data about company
    """
    data = {}

    # Define url and headers
    url = 'https://www.google.com/search?q=site:es.linkedin.com/company+{}&num=20&start=1'.format(target)
    # url = 'http://www.bing.com/search?q="{}"+site:linkedin.com/company&first={}'.format(target, 0)

    # Request the page
    resp = web_request(url)
    http_code = get_statuscode(resp)

    # Check if the request was successful
    if http_code == 200:
        # Obtain first result
        links = extract_links(resp)
        links = [link.get('href') for link in links if link is not None]

        for link in links:
            # print(link)
            
            # Check if the link is a company page
            if link and re.match(r'https://.?.?.?\.linkedin\.com/company/.*?'+target, link):
                print(link)
                # Request the page
                resp = web_request(link)
                http_code = get_statuscode(resp)
                print(resp)
                # Check if the request was successful
                if http_code == 200:
                    # Parse the page
                    data = parse_profile(resp)
                    break
    else:
        Log.warn('None 200 response, exiting search ({})'.format(http_code))

    return data

def parse_field(data):
    """
    Parse field of the company html page
    :param data: HTML raw string with the field
    :returns: String with the field
    """
    try:
        return data.text.strip()
    except:
        return ""

def parse_profile(page):
    """
    Parse html page to scrap company data
    :param page: HTML of the company page
    :returns: Data about the company
    """
    data = {"title": "", "description": "", "address": "", "phone": "", "n_employees": 0}
    soup = BeautifulSoup(page, 'html.parser')

    # Obtain title
    title = soup.find('h1')
    data['title'] = parse_field(title)

    return data

if __name__ == '__main__':
    # Obtain inputs and output template
    name = 'scassi'

    # Scrap company page
    company_data = scrap_company(name)

    print(company_data)
    

    