# -*- coding: utf-8 -*-

import json
import re
import time
import io
import requests
import datetime

class Date_chunk_handle:

    def __init__(self):
        self.orderby_rgx = None
        self.key_words_time = ['上午','中午','晚上','下午','晨','晚','全天']
        self.key_words_type = ['报道','消息','讯','获悉','公布']
        self.time_trigger_words = ['日','日电','日和']
        self.seg_trigger_words = ['-','到','至','和','—','－']
        self.Chinese_num = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八',
                       '十九', '二十', '二十一', '二十二', '二十三', '二十四', '二十五', '二十六', '二十七', '二十八', '二十九', '三十', '三十一']
        self.rule = ["([0-9零一二两三四五六七八九十]+年)", "([0-9一二两三四五六七八九十]+月)", "([0-9一二两三四五六七八九十]+[号日])"]


        week_time_rgx = '星期|周'
        hour_time_rgx = '时|点'
        period_time_rgx = '上午|中午|晚上|下午|晨|晚|全天'
        time_type_rgx = '报道|消息|讯|获悉|公布|电'
        chinese_num_rgx = '零一二两三四五六七八九十'
        year_chinese_num_rgx = '[零一二两三四五六七八九十]{1,4}'
        month_chinese_num_rgx = '[零一二两三四五六七八九十]{1,2}'
        seg_trigger_rgx = '-|到|至|—|和|－'
        anyway_suffix_rgx = '上午|中午|晚上|下午|晨|晚|全天|[(|（](.*?)[)|）]|[零一二两三四五六七八九十]{1,2}时|[零一二两三四五六七八九十]{1,2}点|\d{1,2}时|\d{1,2}点'
        year_arab_num_rgx = '\d{1,4}'
        month_arab_num_rgx = '\d{1,2}'
        anyway_rgx_year = '.{,7}'
        anyway_rgx_month = '.{,2}'
        anyway_rgx_seg = '.{,9}'
        anyway_rgx_day1 = '.{,11}'
        anyway_rgx_day2 = '.{,5}'

        self.datetimes = []
        self.normalize_chunk = re.compile(r'(.*)({0})(.*)'.format(seg_trigger_rgx))

        segment_1 = re.compile(
            r'(.*?)({0}日|{2}日)(?!{1})'.format(month_chinese_num_rgx, time_type_rgx, month_arab_num_rgx))

        segment_2 = re.compile(r'(.*?)({0}日|{2}日)(?!{1})({3})({4})({5})(日)'.format(month_chinese_num_rgx, time_type_rgx,
                                                                                   month_arab_num_rgx, anyway_rgx_seg,
                                                                                   seg_trigger_rgx, anyway_rgx_day1))

        segment_3 = re.compile(
            r'(.*?)({0}日|{2}日)(?!{1})({3})'.format(month_chinese_num_rgx, time_type_rgx, month_arab_num_rgx,anyway_suffix_rgx))

        segment_4 = re.compile(r'(.*?)({0}日|{2}日)(?!{1})({3})({4})({5})(日)({6})'.format(month_chinese_num_rgx, time_type_rgx,
                                                                                   month_arab_num_rgx, anyway_rgx_seg,
                                                                                   seg_trigger_rgx, anyway_rgx_day1,anyway_suffix_rgx))

        integrity_1_0 = re.compile(r'({0}年|{2}年)({3}?)(日)({1})'.format(year_chinese_num_rgx,time_type_rgx,year_arab_num_rgx,anyway_rgx_year))

        integrity_1_1 = re.compile(
            r'({0}月|{2}月)({3})(日)({1})'.format(month_chinese_num_rgx, time_type_rgx, month_arab_num_rgx,anyway_rgx_month))

        integrity_1_2 = re.compile(
            r'({0}日|{2}日)({1})'.format(month_chinese_num_rgx, time_type_rgx, month_arab_num_rgx))

        integrity_2 = re.compile(                                                                                       #s = '去年是2019年5月21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭'
            r'({0}年|{5}年)({7})(日)(?!{6})({8})({1})({9})(日)(?!{6})[(|（](.*?)[)|）]({2})({3}{4}|{10}{4})'.format(year_chinese_num_rgx,          #s = '去年是二零一九年5月21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭'
                                                                                               seg_trigger_rgx,
                                                                                               period_time_rgx,
                                                                                         month_chinese_num_rgx,
                                                                                               hour_time_rgx,
                                                                                          year_arab_num_rgx,
                                                                                            time_type_rgx,
                                                                                            anyway_rgx_year,
                                                                                           anyway_rgx_seg,
                                                                                           anyway_rgx_day1,
                                                                                            month_arab_num_rgx))

        integrity_3 = re.compile(
            r'({0}月|{4}月)({6})(日)(?!{5})({7})({1})({8})(日)(?!{5})[(|（](.*?)[)|）]({2})({0}{3}|{4}{3})'.format(month_chinese_num_rgx,           #s = '去年是5月21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭'
                                                                                    seg_trigger_rgx,                     #s = '去年是五月21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭'
                                                                                    period_time_rgx
                                                                                    ,hour_time_rgx,
                                                                                    month_arab_num_rgx,
                                                                                    time_type_rgx,
                                                                                     anyway_rgx_day2,
                                                                                     anyway_rgx_seg,
                                                                                     anyway_rgx_day1))

        integrity_4 = re.compile(
            r'({0}日|{4}日)(?!{5})({6})({1})({7})(日)(?!{5})[(|（](.*?)[)|）]({2})({0}{3}|{4}{3})'.format(month_chinese_num_rgx,              #s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭
                                                                                    seg_trigger_rgx,                    #s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭
                                                                                    period_time_rgx
                                                                                    , hour_time_rgx,
                                                                                month_arab_num_rgx,
                                                                                  time_type_rgx,
                                                                                  anyway_rgx_seg,
                                                                                  anyway_rgx_day1))

        integrity_5 = re.compile(
            r'({0}年|{3}年)({7})(日)(?!{4})({5})({1})({6})(日)(?!{4})[(|（](.*?)[)|）]({2})'.format(year_chinese_num_rgx,                 #s = '去年是2019年21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                              seg_trigger_rgx,                          #s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                              period_time_rgx,
                                                                              year_arab_num_rgx,
                                                                              time_type_rgx,
                                                                              anyway_rgx_seg,
                                                                              anyway_rgx_day1,
                                                                              anyway_rgx_year))

        integrity_6 = re.compile(
            r'({0}年|{5}年)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})[(|（](.*?)[)|）]({3}{4}|{6}{4})'.format(year_chinese_num_rgx,           #s = '去年是2019年21日（星期五）下午8点到2019年5月22日（星期六）8点一起去吃饭
                                                                                    seg_trigger_rgx,                    #s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日（星期六）八点一起去吃饭
                                                                                    period_time_rgx,
                                                                                    month_chinese_num_rgx,
                                                                                    hour_time_rgx,
                                                                                    year_arab_num_rgx,
                                                                                    month_arab_num_rgx,
                                                                                    time_type_rgx,
                                                                                    anyway_rgx_year,
                                                                                    anyway_rgx_seg,
                                                                                    anyway_rgx_day1))

        integrity_7 = re.compile(
            r'({0}年|{5}年)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})[(|（](.*?)[)|）]'.format(year_chinese_num_rgx,           #s = '去年是2019年21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                                    seg_trigger_rgx,                    #s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                                    period_time_rgx,
                                                                                    month_chinese_num_rgx,
                                                                                    hour_time_rgx,
                                                                                    year_arab_num_rgx,
                                                                                    month_arab_num_rgx,
                                                                                    time_type_rgx,anyway_rgx_year,
                                                                                    anyway_rgx_seg,
                                                                                    anyway_rgx_day1))

        integrity_8 = re.compile(
            r'({0}年|{5}年)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                                         # s = '去年是2019年21日（星期五）下午8点到2019年5月22日8点一起去吃饭
                                                                         seg_trigger_rgx,
                                                                         # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日八点一起去吃饭
                                                                         period_time_rgx,
                                                                         month_chinese_num_rgx,
                                                                         hour_time_rgx,
                                                                         year_arab_num_rgx,
                                                                         month_arab_num_rgx,
                                                                         time_type_rgx,anyway_rgx_year,
                                                                         anyway_rgx_seg,
                                                                         anyway_rgx_day1))

        integrity_9 = re.compile(
            r'({0}年|{5}年)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})({2})'.format(year_chinese_num_rgx,
                                                                     # s = '去年是2019年21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                                     seg_trigger_rgx,
                                                                     # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                                     period_time_rgx,
                                                                     month_chinese_num_rgx,
                                                                     hour_time_rgx,
                                                                     year_arab_num_rgx,
                                                                     month_arab_num_rgx,
                                                                     time_type_rgx,anyway_rgx_year,
                                                                     anyway_rgx_seg,
                                                                     anyway_rgx_day1))

        integrity_23 = re.compile(
            r'({0}年|{5}年)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})'.format(year_chinese_num_rgx,
                                                               # s = '去年是2019年21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                               seg_trigger_rgx,
                                                               # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                               period_time_rgx,
                                                               month_chinese_num_rgx,
                                                               hour_time_rgx,
                                                               year_arab_num_rgx,
                                                               month_arab_num_rgx,
                                                               time_type_rgx,anyway_rgx_year,
                                                                anyway_rgx_seg,
                                                                anyway_rgx_day1))

        integrity_10 = re.compile(
            r'({0}年|{5}年)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})({2})({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                               # s = '去年是2019年21日（星期五）下午8点到2019年5月22日上午八点一起去吃饭
                                                               seg_trigger_rgx,
                                                               # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                               period_time_rgx,
                                                               month_chinese_num_rgx,
                                                               hour_time_rgx,
                                                               year_arab_num_rgx,
                                                               month_arab_num_rgx,
                                                               time_type_rgx,anyway_rgx_year,
                                                                anyway_rgx_seg,
                                                                anyway_rgx_day1))

        integrity_11 = re.compile(
            r'({3}月|{6}月)({8})(日?!{7})(?!{7})({9})({1})({10})(日)(?!{7})[(|（](.*?)[)|）]({2})'.format(year_chinese_num_rgx,
                                                                          # s = '去年是5月21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                          seg_trigger_rgx,
                                                                          # s = '去年是五月21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                          period_time_rgx,
                                                                          month_chinese_num_rgx,
                                                                          hour_time_rgx,
                                                                          year_arab_num_rgx,
                                                                          month_arab_num_rgx,
                                                                          time_type_rgx,
                                                                          anyway_rgx_day2,anyway_rgx_seg,
                                                                          anyway_rgx_day1))

        integrity_12 = re.compile(
            r'({3}月|{6}月)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})[(|（](.*?)[)|）]({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                                              # s = '去年是5月21日（星期五）下午8点到2019年5月22日（星期六）8点一起去吃饭
                                                                              seg_trigger_rgx,
                                                                              # s = '去年是五月21日（星期五）下午8点到2019年5月22日（星期六）八点一起去吃饭
                                                                              period_time_rgx,
                                                                              month_chinese_num_rgx,
                                                                              hour_time_rgx,
                                                                              year_arab_num_rgx,
                                                                              month_arab_num_rgx,
                                                                              time_type_rgx,
                                                                          anyway_rgx_day2,anyway_rgx_seg,
                                                                          anyway_rgx_day1))

        integrity_13 = re.compile(
            r'({3}月|{6}月)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})[(|（](.*?)[)|）]'.format(year_chinese_num_rgx,
                                                                                    # s = '去年是5月21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                                    seg_trigger_rgx,
                                                                                    # s = '去年是五月21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                                    period_time_rgx,
                                                                                    month_chinese_num_rgx,
                                                                                    hour_time_rgx,
                                                                                    year_arab_num_rgx,
                                                                                    month_arab_num_rgx,
                                                                                    time_type_rgx,
                                                                          anyway_rgx_day2,anyway_rgx_seg,
                                                                          anyway_rgx_day1))

        integrity_14 = re.compile(
            r'({3}月|{6}月)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                                         # s = '去年是5月21日（星期五）下午8点到2019年5月22日8点一起去吃饭
                                                                         seg_trigger_rgx,
                                                                         # s = '去年是五月21日（星期五）下午8点到2019年5月22日八点一起去吃饭
                                                                         period_time_rgx,
                                                                         month_chinese_num_rgx,
                                                                         hour_time_rgx,
                                                                         year_arab_num_rgx,
                                                                         month_arab_num_rgx,
                                                                         time_type_rgx,
                                                                          anyway_rgx_day2,anyway_rgx_seg,
                                                                          anyway_rgx_day1))

        integrity_15 = re.compile(
            r'({3}月|{6}月)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})({2})'.format(year_chinese_num_rgx,
                                                                     # s = '去年是5月21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                                     seg_trigger_rgx,
                                                                     # s = '去年是五月21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                                     period_time_rgx,
                                                                     month_chinese_num_rgx,
                                                                     hour_time_rgx,
                                                                     year_arab_num_rgx,
                                                                     month_arab_num_rgx,
                                                                     time_type_rgx,
                                                                     anyway_rgx_day2,anyway_rgx_seg,
                                                                     anyway_rgx_day1))

        integrity_24 = re.compile(
            r'({3}月|{6}月)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})'.format(year_chinese_num_rgx,
                                                               # s = '去年是5月21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                               seg_trigger_rgx,
                                                               # s = '去年是五月21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                               period_time_rgx,
                                                               month_chinese_num_rgx,
                                                               hour_time_rgx,
                                                               year_arab_num_rgx,
                                                               month_arab_num_rgx,
                                                               time_type_rgx,
                                                               anyway_rgx_day2,anyway_rgx_seg,
                                                               anyway_rgx_day1))

        integrity_16 = re.compile(
            r'({3}月|{6}月)({8})(日)(?!{7})({9})({1})({10})(日)(?!{7})({2})({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                               # s = '去年是5月21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                               seg_trigger_rgx,
                                                               # s = '去年是五月21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                               period_time_rgx,
                                                               month_chinese_num_rgx,
                                                               hour_time_rgx,
                                                               year_arab_num_rgx,
                                                               month_arab_num_rgx,
                                                               time_type_rgx,
                                                               anyway_rgx_day2,anyway_rgx_seg,
                                                               anyway_rgx_day1))

        integrity_17 = re.compile(
            r'({0}日|{6}日)(?!{7})({8})({1})({9})(日)(?!{7})[(|（](.*?)[)|）]({2})'.format(year_chinese_num_rgx,
                                                                          # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                          seg_trigger_rgx,
                                                                          # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                          period_time_rgx,
                                                                          month_chinese_num_rgx,
                                                                          hour_time_rgx,
                                                                          year_arab_num_rgx,
                                                                          month_arab_num_rgx,
                                                                          time_type_rgx,anyway_rgx_seg,
                                                                          anyway_rgx_day1))

        integrity_18 = re.compile(
            r'({0}日|{6}日)(?!{7})({8})({1})({9})(日)(?!{7})[(|（](.*?)[)|）]({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                                       # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）8点一起去吃饭
                                                                       seg_trigger_rgx,
                                                                       # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）八点一起去吃饭
                                                                       period_time_rgx,
                                                                       month_chinese_num_rgx,
                                                                       hour_time_rgx,
                                                                       year_arab_num_rgx,
                                                                       month_arab_num_rgx,
                                                                       time_type_rgx,anyway_rgx_seg,
                                                                        anyway_rgx_day1))

        integrity_19 = re.compile(
            r'({0}日|{6}日)(?!{7})({8})({1})({9})(日)(?!{7})[(|（](.*?)[)|）]'.format(year_chinese_num_rgx,
                                                                             # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                             seg_trigger_rgx,
                                                                             # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                             period_time_rgx,
                                                                             month_chinese_num_rgx,
                                                                             hour_time_rgx,
                                                                             year_arab_num_rgx,
                                                                             month_arab_num_rgx,
                                                                             time_type_rgx,anyway_rgx_seg,
                                                                             anyway_rgx_day1))

        integrity_20 = re.compile(
            r'({0}日|{6}日)(?!{7})({8})({1})({9})(日)(?!{7})({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                                 # s = '去年是21日（星期五）下午8点到2019年5月22日8点一起去吃饭
                                                                 seg_trigger_rgx,
                                                                 # s = '去年是二十一日（星期五）下午8点到2019年5月22日八点一起去吃饭
                                                                 period_time_rgx,
                                                                 month_chinese_num_rgx,
                                                                 hour_time_rgx,
                                                                 year_arab_num_rgx,
                                                                 month_arab_num_rgx,
                                                                 time_type_rgx,anyway_rgx_seg,
                                                                  anyway_rgx_day1))

        integrity_21 = re.compile(
            r'({0}日|{6}日)(?!{7})({8})({1})({9})(日)(?!{7})({2})'.format(year_chinese_num_rgx,
                                                              # s = '去年是21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                              seg_trigger_rgx,
                                                              # s = '去年是二十一日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                              period_time_rgx,
                                                              month_chinese_num_rgx,
                                                              hour_time_rgx,
                                                              year_arab_num_rgx,
                                                              month_arab_num_rgx,
                                                              time_type_rgx,anyway_rgx_seg,
                                                              anyway_rgx_day1))

        integrity_22 = re.compile(
            r'({0}日|{6}日)(?!{7})({8})({1})({9})(日)(?!{7})({2})({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                        # s = '去年是21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                        seg_trigger_rgx,
                                                        # s = '去年是二十一日（星期五）下午8点到2019年5月22日上午八点一起去吃饭
                                                        period_time_rgx,
                                                        month_chinese_num_rgx,
                                                        hour_time_rgx,
                                                        year_arab_num_rgx,
                                                        month_arab_num_rgx,
                                                        time_type_rgx,anyway_rgx_seg,
                                                        anyway_rgx_day1))

        integrity_25 = re.compile(
            r'({0}日|{6}日)(?!{7})({8})({1})({9})(日)(?!{7})'.format(year_chinese_num_rgx,
                                                                   # s = '去年是21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                                   seg_trigger_rgx,
                                                                   # s = '去年是二十一日（星期五）下午8点到2019年5月22日一起去吃饭
                                                                   period_time_rgx,
                                                                   month_chinese_num_rgx,
                                                                   hour_time_rgx,
                                                                   year_arab_num_rgx,
                                                                   month_arab_num_rgx,
                                                                   time_type_rgx,anyway_rgx_seg,
                                                                   anyway_rgx_day1))

        integrity_50 = re.compile(
            r'({0}|{6})(?!{7})({8})({1})({9})(日)(?!{7})[(|（](.*?)[)|）]({2})'.format(year_chinese_num_rgx,
                                                                                      # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                                      seg_trigger_rgx,
                                                                                      # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                                      period_time_rgx,
                                                                                      month_chinese_num_rgx,
                                                                                      hour_time_rgx,
                                                                                      year_arab_num_rgx,
                                                                                      month_arab_num_rgx,
                                                                                      time_type_rgx, anyway_rgx_seg,
                                                                                      anyway_rgx_day1))

        integrity_51 = re.compile(
            r'({0}|{6})(?!{7})({8})({1})({9})(日)(?!{7})[(|（](.*?)[)|）]({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                                                                # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）8点一起去吃饭
                                                                                                seg_trigger_rgx,
                                                                                                # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）八点一起去吃饭
                                                                                                period_time_rgx,
                                                                                                month_chinese_num_rgx,
                                                                                                hour_time_rgx,
                                                                                                year_arab_num_rgx,
                                                                                                month_arab_num_rgx,
                                                                                                time_type_rgx,
                                                                                                anyway_rgx_seg,
                                                                                                anyway_rgx_day1))

        integrity_52 = re.compile(
            r'({0}|{6})(?!{7})({8})({1})({9})(日)(?!{7})[(|（](.*?)[)|）]'.format(year_chinese_num_rgx,
                                                                                 # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                                 seg_trigger_rgx,
                                                                                 # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                                 period_time_rgx,
                                                                                 month_chinese_num_rgx,
                                                                                 hour_time_rgx,
                                                                                 year_arab_num_rgx,
                                                                                 month_arab_num_rgx,
                                                                                 time_type_rgx, anyway_rgx_seg,
                                                                                 anyway_rgx_day1))

        integrity_53 = re.compile(
            r'({0}|{6})(?!{7})({8})({1})({9})(日)(?!{7})({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                                                 # s = '去年是21日（星期五）下午8点到2019年5月22日8点一起去吃饭
                                                                                 seg_trigger_rgx,
                                                                                 # s = '去年是二十一日（星期五）下午8点到2019年5月22日八点一起去吃饭
                                                                                 period_time_rgx,
                                                                                 month_chinese_num_rgx,
                                                                                 hour_time_rgx,
                                                                                 year_arab_num_rgx,
                                                                                 month_arab_num_rgx,
                                                                                 time_type_rgx, anyway_rgx_seg,
                                                                                 anyway_rgx_day1))

        integrity_54 = re.compile(
            r'({0}|{6})(?!{7})({8})({1})({9})(日)(?!{7})({2})'.format(year_chinese_num_rgx,
                                                                       # s = '去年是21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                                       seg_trigger_rgx,
                                                                       # s = '去年是二十一日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                                       period_time_rgx,
                                                                       month_chinese_num_rgx,
                                                                       hour_time_rgx,
                                                                       year_arab_num_rgx,
                                                                       month_arab_num_rgx,
                                                                       time_type_rgx, anyway_rgx_seg,
                                                                       anyway_rgx_day1))

        integrity_55 = re.compile(
            r'({0}|{6})(?!{7})({8})({1})({9})(日)(?!{7})({2})({3}{4}|{6}{4})'.format(year_chinese_num_rgx,
                                                                                      # s = '去年是21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                                                      seg_trigger_rgx,
                                                                                      # s = '去年是二十一日（星期五）下午8点到2019年5月22日上午八点一起去吃饭
                                                                                      period_time_rgx,
                                                                                      month_chinese_num_rgx,
                                                                                      hour_time_rgx,
                                                                                      year_arab_num_rgx,
                                                                                      month_arab_num_rgx,
                                                                                      time_type_rgx, anyway_rgx_seg,
                                                                                      anyway_rgx_day1))

        integrity_56 = re.compile(
            r'({0}|{6})(?!{7})({8})({1})({9})(日)(?!{7})'.format(year_chinese_num_rgx,
                                                                  # s = '去年是21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                                  seg_trigger_rgx,
                                                                  # s = '去年是二十一日（星期五）下午8点到2019年5月22日一起去吃饭
                                                                  period_time_rgx,
                                                                  month_chinese_num_rgx,
                                                                  hour_time_rgx,
                                                                  year_arab_num_rgx,
                                                                  month_arab_num_rgx,
                                                                  time_type_rgx, anyway_rgx_seg,
                                                                  anyway_rgx_day1))

        integrity_26 = re.compile(  # s = '去年是2019年5月21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭'
            r'({0}年|{5}年)({7})(日)[(|（](.*?)[)|）]({2})({3}{4}|{8}{4})(?!{6})'.format(year_chinese_num_rgx,
                                                                                         # s = '去年是二零一九年5月21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭'
                                                                                         seg_trigger_rgx,
                                                                                         period_time_rgx,
                                                                                         month_chinese_num_rgx,
                                                                                         hour_time_rgx,
                                                                                         year_arab_num_rgx,
                                                                                         time_type_rgx,
                                                                                         anyway_rgx_year,
                                                                                         month_arab_num_rgx))

        integrity_27 = re.compile(
            r'({0}月|{4}月)({6})(日)[(|（](.*?)[)|）]({2})({0}{3}|{4}{3})(?!{5})'.format(month_chinese_num_rgx,
                                                                                         # s = '去年是5月21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭'
                                                                                         seg_trigger_rgx,
                                                                                         # s = '去年是五月21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭'
                                                                                         period_time_rgx
                                                                                         , hour_time_rgx,
                                                                                         month_arab_num_rgx,
                                                                                         time_type_rgx,
                                                                                         anyway_rgx_day2))

        integrity_28 = re.compile(
            r'({0}日|{4}日)[(|（](.*?)[)|）]({2})({0}{3}|{4}{3})(?!{5})'.format(month_chinese_num_rgx,
                                                                                  # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭
                                                                                  seg_trigger_rgx,
                                                                                  # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）上午9时一起去吃饭
                                                                                  period_time_rgx
                                                                                  , hour_time_rgx,
                                                                                  month_arab_num_rgx,
                                                                                    time_type_rgx))

        integrity_29 = re.compile(
            r'({0}年|{3}年)({5})(日)[(|（](.*?)[)|）]({2})(?!{4})'.format(year_chinese_num_rgx,
                                                                              # s = '去年是2019年21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                              seg_trigger_rgx,
                                                                              # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                              period_time_rgx,
                                                                              year_arab_num_rgx,
                                                                              time_type_rgx,
                                                                              anyway_rgx_year))

        integrity_30 = re.compile(
            r'({0}年|{5}年)({8})(日)[(|（](.*?)[)|）]({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                                                    # s = '去年是2019年21日（星期五）下午8点到2019年5月22日（星期六）8点一起去吃饭
                                                                                    seg_trigger_rgx,
                                                                                    # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日（星期六）八点一起去吃饭
                                                                                    period_time_rgx,
                                                                                    month_chinese_num_rgx,
                                                                                    hour_time_rgx,
                                                                                    year_arab_num_rgx,
                                                                                    month_arab_num_rgx,
                                                                                    time_type_rgx,
                                                                                    anyway_rgx_year))

        integrity_31 = re.compile(
            r'({0}年|{5}年)({8})(日)[(|（](.*?)[)|）](?!{7})'.format(year_chinese_num_rgx,
                                                                         # s = '去年是2019年21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                         seg_trigger_rgx,
                                                                         # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                         period_time_rgx,
                                                                         month_chinese_num_rgx,
                                                                         hour_time_rgx,
                                                                         year_arab_num_rgx,
                                                                         month_arab_num_rgx,
                                                                         time_type_rgx,
                                                                         anyway_rgx_year))

        integrity_32 = re.compile(
            r'({0}年|{5}年)({8})(日)({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                                     # s = '去年是2019年21日（星期五）下午8点到2019年5月22日8点一起去吃饭
                                                                     seg_trigger_rgx,
                                                                     # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日八点一起去吃饭
                                                                     period_time_rgx,
                                                                     month_chinese_num_rgx,
                                                                     hour_time_rgx,
                                                                     year_arab_num_rgx,
                                                                     month_arab_num_rgx,
                                                                     time_type_rgx,
                                                                     anyway_rgx_year))

        integrity_33 = re.compile(
            r'({0}年|{5}年)({8})(日)({2})(?!{7})'.format(year_chinese_num_rgx,
                                                               # s = '去年是2019年21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                               seg_trigger_rgx,
                                                               # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                               period_time_rgx,
                                                               month_chinese_num_rgx,
                                                               hour_time_rgx,
                                                               year_arab_num_rgx,
                                                               month_arab_num_rgx,
                                                               time_type_rgx,
                                                               anyway_rgx_year))

        integrity_34 = re.compile(
            r'({0}年|{5}年)({8})(日)(?!{7})'.format(year_chinese_num_rgx,
                                                          # s = '去年是2019年21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                          seg_trigger_rgx,
                                                          # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                          period_time_rgx,
                                                          month_chinese_num_rgx,
                                                          hour_time_rgx,
                                                          year_arab_num_rgx,
                                                          month_arab_num_rgx,
                                                          time_type_rgx,
                                                          anyway_rgx_year))

        integrity_35 = re.compile(
            r'({0}年|{5}年)({8})(日)({2})({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                                          # s = '去年是2019年21日（星期五）下午8点到2019年5月22日上午八点一起去吃饭
                                                                          seg_trigger_rgx,
                                                                          # s = '去年是二零一九年21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                                          period_time_rgx,
                                                                          month_chinese_num_rgx,
                                                                          hour_time_rgx,
                                                                          year_arab_num_rgx,
                                                                          month_arab_num_rgx,
                                                                          time_type_rgx,
                                                                          anyway_rgx_year))

        integrity_36 = re.compile(
            r'({3}月|{6}月)({8})(日)[(|（](.*?)[)|）]({2})(?!{7})'.format(year_chinese_num_rgx,
                                                                              # s = '去年是5月21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                              seg_trigger_rgx,
                                                                              # s = '去年是五月21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                              period_time_rgx,
                                                                              month_chinese_num_rgx,
                                                                              hour_time_rgx,
                                                                              year_arab_num_rgx,
                                                                              month_arab_num_rgx,
                                                                              time_type_rgx,
                                                                              anyway_rgx_day2))

        integrity_37 = re.compile(
            r'({3}月|{6}月)({8})(日)[(|（](.*?)[)|）]({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                                                    # s = '去年是5月21日（星期五）下午8点到2019年5月22日（星期六）8点一起去吃饭
                                                                                    seg_trigger_rgx,
                                                                                    # s = '去年是五月21日（星期五）下午8点到2019年5月22日（星期六）八点一起去吃饭
                                                                                    period_time_rgx,
                                                                                    month_chinese_num_rgx,
                                                                                    hour_time_rgx,
                                                                                    year_arab_num_rgx,
                                                                                    month_arab_num_rgx,
                                                                                    time_type_rgx,
                                                                                    anyway_rgx_day2))

        integrity_38 = re.compile(
            r'({3}月|{6}月)({8})(日)[(|（](.*?)[)|）](?!{7})'.format(year_chinese_num_rgx,
                                                                         # s = '去年是5月21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                         seg_trigger_rgx,
                                                                         # s = '去年是五月21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                         period_time_rgx,
                                                                         month_chinese_num_rgx,
                                                                         hour_time_rgx,
                                                                         year_arab_num_rgx,
                                                                         month_arab_num_rgx,
                                                                         time_type_rgx,
                                                                         anyway_rgx_day2))

        integrity_39 = re.compile(
            r'({3}月|{6}月)({8})(日)({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                                     # s = '去年是5月21日（星期五）下午8点到2019年5月22日8点一起去吃饭
                                                                     seg_trigger_rgx,
                                                                     # s = '去年是五月21日（星期五）下午8点到2019年5月22日八点一起去吃饭
                                                                     period_time_rgx,
                                                                     month_chinese_num_rgx,
                                                                     hour_time_rgx,
                                                                     year_arab_num_rgx,
                                                                     month_arab_num_rgx,
                                                                     time_type_rgx,
                                                                     anyway_rgx_day2))

        integrity_40 = re.compile(
            r'({3}月|{6}月)({8})(日)({2})(?!{7})'.format(year_chinese_num_rgx,
                                                               # s = '去年是5月21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                               seg_trigger_rgx,
                                                               # s = '去年是五月21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                               period_time_rgx,
                                                               month_chinese_num_rgx,
                                                               hour_time_rgx,
                                                               year_arab_num_rgx,
                                                               month_arab_num_rgx,
                                                               time_type_rgx,
                                                               anyway_rgx_day2))

        integrity_41 = re.compile(
            r'({3}月|{6}月)({8})(日)(?!{7})'.format(year_chinese_num_rgx,
                                                          # s = '去年是5月21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                          seg_trigger_rgx,
                                                          # s = '去年是五月21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                          period_time_rgx,
                                                          month_chinese_num_rgx,
                                                          hour_time_rgx,
                                                          year_arab_num_rgx,
                                                          month_arab_num_rgx,
                                                          time_type_rgx,
                                                          anyway_rgx_day2))

        integrity_42 = re.compile(
            r'({3}月|{6}月)({8})(日)({2})({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                                          # s = '去年是5月21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                                          seg_trigger_rgx,
                                                                          # s = '去年是五月21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                                          period_time_rgx,
                                                                          month_chinese_num_rgx,
                                                                          hour_time_rgx,
                                                                          year_arab_num_rgx,
                                                                          month_arab_num_rgx,
                                                                          time_type_rgx,
                                                                          anyway_rgx_day2))

        integrity_43 = re.compile(
            r'({0}日|{6}日)[(|（](.*?)[)|）]({2})(?!{7})'.format(year_chinese_num_rgx,
                                                                       # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                       seg_trigger_rgx,
                                                                       # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）上午一起去吃饭
                                                                       period_time_rgx,
                                                                       month_chinese_num_rgx,
                                                                       hour_time_rgx,
                                                                       year_arab_num_rgx,
                                                                       month_arab_num_rgx,
                                                                       time_type_rgx))

        integrity_44 = re.compile(
            r'({0}日|{6}日)[(|（](.*?)[)|）]({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                                             # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）8点一起去吃饭
                                                                             seg_trigger_rgx,
                                                                             # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）八点一起去吃饭
                                                                             period_time_rgx,
                                                                             month_chinese_num_rgx,
                                                                             hour_time_rgx,
                                                                             year_arab_num_rgx,
                                                                             month_arab_num_rgx,
                                                                             time_type_rgx))

        integrity_45 = re.compile(
            r'({0}日|{6}日)[(|（](.*?)[)|）](?!{7})'.format(year_chinese_num_rgx,
                                                                  # s = '去年是21日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                  seg_trigger_rgx,
                                                                  # s = '去年是二十一日（星期五）下午8点到2019年5月22日（星期六）一起去吃饭
                                                                  period_time_rgx,
                                                                  month_chinese_num_rgx,
                                                                  hour_time_rgx,
                                                                  year_arab_num_rgx,
                                                                  month_arab_num_rgx,
                                                                  time_type_rgx))

        integrity_46 = re.compile(
            r'({0}日|{6}日)({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                              # s = '去年是21日（星期五）下午8点到2019年5月22日8点一起去吃饭
                                                              seg_trigger_rgx,
                                                              # s = '去年是二十一日（星期五）下午8点到2019年5月22日八点一起去吃饭
                                                              period_time_rgx,
                                                              month_chinese_num_rgx,
                                                              hour_time_rgx,
                                                              year_arab_num_rgx,
                                                              month_arab_num_rgx,
                                                              time_type_rgx))

        integrity_47 = re.compile(
            r'({0}日|{6}日)({2})(?!{7})'.format(year_chinese_num_rgx,
                                                        # s = '去年是21日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                        seg_trigger_rgx,
                                                        # s = '去年是二十一日（星期五）下午8点到2019年5月22日上午一起去吃饭
                                                        period_time_rgx,
                                                        month_chinese_num_rgx,
                                                        hour_time_rgx,
                                                        year_arab_num_rgx,
                                                        month_arab_num_rgx,
                                                        time_type_rgx))

        integrity_48 = re.compile(
            r'({0}日|{6}日)({2})({3}{4}|{6}{4})(?!{7})'.format(year_chinese_num_rgx,
                                                                   # s = '去年是21日（星期五）下午8点到2019年5月22日上午8点一起去吃饭
                                                                   seg_trigger_rgx,
                                                                   # s = '去年是二十一日（星期五）下午8点到2019年5月22日上午八点一起去吃饭
                                                                   period_time_rgx,
                                                                   month_chinese_num_rgx,
                                                                   hour_time_rgx,
                                                                   year_arab_num_rgx,
                                                                   month_arab_num_rgx,
                                                                   time_type_rgx))

        integrity_49 = re.compile(
            r'({0}日|{6}日)(?!{7})'.format(year_chinese_num_rgx,
                                                   # s = '去年是21日（星期五）下午8点到2019年5月22日一起去吃饭
                                                   seg_trigger_rgx,
                                                   # s = '去年是二十一日（星期五）下午8点到2019年5月22日一起去吃饭
                                                   period_time_rgx,
                                                   month_chinese_num_rgx,
                                                   hour_time_rgx,
                                                   year_arab_num_rgx,
                                                   month_arab_num_rgx,
                                                   time_type_rgx))

        self.rpt_orderby_rgx = [integrity_1_0,integrity_1_1,integrity_1_2]
        self.seg_datetimes_rgx = [segment_1,segment_2,segment_3,segment_4]
        self.tmp_orderby_rgx = [integrity_2,integrity_5,integrity_6,integrity_10,integrity_7,integrity_8,integrity_9,integrity_23,integrity_3,integrity_11,integrity_12,
                                integrity_16, integrity_13, integrity_14, integrity_15, integrity_24, integrity_4,
                                integrity_17, integrity_18, integrity_22, integrity_19, integrity_20,
                                integrity_21, integrity_25, integrity_50, integrity_51, integrity_55, integrity_52, integrity_53,
                                integrity_54, integrity_56,integrity_26, integrity_29, integrity_30, integrity_35,
                                integrity_31, integrity_32, integrity_33, integrity_34, integrity_27,
                                integrity_36, integrity_37, integrity_42, integrity_38, integrity_39, integrity_40,
                                integrity_41, integrity_28, integrity_43, integrity_44, integrity_48,
                                integrity_45, integrity_46, integrity_47, integrity_49]


    def get_date_chunk(self,s):

        time_chunk_list = []

        for i in range(0,len(self.rpt_orderby_rgx)):
            item_rgx = self.rpt_orderby_rgx[i].search(s)
            if item_rgx is not None:
                report_time_chunk_dict = {}
                report_time_chunk_dict['offset'] = [item_rgx.span()[0],item_rgx.span()[1]]
                report_time_chunk_dict['time_str'] = item_rgx.group(0)
                report_time_chunk_dict['type'] = 'RPT'
                time_chunk_list.append(report_time_chunk_dict)
                break
            else:
                pass

        for i in range(0,len(self.tmp_orderby_rgx)):
            item_rgx = self.tmp_orderby_rgx[i].search(s)
            if item_rgx is not None:
                event_time_chunk_dict = {}
                event_time_chunk_dict['offset'] = [item_rgx.span()[0], item_rgx.span()[1]]
                event_time_chunk_dict['time_str'] = item_rgx.group(0)
                event_time_chunk_dict['type'] = 'TMP'
                time_chunk_list.append(event_time_chunk_dict)
                # print(item_rgx.groups())
                # print(i)
                # print(self.tmp_orderby_rgx[i])
                break
            else:
                pass

        # print(time_chunk_list)

        return time_chunk_list

    def segment_datetimes(self,s):

        s_list1 = s.split('日')
        t_list = []

        seg_trigger_words = ['-', '到', '至', '和', '—', '－']

        s_list1 = [i for i in s_list1 if i != '']

        i = 0
        while (True):
            if len(s_list1) > 0:
                if i < len(s_list1):
                    j = i
                    strs = s_list1[j]
                    while (True):
                        if j < len(s_list1) - 1:
                            if re.match('.*?([0-9]*)$', s_list1[j]).group(1) == '' or s_list1[j + 1][
                                0] in seg_trigger_words:
                                strs = strs + '日' + s_list1[j + 1]
                                j = j + 1
                            else:
                                strs = strs + '日'
                                t_list.append(str)
                                break
                        else:
                            strs = strs + '日'
                            t_list.append(strs)
                            break
                    i = j
                    i = i + 1
                else:
                    break
            else:
                t_list = [s]
                break

        return s_list1, t_list

    def con_extra_time(self,s):
        date_str = []
        date_idx = []
        flag = 0
        record_len = 0

        lists, t_list = self.segment_datetimes(s)
        print(lists)

        for i in range(0, len(lists) - 1):
            con_str = lists[i] + '日' + lists[i + 1]

            for j in range(0,len(self.tmp_orderby_rgx)):

                result_rgx = self.tmp_orderby_rgx[j].search(con_str)
                if result_rgx is not None:
                    print(result_rgx.group(0))
                    start_idx = result_rgx.span()[0]
                    end_idx = result_rgx.span()[1] + record_len

                    item_idx = [flag,end_idx + record_len]
                    date_idx.append(item_idx)
                    date_str.append(con_str[flag - record_len:end_idx])
                    flag = end_idx + record_len
                    record_len = record_len + len(lists[i])
                    break

        return date_str,date_idx



    # def segment_datetimes(self,s):
    #
    #     datetime_list1 = []
    #     datetime_list = []
    #     start_1 = 0
    #     end_1 = 0
    #     start_2 = 0
    #     end_2 = 0
    #     start_3 = 0
    #     end_3 = 0
    #     start_4 = 0
    #     end_4 = 0
    #     i = 0
    #
    #     s_ = s
    #     while(True):
    #
    #         if len(s) != end_1:
    #             str1_rgx = self.seg_datetimes_rgx[3].match(s_)
    #             start_1 = end_1
    #             end_1 = str1_rgx.span(1)
    #             datetime_list1.extend(s_[start_1:end_1])
    #             s_ = s_[end_1:]
    #
    #             if datetime_list1 is not None:
    #                 datetime_list2 = []
    #                 for item1 in datetime_list1:
    #                     while(True):
    #                         if len(item1) != 0:
    #                             str2_rgx = self.seg_datetimes_rgx[1].match(item1)
    #                             start_2 = end_2
    #                             end_2 = str2_rgx.span(1)
    #                             datetime_list2.extend(item1[start_2:end_2])
    #                             item1 = item1[end_2:]
    #
    #                             if datetime_list1 is not None:
    #                                 datetime_list3 = []
    #                                 for item2 in datetime_list2:
    #                                     while(True):
    #                                         if len(item2) != 0:
    #                                             str3_rgx = self.seg_datetimes_rgx[2].match(item2)
    #                                             start_3 = end_3
    #                                             end_3 = str3_rgx.span(1)
    #                                             datetime_list3.extend(item2[start_3:end_3])
    #                                             item2 = item2[end_3:]
    #
    #                                             if datetime_list3 is not None:
    #                                                 datetime_list4 = []
    #                                                 for item3 in datetime_list3:
    #                                                     while(True):
    #                                                         if len(item3) != 0:
    #                                                             str4_rgx = self.seg_datetimes_rgx[0].match(item3)
    #                                                             start_4 = end_4
    #                                                             end_4 = str4_rgx.span(1)
    #                                                             datetime_list4.extend(item3[start_4:end_4])
    #                                                             item3 = item3[end_4:]
    #                                                         else:
    #                                                             break
    #
    #                                             elif datetime_list3 is None:
    #                                                 datetime_list4 = []
    #                                                 while (True):
    #                                                     if len(s) != 0:
    #                                                         str4_rgx = self.seg_datetimes_rgx[1].match(s)
    #                                                         start_4 = end_4
    #                                                         end_4 = str4_rgx.span(1)
    #                                                         datetime_list4.extend(s_[start_4:end_4])
    #                                                         s = s[end_4:]
    #                                                     else:
    #                                                         break
    #
    #                                         else:
    #                                             break
    #
    #                             elif datetime_list2 is None:
    #                                 datetime_list3 = []
    #                                 while (True):
    #                                     if len(s) != 0:
    #                                         str3_rgx = self.seg_datetimes_rgx[1].match(s)
    #                                         start_3 = end_3
    #                                         end_3 = str3_rgx.span(1)
    #                                         datetime_list3.extend(s_[start_3:end_3])
    #                                         s = s[end_3:]
    #
    #                                         if datetime_list3 is not None:
    #                                             datetime_list4 = []
    #                                             for item3 in datetime_list3:
    #                                                 while (True):
    #                                                     if len(item3) != 0:
    #                                                         str4_rgx = self.seg_datetimes_rgx[1].match(item3)
    #                                                         start_4 = end_4
    #                                                         end_4 = str4_rgx.span(1)
    #                                                         datetime_list4.extend(item3[start_4:end_4])
    #                                                         item3 = item3[end_4:]
    #
    #                                         elif datetime_list3 is None:
    #                                             datetime_list4 = []
    #                                             while (True):
    #                                                 if len(s) != 0:
    #                                                     str4_rgx = self.seg_datetimes_rgx[1].match(s)
    #                                                     start_4 = end_4
    #                                                     end_4 = str4_rgx.span(1)
    #                                                     datetime_list4.extend(s_[start_4:end_4])
    #                                                     s = s[end_4:]
    #                                     else:
    #                                         break
    #
    #                         else:
    #                             break
    #
    #             elif datetime_list1 is None:
    #                 datetime_list2 = []
    #                 while(True):
    #                     if len(s) != 0:
    #                         str2_rgx = self.seg_datetimes_rgx[1].match(s)
    #                         start_2 = end_2
    #                         end_2 = str2_rgx.span(1)
    #                         datetime_list2.extend(s_[start_2:end_2])
    #                         s = s[end_2:]
    #
    #                         if datetime_list2 is not None:
    #                             datetime_list3 = []
    #                             for item2 in datetime_list2:
    #                                 while (True):
    #                                     if len(item2) != 0:
    #                                         str3_rgx = self.seg_datetimes_rgx[1].match(item2)
    #                                         start_3 = end_3
    #                                         end_3 = str3_rgx.span(1)
    #                                         datetime_list3.extend(item2[start_3:end_3])
    #                                         item2 = item2[end_3:]
    #
    #                                         if datetime_list3 is not None:
    #                                             datetime_list4 = []
    #                                             for item3 in datetime_list3:
    #                                                 while (True):
    #                                                     if len(item3) != 0:
    #                                                         str4_rgx = self.seg_datetimes_rgx[2].match(item3)
    #                                                         start_4 = end_4
    #                                                         end_4 = str3_rgx.span(1)
    #                                                         datetime_list3.extend(item3[start_4:end_4])
    #                                                         item3 = item3[end_4:]
    #
    #                                                     else:
    #                                                         break
    #
    #                         elif datetime_list2 is None:
    #                             datetime_list3 = []
    #                             while (True):
    #                                 if len(s) != 0:
    #                                     str3_rgx = self.seg_datetimes_rgx[1].match(s)
    #                                     start_3 = end_3
    #                                     end_3 = str3_rgx.span(1)
    #                                     datetime_list3.extend(s_[start_3:end_3])
    #                                     s = s[end_3:]
    #
    #                                     if datetime_list3 is not None:
    #                                         datetime_list4 = []
    #                                         for item3 in datetime_list3:
    #                                             while (True):
    #                                                 if len(item3) != 0:
    #                                                     str4_rgx = self.seg_datetimes_rgx[1].match(item3)
    #                                                     start_4 = end_4
    #                                                     end_4 = str4_rgx.span(1)
    #                                                     datetime_list4.extend(item3[start_4:end_4])
    #                                                     item3 = item3[end_4:]
    #
    #                                     elif datetime_list3 is None:
    #                                         datetime_list4 = []
    #                                         while (True):
    #                                             if len(s) != 0:
    #                                                 str4_rgx = self.seg_datetimes_rgx[1].match(s)
    #                                                 start_4 = end_4
    #                                                 end_4 = str4_rgx.span(1)
    #                                                 datetime_list4.extend(s_[start_4:end_4])
    #                                                 s = s[end_4:]
    #                                 else:
    #                                     break
    #         else:
    #             break
    #
    #
    #     datetime_list1 = self.seg_datetimes_rgx[3].split(s)
    #     if datetime_list1 is not None:
    #         datetime_list2 = []
    #         for item in datetime_list1:
    #             datetime_list2.extend(self.seg_datetimes_rgx[1].split(item))
    #
    #             if datetime_list2 is not None:
    #                 datetime_list3 = []
    #                 for item_1 in datetime_list2:
    #                     datetime_list3.extend(self.seg_datetimes_rgx[2].split(item_1))
    #
    #                     if datetime_list3 is not None:
    #                         datetime_list4 = []
    #                         for item_2 in datetime_list3:
    #                             datetime_list4.extend(self.seg_datetimes_rgx[0].split(item_2))
    #                     # else:
    #                     #     if
    #
    #
    #     elif datetime_list1 is None:
    #         datetime_list2 = self.seg_datetimes_rgx[2].split(s)
    #
    #         # if datetime_list2 is not None:
    #         #     for item_1 in datetime_list2:



    def normalize_datetime(self,time_chunk_list):

        normalize_chunk = self.normalize_chunk

        if len(time_chunk_list) > 0:

            for time_chunk in time_chunk_list:

                time_str_list = []
                time_chunk_str = time_chunk['time_str']
                time_chunk_rgx = normalize_chunk.search(time_chunk_str)

                if time_chunk_rgx is not None:
                    time_str_list.append(time_chunk_rgx.group(1))
                    time_str_list.append(time_chunk_rgx.group(3))

                else:
                    time_str_list.append(time_chunk_str)

                time_chunk_list[time_chunk_list.index(time_chunk)]['time_str'] = time_str_list

            return time_chunk_list

        else:
            return time_chunk_list

    def parse_datetime(self,time_chunk_list, publishAt):

        arab_num = []
        for i in range(1, 32):
            num = str(i)
            arab_num.append(num)

        Chinese_num = self.Chinese_num

        rule = self.rule

        timeStamp = publishAt / 1000

        timeArray = time.localtime(timeStamp)

        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        otherStyleTime_list = otherStyleTime.split('-')
        otherStyleTime_list[0] = otherStyleTime_list[0] + '年'
        otherStyleTime_list[1] = otherStyleTime_list[1] + '月'
        otherStyleTime_list[2] = otherStyleTime_list[2] + '日'

        time_single_list = []

        for time_chunk in time_chunk_list:
            for item in time_chunk['time_str']:
                time_single_list.append(item)

        for time_chunk in time_chunk_list:

            msgs = time_chunk['time_str']
            time_chunk['full_time_str'] = []
            time_chunk['time_stamp'] = []

            for msg in msgs:
                k = -1

                if msg is None or len(msg) == 0:
                    time_chunk['time_stamp'] = 0
                else:
                    m_1 = re.match(
                        r"([0-9零一二两三四五六七八九十]+年)?([0-9一二两三四五六七八九十]+月)?([0-9一二两三四五六七八九十]+[号日])?([上中下午晚早]+)?([0-9零一二两三四五六七八九十百]+[点:\.时])?([0-9零一二三四五六七八九十百]+分)?([0-9零一二三四五六七八九十百]+秒)?",
                        msg)
                    # print(m_1.group(0))
                    if m_1.group(0) is not None:
                        res_list = ['year', 'month', 'day']
                        res = {
                            "year": m_1.group(1),
                            "month": m_1.group(2),
                            "day": m_1.group(3),
                            # "hour": m_1.group(5) if m_1.group(5) is not None else '00',
                            # "minute": m_1.group(6) if m_1.group(6) is not None else '00',
                            # "second": m_1.group(7) if m_1.group(7) is not None else '00',
                        }
                        params = {}

                        for name in res_list:
                            k = k + 1

                            if res[name] is None:

                                i = time_single_list.index(msg)

                                while (True):
                                    if i >= 0:

                                        m_2 = re.search(rule[k], time_single_list[i])

                                        # if m_2 is not None:
                                        #     print(m_2.group(0))
                                        if m_2 is not None:
                                            res[name] = m_2.group(1)
                                            break
                                        i = i - 1

                                    else:
                                        res[name] = otherStyleTime_list[res_list.index(name)]
                                        break

                        time_str1 = res["year"] + res["month"] + res["day"]
                        year = re.findall(r"(.+?)年", time_str1)
                        month = re.findall(r"年(.+?)月", time_str1)
                        day = re.findall(r"月(.+?)日", time_str1)
                        # print(year)
                        # print(month)
                        # print(day)

                        if day[0] in Chinese_num:
                            day[0] = arab_num[Chinese_num.index(day[0])]

                        if month[0] in Chinese_num:
                            month[0] = arab_num[Chinese_num.index(month[0])]

                        try:
                            dateC = datetime.datetime(int(year[0]), int(month[0]), int(day[0]), 00, 00)
                            # print(dateC)
                            timestamp = int(time.mktime(dateC.timetuple()) * 1000)
                        except Exception as e:
                            dateC = 0
                            timestamp = 0
                            print(e)

                        time_chunk['time_stamp'].append(timestamp)
                        time_chunk['full_time_str'].append(year[0] + '年' + month[0] + '月' + day[0] + '日')

        if time_chunk_list == []:
            full_time_str = str(datetime.datetime.fromtimestamp(publishAt / 1000))

            time_chunk_list = [{'time_stamp': [publishAt], 'offset': [0,0], 'time_str': [''], 'full_time_str': [full_time_str], 'type': 'TMP'}]

        return time_chunk_list


    def recursion_processing(self,s,t_lists,date_chunk_handle,flag,time_chunk_list):

        for chunk_dic in time_chunk_list:
            time_str = chunk_dic['time_str']
            t_lists.append(chunk_dic)
            s = s.replace(time_str,len(time_str) * str(flag),1)
            flag = flag + 1

        time_chunk_list = date_chunk_handle.get_date_chunk(s)

        if len(time_chunk_list) != 0:

            return date_chunk_handle.recursion_processing(s, t_lists,date_chunk_handle,flag,time_chunk_list)

        else:
            return t_lists




