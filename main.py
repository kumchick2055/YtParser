from tls_client import Session
from json import loads, dumps
from time import sleep
from datetime import datetime
from random import choice
from time import time
import re
import os
from config import *
from database import *

FOLDER_WORK = './results'


class Helper:
    @staticmethod
    def get_context(page_content):
        return loads(page_content.split('INNERTUBE_CONTEXT":')[1].split(',"INNERTUBE_CONTEXT_CLIENT_NAME')[0])

    @staticmethod
    def get_profile_data_token(page_content):
        return page_content.split('CONTINUATION_TRIGGER_ON_ITEM_SHOWN')[-1].split('","request":"CONTINUATION_REQUEST_TYPE_BROWSE"')[0].split('token":"')[-1]
    
    @staticmethod
    def get_api_key(page_content):
        return page_content.split('INNERTUBE_API_KEY":"')[1].split('"')[0]
    
    @staticmethod
    def extract_number(subscriber_string):
        if subscriber_string[-1] == 'M':
            return float(subscriber_string[:-1]) * 1000000
        elif subscriber_string[-1] == 'K':
            return float(subscriber_string[:-1]) * 1000
        else:
            return float(subscriber_string)

    @staticmethod
    def get_number_of_subscribers(page_content):
        subscriber_count_raw = page_content.split('subscriberCountText":"')[1].split(' ')[0]
        return Helper.extract_number(subscriber_count_raw)
    
    @staticmethod
    def get_views(page_content):
        views_raw = page_content.split('viewCountText":"')[1].split(' ')[0].replace(',', '')
        return float(views_raw)

    @staticmethod
    def get_country(page_content):
        country = page_content.split('country":"')[1].split('"')[0]
        return country

    @staticmethod
    def get_joined_date(page_content):
        joined_date = page_content.split('"content":"Joined ')[1].split('"')[0]
        return datetime.strptime(joined_date, '%b %d, %Y').year

    @staticmethod
    def get_initial_data(page_content):
        initial_data = page_content.split('">var ytInitialData =')[1].split(';</script>')[0]
        initial_data_json = loads(initial_data)

        return initial_data_json

    @staticmethod
    def extract_links(page_content):
        links = {
            'telegram': [],
            'instagram': [],
            'facebook': [],
            'twitter': []
        }

        telegram_regex = r'(https?:\/\/t\.me\/[a-zA-Z0-9_]+|t\.me\/[a-zA-Z0-9_]+)'
        instagram_regex = r'(https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9_]+|(www\.)?instagram\.com\/[a-zA-Z0-9_]+)'
        facebook_regex = r'(https?:\/\/(www\.)?facebook\.com\/[a-zA-Z0-9_]+|(www\.)?facebook\.com\/[a-zA-Z0-9_]+)'
        twitter_regex = r'(https?:\/\/(www\.)?twitter\.com\/[a-zA-Z0-9_]+|(www\.)?twitter\.com\/[a-zA-Z0-9_]+)'

        links['telegram'] = re.findall(telegram_regex, page_content)
        links['instagram'] = re.findall(instagram_regex, page_content)
        links['facebook'] = re.findall(facebook_regex, page_content)
        links['twitter'] = re.findall(twitter_regex, page_content)

        for key, value in links.items():
            if isinstance(value, list):
                if len(value) == 1 and isinstance(value[0], str):
                    links[key] = value[0]
                elif all(isinstance(item, str) for item in value):
                    links[key] = ', '.join(value)
                elif all(isinstance(item, tuple) and all(isinstance(subitem, str) for subitem in item) for item in value):
                    links[key] = ', '.join([subitem for item in value for subitem in item if subitem])
                else:
                    links[key] = ''
        
        if all(value == '' for i in links.values()):
            return None
        
        return links

