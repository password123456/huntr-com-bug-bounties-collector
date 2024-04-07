__author__ = 'https://github.com/password123456/'
__date__ = '2024.04.02'
__version__ = '1.0.7'
__status__ = 'Production'

import os
import sys
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class Bcolors:
    Black = '\033[30m'
    Red = '\033[31m'
    Green = '\033[32m'
    Yellow = '\033[33m'
    Blue = '\033[34m'
    Magenta = '\033[35m'
    Cyan = '\033[36m'
    White = '\033[37m'
    Endc = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def sha256_hash(string):
    return hashlib.sha256(string.encode()).hexdigest()


def chrome_webdriver():
    chromedriver_path = 'your-chrome-webdriver-path'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/123.0.0.0 Safari/537.36'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f'user-agent={user_agent}')
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def feeds_exists_in_db(feed_db, _hash_to_check):
    try:
        if os.path.exists(feed_db):
            mode = 'r'
        else:
            mode = 'w'
        with open(feed_db, mode, encoding='utf-8') as database:
            for line in database:
                if not len(line.strip()) == 0:
                    hash_in_db = str(line.split('|')[2].replace('\n', ''))
                    if str(_hash_to_check) in str(hash_in_db):
                        return True
        return False
    except Exception as error:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{feeds_exists_in_db.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(error).__name__}] {error}{Bcolors.Endc}', flush=True)


def retrieve_huntr_entries(feed_url, feed_db):
    driver = chrome_webdriver()
    driver.get(feed_url)
    driver.implicitly_wait(10)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    parse_table_id = 'hacktivity-table'
    try:
        table = soup.find('table', id=parse_table_id)
        rows = table.find_all('tr')
    except AttributeError as error:
        message = (f'{os.path.realpath(__file__)}\n\n'
                   f'- [func]: {retrieve_huntr_entries.__name__}\n*{error}*\n\n'
                   f'- [exception]: {feed_url}\n-  Failed to parse HTML elements "{parse_table_id}"')
        print(f'{Bcolors.Yellow}[-] Error: {message} {Bcolors.Endc}\n\n')
        sys.exit(1)

    content_result = ''
    n = 0

    if os.path.exists(feed_db):
        mode = 'a'
    else:
        mode = 'w'

    with open(feed_db, mode, encoding='utf-8') as fa:
        for item in rows:
            title = ''
            link = ''
            date = ''
            product = ''
            cve = ''
            severity = ''
            try:
                title = item.find('a', class_='hover:text-blue-400').text.strip()
                link = f"https://huntr.com{item.find('a', class_='hover:text-blue-400')['href']}"
                date = item.find('div', class_='float-right hidden text-sm font-medium opacity-50 md:inline-block').text.strip()
                product = item.find('a', class_='ml-1 mr-1.5 cursor-pointer underline hover:text-blue-400').text.strip()
                product = product.replace(' ', '').replace('\n', '')
                cve = item.find('a', class_='float-right ml-2 hidden font-medium underline hover:text-blue-400 md:inline').text.strip()
                if not cve.startswith('CVE'):
                    cve = 'CVE: Not yet'
                severity = item.find('span', class_='h-3 self-end').text.strip()
            except AttributeError:
                message = (f'{os.path.realpath(__file__)}\n\n'
                           f'- [func]: {retrieve_huntr_entries.__name__}\n'
                           f'- [exception]: {feed_url}\n-  One of the variable is empty\n'
                           f'> title: {title}\n> link: {link}\n> date: {date}\n'
                           f'> product: {product}\n> severity: {severity}\n> cve_id: {cve}')
                print(f'{Bcolors.Yellow}[-] Error: {message} {Bcolors.Endc}\n\n')
                sys.exit(1)

            # if all variables are not empty, continue processing
            if title and link and date and product and severity:
                hashed_article = sha256_hash(f'{title}_{str(link)}')
                hashed_data = sha256_hash(hashed_article)
                if not feeds_exists_in_db(feed_db, hashed_data):
                    n = n + 1
                    cve_product = f'https://github.com/{product}'
                    fa.write(f'{n}|{datetime.now()}|{hashed_data}|{cve}|{cve_product}|{link}\n')
                    contents = f'{n}. *{title}*\n- {date}\n- *{cve} ({severity})*\n- {cve_product}\n- {link}\n\n'
                    content_result += contents
    return content_result


def main():
    home_path = os.path.dirname(os.path.realpath(__file__))
    feed_db = f'{home_path}/feeds.db'
    feed_url = 'https://huntr.com/bounties/hacktivity'

    result_entries = retrieve_huntr_entries(feed_url, feed_db)
    if result_entries:
        print(result_entries)
        ## Send the result to webhook. ##

    else:
        message = (f'{os.path.realpath(__file__)}\n'
                   f'- [func]: {main.__name__}\n'
                   f'- [exception]: No retrieved new huntr Data\n')
        print(f'{Bcolors.Green}[-] OK: ({datetime.now()})\n{message} {Bcolors.Endc}\n\n')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{__name__.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')
