# coding=utf8
from . import main
from flask import render_template, request, session, redirect, url_for, jsonify, g, flash, send_file
import hashlib, os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from ..ext import db
from app import common
import json
from .. import executecase
from .frontgetdata import *
from ..tools import *
from .testcaseforms import TestCaseProjectForm,TestCaseModuleForm,TestCaseSubModuleForm,TestCaseForm,UploadExcelForm,DownloadExcelForm
from ..tools import login_required, getSection
from ..models import TestCaseProject,TestCaseModule,TestCaseSubModule,TestCase
import xlrd,xlsxwriter
from io import BytesIO
import mimetypes

@main.route('/testcaseprojectlist/', methods=['GET', 'POST'], endpoint='testcaseprojectlist')
@login_required
def testcaseprojectlist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        project_info = TestCaseProject.query.all()
        return render_template('testcaseprojectlist.html', user=user, project_info=project_info)

@main.route('/edittestcaseprojectstatus/', methods=['GET', 'POST'], endpoint='edittestcaseprojectstatus')
@login_required
def edittestcaseprojectstatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    project = TestCaseProject.query.filter_by(id=id).first()
    project.status = status
    project.modifytime = datetime.now()
    project.lastmodifier = user.id
    db.session.add(project)
    db.session.commit()
    return jsonify('{"msg":"测试项目状态修改成功"}')

