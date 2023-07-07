import os

import asyncio
import requests
import telegram

from dotenv import load_dotenv, find_dotenv


async def main():
    load_dotenv(find_dotenv())
    TOKEN = os.environ['TOKEN']
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CHAT_ID = os.environ['CHAT_ID']

    url = 'https://dvmn.org/api/long_polling/'
    header = {
        'Authorization': f'Token {TOKEN}'
        }
    timestamp = ''

    bot = telegram.Bot(BOT_TOKEN)
    while True:
        try:
            params = {'timestamp': timestamp}
            response = requests.get(url, headers=header, params=params, timeout=120)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.ConnectionError as err:
            await asyncio.sleep(180)
            print(err)
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
                async with bot:
                    await bot.send_message(text=f'У Вас проверили работу «{lesson_title}»\n\n{add_text}\n\n {lesson_url}', chat_id=CHAT_ID)


if __name__ == '__main__':
    asyncio.run(main())
