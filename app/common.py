# coding=utf8
import time
from datetime import datetime
import re,json

# 随机手机号
def get_random_mobile():
    random_mobile = time.time()
    random_mobile = int(round(random_mobile * 10))
    return random_mobile
# 时间戳 10位
def timestamp():
    timestamp_ten = int(time.time())
    return timestamp_ten
# 时间戳13位
def current_milli_time():
    timestamp_thirteen = int(round(time.time()*1000))
    return timestamp_thirteen

# 当前时间, 格式: %Y-%m-%d %H:%M:%S
def datetimeformat():
   time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   return time

# 当前时间, 格式: %Y%m%d%H%M%S
def datetimeformat_int():
   time = datetime.now().strftime('%Y%m%d%H%M%S')
   return time

# 当前日期, 格式: %Y-%m-%d
def dateformat():
   time = datetime.now().strftime('%Y-%m-%d')
   return time

# 当前日期, 格式: %Y%m%d
def dateformat_int():
   time = datetime.now().strftime('%Y%m%d')
   return time

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def check_json_format(raw_msg):
    """
    用于判断一个字符串是否符合Json格式
    :param self:
    :return:
    """
    if isinstance(raw_msg, str): # 首先判断变量是否为字符串
        try:
            json.loads(raw_msg, encoding='utf-8')
        except ValueError:
            return False
        return True
    else:
        return False

def convert_to_dict(obj):
    '''把Object对象转换成Dict对象'''
    dict = {}
    dict.update(obj.__dict__)
    return dict


def convert_to_dicts(objs):
    '''把对象列表转换为字典列表'''
    obj_arr = []
    for o in objs:
        # 把Object对象转换成Dict对象
        dict = {}
        dict.update(o.__dict__)
        obj_arr.append(dict)
    return obj_arr


def class_to_dict(obj):
    '''把对象(支持单个对象、list、set)转换成字典'''
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__
    if is_list or is_set:
        obj_arr = []
        for o in obj:
            # 把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict


def get_target_value(key, dic, tmp_list):
    """
    :param key: 目标key值
    :param dic: JSON数据
    :param tmp_list: 用于存储获取的数据
    :return: list
    """
    if not isinstance(dic, dict) or not isinstance(tmp_list, list):  # 对传入数据进行格式校验
        return 'argv[1] not an dict or argv[-1] not an list '

    if key in dic.keys():
        tmp_list.append(str(dic[key]))  # 传入数据存在则存入tmp_list
    for value in dic.values():  # 传入数据不符合则对其value值进行遍历
        if isinstance(value, dict):
            get_target_value(key, value, tmp_list)  # 传入数据的value值是字典，则直接调用自身
        elif isinstance(value, (list, tuple)):
            _get_value(key, value, tmp_list)  # 传入数据的value值是列表或者元组，则调用_get_value
    return tmp_list

def _get_value(key, val, tmp_list):
    for val_ in val:
        if isinstance(val_, dict):
            get_target_value(key, val_, tmp_list)  # 传入数据的value值是字典，则调用get_target_value
        elif isinstance(val_, (list, tuple)):
            _get_value(key, val_, tmp_list)   # 传入数据的value值是列表或者元组，则调用自身

# 查到字典中key的存在，则存key
def haskey(key,dic):
    found = []
    for k, v in dic.items():
        if k == key:
            found.append(k)
        elif isinstance(v, dict):
            results = haskey(key, v)
            for result in results:
                found.append(result)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    more_results = haskey(key, item)
                    for another_result in more_results:
                        found.append(another_result)
    return found

def subString(str): #函数
    rule = r'<(.*?)>'
    slotList = re.findall(rule, str)
    return slotList

def subString2(str): #参数
    rule = r'{{(.*?)}}'
    slotList = re.findall(rule, str)
    return slotList

# src_data 是dst_data的dict子集
# 使用此函数需要定义一个全局变量 _flag
_flag = ""
def cmp_dict(src_data, dst_data):
    global _flag
    if type(src_data) == type(dst_data):
        if _flag != 0:
            _flag = 1
    else:
        _flag = 0
    if isinstance(src_data, dict):
        for key in src_data:
            if key in dst_data:
                cmp_dict(src_data[key], dst_data[key])
    elif isinstance(src_data, list):
        for index, v in enumerate(src_data):
            if isinstance(v, str):
                for src_list, dst_list in zip(sorted(src_data), sorted(dst_data)):
                    cmp_dict(src_list, dst_list)
            elif isinstance(v, list):
                cmp_dict(v, dst_list[index])
            elif isinstance(v, dict):
                for k in v:
                    if k in dst_data[index]:
                        cmp_dict(v[k], dst_data[index][k])
    else:
        if src_data == dst_data:
            if _flag == 1:
                _flag = 1
        else:
            _flag = 0
    return _flag

