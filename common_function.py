from get_signs_chunk import get_special_chunk


def signs_handle(self ,item):
    special_signs = ['（', '(', '<', '《', '【', '[', '{', '「', '‘', '\"', '“', '\'' ,'”' ,'’' ,'」' ,'}' ,']' ,'】' ,'》'
                     ,'>' ,'）' ,')']

    signs_list = get_special_chunk(item)
    for sign_dic in signs_list:
        chunk_str = sign_dic['chunk_str']
        item = item.replace(chunk_str ,'')
    return item ,signs_list