class YtClient(Helper):
    def __init__(self):
        self.session = Session(
            client_identifier='chrome_102'
        )

        self.session.headers.update({
            'authority': 'youtube.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.5',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version-list': '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.225", "Google Chrome";v="120.0.6099.225"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })

    def change_proxy(self, proxy):
        self.session.proxies = proxy

    def clear_session_cookies(self):
        self.session.cookies.clear()

    def get_channels_from_list_videos(self, search_query: str) -> list:
        response = self.session.get('https://www.youtube.com/results', params={
            'search_query': search_query
        })

        channels_list = []

        initial_data_json = self.get_initial_data(response.text)

        contents = initial_data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
        continuation =  contents[-1]

        continuation_token = continuation['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']

        api_key = self.get_api_key(response.text)
        context = self.get_context(response.text)

        visitor_id = context['client']['visitorData']

        for i in contents[0]['itemSectionRenderer']['contents']:
            if i.get('videoRenderer'):
                print(i['videoRenderer']['title']['runs'][0]['text'])

                channels_list.append(i['videoRenderer']['longBylineText']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url'])

        while True:
            sleep(1)

            res = self.session.post('https://www.youtube.com/youtubei/v1/search', params={
                'key': api_key,
                'prettyPrint': 'false'
            }, headers={
                'x-goog-visitor-id': visitor_id,
                'x-youtube-bootstrap-logged-in': 'false',
                'x-youtube-client-name': '1',
                'x-youtube-client-version': '2.20240119.01.00'
            }, json={
                'context': context,
                'continuation': continuation_token
            })

            res_json = res.json()
            continuation_items = res_json['onResponseReceivedCommands'][0]['appendContinuationItemsAction']['continuationItems']

            if len(continuation_items) == 1:
                break

            continuation_token = continuation_items[-1]['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']

            for i in continuation_items[0]['itemSectionRenderer']['contents']:
                if i.get('videoRenderer'):
                    print(i['videoRenderer']['title']['runs'][0]['text'])

                    channels_list.append(i['videoRenderer']['longBylineText']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url'])

        print()
        return list(set(channels_list))

    def get_channel_info(self, channel_url: str):
        res = self.session.get(f'https://www.youtube.com{channel_url}/videos')

        profile_data = self.get_profile_data_token(res.text)
        context = self.get_context(res.text)
        api_key = self.get_api_key(res.text)
        visitor_id = context['client']['visitorData']

        initial_data_json = self.get_initial_data(res.text)
        contents = initial_data_json['contents']['twoColumnBrowseResultsRenderer']['tabs']

        video_list = []

        tab_content = None

        for i in contents:
            if i['tabRenderer'].get('title') == 'Videos':
                tab_content = i
                break

        if tab_content:
            for i in tab_content['tabRenderer']['content']['richGridRenderer']['contents']:
                if i.get('richItemRenderer'):
                    video_id = i['richItemRenderer']['content']['videoRenderer']['videoId']
                    video_list.append(video_id)

        video_list = video_list[:2]

        res = self.session.post('https://www.youtube.com/youtubei/v1/browse', params={
            'key': api_key,
            'prettyPrint': 'false'
        }, headers={
            'x-goog-visitor-id': visitor_id,
            'x-youtube-bootstrap-logged-in': 'false',
            'x-youtube-client-name': '1',
            'x-youtube-client-version': '2.20240119.01.00'
        }, json={
            'context': context,
            'continuation': profile_data
        })

        links = self.extract_links(res.text)

        if links is None:
            for i in video_list:
                video_data = self.session.post('https://www.youtube.com/watch', params={
                    'v': i
                })

                try:
                    split_html = video_data.text.split('"description":')[1].split('lengthSeconds')[0]
                    links = self.extract_links(split_html)
                except:
                    continue

                if links is not None:
                    break

        try:
            subscribers = self.get_number_of_subscribers(res.text)
        except:
            subscribers = None
        
        views = self.get_views(res.text)
        joined_date = self.get_joined_date(res.text)

        try:
            country = self.get_country(res.text)
        except:
            country = None

        return {
            'subscribers': subscribers,
            'views': views,
            'joined_date': joined_date,
            'country': country,
            'links': links,
            'channel_uniqname': channel_url if channel_url.startswith('/channel/') else channel_url[2:]
        }


def main() -> None:
    current_time = int(time())

    if not os.path.exists(FOLDER_WORK):
        os.makedirs(FOLDER_WORK)

    os.makedirs(FOLDER_WORK + f'/{current_time}')
    
    for i in ['twitter', 'facebook', 'instagram', 'telegram']:
        os.makedirs(FOLDER_WORK + f'/{current_time}/{i}')


    keywords = []
    proxy = []

    with open('./keywords.txt', 'r', encoding='utf-8') as f:
        keywords = list(filter(lambda i: i != '', f.read().splitlines()))
    
    with open('./proxy.txt', 'r', encoding='utf-8') as f:
        proxy = list(filter(lambda i: i != '', f.read().splitlines()))

    for i in keywords:
        client = YtClient()

        if USE_PROXY:
            client.change_proxy(PROTOCOL_PROXY + '://' + choice(proxy))

        try:
            channels = client.get_channels_from_list_videos(i)
        except Exception as ex:
            print('Ошибка в получении видео:', str(ex), f'\n\nЗапрос был: {i}\n\n')
            continue

        for j in channels:
            try:
                with DatabaseWorker() as db:
                    try:
                        data = client.get_channel_info(j)
                    except Exception as ex:
                        print('Ошибка в получении информации о канале:', str(ex), f'\n\Канал: {j}\n\n')
                        continue

                    if all(value == '' for value in data['links'].values()):
                        continue

                    if data['country'] in BLACKLIST_COUNTRY:
                        continue

                    if data['subscribers'] < SUBSCRIBERS:
                        continue

                    if data['views'] < VIEWS:
                        continue

                    if data['joined_date'] > YEAR:
                        continue

                    print(data)

                    if not db.check_user_exists(data):
                        db.append_user(data)

                        for x in data['links'].keys():
                            if data['links'][x]:
                                path = FOLDER_WORK + f'/{current_time}/{x}/{data["country"]}'

                                if not os.path.exists(path):
                                    os.makedirs(path)

                                with open(path + '/output.txt', 'a', encoding='utf-8') as f:
                                    f.write(dumps(data) + '\n')

            except Exception as ex:
                print(ex)


if __name__ == '__main__':
    main()