# 统计字段数量 等于 期望字段数量
def countequal(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getlength = len(get_target_value(t[0], actualResults, []))
                if getlength == int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是" + str(t[1]) + ",实际结果是" + getlength + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是" + str(t[1]) + ",实际结果是" + getlength + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getlength = len(get_target_value(t[0], actualResults, []))
            if getlength == int(t[1]):
                if result != 0:
                    result = 1
            else:
                result = 0
                if reasons == "":
                    reasons = str(t[0]) + "的期望结果是" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
                else:
                    reasons = reasons + str(t[0]) + "的期望结果是" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result,reasons

# 统计字段数量 大于 期望字段数量
def countgreater(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getlength = len(get_target_value(t[0], actualResults, []))
                if getlength > int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是大于" + str(t[1]) + ",实际结果是" + getlength + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是大于" + str(t[1]) + ",实际结果是" + getlength + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getlength = len(get_target_value(t[0], actualResults, []))
            if getlength > int(t[1]):
                if result != 0:
                    result = 1
            else:
                result = 0
                if reasons == "":
                    reasons = str(t[0]) + "的期望结果是大于" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
                else:
                    reasons = reasons + str(t[0]) + "的期望结果是大于" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result,reasons

# 统计字段数量 大于等于 期望字段数量
def countgreaterequal(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getlength = len(get_target_value(t[0], actualResults, []))
                if getlength >= int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是大于等于" + str(t[1]) + ",实际结果是" + getlength + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是大于等于" + str(t[1]) + ",实际结果是" + getlength + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getlength = len(get_target_value(t[0], actualResults, []))
            if getlength >= int(t[1]):
                if result != 0:
                    result = 1
            else:
                result = 0
                if reasons == "":
                    reasons = str(t[0]) + "的期望结果是大于等于" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
                else:
                    reasons = reasons + str(t[0]) + "的期望结果是大于等于" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result,reasons

# 统计字段数量 小于 期望字段数量
def countless(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getlength = len(get_target_value(t[0], actualResults, []))
                if getlength < int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是小于" + str(t[1]) + ",实际结果是" + getlength + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是小于" + str(t[1]) + ",实际结果是" + getlength + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getlength = len(get_target_value(t[0], actualResults, []))
            if getlength < int(t[1]):
                if result != 0:
                    result = 1
            else:
                result = 0
                if reasons == "":
                    reasons = str(t[0]) + "的期望结果是小于" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
                else:
                    reasons = reasons + str(t[0]) + "的期望结果是小于" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result,reasons

# 统计字段数量 小于等于 期望字段数量
def countlessequal(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getlength = len(get_target_value(t[0], actualResults, []))
                if getlength <= int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是小于等于" + str(t[1]) + ",实际结果是" + getlength + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是小于等于" + str(t[1]) + ",实际结果是" + getlength + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getlength = len(get_target_value(t[0], actualResults, []))
            if getlength <= int(t[1]):
                if result != 0:
                    result = 1
            else:
                result = 0
                if reasons == "":
                    reasons = str(t[0]) + "的期望结果是小于等于" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
                else:
                    reasons = reasons + str(t[0]) + "的期望结果是小于等于" + str(t[1]) + ",实际结果是" + str(getlength) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result,reasons

# 字段值 等于 期望字段值
def valueequal(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getvaluelist = get_target_value(t[0], actualResults, [])
                for value in getvaluelist:
                    if str(value) == str(t[1]):
                        if result != 0:
                            result = 1
                    else:
                        result = 0
                        if reasons == "":
                            reasons = str(t[0]) + "的期望结果是" + str(t[1]) + ",实际结果是" + str(value) + "。"
                        else:
                            reasons = reasons + str(t[0]) + "的期望结果是" + str(t[1]) + ",实际结果是" + str(value) + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getvaluelist = get_target_value(t[0], actualResults, [])
            for value in getvaluelist:
                if str(value) == str(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是" + str(t[1]) + ",实际结果是" + str(value) + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是" + str(t[1]) + ",实际结果是" + str(value) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result, reasons

# 字段值 大于 期望字段值
def valuegreater(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getvaluelist = get_target_value(t[0], actualResults, [])
                for value in getvaluelist:
                    if int(value) > int(t[1]):
                        if result != 0:
                            result = 1
                    else:
                        result = 0
                        if reasons == "":
                            reasons = str(t[0]) + "的期望结果是大于" + str(t[1]) + ",实际结果是" + str(value) + "。"
                        else:
                            reasons = reasons + str(t[0]) + "的期望结果是大于" + str(t[1]) + ",实际结果是" + str(value) + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getvaluelist = get_target_value(t[0], actualResults, [])
            for value in getvaluelist:
                if int(value) > int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是大于" + str(t[1]) + ",实际结果是" + str(value) + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是大于" + str(t[1]) + ",实际结果是" + str(value) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result, reasons

# 字段值 大于等于 期望字段值
def valuegreaterequal(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getvaluelist = get_target_value(t[0], actualResults, [])
                for value in getvaluelist:
                    if int(value) >= int(t[1]):
                        if result != 0:
                            result = 1
                    else:
                        result = 0
                        if reasons == "":
                            reasons = str(t[0]) + "的期望结果是大于等于" + str(t[1]) + ",实际结果是" + str(value) + "。"
                        else:
                            reasons = reasons + str(t[0]) + "的期望结果是大于等于" + str(t[1]) + ",实际结果是" + str(value) + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getvaluelist = get_target_value(t[0], actualResults, [])
            for value in getvaluelist:
                if int(value) >= int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是大于等于" + str(t[1]) + ",实际结果是" + str(value) + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是大于等于" + str(t[1]) + ",实际结果是" + str(value) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result, reasons

# 字段值 小于 期望字段值
def valueless(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getvaluelist = get_target_value(t[0], actualResults, [])
                for value in getvaluelist:
                    if int(value) < int(t[1]):
                        if result != 0:
                            result = 1
                    else:
                        result = 0
                        if reasons == "":
                            reasons = str(t[0]) + "的期望结果是小于" + str(t[1]) + ",实际结果是" + str(value) + "。"
                        else:
                            reasons = reasons + str(t[0]) + "的期望结果是小于" + str(t[1]) + ",实际结果是" + str(value) + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getvaluelist = get_target_value(t[0], actualResults, [])
            for value in getvaluelist:
                if int(value) < int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是小于" + str(t[1]) + ",实际结果是" + str(value) + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是小于" + str(t[1]) + ",实际结果是" + str(value) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result, reasons

# 字段值 小于等于 期望字段值
def valuelessequal(expectedResults, actualResults,result,reasons):
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getvaluelist = get_target_value(t[0], actualResults, [])
                for value in getvaluelist:
                    if int(value) <= int(t[1]):
                        if result != 0:
                            result = 1
                    else:
                        result = 0
                        if reasons == "":
                            reasons = str(t[0]) + "的期望结果是小于等于" + str(t[1]) + ",实际结果是" + str(value) + "。"
                        else:
                            reasons = reasons + str(t[0]) + "的期望结果是小于等于" + str(t[1]) + ",实际结果是" + str(value) + "。"
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getvaluelist = get_target_value(t[0], actualResults, [])
            for value in getvaluelist:
                if int(value) <= int(t[1]):
                    if result != 0:
                        result = 1
                else:
                    result = 0
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是小于等于" + str(t[1]) + ",实际结果是" + str(value) + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是小于等于" + str(t[1]) + ",实际结果是" + str(value) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result, reasons

# 期望字段 存在
def keyexist(expectedResults, actualResults,result,reasons):
    if not isinstance(actualResults, dict):
        result = 0
        reasons = '不是dict'
        return result,reasons
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            keylist = haskey(n, actualResults)
            if len(keylist) >= 1:
                if result != 0:
                    result = 1
            else:
                result = 0
                if reasons == "":
                    reasons = "字段 " + n + " 不存在。"
                else:
                    reasons = reasons + "字段 " + n + " 不存在。"
    else:
        keylist = haskey(expectedResults, actualResults)
        if len(keylist) >= 1:
            if result != 0:
                result = 1
        else:
            result = 0
            if reasons == "":
                reasons = "字段 " + expectedResults + " 不存在。"
            else:
                reasons = reasons + "字段 " + expectedResults + " 不存在。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result,reasons

# 字段值 包含 期望字段值
def inkeyvalue(expectedResults, actualResults,result,reasons):
    count = 0
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getvaluelist = get_target_value(t[0], actualResults, [])
                for value in getvaluelist:
                    if str(t[1]) in str(value):
                        if result != 0:
                            result = 1
                    else:
                        if count == 1:
                            continue
                        result = 0
                        count = 1
                        if reasons == "":
                            reasons = str(t[0]) + "的期望结果是包含" + str(t[1]) + ",实际结果是不包含" + str(t[1]) + "。"
                        else:
                            reasons = reasons + str(t[0]) + "的期望结果是包含" + str(t[1]) + ",实际结果是不包含" + str(t[1]) + "。"
            count = 0
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getvaluelist = get_target_value(t[0], actualResults, [])
            for value in getvaluelist:
                if str(t[1]) in str(value):
                    if result != 0:
                        result = 1
                else:
                    if count == 1:
                        continue
                    result = 0
                    count = 1
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是包含" + str(t[1]) + ",实际结果是不包含" + str(t[1]) + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是包含" + str(t[1]) + ",实际结果是不包含" + str(t[1]) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result, reasons

# 字段值 不包含 期望字段值
def notinkeyvalue(expectedResults, actualResults,result,reasons):
    count = 0
    if expectedResults.find("|") >= 0:
        r = expectedResults.split("|")
        for n in r:
            if n.find(":") >= 0:
                t = n.split(":")
                getvaluelist = get_target_value(t[0], actualResults, [])
                for value in getvaluelist:
                    if str(t[1]) not in str(value):
                        if result != 0:
                            result = 1
                    else:
                        if count == 1:
                            continue
                        result = 0
                        count = 1
                        if reasons == "":
                            reasons = str(t[0]) + "的期望结果是不包含" + str(t[1]) + ",实际结果是包含" + str(t[1]) + "。"
                        else:
                            reasons = reasons + str(t[0]) + "的期望结果是不包含" + str(t[1]) + ",实际结果是包含" + str(t[1]) + "。"
            count = 0
    else:
        if expectedResults.find(":") >= 0:
            t = expectedResults.split(":")
            getvaluelist = get_target_value(t[0], actualResults, [])
            for value in getvaluelist:
                if str(t[1]) not in str(value):
                    if result != 0:
                        result = 1
                else:
                    if count == 1:
                        continue
                    result = 0
                    count = 1
                    if reasons == "":
                        reasons = str(t[0]) + "的期望结果是不包含" + str(t[1]) + ",实际结果是包含" + str(t[1]) + "。"
                    else:
                        reasons = reasons + str(t[0]) + "的期望结果是不包含" + str(t[1]) + ",实际结果是包含" + str(t[1]) + "。"
    if result == "":
        result = 0
        reasons = "期望结果格式不正确"
    return result, reasons





if __name__ == '__main__':
    # jsondata = {"0": {"id": "{{getvalue}}", "modulename": "{{get_random_mobile}}", "status": "1", "note": "\u5b9a\u91d1\u62c5\u4fdd", "project_id": "1"}, "1": {"id": "2", "modulename": "\u5e93\u5b58\u7ba1\u7406", "status": "1", "note": "\u5e93\u5b58\u7ba1\u7406\u5907\u6ce8", "project_id": "2"}, "2": {"id": "4", "modulename": "\u5e93\u878d\u8d37", "status": "1", "note": "\u5e93\u878d\u8d37", "project_id": "1"}}
    # aaa = get_target_value('modulename',jsondata, [])[1]
    # print(aaa)

    template = "我要<歌手名>的<歌曲名>"
    # print(subString(template))
    # print(subString2(json.dumps(jsondata)))
    # ss = json.dumps(jsondata)
    #
    # b = subString2(ss)
    # print(b)
    # for i in b:
    #     print("====")
    #     new_s = str(eval(i)())
    #     old_s = "{{"+i+"}}"
    #     sss = ss.replace(old_s, new_s)
    #     ss = sss
    # print(ss)

    _flag = ""
    a = {"error":0,"msg":"","data":[{"t":"A","l":[{"pbid":208,"name":"AA品牌1_2","letter":"A","code":"brand-874"},{"pbid":201,"name":"AA品牌2","letter":"A","code":"brand-876"},{"pbid":205,"name":"AA品牌6","letter":"A","code":"brand-880"},{"pbid":206,"name":"AA品牌6","letter":"A","code":"brand-880"},{"pbid":207,"name":"AA品牌7","letter":"A","code":"brand-881"},{"pbid":209,"name":"AA品牌8","letter":"A","code":"brand-882"},{"pbid":165,"name":"AC Schnitzer","letter":"A","code":"brand-859"},{"pbid":232,"name":"alltest-brand","letter":"A","code":"brand-912"},{"pbid":181,"name":"ALPINA","letter":"A","code":"brand-856"},{"pbid":34,"name":"阿斯顿・马丁","letter":"A","code":"brand-13"},{"pbid":3,"name":"奥迪","letter":"A","code":"brand-15"}]}]}

    b = {'error':0,'msg':'','data':[{'t': 'A', 'l': [{'pbid': 208, 'name': 'AA品牌1_2', 'letter': 'A', 'code': 'brand-874'}, {'pbid': 201, 'name': 'AA品牌2', 'letter': 'A', 'code': 'brand-876'}, {'pbid': 205, 'name': 'AA品牌6', 'letter': 'A', 'code': 'brand-880'}, {'pbid': 206, 'name': 'AA品牌6', 'letter': 'A', 'code': 'brand-880'}, {'pbid': 207, 'name': 'AA品牌7', 'letter': 'A', 'code': 'brand-881'}, {'pbid': 209, 'name': 'AA品牌8', 'letter': 'A', 'code': 'brand-882'}, {'pbid': 165, 'name': 'AC Schnitzer', 'letter': 'A', 'code': 'brand-859'}, {'pbid': 232, 'name': 'alltest-brand', 'letter': 'A', 'code': 'brand-912'}, {'pbid': 181, 'name': 'ALPINA', 'letter': 'A', 'code': 'brand-856'}, {'pbid': 34, 'name': '阿斯顿・马丁', 'letter': 'A', 'code': 'brand-13'}, {'pbid': 3, 'name': '奥迪', 'letter': 'A', 'code': 'brand-15'}]}, {'t': 'B', 'l': [{'pbid': 37, 'name': '巴博斯', 'letter': 'B', 'code': 'brand-1018-n'}, {'pbid': 68, 'name': '宝骏', 'letter': 'B', 'code': 'brand-18'}, {'pbid': 1, 'name': '宝马', 'letter': 'B', 'code': 'brand-20'}, {'pbid': 175, 'name': '宝沃', 'letter': 'B', 'code': 'brand-821'}, {'pbid': 15, 'name': '保时捷', 'letter': 'B', 'code': 'brand-22'}, {'pbid': 69, 'name': '北京汽车', 'letter': 'B', 'code': 'brand-534'}, {'pbid': 170, 'name': '北汽幻速', 'letter': 'B', 'code': 'brand-570'}, {'pbid': 187, 'name': '北汽绅宝', 'letter': 'B', 'code': ''}, {'pbid': 169, 'name': '北汽威旺', 'letter': 'B', 'code': 'brand-546'}, {'pbid': 190, 'name': '北汽新能源', 'letter': 'B', 'code': ''}, {'pbid': 35, 'name': '北汽制造', 'letter': 'B', 'code': 'brand-24'}, {'pbid': 2, 'name': '奔驰', 'letter': 'B', 'code': 'brand-25'}, {'pbid': 31, 'name': '奔腾', 'letter': 'B', 'code': 'brand-26'}, {'pbid': 10, 'name': '本田', 'letter': 'B', 'code': 'brand-27'}, {'pbid': 182, 'name': '比速汽车', 'letter': 'B', 'code': 'brand-829'}, {'pbid': 22, 'name': '比亚迪', 'letter': 'B', 'code': 'brand-28'}, {'pbid': 7, 'name': '标致', 'letter': 'B', 'code': 'brand-29'}, {'pbid': 210, 'name': '标致7', 'letter': 'B', 'code': 'brand-883'}, {'pbid': 12, 'name': '别克', 'letter': 'B', 'code': 'brand-30'}, {'pbid': 36, 'name': '宾利', 'letter': 'B', 'code': 'brand-31'}, {'pbid': 157, 'name': '宾仕盾', 'letter': 'B', 'code': 'brand-822'}, {'pbid': 38, 'name': '布加迪', 'letter': 'B', 'code': 'brand-33'}]}, {'t': 'C', 'l': [{'pbid': 71, 'name': '昌河', 'letter': 'C', 'code': 'brand-35'}, {'pbid': 30, 'name': '长安', 'letter': 'C', 'code': 'brand-164'}, {'pbid': 193, 'name': '长安跨越', 'letter': 'C', 'code': 'brand-526'}, {'pbid': 70, 'name': '长安欧尚', 'letter': 'C', 'code': 'brand-526'}, {'pbid': 192, 'name': '长安轻型车', 'letter': 'C', 'code': 'brand-526'}, {'pbid': 23, 'name': '长城', 'letter': 'C', 'code': 'brand-165'}, {'pbid': 130, 'name': '成功', 'letter': 'C', 'code': 'brand-516'}]}, {'t': 'D', 'l': [{'pbid': 98, 'name': 'DS', 'letter': 'D', 'code': 'brand-544'}, {'pbid': 5, 'name': '大众', 'letter': 'D', 'code': 'brand-41'}, {'pbid': 40, 'name': '道奇', 'letter': 'D', 'code': 'brand-42'}, {'pbid': 41, 'name': '东风', 'letter': 'D', 'code': 'brand-506'}, {'pbid': 185, 'name': '东风风度', 'letter': 'D', 'code': 'brand-506'}, {'pbid': 171, 'name': '东风风光', 'letter': 'D', 'code': 'brand-817'}, {'pbid': 172, 'name': '东风风神', 'letter': 'D', 'code': 'brand-522'}, {'pbid': 173, 'name': '东风风行', 'letter': 'D', 'code': 'brand-574'}, {'pbid': 74, 'name': '东风小康', 'letter': 'D', 'code': 'brand-524'}, {'pbid': 76, 'name': '东南', 'letter': 'D', 'code': 'brand-45'}]}, {'t': 'F', 'l': [{'pbid': 42, 'name': '法拉利', 'letter': 'F', 'code': 'brand-46'}, {'pbid': 117, 'name': '菲斯科', 'letter': 'F', 'code': 'brand-820'}, {'pbid': 43, 'name': '菲亚特', 'letter': 'F', 'code': 'brand-48'}, {'pbid': 6, 'name': '丰田', 'letter': 'F', 'code': 'brand-49'}, {'pbid': 134, 'name': '福迪', 'letter': 'F', 'code': 'brand-52'}, {'pbid': 136, 'name': '福汽启腾', 'letter': 'F', 'code': 'brand-508'}, {'pbid': 4, 'name': '福特', 'letter': 'F', 'code': 'brand-53'}, {'pbid': 77, 'name': '福田', 'letter': 'F', 'code': 'brand-54'}]}, {'t': 'G', 'l': [{'pbid': 44, 'name': 'GMC', 'letter': 'G', 'code': 'brand-3'}, {'pbid': 118, 'name': '观致', 'letter': 'G', 'code': 'brand-1001-n'}, {'pbid': 45, 'name': '光冈', 'letter': 'G', 'code': 'brand-580'}, {'pbid': 78, 'name': '广汽传祺', 'letter': 'G', 'code': 'brand-56'}, {'pbid': 174, 'name': '广汽吉奥', 'letter': 'G', 'code': 'brand-71'}]}, {'t': 'H', 'l': [{'pbid': 79, 'name': '哈飞', 'letter': 'H', 'code': 'brand-57'}, {'pbid': 167, 'name': '哈弗', 'letter': 'H', 'code': 'brand-530'}, {'pbid': 80, 'name': '海格', 'letter': 'H', 'code': 'brand-465'}, {'pbid': 46, 'name': '海马', 'letter': 'H', 'code': 'brand-58'}, {'pbid': 180, 'name': '汉腾', 'letter': 'H', 'code': 'brand-835'}, {'pbid': 47, 'name': '悍马', 'letter': 'H', 'code': 'brand-59'}, {'pbid': 137, 'name': '恒天', 'letter': 'H', 'code': 'brand-564'}, {'pbid': 108, 'name': '红旗', 'letter': 'H', 'code': 'brand-62'}, {'pbid': 184, 'name': '华凯', 'letter': 'H', 'code': ''}, {'pbid': 153, 'name': '华颂', 'letter': 'H', 'code': 'brand-741'}, {'pbid': 48, 'name': '华泰', 'letter': 'H', 'code': 'brand-65'}, {'pbid': 81, 'name': '黄海', 'letter': 'H', 'code': 'brand-68'}]}, {'t': 'J', 'l': [{'pbid': 17, 'name': 'Jeep吉普', 'letter': 'J', 'code': 'brand-74'}, {'pbid': 116, 'name': '吉利', 'letter': 'J', 'code': 'brand-72'}, {'pbid': 84, 'name': '江淮', 'letter': 'J', 'code': 'brand-75'}, {'pbid': 85, 'name': '江铃', 'letter': 'J', 'code': 'brand-542'}, {'pbid': 158, 'name': '杰克Jayco', 'letter': 'J', 'code': 'brand-861'}, {'pbid': 49, 'name': '捷豹', 'letter': 'J', 'code': 'brand-78'}, {'pbid': 83, 'name': '金杯', 'letter': 'J', 'code': 'brand-79'}, {'pbid': 143, 'name': '金龙', 'letter': 'J', 'code': 'brand-528'}, {'pbid': 145, 'name': '金旅', 'letter': 'J', 'code': 'brand-552'}, {'pbid': 146, 'name': '九龙', 'letter': 'J', 'code': 'brand-554'}, {'pbid': 197, 'name': '君马汽车', 'letter': 'J', 'code': 'brand-869'}]}, {'t': 'K', 'l': [{'pbid': 122, 'name': 'KTM', 'letter': 'K', 'code': 'brand-562'}, {'pbid': 100, 'name': '卡尔森', 'letter': 'K', 'code': 'brand-538'}, {'pbid': 152, 'name': '卡升', 'letter': 'K', 'code': ''}, {'pbid': 148, 'name': '卡威', 'letter': 'K', 'code': 'brand-576'}, {'pbid': 87, 'name': '开瑞', 'letter': 'K', 'code': 'brand-82'}, {'pbid': 104, 'name': '凯佰赫', 'letter': 'K', 'code': 'brand-866'}, {'pbid': 33, 'name': '凯迪拉克', 'letter': 'K', 'code': 'brand-84'}, {'pbid': 124, 'name': '凯翼', 'letter': 'K', 'code': 'brand-556'}, {'pbid': 161, 'name': '康迪', 'letter': 'K', 'code': 'brand-816'}, {'pbid': 101, 'name': '科尼赛克', 'letter': 'K', 'code': 'brand-540'}, {'pbid': 50, 'name': '克莱斯勒', 'letter': 'K', 'code': 'brand-86'}]}, {'t': 'L', 'l': [{'pbid': 163, 'name': 'LOCAL MOTORS', 'letter': 'L', 'code': ''}, {'pbid': 176, 'name': '拉达', 'letter': 'L', 'code': 'brand-832'}, {'pbid': 51, 'name': '兰博基尼', 'letter': 'L', 'code': 'brand-88'}, {'pbid': 102, 'name': '劳伦士', 'letter': 'L', 'code': 'brand-867'}, {'pbid': 52, 'name': '劳斯莱斯', 'letter': 'L', 'code': 'brand-91'}, {'pbid': 125, 'name': '雷丁', 'letter': 'L', 'code': ''}, {'pbid': 16, 'name': '雷克萨斯', 'letter': 'L', 'code': 'brand-92'}, {'pbid': 53, 'name': '雷诺', 'letter': 'L', 'code': 'brand-93'}, {'pbid': 237, 'name': '雷神', 'letter': 'L', 'code': 'brand-919'}, {'pbid': 95, 'name': '理念', 'letter': 'L', 'code': 'brand-502'}, {'pbid': 88, 'name': '力帆', 'letter': 'L', 'code': 'brand-94'}, {'pbid': 126, 'name': '莲花', 'letter': 'L', 'code': 'brand-95'}, {'pbid': 39, 'name': '猎豹', 'letter': 'L', 'code': 'brand-166'}, {'pbid': 54, 'name': '林肯', 'letter': 'L', 'code': 'brand-96'}, {'pbid': 24, 'name': '铃木', 'letter': 'L', 'code': 'brand-97'}, {'pbid': 196, 'name': '领克', 'letter': 'L', 'code': 'brand-850'}, {'pbid': 127, 'name': '陆地方舟', 'letter': 'L', 'code': 'brand-819'}, {'pbid': 55, 'name': '陆风', 'letter': 'L', 'code': 'brand-98'}, {'pbid': 14, 'name': '路虎', 'letter': 'L', 'code': 'brand-99'}, {'pbid': 56, 'name': '路特斯', 'letter': 'L', 'code': 'brand-518'}]}, {'t': 'M', 'l': [{'pbid': 57, 'name': 'MG', 'letter': 'M', 'code': 'brand-109'}, {'pbid': 20, 'name': 'Mini', 'letter': 'M', 'code': 'brand-108'}, {'pbid': 13, 'name': '马自达', 'letter': 'M', 'code': 'brand-102'}, {'pbid': 58, 'name': '玛莎拉蒂', 'letter': 'M', 'code': 'brand-103'}, {'pbid': 59, 'name': '迈巴赫', 'letter': 'M', 'code': 'brand-104'}, {'pbid': 105, 'name': '迈凯伦', 'letter': 'M', 'code': 'brand-514'}, {'pbid': 110, 'name': '摩根', 'letter': 'M', 'code': 'brand-572'}]}, {'t': 'N', 'l': [{'pbid': 111, 'name': '纳智捷', 'letter': 'N', 'code': 'brand-111'}, {'pbid': 128, 'name': '南京金龙', 'letter': 'N', 'code': 'brand-568'}]}, {'t': 'O', 'l': [{'pbid': 60, 'name': '讴歌', 'letter': 'O', 'code': 'brand-113'}, {'pbid': 129, 'name': '欧朗', 'letter': 'O', 'code': 'brand-558'}, {'pbid': 236, 'name': '欧尚汽车', 'letter': 'O', 'code': 'brand-895'}]}, {'t': 'P', 'l': [{'pbid': 121, 'name': '帕加尼', 'letter': 'P', 'code': 'brand-864'}, {'pbid': 99, 'name': '庞巴迪', 'letter': 'P', 'code': 'brand-868'}]}, {'t': 'Q', 'l': [{'pbid': 21, 'name': '奇瑞', 'letter': 'Q', 'code': 'brand-118'}, {'pbid': 131, 'name': '启辰', 'letter': 'Q', 'code': 'brand-520'}, {'pbid': 25, 'name': '起亚', 'letter': 'Q', 'code': 'brand-119'}, {'pbid': 156, 'name': '前途', 'letter': 'Q', 'code': ''}, {'pbid': 155, 'name': '乔治巴顿', 'letter': 'Q', 'code': 'brand-815'}]}, {'t': 'R', 'l': [{'pbid': 11, 'name': '日产', 'letter': 'R', 'code': 'brand-121'}, {'pbid': 62, 'name': '荣威', 'letter': 'R', 'code': 'brand-122'}, {'pbid': 107, 'name': '如虎', 'letter': 'R', 'code': 'brand-504'}, {'pbid': 133, 'name': '瑞麟', 'letter': 'R', 'code': ''}]}, {'t': 'S', 'l': [{'pbid': 64, 'name': 'smart', 'letter': 'S', 'code': 'brand-10'}, {'pbid': 166, 'name': '赛麟', 'letter': 'S', 'code': 'brand-813'}, {'pbid': 27, 'name': '三菱', 'letter': 'S', 'code': 'brand-126'}, {'pbid': 138, 'name': '陕汽通家', 'letter': 'S', 'code': 'brand-802'}, {'pbid': 140, 'name': '上汽大通', 'letter': 'S', 'code': 'brand-1004-n'}, {'pbid': 112, 'name': '双环', 'letter': 'S', 'code': 'brand-131'}, {'pbid': 66, 'name': '双龙', 'letter': 'S', 'code': 'brand-132'}, {'pbid': 186, 'name': '思铭', 'letter': 'S', 'code': ''}, {'pbid': 19, 'name': '斯巴鲁', 'letter': 'S', 'code': 'brand-134'}, {'pbid': 162, 'name': '斯达泰克', 'letter': 'S', 'code': 'brand-838'}, {'pbid': 32, 'name': '斯柯达', 'letter': 'S', 'code': 'brand-135'}, {'pbid': 178, 'name': '斯威', 'letter': 'S', 'code': 'brand-831'}]}, {'t': 'T', 'l': [{'pbid': 213, 'name': 'tiny品牌', 'letter': 'T', 'code': 'brand-886'}, {'pbid': 215, 'name': 'tiny品牌测试1', 'letter': 'T', 'code': 'brand-888'}, {'pbid': 119, 'name': '泰卡特', 'letter': 'T', 'code': 'brand-827'}, {'pbid': 113, 'name': '特斯拉', 'letter': 'T', 'code': 'brand-510'}, {'pbid': 142, 'name': '腾势', 'letter': 'T', 'code': 'brand-566'}]}, {'t': 'W', 'l': [{'pbid': 183, 'name': 'WEY', 'letter': 'W', 'code': 'brand-837'}, {'pbid': 179, 'name': '瓦滋UAZ', 'letter': 'W', 'code': 'brand-858'}, {'pbid': 144, 'name': '威麟', 'letter': 'W', 'code': ''}, {'pbid': 103, 'name': '威兹曼', 'letter': 'W', 'code': 'brand-145'}, {'pbid': 191, 'name': '蔚来', 'letter': 'W', 'code': 'brand-851'}, {'pbid': 18, 'name': '沃尔沃', 'letter': 'W', 'code': 'brand-146'}, {'pbid': 90, 'name': '五菱', 'letter': 'W', 'code': 'brand-148'}, {'pbid': 147, 'name': '五十铃', 'letter': 'W', 'code': 'brand-550'}]}, {'t': 'X', 'l': [{'pbid': 114, 'name': '西雅特', 'letter': 'X', 'code': 'brand-150'}, {'pbid': 8, 'name': '现代', 'letter': 'X', 'code': 'brand-151'}, {'pbid': 149, 'name': '新凯', 'letter': 'X', 'code': 'brand-807'}, {'pbid': 9, 'name': '雪佛兰', 'letter': 'X', 'code': 'brand-154'}, {'pbid': 26, 'name': '雪铁龙', 'letter': 'X', 'code': 'brand-155'}]}, {'t': 'Y', 'l': [{'pbid': 72, 'name': '野马汽车', 'letter': 'Y', 'code': 'brand-1005-n'}, {'pbid': 29, 'name': '一汽', 'letter': 'Y', 'code': 'brand-156'}, {'pbid': 115, 'name': '依维柯', 'letter': 'Y', 'code': 'brand-157'}, {'pbid': 67, 'name': '英菲尼迪', 'letter': 'Y', 'code': 'brand-158'}, {'pbid': 150, 'name': '英致', 'letter': 'Y', 'code': 'brand-560'}, {'pbid': 151, 'name': '永源', 'letter': 'Y', 'code': 'brand-161'}, {'pbid': 195, 'name': '御捷', 'letter': 'Y', 'code': 'brand-852'}, {'pbid': 194, 'name': '云度', 'letter': 'Y', 'code': 'brand-853'}]}, {'t': 'Z', 'l': [{'pbid': 189, 'name': '金程', 'letter': 'Z', 'code': ''}, {'pbid': 109, 'name': '征服Conquest', 'letter': 'Z', 'code': 'brand-865'}, {'pbid': 120, 'name': '知豆', 'letter': 'Z', 'code': 'brand-532'}, {'pbid': 28, 'name': '中华', 'letter': 'Z', 'code': 'brand-167'}, {'pbid': 188, 'name': '中欧汽车', 'letter': 'Z', 'code': ''}, {'pbid': 93, 'name': '中兴', 'letter': 'Z', 'code': 'brand-170'}, {'pbid': 92, 'name': '众泰', 'letter': 'Z', 'code': 'brand-172'}]}, {'t': '＃', 'l': [{'pbid': 168, 'name': '其它', 'letter': '＃', 'code': ''}, {'pbid': 256, 'name': '其它', 'letter': '＃', 'code': 'brand-871'}]}]}
    print(cmp_dict(a,b))

    xx = {"111": None, "23456": {"22222": 9999, "33333": "0000", "list": ["3333", "4444", "111"]}}
    yy = {"111": None, "23456": {"22222": 9999, "33333": "0000", "list": ["111", "3333", "4444"]}}
    print(cmp_dict(xx, yy))

    c = {"t":"t1","a":"a","data":[{"t":"tt1","l":[{"id":"1","t":"ttt1"},{"id":"2","t":"ttt2"}]},{"t":"tt2","l":[{"id":"3","t":"ttt3"},{"id":"4","t":"ttt4"}]}]}
    aaa = get_target_value('t', c, [])
    print(aaa)