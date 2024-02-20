__author__ = 'https://github.com/password123456/'
__date__ = '2024.02.20'
__version__ = '1.0.4'
__status__ = 'Production'

import os
import sys
import requests
import hashlib
import datetime
import time
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


def sha1_hash(string):
    return hashlib.sha1(string.encode()).hexdigest()


def chrome_webdriver():
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/110.0.0.0 Safari/537.36'
    options = webdriver.ChromeOptions()
    # options.add_argument("--start-maximized")
    options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    service = Service(executable_path=r'$$your-chrome-webdriver-path$$')
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def data_exist_in_db(_feed_db, _hash_to_check):
    try:
        if os.path.exists(_feed_db):
            mode = 'r'
        else:
            mode = 'w'
        with open(_feed_db, mode) as database:
            for line in database:
                if not len(line.strip()) == 0:
                    hash_in_db = str(line.split('|')[2].replace('\n', ''))
                    if str(_hash_to_check) in str(hash_in_db):
                        return True
        return False
    except Exception as e:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{data_exist_in_db.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')


def retrieve_huntr_cve_details(_feed_url, _feed_db):
    # execute chrome webdriver
    driver = chrome_webdriver()
    driver.get(_feed_url)
    driver.implicitly_wait(10)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    try:
        table = soup.find('table', id='hacktivity-table')
        rows = table.find_all('tr')
    except AttributeError as error:
        message = f'{datetime.datetime.now()}\n' \
                  f'[{retrieve_huntr_cve_details.__name__}]\n{error}\n\n' \
                  f'>> Failed to parse HTML elements -> hacktivity-table<<\n'
        print(f'{Bcolors.Yellow} {message} {Bcolors.Endc}')
        ## Send the result to webhook. ##
        sys.exit(1)

    message = ''
    n = 0

    if os.path.exists(_feed_db):
        mode = 'a'
    else:
        mode = 'w'

    with open(_feed_db, mode, encoding='utf-8') as fa:
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
                date = item.find('div', class_="text-sm font-medium opacity-50 float-right hidden md:inline-block").text.strip()
                product = item.find('a', class_="hover:text-blue-400 cursor-pointer ml-1 mr-1.5 underline").text.strip()
                product = product.replace(' ', '').replace('\n', '')
                cve = item.find('a', class_='font-medium float-right hidden md:inline underline hover:text-blue-400 ml-2').text.strip()
                if not cve.startswith('CVE'):
                    cve = 'CVE: Not yet'
                severity = item.find('span', class_='self-end h-3').text.strip()
            except AttributeError:
                print(f'{Bcolors.Yellow}- Exception::{e} {Bcolors.Endc}')
                message = f'Exception: One of the variable is empty\n\n' \
                          f'> title: {title}\n> link: {link}\n> date: {date}\n' \
                          f'> product: {product}\n> severity: {severity}\n> cve_id: {cve}'
                message = f'*{datetime.datetime.now()}*\n\n{message}'
                print(f'{Bcolors.Yellow} {message} {Bcolors.Endc}')
                ## Send the result to webhook. ##
                sys.exit(1)

            # if all variables are not empty, continue processing
            if title and link and date and product and severity:
                _hashed_article = sha1_hash(f'{title}_{str(link)}')
                _hash_result = sha1_hash(_hashed_article)

                if not data_exist_in_db(_feed_db, _hash_result):
                    n = n + 1
                    fa.write(f'{n}|{datetime.datetime.now()}|{_hash_result}|{cve}|{link}\n')
                    contents = f'{n}. {title}\n- {date} / {severity} ({cve})\n- {product}\n- {link}\n\n'
                    message += contents

    if message:
        message = f'{datetime.datetime.now()}\n\n{message}'
        print(message)
    else:
        print(f'{Bcolors.Blue}>>> [OK] ({datetime.datetime.now()}) No New Threads {Bcolors.Endc}')


def main():
    home_path = f'{os.getcwd()}'
    feed_db = f'{home_path}/feeds.db'
    feed_url = 'https://huntr.com/bounties/hacktivity'

    retrieve_huntr_cve_details(feed_url, feed_db)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{__name__.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')
        
