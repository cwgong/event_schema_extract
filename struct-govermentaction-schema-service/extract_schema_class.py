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
        pass

    def get_adjustnorm_schema(self,s,publishAt):
        for rgx in self.buyback_rgx:
            rgx_results = rgx.match(s)
            if rgx_results is not None:
                buyback_value = rgx_results[self.conference_rgx_index[rgx][0]]
                conference_name = rgx_results[self.conference_rgx_index[rgx][1]]
                conference_person = rgx_results[self.conference_rgx_index[rgx][2]]
                buyback_value_basic = "xxx"
                self.buyback_schema = {'buyback_value': buyback_value,
                                       'schema_len': 1,
                                       'extractScope': "sentences",
                                       'type': "buyback"}
                self.event_flag += 1
                self.schema_all.append(self.buyback_schema)
