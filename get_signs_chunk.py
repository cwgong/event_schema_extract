import re

def get_special_chunk(text):
    signs_infos_list = []
    special_signs_rgx = []
    special_signs = [['(', ')'], ['（', '）'], ['<','>'],['《', '》'], ['【', '】'],['[',']'],['{','}'],
                     ['「', '」'], ['‘', '’'], ['\"', '\"'],['“', '”'], ['\'', '\'']]

    for i in range(0,len(special_signs)):
        special_signs_rgx.append(re.compile(r'[{0}](.*?)[{1}]'.format(special_signs[i][0],special_signs[i][1])))

    special_signs = ['（','(','<','《','【','[','{','「','‘','\"','“','\'']

    for item in special_signs_rgx:
        item_rgx = item.finditer(text)
        if item_rgx is not None:
            for m in item_rgx:
                signs_infos = {}
                signs_infos['offset'] = m.span()
                signs_infos['chunk_str'] = m.group(0)
                signs_infos['type'] = str(special_signs[special_signs_rgx.index(item)])
                signs_infos_list.append(signs_infos)
    return signs_infos_list


import re


def get_special_chunk_2(text):
    signs_infos_list = []

    special_signs = [['(', ')'], ['（', '）'], ['<', '>'], ['《', '》'], ['【', '】'], ['[', ']'], ['{', '}'],
                     ['「', '」'], ['‘', '’'], ['\"', '\"'], ['“', '”'], ['\'', '\'']]

    special_signs_rgx_info = []
    for i in range(0, len(special_signs)):
        rgx = re.compile(r'[{0}](.*?)[{1}]'.format(special_signs[i][0], special_signs[i][1]))
        type = special_signs[i][0]
        temp_dic = {}
        temp_dic['rgx'] = rgx
        temp_dic['type'] = type
        special_signs_rgx_info.append(temp_dic)

    for x in special_signs_rgx_info:
        item = x['rgx']
        type = x['type']
        item_rgx = item.finditer(s)
        if item_rgx is not None:
            for m in item_rgx:
                signs_infos = {}
                signs_infos['offset'] = m.span()
                signs_infos['chunk_str'] = m.group(0)
                signs_infos['type'] = type
                signs_infos_list.append(signs_infos)
    print(signs_infos_list)


if __name__ == '__main__':
    s = '"今"天是（星期五）一起去（<吃饭>）,所以“明年”一"起去"{阿萨德快乐}好啊《法法》明天企业所以一起去'
    get_special_chunk(s)
