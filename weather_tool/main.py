import json
from pypinyin import lazy_pinyin
from cli_helpers.tabular_output import TabularOutputFormatter
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.shortcuts import CompleteStyle, prompt
from cli_helpers.tabular_output.preprocessors import style_output
from pygments.style import Style
from pygments.token import Token
from crawl_weather import crawl_weather


with open('city_code') as file:
    lines = file.readlines()
    city_code_dict = {}
    for line in lines:
        arrs = line.strip().split()
        city_code_dict[arrs[0]] = arrs[1]

    # 获得城市列表
    city_lst = list(city_code_dict.keys())
    py_city_map = []
    # 获得城市名称拼音和城市名称之间的映射关系
    for city in city_lst:
        pinyin_lst = lazy_pinyin(city)
        pinyin_lst = [item[0] for item in pinyin_lst]
        pinyin = "".join(pinyin_lst)
        py_city_map.append((pinyin, city))


# 自动补全
class ColorCompleter(Completer):
    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for py, city in py_city_map:
            if py.startswith(word):
                yield Completion(
                    city,
                    start_position=-len(word),
                    style='fg:' + 'blue',
                    selected_style='fg:white bg:blue')

def main():
    formatter = TabularOutputFormatter()
    while True:
        city = prompt('输入城市名称: ', completer=ColorCompleter(),
               complete_style=CompleteStyle.MULTI_COLUMN)

        if city == "exit":
            break

        if city not in city_code_dict:
            print('输入错误，请重新输入')
            continue

        # 设置header样式
        class HeaderStyle(Style):
            default_style = ""
            styles = {
                Token.Output.Header: '#00ff5f bold',
            }

        code = city_code_dict[city]
        url = "http://www.weather.com.cn/weather1d/{code}.shtml".format(code=code)
        res = crawl_weather(url)
        headers = ['城市', '时间', "天气", "气温", "风况"]
        data = []
        for item in res:
            data.append([city, item['header'], item['wea'], item['tem'], item['win']])

        res = formatter.format_output(data, headers, format_name='ascii', style=HeaderStyle)
        for item in res:
            print(item)


if __name__ == '__main__':
    main()