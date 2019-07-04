# coding=utf8
from .ext import db


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Integer,default=0, nullable=False)
    role_id = db.Column(db.Integer)
    telephone = db.Column(db.String(11))
    images = db.Column(db.String(256))
    regtime = db.Column(db.DateTime, nullable=False)
    modifytime = db.Column(db.DateTime)
    lastlogin = db.Column(db.DateTime)
    lastmodifier = db.Column(db.Integer)
    api = db.relationship('Api', backref=db.backref('user'))
    case = db.relationship('Case', backref=db.backref('user'))
    testplan = db.relationship('TestPlan', backref=db.backref('user'))
    testresult = db.relationship('TestResult', backref=db.backref('user'))
    testreport = db.relationship('TestReport', backref=db.backref('user'))
    project = db.relationship('Project', backref=db.backref('user'))
    module = db.relationship('Module', backref=db.backref('user'))
    version = db.relationship('Version', backref=db.backref('user'))
    testcaseproject = db.relationship('TestCaseProject', backref=db.backref('user'))
    testcasemodule  = db.relationship('TestCaseModule', backref=db.backref('user'))
    testcasesubmodule  = db.relationship('TestCaseSubModule', backref=db.backref('user'))
    testcase  = db.relationship('TestCase', backref=db.backref('user'))

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(64), unique=True, index=True)
    lastmodifier = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    projectname = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Integer,default=0, nullable=False)
    note = db.Column(db.Text())
    role_id = db.Column(db.Text())
    users = db.Column(db.Text())
    lastmodifier = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    modules = db.relationship('Module', backref=db.backref('project'))
    version = db.relationship('Version', backref=db.backref('project'))

class Module(db.Model):
    __tablename__ = 'module'
    id = db.Column(db.Integer, primary_key=True)
    modulename = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Integer,default=0, nullable=False)
    note = db.Column(db.Text())
    lastmodifier = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    api = db.relationship('Api', backref=db.backref('module'))


class Version(db.Model):
    __tablename__ = 'version'
    id = db.Column(db.Integer, primary_key=True)
    versionname = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Integer,default=0, nullable=False)
    note = db.Column(db.Text())
    lastmodifier = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    api = db.relationship('Api', backref=db.backref('version'))

