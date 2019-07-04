# coding=utf8
from . import main
from flask import make_response,render_template, request,session,redirect,url_for, jsonify,g
from .. import executecase
from ..tools import login_required,getSection
from decimal import *
import hashlib,os
from werkzeug.utils import secure_filename
from datetime import datetime
from ..ext import db
from ..upload import Pic_str
from .frontgetdata import *
from ..common import *
from ..tools import *
import json
from sqlalchemy import func
from ..models import User,Role,Project,Module,Version,Api,Case,TestResult,TestPlan,TestReport

_global_dict = {}
_global_result = ""
_flag = ""
@login_required
def execase(id,caseid,batchnumber=0,testplan_id=0):
    global _global_dict
    global _global_result
    email = g.user
    user = User.query.filter_by(email=email).first()
    case = Case.query.filter_by(id=id).first()
    api = Api.query.filter_by(id=case.api_id).first()

    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               'Accept-Encoding': 'gzip, deflate, compress',
               'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
               'Cache-Control': 'max-age=0,no-cache',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
               "Upgrade-Insecure-Requests": "1",
               }
    if api.transmethod == 'form-data':
        headers["Content-Type"] = "multipart/form-data"
    if api.transmethod == 'x-www-form-urlencoded':
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if api.transmethod == 'raw':
        headers["Content-Type"] = "application/json"
    beforecase = case.beforecase.strip()
    if beforecase != "":
        if beforecase.find("|") >= 0:
            s = case.beforecase.split("|")
            for n in s:
                if n.find(":") >= 0:
                    m = n.split(":")
                    datas = execase(m[0],caseid,batchnumber,testplan_id)
                    if m[1].find(","):
                        p = m[1].split(",")
                        for i in p:
                            try:
                                _global_dict[i] = get_target_value(i, datas[0][1], [])[0]
                                _global_dict[i] = get_target_value(i,datas[0][2], [])[0]
                            except Exception as e:
                                print(e)
                                return e
                    else:
                        try:
                            _global_dict[m[1]] = get_target_value(m[1], datas[0][1], [])[0]
                            _global_dict[m[1]] = get_target_value(m[1], datas[0][2], [])[0]
                        except Exception as e:
                            print(e)
                            return e
                else:
                    datas = execase(n,caseid,batchnumber,testplan_id)
        else:
            if beforecase.find(":") >= 0:
                m = beforecase.split(":")
                datas = execase(m[0],caseid,batchnumber,testplan_id)
                if m[1].find(","):
                    p = m[1].split(",")
                    for i in p:
                        try:
                            _global_dict[i] = get_target_value(i, datas[0][1], [])[0]
                            _global_dict[i] = get_target_value(i, datas[0][2], [])[0]
                        except Exception as e:
                            print(e)
                            return e
                else:
                    try:
                        _global_dict[m[1]] = get_target_value(m[1], datas[0][1], [])[0]
                        _global_dict[m[1]] = get_target_value(m[1], datas[0][2], [])[0]
                    except Exception as e:
                        print(e)
                        return e
            else:
                datas = execase(beforecase,caseid,batchnumber,testplan_id)
    # for k,v in _global_dict.items():
    #     print(k,v)
    # print("________")

    jsondata = case.jsondata
    fun = subString(jsondata)
    for f in fun:
        new_s = str(eval(f)())
        old_s = "<" + f + ">"
        j = jsondata.replace(old_s, new_s)
        jsondata = j
    param = subString2(jsondata)
    for p in param:
        new_s = _global_dict[p]
        old_s = "{{" + p + "}}"
        n = jsondata.replace(old_s, new_s)
        jsondata = n
    # print(jsondata)

    expectedResults = case.expectedResults
    fun = subString(expectedResults)
    for f in fun:
        new_s = str(eval(f)())
        old_s = "<" + f + ">"
        j = expectedResults.replace(old_s, new_s)
        expectedResults = j
    param = subString2(expectedResults)
    for p in param:
        new_s = _global_dict[p]
        old_s = "{{" + p + "}}"
        n = expectedResults.replace(old_s, new_s)
        expectedResults = n
    # print(type(expectedResults))
    domain = getSection("env.conf", "test")
    url = api.url
    fun = subString(url)
    for f in fun:
        new_s = str(eval(f)())
        old_s = "<" + f + ">"
        j = url.replace(old_s, new_s)
        url = j
    param = subString2(url)
    for p in param:
        new_s = _global_dict[p]
        old_s = "{{" + p + "}}"
        n = url.replace(old_s, new_s)
        url = n
    url2 = api.protocol+"://"+domain[api.domain] + url
    data = eval(jsondata)
    try:
        r = executecase.WebRequests(url2, method=api.method, headers=headers)
        if api.method.upper() == "GET":
            resdata = r.request(params=data)
        if api.method.upper() == "POST":
            if api.transmethod.upper() == "RAW":
                resdata = r.request(json=data)
            else:
                datas = [k + "=" + str(v).replace("'", '"') for k, v in data.items()]
                datas2 = "&".join(datas)
                datas3 = datas2.encode('utf-8')
                resdata = r.request(data=datas3)
        # print(resdata)
    except Exception as e:
        print(e)
        return e
    if id == caseid:
        realcase = 1
    else:
        realcase = 0
    result = ""
    reasons = ""
    if case.comparemethod.lower() == "equal":
        if json.loads(expectedResults) == resdata[2]:
            result = 1
        else:
            result = 0
            reasons = '期望结果和实际结果不一致'
    if case.comparemethod.lower() == "contain":
        if cmp_dict(json.loads(expectedResults),resdata[2]):
            result = 1
        else:
            result = 0
            reasons = '期望结果不是实际结果中的数据'
    if case.comparemethod.lower() == "count":
        getvalue = countequal(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "countgreater":
        getvalue = countgreater(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "countgreaterequal":
        getvalue = countgreaterequal(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "countless":
        getvalue = countless(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "countlessequal":
        getvalue = countlessequal(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "valueequal":
        getvalue = valueequal(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "valuegreater":
        getvalue = valuegreater(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "valuegreaterequal":
        getvalue = valuegreaterequal(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "valueless":
        getvalue = valueless(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "valuelessequal":
        getvalue = valuelessequal(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "keyexist":
        getvalue = keyexist(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "in":
        getvalue = inkeyvalue(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]
    if case.comparemethod.lower() == "notin":
        getvalue = notinkeyvalue(expectedResults, resdata[2], result, reasons)
        result = getvalue[0]
        reasons = getvalue[1]

    testresult = TestResult(testplan_id=testplan_id, batchnumber=batchnumber, api_id=api.id, case_id=id,
                            apiname=api.apiname,
                            method=api.method,
                            domain=domain[api.domain], url=url, protocol=api.protocol,
                            transmethod=api.transmethod, beforecase=case.beforecase, requestheaders=str(headers),
                            jsondata=jsondata,
                            comparemethod=getSection("env.conf", "comparemethod")[case.comparemethod],
                            expectedResults=expectedResults, status_code=resdata[0], reponseheaders=str(resdata[1]),
                            actualResults=str(resdata[2]), result=result, reasons=reasons, realcase=realcase, note=case.note,
                            executor=user.id,
                            createtime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.session.add(testresult)
    db.session.commit()
    # print(testresult.id)

    if realcase == 1:
        testresult.beforeresult = _global_result
        db.session.add(testresult)
        db.session.commit()
        _global_result = ""
    else:
        if _global_result == "":
            _global_result = str(testresult.id)
        else:
            _global_result = _global_result + "," + str(testresult.id)
    return resdata,jsondata,expectedResults,result,reasons

@main.route('/singleexe/', methods=['GET','POST'],endpoint='singleexe')
@login_required
def singleexe(batchnumber=''):
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    caseid = id
    # if batchnumber =='':
    #     batchnumber = datetime.now().strftime('%Y%m%d%H%M%S')
    data = execase(id,caseid)
    _global_dict.clear()
    return jsonify({"actualResults":str(data[0][2]),"jsondata":data[1],"expectedResults":data[2],"result":data[3],"reasons":data[4],"batchnumber":batchnumber})

@main.route('/exeapi/', methods=['GET','POST'],endpoint='exeapi')
@login_required
def exeapi(batchnumber=''):
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    case = Case.query.filter_by(api_id=id,status='valid').all()
    if batchnumber =='':
        batchnumber = datetime.now().strftime('%Y%m%d%H%M%S')
    for c in case:
        execase(c.id,c.id,batchnumber)
        _global_dict.clear()
    return jsonify({"result":"finished"})


@main.route('/exetestplan/', methods=['GET','POST'],endpoint='exetestplan')
@login_required
def exetestplan():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    testplan = TestPlan.query.filter_by(id=id).first()
    if testplan.status == 'executing':
        return jsonify({"result":"此测试计划是正在执行中"})
    if testplan.apis != "":
        if testplan.apis.find(",") >= 0:
            api = testplan.apis.split(",")
        else:
            api = testplan.apis
    else:
        if testplan.modules == '0':
            if testplan.versions == '0':
                modules = Module.query.filter_by(project_id=testplan.project, status=1).all()
                mlist = [m.id for m in modules]
                api = Api.query.filter(Api.module_id.in_(mlist), Api.status == 'valid').all()
            else:
                if testplan.versions.find(",") >= 0:
                    vlist = testplan.versions.split(",")
                    for v in vlist:
                        if v == 0:
                            vlist.remove(v)
                    api = Api.query.filter(Api.version_id.in_(vlist), Api.status == 'valid').all()
                else:
                    vlist = testplan.versions
                    api = Api.query.filter_by(version_id=vlist, status = 'valid').all()
        else:
            if testplan.versions == '0':
                if testplan.modules.find(",") >= 0:
                    mlist = testplan.modules.split(",")
                    for m in mlist:
                        if m == 0:
                            mlist.remove(m)
                    api = Api.query.filter(Api.module_id.in_(mlist), Api.status == 'valid').all()
                else:
                    mlist = testplan.modules
                    api = Api.query.filter_by(module_id=mlist, status = 'valid').all()
            else:
                if testplan.modules.find(",") >= 0:
                    mlist = testplan.modules.split(",")
                    for m in mlist:
                        if m == 0:
                            mlist.remove(m)
                    if testplan.versions.find(",") >= 0:
                        vlist = testplan.versions.split(",")
                        for v in vlist:
                            if v == 0:
                                vlist.remove(v)
                        api = Api.query.filter(Api.module_id.in_(mlist), Api.version_id.in_(vlist),
                                               Api.status == 'valid').all()
                    else:
                        vlist = testplan.versions
                        api = Api.query.filter(Api.module_id.in_(mlist), Api.version_id==vlist,
                                               Api.status == 'valid').all()
                else:
                    mlist = testplan.modules
                    if testplan.versions.find(",") >= 0:
                        vlist = testplan.versions.split(",")
                        for v in vlist:
                            if v == 0:
                                vlist.remove(v)
                        api = Api.query.filter(Api.module_id==mlist, Api.version_id.in_(vlist),
                                               Api.status == 'valid').all()
                    else:
                        vlist = testplan.versions
                        api = Api.query.filter(Api.module_id==mlist, Api.version_id==vlist,
                                               Api.status == 'valid').all()
    batchnumber = datetime.now().strftime('%Y%m%d%H%M%S')
    testplan.actualTime = datetime.now()
    actualTime = time.time()
    testplan.batchnumber = batchnumber
    testplan.status = 'executing'
    testplan.lastexecutor = user.id
    db.session.add(testplan)
    db.session.commit()
    apicount = 0
    casecount = 0
    apilist = []
    caselist = []
    for a in api:
        apicount = apicount + 1
        apilist.append(str(a.id))
        case = Case.query.filter_by(api_id=a.id, status='valid').all()
        for c in case:
            casecount= casecount + 1
            caselist.append(str(c.id))
    if apicount > 1:
        for index, item in enumerate(apilist):
            apilist[index] = str(item)
        apis = ",".join(apilist)
    elif apicount == 1:
        apis = apilist[0]
    else:
        apis = ''
    if casecount > 1:
        for index, item in enumerate(caselist):
            caselist[index] = str(item)
        cases = ",".join(caselist)
    elif casecount == 1:
        cases = caselist[0]
    else:
        cases = ''
    try:
        for a in api:
            case = Case.query.filter_by(api_id=a.id,status='valid').all()
            for c in case:
                execase(c.id,c.id,batchnumber,id)
                _global_dict.clear()
        finishedtestplan = TestPlan.query.filter_by(id=id).first()
        finishedtestplan.exetime = Decimal(time.time()-actualTime).quantize(Decimal('0.000'))
        finishedtestplan.status = 'finished'
        db.session.add(finishedtestplan)
        db.session.commit()
        return jsonify({"result": "finished"})
    except Exception as e:
        finishedtestplan = TestPlan.query.filter_by(id=id).first()
        finishedtestplan.exetime = Decimal(time.time()-actualTime).quantize(Decimal('0.000'))
        finishedtestplan.status = 'failed'
        db.session.add(finishedtestplan)
        db.session.commit()
        return jsonify({"result": "failed"})
    finally:
        passedcount = db.session.query(func.count(TestResult.id)).filter_by(testplan_id=id,batchnumber=batchnumber,result=1,realcase=1).all()[0][0]
        failedcount = db.session.query(func.count(TestResult.id)).filter_by(testplan_id=id,batchnumber=batchnumber, result=0,realcase=1).all()[0][0]
        testresult = db.session.query(TestResult.api_id,TestResult.case_id).filter_by(testplan_id=id,batchnumber=batchnumber,realcase=1).all()
        unexeapis = []
        unexeapicount = 0
        unexecases = []
        unexecasecount = 0
        api_ids = []
        case_ids = []
        for t in testresult:
            api_ids.append(str(t[0]))
            case_ids.append(str(t[1]))
        for a in apilist:
            if a not in api_ids:
                unexeapis.append(a)
                unexeapicount = unexeapicount +1
        for c in caselist:
            if c not in case_ids:
                unexecases.append(c)
                unexecasecount = unexecasecount + 1
        if len(unexeapis) > 1:
            unexeapi = ",".join(unexeapis)
        elif len(unexeapis) == 1:
            unexeapi = unexeapis[0]
        else:
            unexeapi = ''
        if len(unexecases) > 1:
            unexecase = ",".join(unexecases)
        elif len(unexecases) == 1:
            unexecase = unexecases[0]
        else:
            unexecase = ''
        testreport = TestReport(testplan_id=id, batchnumber=batchnumber, apicount=apicount, apis=apis,
                                casecount=casecount, cases=cases, passedcount=passedcount, failedcount=failedcount,
                                unexeapi=unexeapi, unexeapicount=unexeapicount, unexecase=unexecase,
                                unexecasecount=unexecasecount, executor=user.id, createtime=datetime.now())
        db.session.add(testreport)
        db.session.commit()
        testresultlist = TestResult.query.filter_by(batchnumber=batchnumber, realcase=1).all()
        with open(os.path.join(os.getcwd(), 'report', batchnumber + '.html'), 'tw', encoding='utf8') as f:
            f.write(render_template('reportdetail.html', user=user, testreport=testreport, apis=getapisname,
                                    cases=getcasesname, testresultlist=testresultlist, beforeresult=getresultapiname))
        if testplan.sendemail == 1:
            project = Project.query.filter_by(id=testplan.project).first()
            if project.users != '':
                emails = []
                if project.users.find(",") >= 0:
                    ulist = project.users.split(",")
                    users = User.query.filter(User.id.in_(ulist), User.status == 1).all()
                    for user in users:
                        emails.append(str(user.email))
                    receiver = ";".join(emails)
                else:
                    users = User.query.filter_by(id=project.users, status = 1).all()
                    receiver = str(users.email)
                zipfiles(batchnumber)
                emailData = getSection("email.conf", "email")
                sender = emailData['sender']
                psw = emailData['psw']
                smtp_server = emailData['smtp_server']
                port = emailData['port']
                report_file = os.path.join(os.getcwd(), 'report', batchnumber + '.zip')
                send_mail(sender, psw, receiver, smtp_server, report_file, port)  # 发送报告