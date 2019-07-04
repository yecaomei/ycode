# coding=utf8
from . import main
import string
import random
from ..ext import db
from flask import render_template, request, session, redirect, url_for, jsonify, g, flash
from ..tools import login_required, getSection
from ..models import User, Role, Project, Module, Version, Api, Case, TestPlan, TestResult, TestCaseModule, TestCaseSubModule

@main.route('/selectproject/', methods=['GET', 'POST'], endpoint='selectproject')
@login_required
def selectproject():
    data = request.get_json()
    project_id = data.get('project_id')
    mv = {}
    modulelist = {}
    versionlist = []
    if int(project_id) > 0 :
        modules = Module.query.filter_by(project_id=project_id, status=1).all()
        for m in modules:
            modulelist[m.id] = m.modulename
        versions = Version.query.filter_by(project_id=project_id, status=1).order_by(db.desc(Version.id)).all()
        for v in versions:
            versionlist.append({"id":v.id,"versionname":v.versionname})
    mv["modulelist"] = modulelist
    mv["versionlist"] = versionlist
    return jsonify(mv)


@main.route('/changemodule/', methods=['GET', 'POST'], endpoint='changemodule')
@login_required
def changemodule():
    data = request.get_json()
    project_id = data.get('project_id')
    module_id = data.get('module_id')
    version_id = data.get('version_id')
    apis = {}
    if module_id == 0  or version_id == None:
        api = {}
    else:
        if version_id == None or '0' in version_id:
            api = {}
        else:
            api = Api.query.filter(Api.module_id == module_id, Api.version_id == version_id).all()
    for a in api:
        apis[a.id] = a.apiname
    return jsonify(apis)

@main.route('/selectmodule/', methods=['GET', 'POST'], endpoint='selectmodule')
@login_required
def selectmodule():
    data = request.get_json()
    project_id = data.get('project_id')
    module_id = data.get('module_id')
    version_id = data.get('version_id')
    apis = {}
    if '0' in module_id:
        if version_id == None or '0' in version_id:
            modules = Module.query.filter_by(project_id=project_id, status=1).all()
            mlist = [m.id for m in modules]
            api = Api.query.filter(Api.module_id.in_(mlist), Api.status == 'valid').all()
        else:
            if len(version_id) > 1:
                api = Api.query.filter(Api.version_id.in_(version_id), Api.status == 'valid').all()
            else:
                api = Api.query.filter_by(version_id=version_id, status='valid').all()
    else:
        if version_id == None or '0' in version_id:
            if len(module_id) > 1:
                api = Api.query.filter(Api.module_id.in_(module_id), Api.status == 'valid').all()
            else:
                api = Api.query.filter_by(module_id=module_id, status='valid').all()
        else:
            if len(module_id) > 1:
                if len(version_id) > 1:
                    api = Api.query.filter(Api.module_id.in_(module_id), Api.version_id.in_(version_id),
                                           Api.status == 'valid').all()
                else:
                    api = Api.query.filter(Api.module_id.in_(module_id), Api.version_id == version_id,
                                           Api.status == 'valid').all()
            else:
                if len(version_id) > 1:
                    api = Api.query.filter(Api.module_id == module_id, Api.version_id.in_(version_id),
                                           Api.status == 'valid').all()
                else:
                    api = Api.query.filter(Api.module_id == module_id, Api.version_id == version_id,
                                           Api.status == 'valid').all()
    for a in api:
        apis[a.id] = a.apiname
    return jsonify(apis)


@main.route('/changeversion/', methods=['GET', 'POST'], endpoint='changeversion')
@login_required
def changeversion():
    data = request.get_json()
    project_id = data.get('project_id')
    module_id = data.get('module_id')
    version_id = data.get('version_id')
    apis = {}
    if version_id == None or version_id == 0:
        api = {}
    else:
        if module_id == None or module_id == 0:
            api = {}
        else:
            api = Api.query.filter(Api.version_id == version_id, Api.module_id == module_id).all()
    for a in api:
        apis[a.id] = a.apiname
    return jsonify(apis)