class Api(db.Model):
    __tablename__ = 'api'
    id = db.Column(db.Integer, primary_key=True)
    apiname = db.Column(db.String(256), nullable=False)
    method = db.Column(db.String(16), nullable=False)
    domain = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    protocol = db.Column(db.String(16), nullable=False)
    transmethod = db.Column(db.String(64), nullable=False)
    jsondata = db.Column(db.Text(), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    note = db.Column(db.Text())
    lastmodifier = db.Column(db.Integer)
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    locked = db.Column(db.Integer, default=0, nullable=False) # 0：未锁定，1：已锁定
    locker = db.Column(db.Integer, db.ForeignKey('user.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey('version.id'), nullable=False)
    case = db.relationship('Case', backref=db.backref('api'))


class Case(db.Model):
    __tablename__ = 'case'
    id = db.Column(db.Integer, primary_key=True)
    casename = db.Column(db.String(256), nullable=False)
    beforecase = db.Column(db.Text(), nullable=False)
    jsondata = db.Column(db.Text(), nullable=False)
    comparemethod = db.Column(db.String(128), nullable=False)
    expectedResults = db.Column(db.Text(), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    note = db.Column(db.Text())
    lastmodifier = db.Column(db.Integer)
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    locked = db.Column(db.Integer, default=0, nullable=False)  # 0：未锁定，1：已锁定
    locker = db.Column(db.Integer, db.ForeignKey('user.id'))
    api_id = db.Column(db.Integer, db.ForeignKey('api.id'))
    testresult = db.relationship('TestResult', backref=db.backref('case'))


class TestResult(db.Model):
    __tablename__ = 'testresult'
    id = db.Column(db.Integer, primary_key=True)
    testplan_id = db.Column(db.Integer)
    batchnumber = db.Column(db.String(64), nullable=False, index=True)
    api_id = db.Column(db.Integer, nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id') )
    apiname = db.Column(db.String(256), nullable=False)
    method = db.Column(db.String(16), nullable=False)
    domain = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    protocol = db.Column(db.String(16), nullable=False)
    transmethod = db.Column(db.String(64), nullable=False)
    beforecase = db.Column(db.Text(), nullable=False)
    requestheaders = db.Column(db.Text(), nullable=False)
    jsondata = db.Column(db.Text(), nullable=False)
    comparemethod = db.Column(db.String(128), nullable=False)
    expectedResults = db.Column(db.Text(), nullable=False)
    status_code = db.Column(db.Integer,nullable=False)
    reponseheaders = db.Column(db.Text(), nullable=False)
    actualResults = db.Column(db.Text(), nullable=False)
    result = db.Column(db.Integer, nullable=False)
    reasons = db.Column(db.Text())
    note = db.Column(db.Text())
    realcase = db.Column(db.Integer)
    beforeresult = db.Column(db.Text())
    executor = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime, nullable=False)



class TestPlan(db.Model):
    __tablename__ = 'testplan'
    id = db.Column(db.Integer,primary_key=True)
    planname = db.Column(db.String(128), nullable=False)
    project = db.Column(db.Integer, nullable=False)
    modules = db.Column(db.String(256), nullable=False)
    versions = db.Column(db.String(256), nullable=False)
    apis = db.Column(db.Text())
    appointmentTime = db.Column(db.DateTime, nullable=False)
    actualTime = db.Column(db.DateTime)
    exetime = db.Column(db.String(128))
    batchnumber = db.Column(db.String(64), index=True)
    status = db.Column(db.String(64))
    sendemail = db.Column(db.Integer, nullable=False, default=0)
    note = db.Column(db.Text())
    createtime = db.Column(db.DateTime, nullable=False)
    modifytime = db.Column(db.DateTime)
    lastmodifier = db.Column(db.Integer, nullable=False)
    lastexecutor = db.Column(db.Integer, db.ForeignKey('user.id'))
    testreport = db.relationship('TestReport', backref=db.backref('testplan'))


class TestReport(db.Model):
    __tablename__ = 'testreport'
    id = db.Column(db.Integer,primary_key=True)
    testplan_id = db.Column(db.Integer, db.ForeignKey('testplan.id'))
    batchnumber = db.Column(db.String(64), index=True)
    apicount = db.Column(db.Integer, nullable=False)
    apis = db.Column(db.Text())
    casecount = db.Column(db.Integer, nullable=False)
    cases = db.Column(db.Text())
    passedcount = db.Column(db.Integer, nullable=False)
    failedcount = db.Column(db.Integer, nullable=False)
    unexeapi = db.Column(db.Text())
    unexeapicount = db.Column(db.Integer, nullable=False)
    unexecase = db.Column(db.Text())
    unexecasecount = db.Column(db.Integer, nullable=False)
    executor = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime, nullable=False)

class TestCaseProject(db.Model):
    __tablename__ = 'testcaseproject'
    id = db.Column(db.Integer, primary_key=True)
    projectname = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Integer,default=0, nullable=False)
    note = db.Column(db.String(128))
    lastmodifier = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    modules = db.relationship('TestCaseModule', backref=db.backref('testcaseproject'))


class TestCaseModule(db.Model):
    __tablename__ = 'testcasemodule'
    id = db.Column(db.Integer, primary_key=True)
    modulename = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Integer,default=0, nullable=False)
    note = db.Column(db.String(128))
    lastmodifier = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('testcaseproject.id'), nullable=False)
    submodules = db.relationship('TestCaseSubModule', backref=db.backref('testcasemodule'))

class TestCaseSubModule(db.Model):
    __tablename__ = 'testcasesubmodule'
    id = db.Column(db.Integer, primary_key=True)
    submodulename = db.Column(db.String(128), nullable=False)
    status = db.Column(db.Integer,default=0, nullable=False)
    note = db.Column(db.String(128))
    lastmodifier = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    module_id = db.Column(db.Integer, db.ForeignKey('testcasemodule.id'), nullable=False)
    testcases = db.relationship('TestCase', backref=db.backref('testcasesubmodule'))

class TestCase(db.Model):
    __tablename__ = 'testcase'
    id = db.Column(db.Integer, primary_key=True)
    caseNo = db.Column(db.Integer, nullable=False)
    testcasename = db.Column(db.String(256), nullable=False)
    precondition = db.Column(db.String(256))
    steps = db.Column(db.Text())
    logicalresult = db.Column(db.Text())
    databaseresult = db.Column(db.Text())
    priority = db.Column(db.String(16), nullable=False)
    version = db.Column(db.String(32))
    status = db.Column(db.Integer,default=1, nullable=False)
    note = db.Column(db.String(128))
    lastmodifier = db.Column(db.Integer, db.ForeignKey('user.id'))
    createtime = db.Column(db.DateTime)
    modifytime = db.Column(db.DateTime)
    submodule_id = db.Column(db.Integer, db.ForeignKey('testcasesubmodule.id'), nullable=False)