if __name__ == '__main__':

    s = '年是年2月3日是年是年是sada28日电2019年5月21日（星期五）下午８点-5月22日（星期六）上午9时一起去吃饭最后我们吃了米饭sada28日报道。'

    date_chunk_handle = Date_chunk_handle()
    # str_,idx = date_chunk_handle.con_extra_time(s)
    # print(str_)
    # print(idx)
    flag = 0
    t_lists = []
    time_chunk_list = date_chunk_handle.get_date_chunk(s)
    recursion_time_chunk = date_chunk_handle.recursion_processing(s,t_lists,date_chunk_handle,flag,time_chunk_list)
    print(recursion_time_chunk)
    normalize_list = date_chunk_handle.normalize_datetime(recursion_time_chunk)
    print(normalize_list)
    publishAt = 1555862400000
    time_stamp_list = date_chunk_handle.parse_datetime(normalize_list, publishAt)
    print(time_stamp_list)
    print("******************************************************************************")



    # with io.open('./2019-04-04_events.txt','r',encoding='utf-8') as f:
    #     while True:
    #         line = f.readline()
    #
    #         if len(line) > 0:
    #             json_data = json.loads(line)
    #             str1 = json_data["event_discription"]
    #             print(str1)
    #             time_chunk_list = date_chunk_handle.get_date_chunk(str1)
    #             normalize_list = date_chunk_handle.normalize_datetime(time_chunk_list)
    #             print(normalize_list)
    #             publishAt = 1555862400000
    #             time_stamp_list = date_chunk_handle.parse_datetime(normalize_list, publishAt)
    #             print(time_stamp_list)
    #             print("******************************************************************************")
    #
    #         else:
    #             break

        # print("End.")
