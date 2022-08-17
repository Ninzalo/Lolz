import requests
import os
import re
import json
import random
import time
import datetime
from bs4 import BeautifulSoup
from typing import List, Literal


def page_tab(page: int) -> str:
    if page < 10:
        page_str = f'  {page}'
    elif page < 100 and page >= 10:
        page_str = f' {page}'
    else:
        page_str = f'{page}'
    return page_str


def num_tab(num: int) -> str:
    if num >= 10000:
        num_str = f'{num}'
    elif num >= 1000:
        num_str = f' {num}'
    elif num >= 100:
        num_str = f'  {num}'
    elif num >= 10:
        num_str = f'   {num}'
    else:
        num_str = f'    {num}'
    return num_str


def fetch_threads(headers, cookies, session):
    overall_time = datetime.datetime.now()
    all_thread_links = []
    for page in range(1, 500)[:]:
        try:
            start_time = datetime.datetime.now()
            page_links = threads_parse(page=page, session=session, 
                    headers=headers, cookies=cookies)
            for url in page_links:
                all_thread_links.append(url)
            time.sleep(random.randrange(1, 3))
            page = page_tab(page=page)
            print(f'[INFO] Page {page} / 500 completed in '\
                    f'{datetime.datetime.now() - start_time}')
        except:
            print(f'[INFO] Error on page {page} / 500')
    with open('thread_urls.json', 'w') as f:
        json.dump(all_thread_links, f, indent=4, ensure_ascii=False)
    print(f'[INFO] Finished in {datetime.datetime.now() - overall_time}')


def check_amount(path: str, params: list|None=None):
    with open(path, encoding='utf-8') as f:
        list_of_items = json.load(f)
    all_posts = list_of_items
    if params:
        if 'no_hide' in params:
            list_of_items = [i for i in list_of_items if i['hide'] == 0]
        elif 'hide' in params:
            list_of_items = [i for i in list_of_items if i['hide'] == 1]

        if 'is_video' in params:
            list_of_items = [i for i in list_of_items if i['is_video'] == 1]
        elif 'no_video' in params:
            list_of_items = [i for i in list_of_items if i['is_video'] == 0]

        if 'is_pack' in params:
            list_of_items = [i for i in list_of_items if i['is_pack'] == 1]
        elif 'no_pack' in params:
            list_of_items = [i for i in list_of_items if i['is_pack'] == 0]

        if 'is_only' in params:
            list_of_items = [i for i in list_of_items if i['is_only'] == 1]
        elif 'no_only' in params:
            list_of_items = [i for i in list_of_items if i['is_only'] == 0]

        all_posts = list_of_items
        if 'mail' in params:
            list_of_items = [i for i in list_of_items if 'cloud.mail' in i['message'].lower()]

            for item in list_of_items:
                item['message'] = item['message'].replace(r'\n', ' ').replace(f'\n', ' ')

            for item in list_of_items:
                links_in_message = re.findall(r'(https?://\S+)', item['message'])
                links_in_message = [i for i in links_in_message if 'cloud.mail' in i.lower()]
                item['links_in_message'] = links_in_message
                all_posts.append(item)

        if 'yandex' in params:
            list_of_items = [i for i in all_posts if 'disk.yandex' in i['message'].lower()]

            for item in list_of_items:
                item['message'] = item['message'].replace(r'\n', ' ').replace(f'\n', ' ')

            for item in list_of_items:
                links_in_message = re.findall(r'(https?://\S+)', item['message'])
                links_in_message = [i for i in links_in_message if 'disk.yandex' in i.lower()]
                item['links_in_message'] = links_in_message
                all_posts.append(item)

        for post in all_posts:
            if str(post.get('links_in_message')) == 'None':
                post['links_in_message'] = []


    output_text = f'[INFO] Amount is {len(all_posts)}'
    if params:
        output_text += f' with params {params}'
    print(output_text)
    return all_posts


