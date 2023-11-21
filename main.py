import os
import time
import requests
import telegram
import logging

from dotenv import load_dotenv, find_dotenv


class TelegramBotHandler(logging.Handler):

    def __init__(self, log_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.log_bot = log_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.log_bot.send_message(text=log_entry, chat_id=self.chat_id)


def main():
    load_dotenv(find_dotenv())
    token = os.environ['TOKEN']
    bot_token = os.environ['BOT_TOKEN']
    log_bot_token = os.environ['LOG_BOT_TOKEN']
    chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(bot_token)
    log_bot = telegram.Bot(log_bot_token)

    logger = logging.getLogger('check_lessons')
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramBotHandler(log_bot, chat_id))
    try:
        url = 'https://dvmn.org/api/long_polling/'
        header = {
            'Authorization': f'Token {token}'
            }
        timestamp = ''

        logger.info('Bot started')
        while True:
            try:
                params = {'timestamp': timestamp}
                response = requests.get(url, headers=header, params=params, timeout=120)
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
                    bot.send_message(text=f'У Вас проверили работу «{lesson_title}»\n\n{add_text}\n\n {lesson_url}', chat_id=chat_id)
    except Exception as err:
        logger.fatal(err)


if __name__ == '__main__':
    main()