@main.route('/selectversion/', methods=['GET', 'POST'], endpoint='selectversion')
@login_required
def selectversion():
    data = request.get_json()
    project_id = data.get('project_id')
    module_id = data.get('module_id')
    version_id = data.get('version_id')
    apis = {}
    if '0' in version_id:
        if module_id == None or '0' in module_id:
            versions = Version.query.filter_by(project_id=project_id, status=1).all()
            vlist = [v.id for v in versions]
            api = Api.query.filter(Api.version_id.in_(vlist), Api.status == 'valid').all()
        else:
            if len(module_id) > 1:
                api = Api.query.filter(Api.module_id.in_(module_id), Api.status == 'valid').all()
            else:
                api = Api.query.filter_by(module_id=module_id, status='valid').all()
    else:
        if module_id == None or '0' in module_id:
            if len(version_id) > 1:
                api = Api.query.filter(Api.version_id.in_(version_id), Api.status == 'valid').all()
            else:
                api = Api.query.filter_by(version_id=version_id, status='valid').all()
        else:
            if len(version_id) > 1:
                if len(module_id) > 1:
                    api = Api.query.filter(Api.version_id.in_(version_id), Api.module_id.in_(module_id),
                                           Api.status == 'valid').all()
                else:
                    api = Api.query.filter(Api.version_id.in_(version_id), Api.module_id == module_id,
                                           Api.status == 'valid').all()
            else:
                if len(module_id) > 1:
                    api = Api.query.filter(Api.version_id == version_id, Api.module_id.in_(module_id),
                                           Api.status == 'valid').all()
                else:
                    api = Api.query.filter(Api.version_id == version_id, Api.module_id == module_id,
                                           Api.status == 'valid').all()
    for a in api:
        apis[a.id] = a.apiname
    return jsonify(apis)

@main.route('/selectapi/', methods=['GET', 'POST'], endpoint='selectapi')
@login_required
def selectapi():
    data = request.get_json()
    api_id = data.get('api_id')
    if api_id == None or api_id == '0':
        jsondata = ''
    else:
        api = Api.query.filter_by(id = api_id).first()
        jsondata = api.jsondata
    return jsonify(jsondata)


def getapis(project_id, module_id, version_id):
    apis = {}
    if module_id == None:
        return apis
    if version_id == None:
        return apis
    if len(module_id)>0 or len(version_id)>0:
        if 0 in module_id:
            if version_id == None or 0 in version_id:
                modules = Module.query.filter_by(project_id=project_id).all()
                mlist = [m.id for m in modules]
                api = Api.query.filter(Api.module_id.in_(mlist), Api.status == 'valid').all()
            else:
                if len(version_id) > 1:
                    api = Api.query.filter(Api.version_id.in_(version_id), Api.status == 'valid').all()
                else:
                    api = Api.query.filter_by(version_id=version_id, status='valid').all()
        else:
            if version_id == None or 0 in version_id:
                if len(module_id) > 1:
                    api = Api.query.filter(Api.module_id.in_(module_id), Api.status == 'valid').all()
                else:
                    api = Api.query.filter_by(module_id=module_id, status='valid').all()
            else:
                if len(module_id) > 1:
                    if len(version_id) > 1:
                        api = Api.query.filter(Api.module_id.in_(module_id), Api.version_id.in_(version_id),
                                               Api.status == 'valid').all()
                    else:
                        api = Api.query.filter(Api.module_id.in_(module_id), Api.version_id == version_id,
                                               Api.status == 'valid').all()
                else:
                    if len(version_id) > 1:
                        api = Api.query.filter(Api.module_id == module_id, Api.version_id.in_(version_id),
                                               Api.status == 'valid').all()
                    else:
                        api = Api.query.filter(Api.module_id == module_id, Api.version_id == version_id,
                                               Api.status == 'valid').all()
        for a in api:
            apis[a.id] = a.apiname

    return apis

def getmodulename(mstr, project_id):
    if mstr != "":
        if mstr.find(",") >= 0:
            mlist = mstr.split(",")
            modulelist = Module.query.filter(Module.id.in_(mlist)).all()
            module = [module.modulename for module in modulelist]
            modulestr = ','.join(module)
        else:
            if mstr == '0':
                modulelist = Module.query.filter_by(project_id=project_id , status = 1).all()
                module = [module.modulename for module in modulelist]
                modulestr = ','.join(module)
            else:
                modulelist = Module.query.filter_by(id=mstr).first()
                modulestr = modulelist.modulename
    else:
        modulestr = ''
    return modulestr


def getversionname(vstr, project_id):
    if vstr != "":
        if vstr.find(",") >= 0:
            vlist = vstr.split(",")
            versionlist = Version.query.filter(Version.id.in_(vlist)).all()
            version = [version.versionname for version in versionlist]
            versionstr = ','.join(version)
        else:
            if vstr == '0':
                versionlist = Version.query.filter_by(project_id=project_id , status = 1).all()
                version = [version.versionname for version in versionlist]
                versionstr = ','.join(version)
            else:
                versionlist = Version.query.filter_by(id=vstr).first()
                versionstr = versionlist.versionname
    else:
        versionstr = ''
    return versionstr


