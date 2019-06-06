import requests
import time
from functools import wraps
from lxml import etree

class HttpCodeException(Exception):
    pass

def retry(retry_count=5, sleep_time=1):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            for i in range(retry_count):
                try:
                    res = func(*args, **kwargs)
                    return res
                except:
                    time.sleep(sleep_time)
                    continue
            return None
        return inner
    return wrapper

@retry()
def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.87 Mobile Safari/537.36',
        'Host': 'www.weather.com.cn',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HttpCodeException
    res.encoding = 'utf-8'
    return res.text


def crawl_weather(url):
    html = get_html(url)
    html = etree.HTML(html)

    tem_lst = []
    tem_nodes = html.xpath("//ul[@class='clearfix']//p[@class='tem']")
    for index, node in enumerate(tem_nodes):
        info = {}
        # 像文件路径一样,连个. 表示上一级目录,找到父节点
        parent = node.xpath("..")[0]
        header = parent.xpath("h1")[0].text.strip()
        wea = parent.xpath("p[@class='wea']")[0].text.strip()
        tem = parent.xpath("string(p[@class='tem'])").strip()
        win = parent.xpath("p[@class='win']/span")[0]
        win_text = win.attrib["title"].strip() + ": " +  win.text.strip()

        info['header'] = header
        info['wea'] = wea
        info['tem'] = tem
        info['win'] = win_text
        tem_lst.append(info)

    return tem_lst

if __name__ == '__main__':
    url = "http://www.weather.com.cn/weather1d/101010100.shtml"
    data = crawl_weather(url)
    print(data)