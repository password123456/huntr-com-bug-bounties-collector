__author__ = 'https://github.com/password123456/'
__date__ = '2023.02.12'
__version__ = '1.0.0'
__status__ = 'Production'

import os
import sys
import requests
import hashlib
import datetime
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

_home_path_ = f'{os.getcwd()}'
_feed_list_ = f'{_home_path_}/list.txt'


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
    chrome_service = ChromeService(executable_path=ChromeDriverManager().install())
    options = Options()
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/110.0.0.0 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--headless')
    options.add_experimental_option('detach', True)    
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(service=chrome_service, options=options)
    return driver


def feeds_exist_in_db(_feed_db, _check_hash):
    try:
        if os.path.exists(_feed_db):
            mode = 'r'
        else:
            mode = 'w'

        with open(_feed_db, mode) as database:
            for line in database:
                loaded_hash = str(line.split(',')[2].replace('\n', ''))
                if str(_check_hash) in str(loaded_hash):
                    return True
            return False
    except Exception as e:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{feeds_exist_in_db.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')


def get_feed_url():
    try:
        if os.path.exists(_feed_list_):
            with open(_feed_list_, 'rt', encoding='utf-8') as f:
                for line in f:
                    if not line.startswith('#'):
                        _feed_category = line.split(',')[0].strip()
                        _feed_name = line.split(',')[1].strip()
                        _feed_url = line.split(',')[2].strip()

                        if _feed_category and _feed_url and _feed_name:
                            if _feed_name == 'huntr':
                                get_huntr_dev(_feed_name, _feed_url)
                            else:
                                sys.exit(0)
                        else:
                            print(f'{Bcolors.Yellow}- Feed config is invalid.! check {_feed_list_} {Bcolors.Endc}')
                            sys.exit(1)
            f.close()
        else:
            print(f'{Bcolors.Yellow}- RSS Feed file not found.! check {_feed_list_} {Bcolors.Endc}')
    except Exception as e:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{get_feed_url.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')


def get_huntr_dev(_feed_name, _feed_url):

    _feed_db = f'{_home_path_}/{datetime.date.today().strftime("%Y%m%d")}_{_feed_name}_feeds.db'

    if os.path.exists(_feed_db):
        mode = 'a'
    else:
        mode = 'w'

    # run chrome webdriver
    driver = chrome_webdriver()
    driver.get(_feed_url)
    driver.implicitly_wait(10)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    table = soup.find('table', id='hacktivity-table')
    rows = table.find_all('tr')

    message = ''
    n = 0
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
                link = f"https://huntr.dev{item.find('a', class_='hover:text-blue-400')['href']}"
                date = item.find('div', class_="text-sm font-medium opacity-50 float-right hidden md:inline-block").text.strip()
                product = item.find('a', class_="hover:text-blue-400 cursor-pointer ml-1 mr-1.5 underline").text.strip()
                product = product.replace(' ', '').replace('\n', '')
                cve = item.find('a', class_='font-medium float-right hidden md:inline underline hover:text-blue-400 ml-2').text.strip()
                if not cve.startswith('CVE'):
                    cve = 'CVE: Not yet'
                severity = item.find('span', class_='self-end h-3').text.strip()
            except Exception as e:
                print(f'{Bcolors.Yellow}- Exception::{e} {Bcolors.Endc}')
                message = f'Exception: {_feed_name}\n- One of the variable is empty\n\n' \
                          f'> title: {title}\n> link: {link}\n> date: {date}\n' \
                          f'> product: {product}\n> severity: {severity}\n> cve_id: {cve}'
                message = f'{datetime.datetime.now()}\n\n{message}'
                print(message)
                sys.exit(1)

            # if all variables are not empty, continue processing
            if title and link and date and product and severity:
                _hashed_article = sha1_hash(f'{title}_{str(link)}')
                _hash_result = sha1_hash(_hashed_article)

                if not feeds_exist_in_db(_feed_db, _hash_result):
                    n = n + 1
                    fa.write(f'{n},{datetime.datetime.now()},{_hash_result},{_feed_name},{link}\n')
                    contents = f'{n}. {title}\n- {date} / {severity} ({cve})\n- {product}\n-{link}\n\n'
                    message += contents

    if message:
        message = f'{datetime.datetime.now()}\n\n{message}'
        print(message)
        # If you want to send a message to somewhere, code it here.
    else:
        print(f'{Bcolors.Blue}>>> [OK] ({datetime.date.today()}) No NEW vulnerability bounty: [{_feed_name}] {Bcolors.Endc}')


def main():
    get_feed_url()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{__name__.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')
