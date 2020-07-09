# -*- coding: utf-8 -*-

import io
import json
import uuid
from time_utils import timestamp_to_date,current_time
import requests
import collections
import re
import logging
import codecs
from date_chunk_handle_class import Date_chunk_handle

class Extract_Schema:

    def __init__(self):
        conference1_rgx = ''

        self.conference_rgx = [conference1_rgx]
        self.conference_rgx_index = {}

        for rgx in self.conference_rgx:
            self.conference_rgx_index[rgx] = [1, 2, 3]

    def get_conference_schema(self, abstract,title, publishAt):
        schema_all_article = []
        conference_schema = {}
        for rgx in self.conference_rgx:
            rgx_results = rgx.match(abstract)
            if rgx_results is not None:
                conference_org = rgx_results[self.conference_rgx_index[rgx][0]]
                conference_name = rgx_results[self.conference_rgx_index[rgx][1]]
                conference_person = rgx_results[self.conference_rgx_index[rgx][2]]
                # 此处需要调用知识图谱的接口来获取基词信息
                conference_org_basic = "xxx"
                conference_name_basic = "xxx"
                conference_person_basic = "xxx"
                # 此处注意需要和开放域的抽取数据结构保持一致，在开放域中一句话有多个schema，会将一个schema携带该句子完整的信息，多个schema以字典的形式存储在一个大的列表中，因此该列表包含该句子所有的schema信息
                conference_schema = {'conference_org': conference_org,
                                          'conference_name': conference_name,
                                          'conference_person': conference_person,
                                          'conference_org_basic': conference_org_basic,
                                          'conference_name_basic': conference_name_basic,
                                          'conference_person_basic': conference_person_basic,
                                          'schema_len': 1,
                                          'extractScope': "sentences",
                                          'type': "conference"}
                # self.event_flag += 1
                schema_all_article.append(conference_schema)
                return schema_all_article