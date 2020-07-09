import requests
import collections
import re
from hanlp_class import HanLP_LTP
import logging
import codecs
from date_chunk_handle_class import Date_chunk_handle
from extract_schema_class import Extract_Schema
import common_function
import numpy as np
import io
import json

def split_sentence(sen):
    nlp_url = 'http://hanlp-rough-service:31001/hanlp/segment/rough'
    try:
        cut_sen = dict()
        cut_sen['content'] = sen
        data = json.dumps(cut_sen).encode("UTF-8")
        cut_response = requests.post(nlp_url, data=data, headers={'Connection': 'close'})
        cut_response_json = cut_response.json()
        return cut_response_json['data']
    except Exception as e:
        print.exception("Exception: {}".format(e))
        return []


def removeAllTag(s):
    s = re.sub('<[^>]+>', '', s)
    return s

def FullToHalf(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += chr(inside_code)

    return rstring

def event_discription_rule(p, p_seg=None):
    if len(p) > 40 and len(p) < 500:

        if '摄' in p and len(p) < 60:
            return 0

        if p_seg is not None:
            x = p_seg
        else:
            x = split_sentence(p)

        x_ = list(filter(lambda x: len(x['word'].strip()) > 0, x))

        natures = [a['nature'] for a in x_]
        words = [a['word'] for a in x_]

        if '日电' in words:
            return 1

        for i in range(0, len(words)):
            if words[i] == '日':
                if i - 1 >= 0:
                    if natures[i - 1] == 'm':
                        return 1
    return 0

def split_content_to_paragraph(content):
    # 爬虫数据进行分段
    # 1、char.strip() 与 FullToHalf(char.isdigit())
    # 2、'</p><p>' 与 '</p></p><p><p>'
    # 3、removeAllTag(p) 去掉 p = “”

    content_ = ''
    for char in content:
        char = char.strip()
        if len(char) != 0:
            if char.isdigit():
                char = FullToHalf(char)
            content_ += char

    paragraphs = []
    if dataSource == "CRAWL":
        paragraphs = content_.split('</p><p>')
    else:
        paragraphs = content_.split('</p></p><p><p>')

    paragraphs = [removeAllTag(p) for p in paragraphs if len(removeAllTag(p).strip()) != 0]

    return paragraphs


def core_s_punctuation_process(s):
    # 由于之前的 char.strip() 和 「电头」不存在标点导致
    # “新华社xxx日电（记者 xxx）中央政治局会议在xx召开”

    s_ = s
    if '日电' in s:
        ids = s.index('日电')
        s_ = s[ids + 2:]
    if '月电' in s:
        ids = s.index('月电')
        s_ = s[ids + 2:]
    if '（' in s_ and '）' in s_:
        special_strings = re.findall("\（(.*)\）", s)
        for special_string in special_strings:
            s_ = s_.replace('（' + special_string + '）', '')

    return s_

def get_atomic_sentence_split(p):
    # s.strip()
    split_symbpls = ['。', '，', '；', ',', ';']
    for ss in split_symbpls:
        p = p.replace(ss, '。')

    s_list = [s.strip() for s in p.split('。') if len(s.strip()) > 0]

    return s_list


def get_event_description_from_article(paragraphs):
    # 假设：
    #   1、每篇资讯最多只讲一件最主要的「事件」（也可能不讲）
    #   2、这个主要「事件」出现在开篇处
    # 每篇资讯进行分段（通过永焕给出的规则 ***重要*** ）
    event_description = ''

    for p in paragraphs[0:15]:
        p_seg = split_sentence(p)
        if event_discription_rule(p, p_seg=p_seg) == 1:
            event_description = p
            break

    return event_description


def load_json_line_data(filepath):
    data = []
    with io.open(filepath, "r", encoding='utf-8') as f:
        while True:
            line = f.readline()
            if len(line) > 0:
                data.append(json.loads(line.strip()))
            else:
                break
    return data


if __name__ == '__main__':

    extract_schema = Extract_Schema()

    events_data = load_json_line_data('aaa')

    print('len(foreign_affairs_data): ', len(events_data))

    article_count = 0
    event_description_count = 0
    core_sentence_count = 0
    signs = ['。','；',';']

    for article in events_data:

        article_count += 1
        article_words = []

        if article_count % 100 == 1:
            print('article_count: ', article_count)

        try:
            title = article['title']
            content = article['content']
            dataSource = article["dataSource"]
            url = article['url']
            publishAt = article['publishAt']
            types = article['contentType']

            contentSource = ''
            if 'contentSource' in article:
                contentSource = article['contentSource']

            mediaFrom = ''
            if 'mediaFrom' in article:
                contentSource = article['mediaFrom']

        except Exception as e:
            print('key error！')
            print("Exception: {}".format(e))
            continue

        paragraphs = split_content_to_paragraph(content)
        if len(paragraphs) > 0:
            # 找到该篇文章的abstruct
            event_description = get_event_description_from_article(paragraphs)
            paragraphs.remove(event_description)
        else:
            event_description = ''

#       直接对一篇文章的所有的段落进行分句
        if len(paragraphs) > 0:
            for p in paragraphs:
                for sign in signs:
                    p_ = p.replace(sign,'。')
                article_words.append(p_.split('。'))

        for words in article_words:
            if len(words) > 10:
#
#                此处应该调用各个类别的抽取对象中的函数进行抽取，返回一个包含抽取结果的字典，然后存储到该句话对应的元素中。再提取出实体（基词替换）存储包含该实体的句子
                event_description1 = words

                # 剔除概述中包含双引号等特殊字符后的句子
                event_description1, signs_list = common_function.signs_handle(event_description1)

                date_full_start = ''
                date_full_end = ''
                date_full_start_stamp = ''
                date_full_end_stamp = ''

                if event_description1 != '':
                    event_description1 = core_s_punctuation_process(event_description1)
                extract_schema.get_schema_all(event_description1,'content',title)

#         篇章集类似于之前的抽取规则，其中找中心句步骤可结合句子集抽取一起，提高效率
#         event_description = get_event_description_from_article(paragraphs)
#         篇章级抽取只会在abstruct存在的情况下进行
        if event_description != '':
            event_description1 = event_description

            # 剔除概述中包含双引号等特殊字符后的句子
            event_description1, signs_list = common_function.signs_handle(event_description1)

            date_full_start = ''
            date_full_end = ''
            date_full_start_stamp = ''
            date_full_end_stamp = ''

            # 去头部的‘日电’
            if event_description1 != '':
                event_description1 = core_s_punctuation_process(event_description1)

            event_sentences = get_atomic_sentence_split(event_description1)

            if len(event_sentences) > 0:
                for sentence in event_sentences:
                    if len(sentence) > 10:
                        extract_schema.get_schema_all(sentence,'abstruct',title)
    #                   取得schema列表之后需要给每一个列表元素单独加入时间这一key