def threads_parse(page: int, headers, cookies, session):
    url = f'https://lolz.guru/forums/media-leaks18/page-{page}'
    resp = session.get(url=url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(resp.text, 'lxml')
    page_links_list = []
    all_page_links = soup.find('div', class_='latestThreads _insertLoadedContent')
    all_page_divs = all_page_links.find_all('div', class_='discussionListItem--Wrapper')
    for div in all_page_divs[:]:
        try:
            href = div.find('a', class_='listBlock main PreviewTooltip').get('href')
            href = f'https://lolz.guru/{href}'
            page_links_list.append(href)
        except:
            pass
    return page_links_list


def fetch_posts(thread_urls, headers, cookies, session):
    with open(thread_urls) as f:
        list_of_threads = json.load(f)
    list_of_threads = set(list_of_threads)
    list_of_threads = list(list_of_threads)
    print(f'Fetched amount - {len(list_of_threads)}')
    list_of_dicts = []
    for url in list_of_threads[:]:
        try:
            page_dict = post_parse(url=url, 
                    cookies=cookies, session=session)
            list_of_dicts.append(page_dict)
            time.sleep(random.randrange(1,3))
        except:
            pass
    with open('page_dict.json', 'w', encoding='utf-8') as f:
        json.dump(list_of_dicts, f, indent=4, ensure_ascii=False)


def post_parse(url: str, cookies, session):
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
        'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    resp = session.get(url=url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(resp.content, 'lxml')
    title_bar = soup.find('div', class_='titleBar')

    video_prefix = title_bar.find('span', class_='prefix videoleaks general')
    if str(video_prefix) != 'None':
        is_video = 1
    else:
        is_video = 0

    prefix_general = title_bar.find('span', class_='prefix general')
    if str(prefix_general) != 'None':
        if str(prefix_general.text.strip()) == 'OnlyFans':
            is_only = 1
        else:
            is_only = 0
        if str(prefix_general.text.strip()) == 'Пак':
            is_pack = 1
        else:
            is_pack = 0
    else:
        is_pack = 0
        is_only = 0

    title = title_bar.find('h1').get('title')

    page_description = title_bar.find('p', id='pageDescription')
    date = page_description.find('span', class_='DateTime').get('title')

    all_messages = soup.find('ol', class_='messageList')
    all_messages = all_messages.find_all('li')
    needed_message = all_messages[0]
    message_content = needed_message.find('div', class_='messageContent')
    hide = message_content.find('div', class_='bbCodeBlock bbCodeQuote bbCodeHide')
    return_dict = {}
    if str(hide) != 'None':
        # print(f'Hide in thread {title} {url}')
        message = message_content.find('blockquote', class_='messageText SelectQuoteContainer baseHtml ugc')
        return_dict['hide'] = 1
    else:
        print(f'{url} | {title}')
        message = message_content.find('blockquote', class_='messageText SelectQuoteContainer baseHtml ugc')
        return_dict['hide'] = 0
    return_dict['title'] = str(title)
    return_dict['url'] = url
    return_dict['date'] = date
    return_dict['message'] = message.text.strip().replace(f'\n', ' ')
    return_dict['is_video'] = is_video
    return_dict['is_pack'] = is_pack
    return_dict['is_only'] = is_only
    
    return return_dict


def count_links(needed_posts: list):
    links_in_posts = []
    for post in needed_posts:
        for link in post['links_in_message']:
            links_in_posts.append({
                'hide': post['hide'],
                'title': post['title'],
                'url': post['url'],
                'date': post['date'],
                'message': post['message'],
                'is_video': post['is_video'],
                'is_pack': post['is_pack'],
                'is_only': post['is_only'],
                'link': link
                })
    return links_in_posts


def mail_validate(url: str, session):
    headers = {
        'authority': 'xray.mail.ru',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://cloud.mail.ru',
        'referer': 'https://cloud.mail.ru/',
        'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
    }
    resp = session.get(url=url, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    error = soup.find('div', class_='http-error__message__title')
    # print(url, error)
    return url, str(error)
    

def yandex_validate(url: str, session):
    headers = {
        'authority': 'mc.yandex.ru',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'origin': 'https://disk.yandex.ru',
        'referer': 'https://disk.yandex.ru/',
        'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
    }
    resp = session.get(url=url, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    error = soup.find('div', class_='error__title')
    # print(url, error)
    return url, str(error)


def validate(links_in_posts: list, params: list, session):
    validated_urls = []
    failed = []
    validated_urls_mail = []
    validated_urls_yandex = []
    iteration = 0
    while True:
        if 'mail' in params:
            links_for_mail = [i for i in links_in_posts if 'cloud.mail' in i['link']]
            for num, post in enumerate(links_for_mail[:]):
                try:
                    _, error = mail_validate(url=post['link'], session=session)
                    if error == 'None':
                        validated_urls_mail.append(post)
                        error = 0
                    else:
                        error = 1
                    time.sleep(random.randrange(1,2))
                    print(f'[MAIL] Validated {num_tab(num + 1)} / '\
                            f'{len(links_for_mail)} | Error - {error} | '\
                            f'Amount of fails - {len(failed)}')
                except:
                    failed.append(post)
                    time.sleep(random.randrange(5, 10))

            with open('validate_mail.json', 'w', encoding='utf-8') as f:
                json.dump(validated_urls_mail, f, indent=4, ensure_ascii=False)

            for item in validated_urls_mail:
                validated_urls.append(item)

        if 'yandex' in params:
            links_for_yandex = [i for i in links_in_posts if 'disk.yandex' in i['link']]
            for num, post in enumerate(links_for_yandex[:]):
                try:
                    _, error = yandex_validate(url=post['link'], session=session)
                    if error == 'None':
                        validated_urls_yandex.append(post)
                        error = 0
                    else:
                        error = 1
                    time.sleep(random.randrange(1,2))
                    print(f'[YANDEX] Validated {num_tab(num + 1)} / '\
                            f'{len(links_for_yandex)} | Error - {error} | '\
                            f'Amount of fails - {len(failed)}')
                except:
                    failed.append(post)
                    time.sleep(random.randrange(5, 10))

            with open('validate_yandex.json', 'w', encoding='utf-8') as f:
                json.dump(validated_urls_yandex, f, indent=4, ensure_ascii=False)

            for item in validated_urls_yandex:
                validated_urls.append(item)
        if len(failed) == 0:
            break
        else:
            links_in_posts = [i for i in failed]
            failed = []
        iteration += 1
        if iteration > len(failed) + 100:
            break

    return validated_urls


def main() -> None:
    cookies = {
        '_ga': 'GA1.1.1431711472.1644256167',
        '_ym_d': '1644256168',
        '_ym_uid': '1644256168315320725',
        'G_ENABLED_IDPS': 'google',
        'xf_tfa_trust': '-nArGv6YsXQCTJMcX8hXqUxLTwHn05dm',
        'xf_user': '377204%2C088050a9dedaeb180895c6cb1c3e71ae0d005b8b',
        'xf_logged_in': '1',
        'xf_is_not_mobile': '1',
        'sfwefwe': 'c95d0e3eac77971eece8bc4e8458f82d',
        '_ym_isad': '1',
        'xf_session': 'edbdf43ae31d64a39d3dd2e53feaf756',
        'xf_feed_custom_order': 'last_post_date',
        '_ga_J7RS527GFK': 'GS1.1.1659122496.124.1.1659125772.0',
    }
    headers = {
        'authority': 'lolz.guru',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'referer': 'https://lolz.guru/forums/media-leaks18/',
        'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
        'x-requested-with': 'XMLHttpRequest',
    }
    start_time = datetime.datetime.now()
    session = requests.Session()
    # fetch_threads(headers=headers, cookies=cookies, session=session)
    check_amount(path='thread_urls.json')
    # fetch_posts(thread_urls='thread_urls.json', headers=headers , 
    #         cookies=cookies, session=session)
    params = ['no_hide', 'mail', 'yandex']
    needed_posts = check_amount(path='page_dict.json', params=params)
    links_in_posts = count_links(needed_posts=needed_posts)
    # links_in_posts = set(links_in_posts)
    # links_in_posts = list(links_in_posts)

    # validated_urls = validate(links_in_posts=links_in_posts, params=params, 
            # session=session)

    validated_urls = []
    with open('validate_mail.json', encoding='utf-8') as f:
        urls = json.load(f)
        for url in urls:
            validated_urls.append(url)
    with open('validate_yandex.json', encoding='utf-8') as f:
        urls = json.load(f)
        for url in urls:
            validated_urls.append(url)

    print(f'[INFO] Validation finished in '\
            f'{datetime.datetime.now() - start_time}')

    if 'mail' in params or 'yandex' in params:
        print(f'[INFO] All amount of valid urls {len(validated_urls)}')
    for item in validated_urls:
        if item['is_video'] == 1:
            print(item['link'])



if __name__ == '__main__':
    main()