def getapiname(astr, mstr, vstr, project_id):
    if astr == '':
        if mstr == '0':
            modulelist = Module.query.filter_by(project_id=project_id, status=1).all()
            module = [module.id for module in modulelist]
            if vstr == '0':
                versionlist = Version.query.filter_by(project_id=project_id, status=1).all()
                version = [version.id for version in versionlist]
                apilist = Api.query.filter(Api.module_id.in_(module), Api.version_id.in_(version), Api.status=='valid').all()
            else:
                if vstr.find(",") >= 0:
                    vlist = vstr.split(",")
                    apilist = Api.query.filter(Api.module_id.in_(module), Api.version_id.in_(vlist), Api.status == 'valid').all()
                else:
                    apilist = Api.query.filter(Api.module_id.in_(module), Api.version_id==vstr, Api.status == 'valid').all()
        else:
            if mstr.find(",") >= 0:
                mlist = mstr.split(",")
                modulelist = Module.query.filter(Module.id.in_(mlist)).all()
                module = [module.id for module in modulelist]
                if vstr == '0':
                    versionlist = Version.query.filter_by(project_id=project_id, status=1).all()
                    version = [version.id for version in versionlist]
                    apilist = Api.query.filter(Api.module_id.in_(module), Api.version_id.in_(version), Api.status == 'valid').all()
                else:
                    if vstr.find(",") >= 0:
                        vlist = vstr.split(",")
                        apilist = Api.query.filter(Api.module_id.in_(module), Api.version_id.in_(vlist), Api.status == 'valid').all()
                    else:
                        apilist = Api.query.filter(Api.module_id.in_(module), Api.version_id == vstr, Api.status == 'valid').all()
            else:
                if vstr == '0':
                    versionlist = Version.query.filter_by(project_id=project_id, status=1).all()
                    version = [version.id for version in versionlist]
                    apilist = Api.query.filter(Api.module_id == mstr, Api.version_id.in_(version), Api.status == 'valid').all()
                else:
                    if vstr.find(",") >= 0:
                        vlist = vstr.split(",")
                        apilist = Api.query.filter(Api.module_id == mstr, Api.version_id.in_(vlist), Api.status == 'valid').all()
                    else:
                        apilist = Api.query.filter(Api.module_id == mstr, Api.version_id == vstr, Api.status == 'valid').all()
        api = [api.apiname for api in apilist]
        apistr = ','.join(api)
    else:
        if astr.find(",") >= 0:
            alist = astr.split(",")
            apilist = Api.query.filter(Api.id.in_(alist)).all()
            api = [api.apiname for api in apilist]
            apistr = ','.join(api)
        else:
            apilist = Api.query.filter_by(id=astr).first()
            apistr = apilist.apiname
    return apistr

#根据测试结果表的id字符串获取接口的名字
def getresultapiname(beforeresult):
    beforeresult = str(beforeresult)
    apilist = {}
    if beforeresult == '':
        apilist = {}
    else:
        if beforeresult.find(",") >= 0:
            result = beforeresult.split(",")
            for r in result:
                testresult = TestResult.query.filter_by(id=r).first()
                apilist[r] = testresult.apiname
        else:
            testresult = TestResult.query.filter_by(id=beforeresult).first()
            apilist[beforeresult] = testresult.apiname
    return apilist

def getapisname(apistr):
    apistr = str(apistr)
    apilist = {}
    if apistr == '':
        apilist = {}
    else:
        if apistr.find(",") >= 0:
            api = apistr.split(",")
            for a in api:
                apis = Api.query.filter_by(id=a).first()
                apilist[a] = apis.apiname
        else:
            apis = Api.query.filter_by(id=apistr).first()
            apilist[apistr] = apis.apiname
    return apilist

def getcasesname(casestr):
    casestr = str(casestr)
    caselist = {}
    if casestr == '':
        caselist = {}
    else:
        if casestr.find(",") >= 0:
            case = casestr.split(",")
            for c in case:
                cases = Case.query.filter_by(id=c).first()
                caselist[c] = cases.casename
        else:
            cases = Case.query.filter_by(id=casestr).first()
            caselist[casestr] = cases.casename
    return caselist

