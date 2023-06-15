import requests
import os

from dotenv import load_dotenv, find_dotenv



load_dotenv(find_dotenv())
TOKEN = os.environ['TOKEN']


def main():
    url = 'https://dvmn.org/api/long_polling/'
    header = {
        'Authorization': f'Token {TOKEN}'
        }
    flag = True
    while flag:
        response = requests.get(url, headers=header, timeout=60)
        response.raise_for_status()
        print(response.json())


if __name__ == '__main__':
    main()