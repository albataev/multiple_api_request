from modules_api import process_data_api
from modules_api.request_api import Fetcher
import aiohttp
from datetime import datetime
import pytz
import time
import asyncio
import ujson


def get_settings(fname = 'settings.json'):
    try:
        with open(fname, 'r') as f:
            settings = ujson.loads(f.read())
            print(settings)
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        raise
    except ValueError as e:
        print("Value error: {}".format(e))
        raise
    except:
        print("Unexpected error")
        raise
    return settings


settings = get_settings()
TIMEZONE = settings['timezone']
URL = settings['url']
#URL = 'http://ya.ru'
TIME_INTERVAL = settings['API_request_interval'] #60 interval between requests from the same IP
PROXY_LIST = settings['proxy_list']
JSON_KEY = 'result' #json item to be extracted from tje API response
PG_PARAMS = settings['database_credentials']

SQL = 'INSERT INTO crypto (ask, baseVolume, bid, created, high, last, low, \
marketName, openBuyOrders, openSellOrders, prevDay, timestamp, volume, query_tstamp, user_id) \
VALUES (%(Ask)s, %(BaseVolume)s, %(Bid)s, \
%(Created)s, %(High)s, %(Last)s, %(Low)s, %(MarketName)s, \
%(OpenBuyOrders)s, %(OpenSellOrders)s, %(PrevDay)s, %(TimeStamp)s, \
%(Volume)s, %(query_tstamp)s, %(user_id)s)' #database table and columns with corresponding
                                            # elements from JSON API response

NEW_ITEMS = {'query_tstamp': '',
            'user_id': 'user1'} #new fields to be added to each json item during json processing


def new_items(template):
    template['query_tstamp'] = datetime.fromtimestamp(time.time(), \
                            pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S.%f%z")
    return template


def _main(Fetcher_class, api_url, time_interval, proxy_list, Resp_formatter, new_items):
    loop = asyncio.get_event_loop()
    #build list of API requesters. Number of requesters is the number of proxies availaible
    requesters_list = [Fetcher_class(api_url, aiohttp.ClientSession(loop=loop), proxy) for proxy in proxy_list]
    resp_formatter = Resp_formatter()
    proxy_number = 0
    calc_interval = time_interval / len(proxy_list)
    try:
        db_writer = process_data_api.Db_writer(PG_PARAMS)
    except Exception as error:
        print('exception while db_writer', error)
    while True:
        try:
            response = loop.run_until_complete(requesters_list[proxy_number].fetch())
            formatted_response = resp_formatter.do(response, new_items(NEW_ITEMS), JSON_KEY)
            if formatted_response:
                print('formatted_response received')
                db_writer.prepare_request(SQL, formatted_response)
                db_writer.commit()
            else:
                print('incorrect response received', formatted_response)
                #log somewhere
            proxy_number += 1
            print('sleeping...:', calc_interval)
            time.sleep(calc_interval)
            if proxy_number == len(proxy_list): #finished looping over proxy list
                proxy_number = 0
        except KeyboardInterrupt:
            print('keyboard interrupt')
            for requester in requesters_list:
                requester.close_session()
            db_writer.close()
            break


if __name__ == '__main__':
    _main(Fetcher, URL, TIME_INTERVAL, PROXY_LIST, process_data_api.Format_resp, new_items)
    print('new items', NEW_ITEMS)
