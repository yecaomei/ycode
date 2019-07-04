import os

import xlrd, xlsxwriter

__author__ = 'jiabaili'
# coding:utf-8
import requests
import pymysql
from flask import jsonify

def request(url, method, params=None, data=None, json=None, **kwargs):
    kwargs['params'] = params
    kwargs['data'] = data
    kwargs['json'] = json
    kwargs.setdefault('allow_redirects', False)
    return requests.request(method, url, **kwargs)


class WebRequests(object):
    def __init__(self, url, method='GET', headers=None, cookies=None, timeout=None, verify=False, allow_redirects=False):
        self.url = url
        self.method = method.upper()
        self.headers = headers
        self.cookies = cookies
        self.timeout = timeout
        self.verify = verify
        self.allow_redirects = allow_redirects

    def send(self, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return requests.request(self.method, self.url, headers=self.headers, cookies=self.cookies, timeout=self.timeout,verify=self.verify,
                                **kwargs)

    def request(self, params=None, data=None, json=None, is_jsonres=True, **kwargs):
        kwargs['params'] = params
        kwargs['data'] = data
        kwargs['json'] = json
        req = self.send(**kwargs)
        if is_jsonres:
            response_body = req.json()
        else:
            response_body = req.text
        return req.status_code, req.headers, response_body

    def requestText(self, params=None, data=None, json=None, **kwargs):
        kwargs['params'] = params
        kwargs['data'] = data
        kwargs['json'] = json
        return self.send(**kwargs).text

    def requestJson(self, params=None, data=None, json=None, **kwargs):
        kwargs['params'] = params
        kwargs['data'] = data
        kwargs['json'] = json
        return self.send(**kwargs).json()

    def raiseCodeError(self):
        requests.request(self.method, self.url).raise_for_status()

if __name__ == '__main__':
    # url = "http://sctest-apich.cheoo.com/a_v45.php?U=1Qay9_l4eaHdv01s&c=publish&m=pubAdd"
    # para = {"U": "1quZm_l4eaHdv01s", "version": 422}
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               'Accept-Encoding': 'gzip, deflate, compress',
               'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
               "Upgrade-Insecure-Requests": "1",
               'Content-Type': 'application/x-www-form-urlencoded'
               }
    # data = '{"price_input":5.66,"img":[],"insidecolor":"\u68d5","config_price":0,"color":"\u671d\u971e\u7ea2","city":"","mid":30184,"psid":1770,"remark":"","configure":"","formalities":"","title":"\u5b9d\u9a8f310 17\u6b3e 1.5l \u624b\u52a8\u8c6a\u534e","timelimit":3,"mode":0,"toshoptime":"","arrivaltime":"","price_type":0,"salesregion":"","vin":""}'
    # data = eval(data)

    # print(type(data))

    # r = WebRequests(url,method='post', headers=headers)
    # resText = r.request(data=data)
    # print(resText)

    # print('get请求获取的响应结果json类型', resText.text)
    # print("get请求获取响应状态码", resText.status_code)
    # print("get请求获取响应头", resText.headers['Content-Type'])


    # 响应的json数据转换为可被python识别的数据类型
    # json_r = resText.json()
    # print(type(json_r))


    # def get_target_value(key, dic, tmp_list):
    #     """
    #     :param key: 目标key值
    #     :param dic: JSON数据
    #     :param tmp_list: 用于存储获取的数据
    #     :return: list
    #     """
    #     if not isinstance(dic, dict) or not isinstance(tmp_list, list):  # 对传入数据进行格式校验
    #         return 'argv[1] not an dict or argv[-1] not an list '
    #
    #     if key in dic.keys():
    #         tmp_list.append(dic[key])  # 传入数据存在则存入tmp_list
    #     else:
    #         for value in dic.values():  # 传入数据不符合则对其value值进行遍历
    #             if isinstance(value, dict):
    #                 get_target_value(key, value, tmp_list)  # 传入数据的value值是字典，则直接调用自身
    #             elif isinstance(value, (list, tuple)):
    #                 _get_value(key, value, tmp_list)  # 传入数据的value值是列表或者元组，则调用_get_value
    #     return tmp_list
    #
    #
    # def _get_value(key, val, tmp_list):
    #     for val_ in val:
    #         if isinstance(val_, dict):
    #             get_target_value(key, val_, tmp_list)  # 传入数据的value值是字典，则调用get_target_value
    #         elif isinstance(val_, (list, tuple)):
    #             _get_value(key, val_, tmp_list)  # 传入数据的value值是列表或者元组，则调用自身
    # conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='a1111111', db='yll')
    # cur = conn.cursor()
    # f = open("carcode.txt", "r")
    # lines = f.readlines()  # 读取全部内容
    # for line in lines:
    #     url = 'http://test-www.cheoo.com/baseApi/order/oneCar?carCode='+line.strip()
    #     r = WebRequests(url, method='get')
    #     resText = r.requestJson()
    #     if len(get_target_value('data', resText, [])[0]):
    #         brandname = get_target_value('brandName', resText, [])[0]
    #         seriesname = get_target_value('seriesName', resText, [])[0]
    #         modelname = get_target_value('modelName', resText, [])[0]
    #         print(brandname+"==="+seriesname+"===="+modelname)
    #         sql = "insert into fromcarcode(brandName,seriesName,modelName) values('"+brandname+"','"+seriesname+"','"+modelname+"')"
    #         # print(sql)
    #         cur.execute(sql)
    #         conn.commit()
    #
    # cur.close()
    url = ['https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=spot&from=webmap&c=2279&wd=%E5%BB%BA%E6%9D%90%E5%9F%8E&rn=50&pn=0&nn=0',
           'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=spot&from=webmap&c=2279&wd=%E5%BB%BA%E6%9D%90%E5%9F%8E&rn=50&pn=1&nn=50',
           'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=spot&from=webmap&c=2279&wd=%E5%BB%BA%E6%9D%90%E5%9F%8E&rn=50&pn=2&nn=100',
           'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=spot&from=webmap&c=2279&wd=%E5%BB%BA%E6%9D%90%E5%9F%8E&rn=50&pn=3&nn=150',
           ]
    for x in range(len(url)):
        r = WebRequests(url[x],method='get', headers=headers)
        data=''
        resText = r.requestJson(data=data)
        datas = resText['content']
        print(resText['result']['total'])
        dictdatas = {}
        i=0
        for data in datas:

            # dictdata['name'] = data['name']
            # dictdata['city_name'] = data['admin_info']['city_name']
            # dictdata['area_name'] = data['admin_info']['area_name']
            # dictdata['addr'] = data['addr']
            if 'tel' in data.keys():
                tel = data['tel']
            else:
                tel = ''
            dictdata = [data['name'], data['admin_info']['city_name'], data['admin_info']['area_name'], data['addr'], tel]
            dictdatas[i] = dictdata
            i = i+1
        # print(dictdatas)
        cur_path = os.path.dirname(os.path.realpath(__file__))
        cur_path = os.path.join(os.path.dirname(cur_path), 'aa')
        filename = 'aa'+str(x)+'.xlsx'
        wfile_path = os.path.join(cur_path, filename)
        create_excel_file = xlsxwriter.Workbook(wfile_path)
        worksheet1 = create_excel_file.add_worksheet("Sheet1")

        # excel_title = ['店名','城市','区县','地址','电话']
        # for i, j in enumerate(excel_title):
        #     worksheet1.set_column(i, i, len(j) + 1)
        #     worksheet1.write_string(0, i, j)
        for k,v in dictdatas.items():
            for i in range(len(v)):
                j = v[i]
                worksheet1.write_string(k,i,j)

        create_excel_file.close()