def getrolename(roleids):
    roleids = str(roleids)
    roleidlist = {}
    if roleids == '':
        roleidlist = {}
    else:
        if roleids.find(",") >= 0:
            rolelist = roleids.split(",")
            for r in rolelist:
                role = Role.query.filter_by(id=r).first()
                roleidlist[r] = role.rolename
        else:
            role = Role.query.filter_by(id=roleids).first()
            roleidlist[roleids] = role.rolename
    return roleidlist

def getuseremail(users):
    users = str(users)
    userlist = {}
    if users == '':
        userlist = {}
    else:
        if users.find(",") >= 0:
            user = users.split(",")
            for u in user:
                useremail = User.query.filter_by(id=u).first()
                userlist[useremail.email] = useremail.username
        else:
            useremail = User.query.filter_by(id=users).first()
            userlist[useremail.email] = useremail.username
    return userlist

def getuserrole(role_id):
    if role_id:
        role = Role.query.filter_by(id=role_id).first()
        if role==None:
            rolename = ""
        else:
            rolename = role.rolename
    else:
        rolename=""
    return rolename

def getusername(user_id):
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        if user_id==None:
            username = ""
        else:
            username = user.username
    else:
        username=""
    return username

@main.route('/selecttestcaseproject/', methods=['GET', 'POST'], endpoint='selecttestcaseproject')
@login_required
def selecttestcaseproject():
    data = request.get_json()
    project_id = data.get('project_id')
    mv = {}
    modulelist = {}
    if int(project_id) > 0 :
        modules = TestCaseModule.query.filter_by(project_id=project_id, status=1).all()
        for m in modules:
            modulelist[m.id] = m.modulename
    mv["modulelist"] = modulelist
    return jsonify(mv)

@main.route('/selecttestcasemodule/', methods=['GET', 'POST'], endpoint='selecttestcasemodule')
@login_required
def selecttestcasemodule():
    data = request.get_json()
    module_id = data.get('module_id')
    mv = {}
    submodulelist = {}
    if int(module_id) > 0 :
        submodules = TestCaseSubModule.query.filter_by(module_id=module_id, status=1).all()
        for m in submodules:
            submodulelist[m.id] = m.submodulename
    mv["submodulelist"] = submodulelist
    return jsonify(mv)

@main.route('/selecttestcasemodules/', methods=['GET', 'POST'], endpoint='selecttestcasemodules')
@login_required
def selecttestcasemodules():
    data = request.get_json()
    project_id = data.get('project_id')
    module_id = data.get('module_id')
    submodulenames = {}
    if '0' in module_id:
        modulenames = TestCaseModule.query.filter_by(project_id=project_id).all()
        mlist = [m.id for m in modulenames]
        submodules = TestCaseSubModule.query.filter(TestCaseSubModule.module_id.in_(mlist), TestCaseSubModule.status==1).all()
    else:
        submodules = TestCaseSubModule.query.filter(TestCaseSubModule.module_id.in_(module_id), TestCaseSubModule.status==1).all()
    for m in submodules:
        submodulenames[m.id] = m.submodulename
    return jsonify(submodulenames)

@main.route('/gettestcasesubmodules/', methods=['GET', 'POST'], endpoint='gettestcasesubmodules')
@login_required
def gettestcasesubmodules(project_id, module_id):
    submodulenames = {}
    if module_id == None or len(module_id) == 0:
        pass
    else:
        if '0' in module_id:
            modulenames = TestCaseModule.query.filter_by(project_id=project_id).all()
            mlist = [m.id for m in modulenames]
            submodules = TestCaseSubModule.query.filter(TestCaseSubModule.module_id.in_(mlist), TestCaseSubModule.status==1).all()
        else:
            submodules = TestCaseSubModule.query.filter(TestCaseSubModule.module_id.in_(module_id), TestCaseSubModule.status==1).all()
        for m in submodules:
            submodulenames[m.id] = m.submodulename
    return submodulenames

def getpassword(length):
    # 随机生成数字个数
    Ofnum = random.randint(1, length)
    Ofletter = length - Ofnum
    # 选中ofnum个数字
    slcNum = [random.choice(string.digits) for i in range(Ofnum)]
    # 选中ofletter个字母
    slcLetter = [random.choice(string.ascii_letters) for i in range(Ofletter)]
    # 打乱组合
    slcChar = slcLetter + slcNum
    random.shuffle(slcChar)
    # 生成随机密码
    getPwd = ''.join([i for i in slcChar])
    return getPwd
