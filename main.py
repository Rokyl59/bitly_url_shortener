from dotenv import load_dotenv
import requests
import os
import argparse
from urllib.parse import urlparse


def is_bitlink(token, url):
    parser_url = urlparse(url)
    bitlink = f"{parser_url.netloc}{parser_url.path}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"https://api-ssl.bitly.com/v4/bitlinks/{url}",
        headers=headers
    )
    return response.ok


def shorten_link(token, long_url):
    headers = {"Authorization": f"Bearer {token}"}
    body = {"long_url": long_url}
    response = requests.post(
        "https://api-ssl.bitly.com/v4/bitlinks",
        json=body,
        headers=headers
    )
    response.raise_for_status()
    return response.json().get("link")


def count_clicks(token, bitlink):
    parsed_bitlink = urlparse(bitlink)
    clean_bitlink = f"{parsed_bitlink.netloc}{parsed_bitlink.path}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"unit": "day", "units": -1, "size": 1}
    response = requests.get(
        f"https://api-ssl.bitly.com/v4/bitlinks/{clean_bitlink}/clicks/summary",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json().get("total_clicks")


def main():
    parser = argparse.ArgumentParser(description='bit.ly link.')
    parser.add_argument('url', help='the url shorten or expand')
    args = parser.parse_args()

    load_dotenv()
    bitly_token = os.environ['BITLY_TOKEN']
    user_input_url = args.url

    actions = {
        True: (count_clicks, "Количество кликов по вашей ссылке: {}"),
        False: (shorten_link, "Сокращенная ссылка: {}")
    }

    try:
        parsed_url = urlparse(user_input_url)
        formatted_url = f"{parsed_url.netloc}{parsed_url.path}"
        is_link = is_bitlink(bitly_token, formatted_url)
        func, message = actions[is_link]
        result = func(bitly_token, user_input_url)
        print(message.format(
            result if result is not None else "Ошибка при получении данных"
        ))
    except requests.exceptions.HTTPError as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")


if __name__ == "__main__":
    main()