@main.route('/addtestcaseproject/', methods=['GET', 'POST'], endpoint='addtestcaseproject')
@login_required
def addtestcaseproject():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = TestCaseProjectForm()
        return render_template('addtestcaseproject.html', user=user, form=form)
    else:
        form = TestCaseProjectForm(request.form)
        projectname = form.projectname.data
        note = form.note.data
        if form.validate_on_submit():
            name = TestCaseProject.query.filter_by(projectname=projectname).count()
            if name > 0:
                form.errors['projectname'] = ['此测试项目名称已存在']
                return render_template('addtestcaseproject.html', user=user, form=form)
            project = TestCaseProject(projectname=projectname, note=note, status=1, createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(project)
            db.session.commit()
            flash('测试项目添加成功', 'ok')
            return redirect(url_for('.addtestcaseproject'))
        else:
            return render_template('addtestcaseproject.html', user=user, form=form)

@main.route('/edittestcaseproject/<int:id>', methods=['GET', 'POST'], endpoint='edittestcaseproject')
@login_required
def edittestcaseproject(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    project_info = TestCaseProject.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = TestCaseProjectForm()
        form.projectname.data = project_info.projectname
        form.note.data = project_info.note
        return render_template('edittestcaseproject.html', user=user, form=form)
    else:
        form = TestCaseProjectForm(request.form)
        if form.validate_on_submit():
            projectname = form.projectname.data
            project_info.note = form.note.data
            name = TestCaseProject.query.filter_by(projectname=projectname).count()
            if name > 1:
                form.errors['projectname'] = ['此测试项目名称已存在']
                return render_template('edittestcaseproject.html', user=user, form=form)
            if name == 1:
                p = TestCaseProject.query.filter_by(projectname=projectname).first()
                if p.id != id:
                    form.errors['projectname'] = ['此测试项目名称已存在']
                    return render_template('edittestcaseproject.html', user=user, form=form)
            project_info.projectname = form.projectname.data
            project_info.modifytime = datetime.now()
            project_info.lastmodifier = user.id
            db.session.add(project_info)
            db.session.commit()
            flash('测试项目编辑成功', 'ok')
            return redirect(url_for('.edittestcaseproject',id=id))
        else:
            return render_template('edittestcaseproject.html', user=user, form=form)

@main.route('/testcasemodulelist/', methods=['GET', 'POST'], endpoint='testcasemodulelist')
@login_required
def testcasemodulelist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        modulelist = TestCaseModule.query.all()
        return render_template('testcasemodulelist.html', user=user, modulelist=modulelist)

@main.route('/edittestcasemodulestatus/', methods=['GET', 'POST'], endpoint='edittestcasemodulestatus')
@login_required
def edittestcasemodulestatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    module = TestCaseModule.query.filter_by(id=id).first()
    module.status = status
    module.modifytime = datetime.now()
    module.lastmodifier = user.id
    db.session.add(module)
    db.session.commit()
    return jsonify('{"msg":"测试用例模块状态修改成功"}')

@main.route('/addtestcasemodule/', methods=['GET', 'POST'], endpoint='addtestcasemodule')
@login_required
def addtestcasemodule():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = TestCaseModuleForm()
        return render_template('addtestcasemodule.html', user=user, form=form)
    else:
        form = TestCaseModuleForm(request.form)
        modulename = form.modulename.data
        project_id = form.projectname.data
        note = form.note.data
        if form.validate_on_submit():
            name = TestCaseModule.query.filter_by(modulename=modulename,project_id=project_id).count()
            if name > 0:
                form.errors['modulename'] = ['此测试用例模块名称已存在']
                return render_template('addtestcasemodule.html', user=user, form=form)
            module = TestCaseModule(project_id=project_id, modulename=modulename, note=note, status=1, createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(module)
            db.session.commit()
            flash('测试用例模块添加成功', 'ok')
            return redirect(url_for('.addtestcasemodule'))
        else:
            return render_template('addtestcasemodule.html', user=user, form=form)

@main.route('/edittestcasemodule/<int:id>', methods=['GET', 'POST'], endpoint='edittestcasemodule')
@login_required
def edittestcasemodule(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    module_info = TestCaseModule.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = TestCaseModuleForm()
        form.modulename.data = module_info.modulename
        form.projectname.data = module_info.project_id
        form.note.data = module_info.note
        return render_template('edittestcasemodule.html', user=user, form=form)
    else:
        form = TestCaseModuleForm(request.form)
        if form.validate_on_submit():
            project_id = form.projectname.data
            modulename = form.modulename.data
            module_info.note = form.note.data
            name = TestCaseModule.query.filter_by(project_id=project_id,modulename=modulename).count()
            if name > 1:
                form.errors['modulename'] = ['此测试用例模块名称已存在']
                return render_template('edittestcasemodule.html', user=user, form=form)
            if name == 1:
                m = TestCaseModule.query.filter_by(project_id=project_id,modulename=modulename).first()
                if m.id != id:
                    form.errors['modulename'] = ['此测试用例模块名称已存在']
                    return render_template('edittestcasemodule.html', user=user, form=form)
            module_info.project_id = form.projectname.data
            module_info.modulename = form.modulename.data
            module_info.modifytime = datetime.now()
            module_info.lastmodifier = user.id
            db.session.add(module_info)
            db.session.commit()
            flash('测试用例模块编辑成功', 'ok')
            return redirect(url_for('.edittestcasemodule',id=id))
        else:
            return render_template('edittestcasemodule.html', user=user, form=form)

@main.route('/testcasesubmodulelist/', methods=['GET', 'POST'], endpoint='testcasesubmodulelist')
@login_required
def testcasesubmodulelist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        testcasesubmodulelist = TestCaseSubModule.query.all()
        return render_template('testcasesubmodulelist.html', user=user, testcasesubmodulelist=testcasesubmodulelist)

@main.route('/edittestcasesubmodulestatus/', methods=['GET', 'POST'], endpoint='edittestcasesubmodulestatus')
@login_required
def edittestcasesubmodulestatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    submodule = TestCaseSubModule.query.filter_by(id=id).first()
    submodule.status = status
    submodule.lastmodifier = user.id
    submodule.modifytime = datetime.now()
    db.session.add(submodule)
    db.session.commit()
    return jsonify('{"msg":"测试用例子模块状态修改成功"}')

@main.route('/addtestcasesubmodule/', methods=['GET', 'POST'], endpoint='addtestcasesubmodule')
@login_required
def addtestcasesubmodule():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = TestCaseSubModuleForm()
        return render_template('addtestcasesubmodule.html', user=user, form=form)
    else:
        form = TestCaseSubModuleForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择测试用例模块")]
        if project_id:
            for m in TestCaseModule.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            submodulename = form.submodulename.data
            note = form.note.data
            name = TestCaseSubModule.query.filter_by(submodulename=submodulename, module_id=module_id).count()
            if name > 0:
                form.errors['submodulename'] = ['此测试用例子模块名称已存在']
                return render_template('addtestcasesubmodule.html', user=user, form=form)
            submodule = TestCaseSubModule(module_id=module_id, submodulename=submodulename, note=note,
                      status=1, createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(submodule)
            db.session.commit()
            flash('测试用例子模块添加成功', 'ok')
            form = TestCaseSubModuleForm()
            return redirect(url_for('.addtestcasesubmodule'))
        else:
            return render_template('addtestcasesubmodule.html', user=user, form=form)

@main.route('/edittestcasesubmodule/<int:id>/', methods=['GET', 'POST'], endpoint='edittestcasesubmodule')
@login_required
def edittestcasesubmodule(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    submodule = TestCaseSubModule.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = TestCaseSubModuleForm()
        module_id = TestCaseModule.query.filter_by(id=submodule.module_id).first()
        projects = TestCaseProject.query.filter_by(id=module_id.project_id).first()
        form.projectname.data = projects.id
        form.modulename.data = module_id.id
        if projects.id:
            for m in TestCaseModule.query.filter_by(project_id=projects.id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        form.submodulename.data = submodule.submodulename
        form.note.data = submodule.note
        return render_template('edittestcasesubmodule.html', user=user, form=form)
    else:
        form = TestCaseSubModuleForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择测试用例模块")]
        if project_id:
            for m in TestCaseModule.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        if form.validate_on_submit():
            projectname = form.projectname.data
            submodule.module_id = form.modulename.data
            submodule.submodulename = form.submodulename.data
            name = TestCaseSubModule.query.filter_by(module_id=submodule.module_id, submodulename=submodule.submodulename).count()
            if name > 1:
                form.errors['submodulename'] = ['此测试用例子模块名称已存在']
                return render_template('edittestcasesubmodule.html', user=user, form=form)
            if name == 1:
                m = TestCaseSubModule.query.filter_by(module_id=submodule.module_id, submodulename=submodule.submodulename).first()
                if m.id != id:
                    form.errors['submodulename'] = ['此测试用例子模块名称已存在']
                    return render_template('edittestcasesubmodule.html', user=user, form=form)
            submodule.note = form.note.data
            submodule.modifytime = datetime.now()
            submodule.lastmodifier = user.id
            db.session.add(submodule)
            db.session.commit()
            flash('测试用例子模块修改成功', 'ok')
            return redirect(url_for('.edittestcasesubmodule', id=submodule.id))
        else:
            return render_template('edittestcasesubmodule.html', user=user, form=form)

@main.route('/testcaselist/', methods=['GET', 'POST'], endpoint='testcaselist')
@login_required
def testcaselist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        testcaselist = TestCase.query.all()
        form = UploadExcelForm()
        return render_template('testcaselist.html', user=user, testcaselist=testcaselist)

@main.route('/edittestcasestatus/', methods=['GET', 'POST'], endpoint='edittestcasestatus')
@login_required
def edittestcasestatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    testcase = TestCase.query.filter_by(id=id).first()
    testcase.status = status
    testcase.lastmodifier = user.id
    testcase.modifytime = datetime.now()
    db.session.add(testcase)
    db.session.commit()
    return jsonify('{"msg":"测试用例状态修改成功"}')

@main.route('/addtestcase/', methods=['GET', 'POST'], endpoint='addtestcase')
@login_required
def addtestcase():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = TestCaseForm()
        return render_template('addtestcase.html', user=user, form=form)
    else:
        form = TestCaseForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择测试用例模块")]
        if project_id:
            for m in TestCaseModule.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        module_id = form.modulename.data
        form.submodulename.choices = [(0, "请选择测试用例子模块")]
        if module_id:
            for m in TestCaseSubModule.query.filter_by(module_id=module_id, status=1).all():
                form.submodulename.choices.append((m.id, m.submodulename))
        submodule_id = form.submodulename.data
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            submodule_id = form.submodulename.data
            caseNo = form.caseNo.data
            testcasename = form.testcasename.data
            precondition = form.precondition.data
            steps = form.steps.data
            logicalresult = form.logicalresult.data
            databaseresult = form.databaseresult.data
            priority = form.priority.data
            version = form.version.data
            note = form.note.data
            testcase = TestCase(submodule_id=submodule_id, caseNo=caseNo, testcasename=testcasename, precondition=precondition, steps=steps,
                                logicalresult=logicalresult, databaseresult=databaseresult, priority=priority, version=version, note=note, status=1,
                                createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(testcase)
            db.session.commit()
            flash('测试用例添加成功', 'ok')
            form = TestCaseForm()
            return redirect(url_for('.addtestcase'))
        else:
            return render_template('addtestcase.html', user=user, form=form)


@main.route('/addsubmoduletestcase/<int:id>', methods=['GET', 'POST'], endpoint='addsubmoduletestcase')
@login_required
def addsubmoduletestcase(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = TestCaseForm()
        submodule_id = TestCaseSubModule.query.filter_by(id=id).first()
        module_id = TestCaseModule.query.filter_by(id=submodule_id.module_id).first()
        project_id = TestCaseProject.query.filter_by(id=module_id.project_id).first()
        form.projectname.data = project_id.id
        form.modulename.data = module_id.id
        form.submodulename.data = submodule_id.id
        if project_id.id:
            for m in TestCaseModule.query.filter_by(project_id=project_id.id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        if module_id.id:
            for m in TestCaseSubModule.query.filter_by(module_id=module_id.id, status=1).all():
                form.submodulename.choices.append((m.id, m.submodulename))
        return render_template('addtestcase.html', user=user, form=form)
    else:
        form = TestCaseForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择测试用例模块")]
        if project_id:
            for m in TestCaseModule.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        module_id = form.modulename.data
        form.submodulename.choices = [(0, "请选择测试用例子模块")]
        if module_id:
            for m in TestCaseSubModule.query.filter_by(module_id=module_id, status=1).all():
                form.submodulename.choices.append((m.id, m.submodulename))
        submodule_id = form.submodulename.data
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            submodule_id = form.submodulename.data
            caseNo = form.caseNo.data
            testcasename = form.testcasename.data
            precondition = form.precondition.data
            steps = form.steps.data
            logicalresult = form.logicalresult.data
            databaseresult = form.databaseresult.data
            priority = form.priority.data
            version = form.version.data
            note = form.note.data
            testcase = TestCase(submodule_id=submodule_id, caseNo=caseNo, testcasename=testcasename, precondition=precondition, steps=steps,
                                logicalresult=logicalresult, databaseresult=databaseresult, priority=priority, version=version, note=note, status=1,
                                createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(testcase)
            db.session.commit()
            flash('测试用例添加成功', 'ok')
            form = TestCaseForm()
            return redirect(url_for('.addsubmoduletestcase',id=id))
        else:
            return render_template('addtestcase.html', user=user, form=form)


@main.route('/edittestcase/<int:id>/', methods=['GET', 'POST'], endpoint='edittestcase')
@login_required
def edittestcase(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    testcase = TestCase.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = TestCaseForm()
        submodule_id = TestCaseSubModule.query.filter_by(id=testcase.submodule_id).first()
        module_id = TestCaseModule.query.filter_by(id=submodule_id.module_id).first()
        projects = TestCaseProject.query.filter_by(id=module_id.project_id).first()
        form.projectname.data = projects.id
        form.modulename.data = module_id.id
        form.submodulename.data = submodule_id.id
        if projects.id:
            for m in TestCaseModule.query.filter_by(project_id=projects.id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        if module_id.id:
            for m in TestCaseSubModule.query.filter_by(module_id=module_id.id, status=1).all():
                form.submodulename.choices.append((m.id, m.submodulename))
        form.caseNo.data = testcase.caseNo
        form.testcasename.data = testcase.testcasename
        form.precondition.data = testcase.precondition
        form.steps.data = testcase.steps
        form.logicalresult.data = testcase.logicalresult
        form.databaseresult.data = testcase.databaseresult
        form.priority.data = testcase.priority
        form.version.data = testcase.version
        form.note.data = testcase.note
        return render_template('edittestcase.html', user=user, form=form)
    else:
        form = TestCaseForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择测试用例模块")]
        form.submodulename.choices = [(0, "请选择测试用例子模块")]
        if project_id:
            for m in TestCaseModule.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        module_id = form.modulename.data
        if module_id:
            for m in TestCaseSubModule.query.filter_by(module_id=module_id, status=1).all():
                form.submodulename.choices.append((m.id, m.submodulename))
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            submodule_id = form.submodulename.data
            testcase.caseNo = form.caseNo.data
            testcase.testcasename = form.testcasename.data
            testcase.precondition = form.precondition.data
            testcase.steps = form.steps.data
            testcase.logicalresult = form.logicalresult.data
            testcase.databaseresult = form.databaseresult.data
            testcase.priority = form.priority.data
            testcase.version = form.version.data
            testcase.note = form.note.data
            testcase.modifytime = datetime.now()
            testcase.lastmodifier = user.id
            db.session.add(testcase)
            db.session.commit()
            flash('测试用例修改成功', 'ok')
            return redirect(url_for('.edittestcase', id=testcase.id))
        else:
            return render_template('edittestcase.html', user=user, form=form)


@main.route('/copytestcase/<int:id>/', methods=['GET', 'POST'], endpoint='copytestcase')
@login_required
def copytestcase(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    testcase = TestCase.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = TestCaseForm()
        submodule_id = TestCaseSubModule.query.filter_by(id=testcase.submodule_id).first()
        module_id = TestCaseModule.query.filter_by(id=submodule_id.module_id).first()
        projects = TestCaseProject.query.filter_by(id=module_id.project_id).first()
        form.projectname.data = projects.id
        form.modulename.data = module_id.id
        form.submodulename.data = submodule_id.id
        if projects.id:
            for m in TestCaseModule.query.filter_by(project_id=projects.id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        if module_id.id:
            for m in TestCaseSubModule.query.filter_by(module_id=module_id.id, status=1).all():
                form.submodulename.choices.append((m.id, m.submodulename))
        form.caseNo.data = testcase.caseNo
        form.testcasename.data = testcase.testcasename
        form.precondition.data = testcase.precondition
        form.steps.data = testcase.steps
        form.logicalresult.data = testcase.logicalresult
        form.databaseresult.data = testcase.databaseresult
        form.priority.data = testcase.priority
        form.version.data = testcase.version
        form.note.data = testcase.note
        return render_template('addtestcase.html', user=user, form=form)
    else:
        form = TestCaseForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择测试用例模块")]
        if project_id:
            for m in TestCaseModule.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        module_id = form.modulename.data
        form.submodulename.choices = [(0, "请选择测试用例子模块")]
        if module_id:
            for m in TestCaseSubModule.query.filter_by(module_id=module_id, status=1).all():
                form.submodulename.choices.append((m.id, m.submodulename))
        submodule_id = form.submodulename.data
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            submodule_id = form.submodulename.data
            caseNo = form.caseNo.data
            testcasename = form.testcasename.data
            precondition = form.precondition.data
            steps = form.steps.data
            logicalresult = form.logicalresult.data
            databaseresult = form.databaseresult.data
            priority = form.priority.data
            version = form.version.data
            note = form.note.data
            testcase = TestCase(submodule_id=submodule_id, caseNo=caseNo, testcasename=testcasename,
                                precondition=precondition, steps=steps,
                                logicalresult=logicalresult, databaseresult=databaseresult, priority=priority,
                                version=version, note=note, status=1,
                                createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(testcase)
            db.session.commit()
            flash('测试用例添加成功', 'ok')
            form = TestCaseForm()
            return redirect(url_for('.copytestcase', id=id))
        else:
            return render_template('addtestcase.html', user=user, form=form)


@main.route('/submoduletestcaselist/<int:id>/', methods=['GET', 'POST'], endpoint='submoduletestcaselist')
@login_required
def submoduletestcaselist(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        testcaselist = TestCase.query.filter_by(submodule_id=id).all()
        return render_template('testcaselist.html', user=user, testcaselist=testcaselist)

@main.route('/uploadtestcase/', methods=['GET', 'POST'], endpoint='uploadtestcase')
@login_required
def uploadtestcase():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = UploadExcelForm()
        return render_template('uploadtestcase.html', user=user, form=form)
    else:
        form = UploadExcelForm(request.form)
        if form.validate_on_submit():
            file = request.files.get("excelfile")
            f = file.read()
            try:
                data = xlrd.open_workbook(file_contents=f)
                sheetnames = data.sheet_names()  # 返回book中所有工作表的名字
                sheetcount = len(sheetnames)
                casedatas = []
                flashmsg = []
                for i in range(0, sheetcount):
                    table = data.sheets()[i]
                    nrows = table.nrows  # 获取该sheet中的有效行数
                    casedata = []
                    for j in range(1, nrows):
                        submodule = TestCaseSubModule.query.filter_by(id=table.row_values(j)[0], status=1).count()
                        if submodule == 0:
                            flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 子模块 ' + str(table.row_values(j)[1]) + ' ID 不存在或无效')
                        if table.row_values(j)[2] !='':
                            caseid = TestCase.query.filter_by(id=table.row_values(j)[2]).count()
                            if caseid == 0:
                                flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 用例ID：' + str(table.row_values(j)[2]) + ' 不存在')
                            if str(table.row_values(j)[11]) not in ['update','delete','']:
                                flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 操作方式：' + str(table.row_values(j)[11]) + ' 不正确，应为update or delete')
                        else:
                            if str(table.row_values(j)[11]) not in ['add','']:
                                flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 操作方式：' + str(table.row_values(j)[11]) + ' 不正确，应为add')
                        if str(table.row_values(j)[11]) not in ['update','delete','add', '']:
                            flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 操作方式：' + str(table.row_values(j)[11]) + ' 不正确，请检查')
                        if table.row_values(j)[4] == '':
                            flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 测试用例标题' + ' 不能为空，请检查')
                        if table.row_values(j)[6] == '':
                            flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 操作步骤' + ' 不能为空，请检查')
                        if table.row_values(j)[7] == '':
                            flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 页面逻辑结果' + ' 不能为空，请检查')
                        if table.row_values(j)[9] == '':
                            flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 优先级' + ' 不能为空，请检查')
                        if str(table.row_values(j)[9]) not in ['P1','P2','P3','P4']:
                            flashmsg.append(str(sheetnames[i]) + 'sheet的第 ' + str(j) + ' 行 优先级：' + str(table.row_values(j)[9]) + ' 不正确，请检查')
                        casedata.append(table.row_values(j))
                    casedatas.append(casedata)
                caseids = []
                for cases in casedatas:
                    for case in cases:
                        if str(case[2]) != '':
                            if str(case[2]) not in caseids:
                                caseids.append(str(case[2]))
                            else:
                                flashmsg.append('用例ID：' + str(int(case[2])) + ' 出现重复')
                if len(flashmsg)>0:
                    flash(flashmsg, 'ok')
                    return render_template('uploadtestcase.html', user=user, form=form)
                for cases in casedatas:
                    for case in cases:
                        if case[2] == '' and case[11] in ['add','']:
                            testcase = TestCase(submodule_id=case[0], caseNo=case[3], testcasename=case[4],
                                                precondition=case[5], steps=case[6],
                                                logicalresult=case[7], databaseresult=case[8],
                                                priority=case[9],
                                                version=str(case[10]), note=case[13], status=1,
                                                createtime=datetime.now(), modifytime=datetime.now(),
                                                lastmodifier=user.id)
                            db.session.add(testcase)
                            db.session.commit()
                        elif case[2] != '' and case[11] in ['update','']:
                            testcase = TestCase.query.filter_by(id=case[2]).first()
                            testcase.submodule_id = case[0]
                            testcase.caseNo = case[3]
                            testcase.testcasename = case[4]
                            testcase.precondition = case[5]
                            testcase.steps = case[6]
                            testcase.logicalresult = case[7]
                            testcase.databaseresult = case[8]
                            testcase.priority = case[9]
                            testcase.version = str(case[10])
                            testcase.note = case[13]
                            testcase.status = 1
                            testcase.modifytime = datetime.now()
                            testcase.lastmodifier = user.id
                            db.session.add(testcase)
                            db.session.commit()
                        elif case[2] != '' and case[11] == 'delete':
                            testcase = TestCase.query.filter_by(id=case[2]).first()
                            testcase.submodule_id = case[0]
                            testcase.caseNo = case[3]
                            testcase.testcasename = case[4]
                            testcase.precondition = case[5]
                            testcase.steps = case[6]
                            testcase.logicalresult = case[7]
                            testcase.databaseresult = case[8]
                            testcase.priority = case[9]
                            testcase.version = str(case[10])
                            testcase.note = case[13]
                            testcase.status = 0
                            testcase.modifytime = datetime.now()
                            testcase.lastmodifier = user.id
                            db.session.add(testcase)
                            db.session.commit()
                flash(['上传用例成功'], 'ok')
                return render_template('uploadtestcase.html', user=user, form=form)
            except Exception as e:
                print(str(e))

@main.route('/downloadtestcase/', methods=['GET', 'POST'], endpoint='downloadtestcase')
@login_required
def downloadtestcase():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = DownloadExcelForm()
        form.submodulename.choices.remove((0, "请选择测试用例子模块"))
        return render_template('downloadtestcase.html', user=user, form=form)
    else:
        form = DownloadExcelForm(request.form)
        project_id = form.projectname.data
        if project_id:
            form.modulename.choices = [(0, "全部模块")]
            for m in TestCaseModule.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
        else:
            form.modulename.choices = [('', "请选择测试用例模块")]
        if form.modulename.data == None:
            form.modulename.data = None
        if len(form.modulename.data) == 0:
            form.modulename.data = None
        module_id = form.modulename.data

        if form.modulename.data == None:
            form.submodulename.choices.remove((0, "请选择测试用例子模块"))

        submodules = gettestcasesubmodules(project_id, module_id)
        for k, v in submodules.items():
            form.submodulename.choices.append((k, "子模块ID(" + str(k) + ")---" + v))
        if form.submodulename.data == None or len(form.submodulename.data) == 0:
            form.submodulename.data = None
        submodulename = form.submodulename.data

        if form.validate_on_submit():
            testcasedatas = {}
            if module_id != None:
                if len(module_id) > 1:
                    for index, item in enumerate(module_id):
                        if module_id[index] == 0:
                            form.errors['modulename'] = ['选择了全部，请勿选择单个模块']
                            return render_template('downloadtestcase.html', user=user, form=form)
                    if submodulename == None:
                        for m in module_id:
                            submodule_ids = TestCaseSubModule.query.filter_by(module_id=m, status=1).all()
                            casedata = []
                            for subm in submodule_ids:
                                cases = TestCase.query.filter_by(submodule_id=subm.id,status=1).order_by(db.asc(TestCase.caseNo)).all()
                                for c in cases:
                                    user = User.query.filter_by(id=c.lastmodifier).first()
                                    casedata.append([subm.id, subm.submodulename, c.id, c.caseNo, c.testcasename, c.precondition, c.steps, c.logicalresult, c.databaseresult, c.priority, c.version, '', user.username, c.note])
                            module = TestCaseModule.query.filter_by(id=m).first()
                            testcasedatas[module.modulename] = casedata
                    else:
                        submoduledict = {}
                        for m in module_id:
                            submodule_ids = TestCaseSubModule.query.filter_by(module_id=m, status=1).all()
                            submlist = [s.id for s in submodule_ids]
                            submoduledict[str(m)] = []
                            for sm in submodulename:
                                if sm in submlist:
                                    submoduledict[str(m)].append(sm)
                        for k,v in submoduledict.items():
                            casedata = []
                            for subm in v:
                                cases = TestCase.query.filter_by(submodule_id=subm, status=1).order_by(db.asc(TestCase.caseNo)).all()
                                for c in cases:
                                    submodule = TestCaseSubModule.query.filter_by(id=subm).first()
                                    user = User.query.filter_by(id=c.lastmodifier).first()
                                    casedata.append([subm, submodule.submodulename, c.id, c.caseNo, c.testcasename, c.precondition,c.steps, c.logicalresult, c.databaseresult, c.priority, c.version, '', user.username, c.note])
                            module = TestCaseModule.query.filter_by(id=k).first()
                            testcasedatas[module.modulename] = casedata
                else:
                    if module_id[0] == 0:
                        module_ids = TestCaseModule.query.filter_by(project_id=project_id, status=1).all()
                        if submodulename == None:
                            for m in module_ids:
                                submodule_ids = TestCaseSubModule.query.filter_by(module_id=m.id, status=1).all()
                                casedata = []
                                for subm in submodule_ids:
                                    cases = TestCase.query.filter_by(submodule_id=subm.id, status=1).order_by(
                                        db.asc(TestCase.caseNo)).all()
                                    for c in cases:
                                        user = User.query.filter_by(id=c.lastmodifier).first()
                                        casedata.append([subm.id, subm.submodulename, c.id, c.caseNo, c.testcasename,
                                                         c.precondition, c.steps, c.logicalresult, c.databaseresult,
                                                         c.priority, c.version, '', user.username, c.note])
                                module = TestCaseModule.query.filter_by(id=m.id).first()
                                testcasedatas[module.modulename] = casedata
                        else:
                            submoduledict = {}
                            for m in module_ids:
                                submodule_ids = TestCaseSubModule.query.filter_by(module_id=m, status=1).all()
                                submlist = [s.id for s in submodule_ids]
                                submoduledict[str(m)] = []
                                for sm in submodulename:
                                    if sm in submlist:
                                        submoduledict[str(m)].append(sm)
                            for k, v in submoduledict.items():
                                casedata = []
                                for subm in v:
                                    cases = TestCase.query.filter_by(submodule_id=subm, status=1).order_by(
                                        db.asc(TestCase.caseNo)).all()
                                    for c in cases:
                                        submodule = TestCaseSubModule.query.filter_by(id=subm).first()
                                        user = User.query.filter_by(id=c.lastmodifier).first()
                                        casedata.append([subm, submodule.submodulename, c.id, c.caseNo, c.testcasename,
                                                         c.precondition, c.steps, c.logicalresult, c.databaseresult,
                                                         c.priority, c.version, '', user.username, c.note])
                                module = TestCaseModule.query.filter_by(id=k).first()
                                testcasedatas[module.modulename] = casedata
                    else:
                        if submodulename == None:
                            submodule_ids = TestCaseSubModule.query.filter_by(module_id=module_id[0], status=1).all()
                            casedata = []
                            for subm in submodule_ids:
                                cases = TestCase.query.filter_by(submodule_id=subm.id, status=1).order_by(
                                    db.asc(TestCase.caseNo)).all()
                                for c in cases:
                                    user = User.query.filter_by(id=c.lastmodifier).first()
                                    casedata.append([subm.id, subm.submodulename, c.id, c.caseNo, c.testcasename,
                                                     c.precondition, c.steps, c.logicalresult, c.databaseresult,
                                                     c.priority, c.version, '', user.username, c.note])
                            module = TestCaseModule.query.filter_by(id=module_id[0]).first()
                            testcasedatas[module.modulename] = casedata
                        else:
                            casedata = []
                            for subm in submodulename:
                                cases = TestCase.query.filter_by(submodule_id=subm, status=1).order_by(db.asc(TestCase.caseNo)).all()
                                for c in cases:
                                    submodule = TestCaseSubModule.query.filter_by(id=subm).first()
                                    user = User.query.filter_by(id=c.lastmodifier).first()
                                    casedata.append([subm, submodule.submodulename, c.id, c.caseNo, c.testcasename,
                                                     c.precondition, c.steps, c.logicalresult, c.databaseresult,
                                                     c.priority, c.version, '', user.username, c.note])
                            module = TestCaseModule.query.filter_by(id=module_id[0]).first()
                            testcasedatas[module.modulename] = casedata
            else:
                module_ids = TestCaseModule.query.filter_by(project_id=project_id, status=1).all()
                for m in module_ids:
                    submodule_ids = TestCaseSubModule.query.filter_by(module_id=m.id, status=1).all()
                    casedata = []
                    for subm in submodule_ids:
                        cases = TestCase.query.filter_by(submodule_id=subm.id, status=1).order_by(
                            db.asc(TestCase.caseNo)).all()
                        for c in cases:
                            user = User.query.filter_by(id=c.lastmodifier).first()
                            casedata.append([subm.id, subm.submodulename, c.id, c.caseNo, c.testcasename,
                                             c.precondition, c.steps, c.logicalresult, c.databaseresult,
                                             c.priority, c.version, '', user.username, c.note])
                    module = TestCaseModule.query.filter_by(id=m.id).first()
                    testcasedatas[module.modulename] = casedata

            # with open(os.path.join(os.getcwd(), 'report', 'aa.txt'), 'tw', encoding='utf8') as f:
            #     f.write(str(testcasedatas))
            output = BytesIO()
            workfile = xlsxwriter.Workbook(output, {'in_memory': True})  # 创建Excel文件,不保存,直接输出
            title_bold = workfile.add_format({
                'bold': True,  # 字体加粗
                'border': 1,  # 单元格边框宽度
                'align': 'center',  # 水平对齐方式
                'valign': 'vcenter',  # 垂直对齐方式
                'fg_color': '#999999',  # 单元格背景颜色
            })
            bold = workfile.add_format({
                                        'bold':  False,  # 字体加粗
                                        'border': 1,  # 单元格边框宽度
                                        'align': 'left',  # 水平对齐方式
                                        'valign': 'vcenter',  # 垂直对齐方式
                                        'text_wrap': True,  # 是否自动换行
                                        })
            for k, v in testcasedatas.items():
                worksheet = workfile.add_worksheet(k)  # 创建工作表
                excel_title = ['子模块ID','子模块','用例ID','用例序号','测试用例标题','前置条件','操作步骤','页面逻辑结果','数据库结果','优先级','版本','操作','编写人','备注']
                worksheet.write_row('A1', excel_title, cell_format=title_bold)
                for i in range(len(v)):
                    for j in range(len(excel_title)):
                        worksheet.write(i+1, j, str(v[i][j]).replace('\r\n','\n'), bold)
            workfile.close()
            projectname = TestCaseProject.query.filter_by(id=project_id).first()
            output.seek(0)
            return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, attachment_filename=projectname.projectname+'.xlsx')
        else:
            return render_template('downloadtestcase.html', user=user, form=form)