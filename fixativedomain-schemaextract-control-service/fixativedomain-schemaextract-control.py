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
        self.event_flag = 0

        self.conference_rgx = []
        self.adjust_norm_rgx = []
        self.data_shift_rgx = []
        self.buyback_rgx = []
        self.schema_all = []

        self.adjust_norm_rgx_index = {}
        self.data_shift_rgx_index = {}
        self.conference_rgx_index = {}
        self.buyback_rgx_index = {}

        self.conference_schema = {}
        self.adjust_norm_schema = {}
        self.buyback_schema = {}
        self.data_shif_schema = {}

        for rgx in self.adjust_norm_rgx:
            self.adjust_norm_rgx_index[rgx] = [1,2,3]

        for rgx in self.data_shift_rgx:
            self.data_shift_rgx_index[rgx] = [1,2,3]

        for rgx in self.conference_rgx:
            # if rgx == 1:
            self.conference_rgx_index[rgx] = [1,2,3]

        for rgx in self.buyback_rgx:
            # if rgx == 1:
            self.buyback_rgx_index[rgx] = [1,2,3]


    def get_schema_sen(self, s, publishAt):

        conference_url = ''
        adjustnorms_url = ''
        datashift_url = ''
        govermentaction_url = ''
        naturaldisater_url = ''
        schemas_all = []

        # 会议类别的抽取
        try:
            conference_schema_dic = {}
            conference_schema_dic['s'] = s
            conference_schema_dic['publishAt'] = publishAt
            data = json.dumps(conference_schema_dic).encode("UTF-8")
            conference_schema = requests.post(url=conference_url,data=data)
            conference_schema = conference_schema.json()
            schemas_all.extend(conference_schema)

        except Exception as e:
            logging.info(e)

        # 规则变动类别的抽取
        try:
            adjustnorms_schema_dic = {}
            adjustnorms_schema_dic['s'] = s
            adjustnorms_schema_dic['publishAt'] = publishAt
            data = json.dumps(adjustnorms_schema_dic).encode("UTF-8")
            adjustnorms_schema = requests.post(url=adjustnorms_url,data=data)
            adjustnorms_schema = adjustnorms_schema.json()
            schemas_all.extend(adjustnorms_schema)

        except Exception as e:
            logging.info(e)

        # 数据改变类别的抽取
        try:
            datashift_schema_dic = {}
            datashift_schema_dic['s'] = s
            datashift_schema_dic['publishAt'] = publishAt
            data = json.dumps(datashift_schema_dic).encode("UTF-8")
            datashift_schema = requests.post(url=datashift_url, data=data)
            datashift_schema = datashift_schema.json()
            schemas_all.extend(datashift_schema)

        except Exception as e:
            logging.info(e)

        # 政府行为类别的抽取
        try:
            govermentaction_schema_dic = {}
            govermentaction_schema_dic['s'] = s
            govermentaction_schema_dic['publishAt'] = publishAt
            data = json.dumps(govermentaction_schema_dic).encode("UTF-8")
            govermentaction_schema = requests.post(url=govermentaction_url, data=data)
            govermentaction_schema = govermentaction_schema.json()
            schemas_all.extend(govermentaction_schema)

        except Exception as e:
            logging.info(e)

        # 自然灾害类别的抽取
        try:
            naturaldisater_schema_dic = {}
            naturaldisater_schema_dic['s'] = s
            naturaldisater_schema_dic['publishAt'] = publishAt
            data = json.dumps(naturaldisater_schema_dic).encode("UTF-8")
            naturaldisater_schema = requests.post(url=naturaldisater_url, data=data)
            naturaldisater_schema = naturaldisater_schema.json()
            schemas_all.extend(naturaldisater_schema)

        except Exception as e:
            logging.info(e)


        # for rgx in self.conference_rgx:
        #     rgx_results = rgx.match(s)
        #     if rgx_results is not None:
        #         conference_org = rgx_results[self.conference_rgx_index[rgx][0]]
        #         conference_name = rgx_results[self.conference_rgx_index[rgx][1]]
        #         conference_person = rgx_results[self.conference_rgx_index[rgx][2]]
        #         conference_org_basic = "xxx"
        #         conference_name_basic = "xxx"
        #         conference_person_basic = "xxx"
        #         self.conference_schema = {'conference_org': conference_org,
        #                                   'conference_name': conference_name,
        #                                   'conference_person': conference_person,
        #                                   'conference_org_basic': conference_org_basic,
        #                                   'conference_name_basic': conference_name_basic,
        #                                   'conference_person_basic': conference_person_basic,
        #                                   'schema_len': 1,
        #                                   'extractScope': "sentences",
        #                                   'type': "conference"}
        #         self.event_flag += 1
        #         self.schema_all.append(self.conference_schema)
        #
        # for rgx in self.adjust_norm_rgx:
        #     rgx_results = rgx.match(s)
        #     if rgx_results is not None:
        #         adjust_norm_org = rgx_results[self.adjust_norm_rgx_index[rgx][0]]
        #         adjust_norm_name = rgx_results[self.adjust_norm_rgx_index[rgx][1]]
        #         adjust_norm_direct = rgx_results[self.adjust_norm_rgx_index[rgx][2]]
        #         adjust_norm_value = rgx_results[self.adjust_norm_rgx_index[rgx][3]]
        #         adjust_norm_org_basic = "xxx"
        #         self.adjust_norm_schema = {'adjust_norm_org': adjust_norm_org,
        #                                    'adjust_norm_name': adjust_norm_name,
        #                                    'adjust_norm_direct': adjust_norm_direct,
        #                                    'adjust_norm_value': adjust_norm_value,
        #                                    'schema_len': 1,
        #                                    'extractScope': "sentences",
        #                                    'type': "adjust_norm"}
        #         self.event_flag += 1
        #         self.schema_all.append(self.adjust_norm_rgx)
        #
        # for rgx in self.data_shift_rgx:
        #     rgx_results = rgx.match(s)
        #     if rgx_results is not None:
        #         data_shift_value = rgx_results[self.data_shift_rgx_index[rgx][0]]
        #         conference_name = rgx_results[self.data_shift_rgx_index[rgx][1]]
        #         conference_person = rgx_results[self.data_shift_rgx_index[rgx][2]]
        #         data_shift_value_basic = "xxx"
        #         self.data_shif_schema = {'data_shift_value': data_shift_value,
        #                                  'schema_len': 1,
        #                                  'extractScope': "sentences",
        #                                  'type': "data_shift"}
        #         self.event_flag += 1
        #         self.schema_all.append(self.data_shif_schema)
        #
        # for rgx in self.buyback_rgx:
        #     rgx_results = rgx.match(s)
        #     if rgx_results is not None:
        #         buyback_value = rgx_results[self.conference_rgx_index[rgx][0]]
        #         conference_name = rgx_results[self.conference_rgx_index[rgx][1]]
        #         conference_person = rgx_results[self.conference_rgx_index[rgx][2]]
        #         buyback_value_basic = "xxx"
        #         self.buyback_schema = {'buyback_value': buyback_value,
        #                                'schema_len': 1,
        #                                'extractScope': "sentences",
        #                                'type': "buyback"}
        #         self.event_flag += 1
        #         self.schema_all.append(self.buyback_schema)

        if type != 'abstract':
            return self.schema_all

        if len(self.schema_all) > 0:
            return self.schema_all

    #         篇章级抽取

    def get_schema_article(self,doc):
        pass
