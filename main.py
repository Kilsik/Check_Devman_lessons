from logging import LogRecord
import os
import time
import asyncio
import requests
import telegram
import logging

from dotenv import load_dotenv, find_dotenv


def main():
    load_dotenv(find_dotenv())
    TOKEN = os.environ['TOKEN']
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CHAT_ID = os.environ['CHAT_ID']
    bot = telegram.Bot(BOT_TOKEN)

    class TelegramBotHandler(logging.Handler):

        def emit(self, record):
            log_entry = self.format(record)
            bot.send_message(text=log_entry, chat_id=CHAT_ID)

    logger = logging.getLogger('check_lessons')
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramBotHandler())

    url = 'https://dvmn.org/api/long_polling/'
    header = {
        'Authorization': f'Token {TOKEN}'
        }
    timestamp = ''

    logger.info('Bot started')
    while True:
        try:
            params = {'timestamp': timestamp}
            response = requests.get(url, headers=header, params=params, timeout=20)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            logger.info('Надо ж дать')
            continue
        except requests.ConnectionError as err:
            time.sleep(180)
            logger.error(err)
            continue
        response_attempts = response.json()
        if 'timestamp_to_request' in response_attempts:
            timestamp = response_attempts['timestamp_to_request']
        else:
            timestamp = response_attempts['last_attempt_timestamp']
            new_attempts = response_attempts['new_attempts']
            for attempt in new_attempts:
                lesson_title = attempt['lesson_title']
                if attempt['is_negative']:
                    add_text = 'К сожалению, в работе нашлись ошибки.'
                else:
                    add_text = 'Преподавателю все понравилось, можно приступать к следующему уроку!'
                lesson_url = attempt['lesson_url']
                bot.send_message(text=f'У Вас проверили работу «{lesson_title}»\n\n{add_text}\n\n {lesson_url}', chat_id=CHAT_ID)


if __name__ == '__main__':
    main()
