# coding=utf8
from . import main
from flask import render_template, request, session, redirect, url_for, jsonify, g, flash
import hashlib, os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from ..ext import db
from ..upload import Pic_str
from app import common
import json
from .. import executecase
from .frontgetdata import *
from ..tools import *
from .forms import LoginForm, RegistrationForm, ApiForm, CaseForm, TestPlanForm, ProjectForm, ModuleForm, VersionForm, RoleForm, UserForm, PasswordForm, ResetpwdForm
from ..tools import login_required, getSection
from ..models import User, Role, Project, Module, Version, Api, Case, TestPlan, TestResult, TestReport


@main.route('/', methods=['GET', 'POST'])
def login():
    # db.drop_all()
    # db.create_all()
    if request.method == 'GET':
        form = LoginForm()
        form2 = ResetpwdForm()
        return render_template('login.html', form=form, form2=form2)
    else:
        form = LoginForm(request.form)
        form2 = ResetpwdForm(request.form)
        if form.validate_on_submit():
            email = form.email.data
            pwd = form.password.data
            password = hashlib.md5(pwd.encode("utf-8")).hexdigest()
            remember = form.remember.data
            user = User.query.filter_by(email=email, password=password).first()
            if user is None:
                flash('邮箱地址或密码错误', 'error')
                return render_template('login.html', form=form, form2=form2)
            if user.status == 0:
                flash('您的账号已失效，请联系管理员', 'error')
                return render_template('login.html', form=form, form2=form2)
            session['user'] = email
            g.user = session['user']
            addtime = User.query.filter_by(email=email, password=password).first()
            addtime.lastlogin = datetime.now()
            db.session.add(addtime)
            db.session.commit()
            if remember:
                session.permanent = True
                main.permanent_session_lifetime = timedelta(days=7)
            return redirect(url_for('.admin'))
        else:
            return render_template('login.html', form=form, form2=form2)  # 格式验证失败就重定向到登录页面

@main.route('/resetpwd/', methods=['GET', 'POST'])
def resetpwd():
    if request.method == 'GET':
        return redirect(url_for('.login'))
    else:
        form = LoginForm()
        form2 = ResetpwdForm(request.form)
        if form2.validate_on_submit():
            email = form2.useremail.data
            user = User.query.filter_by(email=email).first()
            if user:
                pwd = getpassword(10)
                password = hashlib.md5(pwd.encode("utf-8")).hexdigest()
                user.password = password
                user.modifytime = datetime.now()
                db.session.add(user)
                db.session.commit()
                emailData = getSection("email.conf", "email")
                sender = emailData['sender']
                receiver = email
                psw = emailData['psw']
                smtp_server = emailData['smtp_server']
                port = emailData['port']
                mail_body = "<html><head></head><body>您好：<br>&nbsp; &nbsp; &nbsp; &nbsp; 系统重置的密码为"+pwd+"。</p></body></html>"
                # 定义邮件内容
                msg = MIMEMultipart()
                body = MIMEText(mail_body, _subtype='html', _charset='utf-8')
                msg['Subject'] = '密码重置'
                msg['From'] = sender
                msg['To'] = receiver
                msg.attach(body)
                try:
                    smtp = smtplib.SMTP_SSL(smtp_server, port)
                except:
                    smtp = smtplib.SMTP()
                    smtp.connect(smtp_server, port)
                # 用户名密码
                smtp.starttls()
                smtp.login(sender, psw)
                smtp.sendmail(sender, receiver, msg.as_string())
                smtp.quit()
            flash("密码重置已发邮件，请查看邮件")
            return redirect(url_for('.login'))
        else:
            return render_template('login.html', form=form, form2=form2)  # 格式验证失败就重定向到登录页面

@main.route('/logout/', methods=['GET', 'POST'])
def logout():
    # name = session.pop('user')
    del session['user']
    return redirect(url_for('.login'))

@main.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        form = RegistrationForm()
        return render_template('registration.html', form=form)
    else:
        form = RegistrationForm(request.form)
        # print(form.password.data)
        if form.validate_on_submit():
            email = form.email.data
            # 在forms里已经校验
            # account = User.query.filter_by(email=email).count()
            # if account > 0:
            #     form.errors['email'] = ['此邮箱已经注册']
            #     return render_template('registration.html', form=form)
            username = form.username.data
            pwd = form.password.data
            password = hashlib.md5(pwd.encode("utf-8")).hexdigest()
            user = User(email=email, username=username, password=password, status=0, regtime=datetime.now(), modifytime=datetime.now())
            db.session.add(user)
            db.session.commit()
            flash('注册成功，登录吧~', 'ok')
            return redirect(url_for('.login'))
        else:
            return render_template('registration.html', form=form)


@main.route('/admin/', methods=['GET', 'POST'], endpoint='admin')
@login_required
def admin():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = PasswordForm()
        return render_template('admin.html', user=user, getrole=getuserrole, getusername=getusername, form=form)
    else:
        form = PasswordForm(request.form)
        if form.validate_on_submit():
            pwd = form.password.data
            password = hashlib.md5(pwd.encode("utf-8")).hexdigest()
            user.password = password
            user.modifytime = datetime.now()
            user.lastmodifier = user.id
            db.session.add(user)
            db.session.commit()
            del session['user']
            flash("修改密码成功,请重新登录")
            return redirect(url_for('.login'))
        else:
            return render_template('admin.html', user=user, getrole=getuserrole, getusername=getusername, form=form)


@main.route('/userlist/', methods=['GET', 'POST'], endpoint='userlist')
@login_required
def userlist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        users_info = User.query.all()
        return render_template('userlist.html', user=user, users_info=users_info, getrole=getuserrole)

@main.route('/edituserstatus/', methods=['GET', 'POST'], endpoint='edituserstatus')
@login_required
def edituserstatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    user2 = User.query.filter_by(id=id).first()
    user2.status = status
    user2.modifytime = datetime.now()
    user2.lastmodifier = user.id
    db.session.add(user2)
    db.session.commit()
    return jsonify('{"msg":"用户状态修改成功"}')

@main.route('/userdetail/<int:id>/', endpoint='userdetail')
@login_required
def userdetail(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    users_info = User.query.filter_by(id=id).first()
    return render_template('userdetail.html', user=user, users_info=users_info, getrole=getuserrole, getusername=getusername)


@main.route('/useredit/<int:id>/', methods=['GET', 'POST'], endpoint='useredit')
@login_required
def useredit(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    users_info = User.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = UserForm()
        form.images.data = users_info.images
        form.username.data = users_info.username
        form.telephone.data = users_info.telephone
        form.role_id.data = users_info.role_id
        return render_template('useredit.html', user=user, form=form, users_info=users_info)
    else:
        form = UserForm(request.form)
        if form.validate_on_submit():
            f = request.files.get("images")
            # print(f)
            if f:
                upload_path = os.path.join(main.static_folder, '..', 'static', 'images', 'photos',
                                           'uploads')  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                fname = secure_filename(f.filename)
                ext = fname.rsplit('.', 1)[1]
                new_filename = Pic_str().create_uuid() + '.' + ext
                f.save(os.path.join(upload_path, new_filename))
                images = os.path.join(os.path.sep, 'images', 'photos', 'uploads', new_filename)
                print(images)
                users_info.images = images
            users_info.username = form.username.data
            password = form.password.data
            if password:
                users_info.password = hashlib.md5(password.encode("utf-8")).hexdigest()
            users_info.telephone = form.telephone.data
            users_info.role_id = form.role_id.data
            users_info.modifytime = datetime.now()
            users_info.lastmodifier = user.id
            db.session.add(users_info)
            db.session.commit()
            flash('用户信息修改成功', 'ok')
            return redirect(url_for('.useredit', id=id))
        else:
            return render_template('useredit.html', user=user, form=form, users_info=users_info)

@main.route('/rolelist/', methods=['GET', 'POST'], endpoint='rolelist')
@login_required
def rolelist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        roledata = Role.query.all()
        return render_template('rolelist.html', user=user, roledata=roledata)

@main.route('/addrole/', methods=['GET', 'POST'], endpoint='addrole')
@login_required
def addrole():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = RoleForm()
        return render_template('addrole.html', user=user, form=form)
    else:
        form = RoleForm(request.form)
        rolename = form.rolename.data
        if form.validate_on_submit():
            name = Role.query.filter_by(rolename=rolename).count()
            if name > 0:
                form.errors['rolename'] = ['此角色名称已存在']
                return render_template('addrole.html', user=user, form=form)
            role = Role(rolename=rolename, createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(role)
            db.session.commit()
            flash('角色名称添加成功', 'ok')
            return redirect(url_for('.addrole'))
        else:
            return render_template('addrole.html', user=user, form=form)

@main.route('/editrole/<int:id>', methods=['GET', 'POST'], endpoint='editrole')
@login_required
def editrole(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    role_info = Role.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = RoleForm()
        form.rolename.data = role_info.rolename
        return render_template('editrole.html', user=user, form=form)
    else:
        form = RoleForm(request.form)
        if form.validate_on_submit():
            rolename = form.rolename.data
            name = Role.query.filter_by(rolename=rolename).count()
            if name > 1:
                form.errors['rolename'] = ['此角色名称已存在']
                return render_template('editrole.html', user=user, form=form)
            if name == 1:
                r = Role.query.filter_by(rolename=rolename).first()
                if r.id != id:
                    form.errors['rolename'] = ['此角色名称已存在']
                    return render_template('editrole.html', user=user, form=form)
            role_info.rolename = form.rolename.data
            role_info.modifytime = datetime.now()
            role_info.lastmodifier = user.id
            db.session.add(role_info)
            db.session.commit()
            flash('角色名称编辑成功', 'ok')
            return redirect(url_for('.editrole',id=id))
        else:
            return render_template('editrole.html', user=user, form=form)


@main.route('/projectlist/', methods=['GET', 'POST'], endpoint='projectlist')
@login_required
def projectlist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        project_info = Project.query.all()
        return render_template('projectlist.html', user=user, project_info=project_info, roles=getrolename,users=getuseremail)

@main.route('/editprojectstatus/', methods=['GET', 'POST'], endpoint='editprojectstatus')
@login_required
def editprojectstatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    project = Project.query.filter_by(id=id).first()
    project.status = status
    project.modifytime = datetime.now()
    project.lastmodifier = user.id
    db.session.add(project)
    db.session.commit()
    return jsonify('{"msg":"项目状态修改成功"}')

@main.route('/addproject/', methods=['GET', 'POST'], endpoint='addproject')
@login_required
def addproject():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = ProjectForm()
        return render_template('addproject.html', user=user, form=form)
    else:
        form = ProjectForm(request.form)
        projectname = form.projectname.data
        roles = form.role_id.data
        usersdata = form.users.data
        note = form.note.data
        if form.validate_on_submit():
            name = Project.query.filter_by(projectname=projectname).count()
            if name > 0:
                form.errors['projectname'] = ['此项目名称已存在']
                return render_template('addproject.html', user=user, form=form)
            if len(roles) > 1:
                for index, item in enumerate(roles):
                    roles[index] = str(item)
                role_id = ",".join(roles)
            else:
                role_id = roles[0]
            if len(usersdata) > 1:
                for index, item in enumerate(usersdata):
                    usersdata[index] = str(item)
                users = ",".join(usersdata)
            else:
                users = usersdata[0]
            project = Project(projectname=projectname, role_id=role_id, users=users, note=note, status=0, createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(project)
            db.session.commit()
            flash('项目添加成功', 'ok')
            return redirect(url_for('.addproject'))
        else:
            return render_template('addproject.html', user=user, form=form)

@main.route('/editproject/<int:id>', methods=['GET', 'POST'], endpoint='editproject')
@login_required
def editproject(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    project_info = Project.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = ProjectForm()
        form.projectname.data = project_info.projectname
        if project_info.role_id==None:
            role_id = None
        elif project_info.role_id.find(",") >= 0:
            role_id = [int(x) for x in project_info.role_id.split(",")]
        else:
            role_id = [int(x) for x in project_info.role_id]
        form.role_id.data = role_id
        if project_info.users== None:
            users = None
        elif project_info.users.find(",") >= 0:
            users = [int(x) for x in project_info.users.split(",")]
        else:
            users = [int(x) for x in project_info.users]
        form.users.data = users
        form.note.data = project_info.note
        return render_template('editproject.html', user=user, form=form)
    else:
        form = ProjectForm(request.form)
        if form.validate_on_submit():
            projectname = form.projectname.data
            roles = form.role_id.data
            usersdata = form.users.data
            project_info.note = form.note.data
            name = Project.query.filter_by(projectname=projectname).count()
            if name > 1:
                form.errors['projectname'] = ['此项目名称已存在']
                return render_template('editproject.html', user=user, form=form)
            if name == 1:
                p = Project.query.filter_by(projectname=projectname).first()
                if p.id != id:
                    form.errors['projectname'] = ['此项目名称已存在']
                    return render_template('editproject.html', user=user, form=form)
            project_info.projectname = form.projectname.data
            if len(roles) > 1:
                for index, item in enumerate(roles):
                    roles[index] = str(item)
                project_info.role_id = ",".join(roles)
            else:
                project_info.role_id = roles[0]
            if len(usersdata) > 1:
                for index, item in enumerate(usersdata):
                    usersdata[index] = str(item)
                project_info.users = ",".join(usersdata)
            else:
                project_info.users = usersdata[0]
            project_info.modifytime = datetime.now()
            project_info.lastmodifier = user.id
            db.session.add(project_info)
            db.session.commit()
            flash('项目编辑成功', 'ok')
            return redirect(url_for('.editproject',id=id))
        else:
            return render_template('editproject.html', user=user, form=form)


@main.route('/modulelist/', methods=['GET', 'POST'], endpoint='modulelist')
@login_required
def modulelist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        modulelist = Module.query.all()
        return render_template('modulelist.html', user=user, modulelist=modulelist)

@main.route('/editmodulestatus/', methods=['GET', 'POST'], endpoint='editmodulestatus')
@login_required
def editmodulestatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    module = Module.query.filter_by(id=id).first()
    module.status = status
    module.modifytime = datetime.now()
    module.lastmodifier = user.id
    db.session.add(module)
    db.session.commit()
    return jsonify('{"msg":"模块状态修改成功"}')

@main.route('/addmodule/', methods=['GET', 'POST'], endpoint='addmodule')
@login_required
def addmodule():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = ModuleForm()
        return render_template('addmodule.html', user=user, form=form)
    else:
        form = ModuleForm(request.form)
        modulename = form.modulename.data
        project_id = form.projectname.data
        note = form.note.data
        if form.validate_on_submit():
            name = Module.query.filter_by(modulename=modulename,project_id=project_id).count()
            if name > 0:
                form.errors['modulename'] = ['此项目模块名称已存在']
                return render_template('addmodule.html', user=user, form=form)
            module = Module(project_id=project_id, modulename=modulename, note=note, status=0, createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(module)
            db.session.commit()
            flash('项目模块添加成功', 'ok')
            return redirect(url_for('.addmodule'))
        else:
            return render_template('addmodule.html', user=user, form=form)

@main.route('/editmodule/<int:id>', methods=['GET', 'POST'], endpoint='editmodule')
@login_required
def editmodule(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    module_info = Module.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = ModuleForm()
        form.modulename.data = module_info.modulename
        form.projectname.data = module_info.project_id
        form.note.data = module_info.note
        return render_template('editmodule.html', user=user, form=form)
    else:
        form = ModuleForm(request.form)
        if form.validate_on_submit():
            project_id = form.projectname.data
            modulename = form.modulename.data
            module_info.note = form.note.data
            name = Module.query.filter_by(project_id=project_id,modulename=modulename).count()
            if name > 1:
                form.errors['modulename'] = ['此项目模块名称已存在']
                return render_template('editmodule.html', user=user, form=form)
            if name == 1:
                m = Module.query.filter_by(project_id=project_id,modulename=modulename).first()
                if m.id != id:
                    form.errors['modulename'] = ['此项目模块名称已存在']
                    return render_template('editmodule.html', user=user, form=form)
            module_info.project_id = form.projectname.data
            module_info.modulename = form.modulename.data
            module_info.modifytime = datetime.now()
            module_info.lastmodifier = user.id
            db.session.add(module_info)
            db.session.commit()
            flash('项目模块编辑成功', 'ok')
            return redirect(url_for('.editmodule',id=id))
        else:
            return render_template('editmodule.html', user=user, form=form)

@main.route('/versionlist/', methods=['GET', 'POST'], endpoint='versionlist')
@login_required
def versionlist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        versionlist = Version.query.all()
        return render_template('versionlist.html', user=user, versionlist=versionlist)

@main.route('/editversionstatus/', methods=['GET', 'POST'], endpoint='editversionstatus')
@login_required
def editversionstatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    version = Version.query.filter_by(id=id).first()
    version.status = status
    version.modifytime = datetime.now()
    version.lastmodifier = user.id
    db.session.add(version)
    db.session.commit()
    return jsonify('{"msg":"版本状态修改成功"}')

@main.route('/addversion/', methods=['GET', 'POST'], endpoint='addversion')
@login_required
def addversion():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = VersionForm()
        return render_template('addversion.html', user=user, form=form)
    else:
        form = VersionForm(request.form)
        versionname = form.versionname.data
        project_id = form.projectname.data
        note = form.note.data
        if form.validate_on_submit():
            name = Version.query.filter_by(versionname=versionname,project_id=project_id).count()
            if name > 0:
                form.errors['versionname'] = ['此项目模块名称已存在']
                return render_template('addversion.html', user=user, form=form)
            version = Version(project_id=project_id, versionname=versionname, note=note, status=0, createtime=datetime.now(), modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(version)
            db.session.commit()
            flash('接口版本添加成功', 'ok')
            return redirect(url_for('.addversion'))
        else:
            return render_template('addversion.html', user=user, form=form)

@main.route('/editversion/<int:id>', methods=['GET', 'POST'], endpoint='editversion')
@login_required
def editversion(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    version_info = Version.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = VersionForm()
        form.versionname.data = version_info.versionname
        form.projectname.data = version_info.project_id
        form.note.data = version_info.note
        return render_template('editversion.html', user=user, form=form)
    else:
        form = VersionForm(request.form)
        if form.validate_on_submit():
            project_id = form.projectname.data
            versionname = form.versionname.data
            version_info.note = form.note.data
            name = Version.query.filter_by(project_id=project_id,versionname=versionname).count()
            if name > 1:
                form.errors['versionname'] = ['此项目模块名称已存在']
                return render_template('editversion.html', user=user, form=form)
            if name == 1:
                v = Version.query.filter_by(project_id=project_id,versionname=versionname).first()
                if v.id != id:
                    form.errors['versionname'] = ['此项目模块名称已存在']
                    return render_template('editversion.html', user=user, form=form)
            version_info.project_id = form.projectname.data
            version_info.versionname = form.versionname.data
            version_info.modifytime = datetime.now()
            version_info.lastmodifier = user.id
            db.session.add(version_info)
            db.session.commit()
            flash('接口版本编辑成功', 'ok')
            return redirect(url_for('.editversion',id=id))
        else:
            return render_template('editversion.html', user=user, form=form)

@main.route('/apilist/', methods=['GET', 'POST'], endpoint='apilist')
@login_required
def apilist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    company = getSection("env.conf", "company")
    apistatus = getSection("env.conf", "apistatus")
    if request.method == 'GET':
        apilist = db.session.query(Api, User).join(User, Api.lastmodifier == User.id).all()
        return render_template('apilist.html', user=user, apilist=apilist, company=company, apistatus=apistatus)


@main.route('/editapistatus/', methods=['GET', 'POST'], endpoint='editapistatus')
@login_required
def editapistatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    api = Api.query.filter_by(id=id).first()
    api.status = status
    api.lastmodifier = user.id
    db.session.add(api)
    db.session.commit()
    return jsonify('{"msg":"接口状态修改成功"}')


@main.route('/lockapi/', methods=['GET', 'POST'], endpoint='lockapi')
@login_required
def lockapi():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    api = Api.query.filter_by(id=id).first()
    api.locked = 1
    api.locker = user.id
    db.session.add(api)
    db.session.commit()
    return jsonify('{"msg":"接口已被锁定"}')


@main.route('/unlockapi/', methods=['GET', 'POST'], endpoint='unlockapi')
@login_required
def unlockapi():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    api = Api.query.filter_by(id=id).first()
    if api.locker == user.id:
        api.locked = 0
        db.session.add(api)
        db.session.commit()
        return jsonify('{"msg":"接口已被解锁"}')
    else:
        return jsonify('{"msg":"不是锁定人，不能解锁"}')


@main.route('/addapi/', methods=['GET', 'POST'], endpoint='addapi')
@login_required
def addapi():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = ApiForm()
        return render_template('addapi.html', user=user, form=form)
    else:
        form = ApiForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择所属模块")]
        form.versionname.choices = [(0, "请选择所属版本")]
        if project_id:
            for m in Module.query.filter_by(project_id=project_id, status = 1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=project_id, status = 1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            version_id = form.versionname.data
            apiname = form.apiname.data
            method = form.method.data
            domain = form.domain.data
            url = form.url.data
            protocol = form.protocol.data
            transmethod = form.transmethod.data
            jsondata = form.jsondata.data
            if common.check_json_format(jsondata) == False:
                form.jsondata.errors = ['body参数格式不正确']
                return render_template('addapi.html', user=user, form=form)
            jsondata = jsondata.strip().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            jsondata = json.dumps(eval(jsondata))
            # print(json.dumps(eval(jsondata)))
            note = form.note.data
            api = Api(module_id=module_id, version_id=version_id, apiname=apiname, method=method, domain=domain,
                      url=url, protocol=protocol, transmethod=transmethod, jsondata=jsondata, note=note,
                      status="unsubmitted", createtime=datetime.now(), modifytime=datetime.now(), locked=0,
                      lastmodifier=user.id)
            db.session.add(api)
            db.session.commit()
            flash('接口添加成功', 'ok')
            form = ApiForm()
            return redirect(url_for('.addapi'))
        else:
            return render_template('addapi.html', user=user, form=form)


@main.route('/editapi/<int:id>/', methods=['GET', 'POST'], endpoint='editapi')
@login_required
def editapi(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    api = Api.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = ApiForm()
        module_id = Module.query.filter_by(id=api.module_id).first()
        version_id = Version.query.filter_by(id=api.version_id).first()
        projects = Project.query.filter_by(id=module_id.project_id).first()
        form.projectname.data = projects.id
        form.modulename.data = module_id.id
        form.versionname.data = version_id.id
        if projects.id:
            for m in Module.query.filter_by(project_id=projects.id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=projects.id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        form.apiname.data = api.apiname
        form.method.data = api.method
        form.domain.data = api.domain
        form.url.data = api.url
        form.protocol.data = api.protocol
        form.transmethod.data = api.transmethod
        form.jsondata.data = api.jsondata
        form.note.data = api.note
        return render_template('editapi.html', user=user, form=form)
    else:
        form = ApiForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择所属模块")]
        form.versionname.choices = [(0, "请选择所属版本")]
        if project_id:
            for m in Module.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=project_id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        if form.validate_on_submit():
            if api.locked == 1 and api.locker != user.id:
                flash('此接口已被人锁定，你不能修改', 'error')
                return render_template('editapi.html', user=user, form=form)
            projectname = form.projectname.data
            api.module_id = form.modulename.data
            api.version_id = form.versionname.data
            api.apiname = form.apiname.data
            api.method = form.method.data
            api.domain = form.domain.data
            api.url = form.url.data
            api.protocol = form.protocol.data
            api.transmethod = form.transmethod.data
            jsondata = form.jsondata.data
            if common.check_json_format(jsondata) == False:
                form.jsondata.errors = ['body参数格式不正确']
                return render_template('editapi.html', user=user, form=form)
            jsondata = jsondata.strip().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            api.jsondata = json.dumps(eval(jsondata))
            # print(json.dumps(eval(jsondata)))
            api.note = form.note.data
            api.status = "unsubmitted"
            api.modifytime = datetime.now()
            api.lastmodifier = user.id
            db.session.add(api)
            db.session.commit()
            flash('接口修改成功,接口状态为待提交', 'ok')
            return redirect(url_for('.editapi', id=api.id))
        else:
            return render_template('editapi.html', user=user, form=form)


@main.route('/caselist/', methods=['GET', 'POST'], endpoint='caselist')
@login_required
def caselist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    company = getSection("env.conf", "company")
    apistatus = getSection("env.conf", "apistatus")
    casestatus = getSection("env.conf", "casestatus")
    comparemethod = getSection("env.conf", "comparemethod")
    if request.method == 'GET':
        caselist = db.session.query(Case, User).join(User, Case.lastmodifier == User.id).all()
        return render_template('caselist.html', user=user, caselist=caselist, company=company, apistatus=apistatus,
                               casestatus=casestatus, comparemethod=comparemethod)


@main.route('/editcasestatus/', methods=['GET', 'POST'], endpoint='editcasestatus')
@login_required
def editcasestatus():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    status = data.get('status')
    case = Case.query.filter_by(id=id).first()
    case.status = status
    case.lastmodifier = user.id
    db.session.add(case)
    db.session.commit()
    return jsonify('{"msg":"用例状态修改成功"}')


@main.route('/lockcase/', methods=['GET', 'POST'], endpoint='lockcase')
@login_required
def lockcase():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    case = Case.query.filter_by(id=id).first()
    case.locked = 1
    case.locker = user.id
    db.session.add(case)
    db.session.commit()
    return jsonify('{"msg":"用例已被锁定"}')


@main.route('/unlockcase/', methods=['GET', 'POST'], endpoint='unlockcase')
@login_required
def unlockcase():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    case = Case.query.filter_by(id=id).first()
    if case.locker == user.id:
        case.locked = 0
        db.session.add(case)
        db.session.commit()
        return jsonify('{"msg":"用例已被解锁"}')
    else:
        return jsonify('{"msg":"不是锁定人，不能解锁"}')


@main.route('/addcase/', methods=['GET', 'POST'], endpoint='addcase')
@login_required
def addcase():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = CaseForm()
        return render_template('addcase.html', user=user, form=form)
    else:
        form = CaseForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择所属模块")]
        form.versionname.choices = [(0, "请选择所属版本")]
        if project_id:
            for m in Module.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=project_id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        module_id = form.modulename.data
        version_id = form.versionname.data
        form.api_id.choices = [(0, "请选择所属接口")]
        if module_id and version_id:
            for a in Api.query.filter_by(module_id=module_id, version_id=version_id):
                form.api_id.choices.append((a.id, "接口ID(" + str(a.id) + ")---" + a.apiname))
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            version_id = form.versionname.data
            api_id = form.api_id.data
            casename = form.casename.data
            beforecase = form.beforecase.data
            jsondata = form.jsondata.data
            if common.check_json_format(jsondata) == False:
                form.jsondata.errors = ['body参数格式不正确']
                return render_template('addcase.html', user=user, form=form)
            jsondata = jsondata.strip().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            jsondata = json.dumps(eval(jsondata))
            # print(json.dumps(eval(jsondata)))
            comparemethod = form.comparemethod.data
            expectedResults = form.expectedResults.data
            note = form.note.data
            case = Case(api_id=api_id, casename=casename, beforecase=beforecase, jsondata=jsondata,
                        comparemethod=comparemethod, expectedResults=expectedResults, note=note, status="unsubmitted",
                        createtime=datetime.now(), modifytime=datetime.now(), locked=0, lastmodifier=user.id)
            db.session.add(case)
            db.session.commit()
            flash('测试用例添加成功', 'ok')
            form = CaseForm()
            return redirect(url_for('.addcase'))
        else:
            return render_template('addcase.html', user=user, form=form)


@main.route('/addapicase/<int:id>', methods=['GET', 'POST'], endpoint='addapicase')
@login_required
def addapicase(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    caseapi = Api.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = CaseForm()
        module_id = Module.query.filter_by(id=caseapi.module_id).first()
        version_id = Version.query.filter_by(id=caseapi.version_id).first()
        projects = Project.query.filter_by(id=module_id.project_id).first()
        form.projectname.data = projects.id
        form.modulename.data = module_id.id
        form.versionname.data = version_id.id
        form.api_id.data = id
        if projects.id:
            for m in Module.query.filter_by(project_id=projects.id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=projects.id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        if module_id.id and version_id.id:
            for a in Api.query.filter_by(module_id=module_id.id, version_id=version_id.id):
                form.api_id.choices.append((a.id, "接口ID(" + str(a.id) + ")---" + a.apiname))
        form.jsondata.data = caseapi.jsondata
        return render_template('addcase.html', user=user, form=form)
    else:
        form = CaseForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择所属模块")]
        form.versionname.choices = [(0, "请选择所属版本")]
        if project_id:
            for m in Module.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=project_id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        module_id = form.modulename.data
        version_id = form.versionname.data
        form.api_id.choices = [(0, "请选择所属接口")]
        if module_id and version_id:
            for a in Api.query.filter_by(module_id=module_id, version_id=version_id):
                form.api_id.choices.append((a.id, "接口ID(" + str(a.id) + ")---" + a.apiname))
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            version_id = form.versionname.data
            api_id = form.api_id.data
            casename = form.casename.data
            beforecase = form.beforecase.data
            jsondata = form.jsondata.data
            if common.check_json_format(jsondata) == False:
                form.jsondata.errors = ['body参数格式不正确']
                return render_template('addcase.html', user=user, form=form)
            jsondata = jsondata.strip().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            jsondata = json.dumps(eval(jsondata))
            # print(json.dumps(eval(jsondata)))
            comparemethod = form.comparemethod.data
            expectedResults = form.expectedResults.data
            note = form.note.data
            case = Case(api_id=api_id, casename=casename, beforecase=beforecase, jsondata=jsondata,
                        comparemethod=comparemethod, expectedResults=expectedResults, note=note, status="unsubmitted",
                        createtime=datetime.now(), modifytime=datetime.now(), locked=0, lastmodifier=user.id)
            db.session.add(case)
            db.session.commit()
            flash('测试用例添加成功', 'ok')
            form = CaseForm()
            return redirect(url_for('.addapicase', id=id))
        else:
            return render_template('addcase.html', user=user, form=form)


@main.route('/editcase/<int:id>/', methods=['GET', 'POST'], endpoint='editcase')
@login_required
def editcase(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    case = Case.query.filter_by(id=id).first()
    caseapi = Api.query.filter_by(id=case.api_id).first()
    if request.method == 'GET':
        form = CaseForm()
        module_id = Module.query.filter_by(id=caseapi.module_id).first()
        version_id = Version.query.filter_by(id=caseapi.version_id).first()
        projects = Project.query.filter_by(id=module_id.project_id).first()
        form.projectname.data = projects.id
        form.modulename.data = module_id.id
        form.versionname.data = version_id.id
        form.api_id.data = case.api_id
        if projects.id:
            for m in Module.query.filter_by(project_id=projects.id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=projects.id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        if module_id.id and version_id.id:
            for a in Api.query.filter_by(module_id=module_id.id, version_id=version_id.id):
                form.api_id.choices.append((a.id, "接口ID(" + str(a.id) + ")---" + a.apiname))
        form.casename.data = case.casename
        form.beforecase.data = case.beforecase
        form.jsondata.data = case.jsondata
        form.comparemethod.data = case.comparemethod
        form.expectedResults.data = case.expectedResults
        form.note.data = case.note
        return render_template('editcase.html', user=user, form=form)
    else:
        form = CaseForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择所属模块")]
        form.versionname.choices = [(0, "请选择所属版本")]
        if project_id:
            for m in Module.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=project_id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        module_id = form.modulename.data
        version_id = form.versionname.data
        form.api_id.choices = [(0, "请选择所属接口")]
        if module_id and version_id:
            for a in Api.query.filter_by(module_id=module_id, version_id=version_id):
                form.api_id.choices.append((a.id, "接口ID(" + str(a.id) + ")---" + a.apiname))
        if form.validate_on_submit():
            if case.locked == 1 and case.locker != user.id:
                flash('此用例已被人锁定，你不能修改', 'error')
                return render_template('editcase.html', user=user, form=form)
            projectname = form.projectname.data
            module_id = form.modulename.data
            version_id = form.versionname.data
            case.api_id = form.api_id.data
            case.casename = form.casename.data
            case.beforecase = form.beforecase.data
            jsondata = form.jsondata.data
            if common.check_json_format(jsondata) == False:
                form.jsondata.errors = ['body参数格式不正确']
                return render_template('editcase.html', user=user, form=form)
            jsondata = jsondata.strip().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            case.jsondata = json.dumps(eval(jsondata))
            # print(json.dumps(eval(jsondata)))
            case.comparemethod = form.comparemethod.data
            case.expectedResults = form.expectedResults.data
            case.note = form.note.data
            case.status = "unsubmitted"
            case.modifytime = datetime.now()
            case.lastmodifier = user.id
            db.session.add(case)
            db.session.commit()
            flash('用例修改成功,接口状态为待提交', 'ok')
            return redirect(url_for('.editcase', id=case.id))
        else:
            return render_template('editcase.html', user=user, form=form)


@main.route('/copycase/<int:id>/', methods=['GET', 'POST'], endpoint='copycase')
@login_required
def copycase(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    case = Case.query.filter_by(id=id).first()
    caseapi = Api.query.filter_by(id=case.api_id).first()
    if request.method == 'GET':
        form = CaseForm()
        module_id = Module.query.filter_by(id=caseapi.module_id).first()
        version_id = Version.query.filter_by(id=caseapi.version_id).first()
        projects = Project.query.filter_by(id=module_id.project_id).first()
        form.projectname.data = projects.id
        form.modulename.data = module_id.id
        form.versionname.data = version_id.id
        form.api_id.data = case.api_id
        if projects.id:
            for m in Module.query.filter_by(project_id=projects.id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=projects.id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        if module_id.id and version_id.id:
            for a in Api.query.filter_by(module_id=module_id.id, version_id=version_id.id):
                form.api_id.choices.append((a.id, "接口ID(" + str(a.id) + ")---" + a.apiname))
        form.casename.data = case.casename
        form.beforecase.data = case.beforecase
        form.jsondata.data = case.jsondata
        form.comparemethod.data = case.comparemethod
        form.expectedResults.data = case.expectedResults
        form.note.data = case.note
        return render_template('addcase.html', user=user, form=form)
    else:
        form = CaseForm(request.form)
        project_id = form.projectname.data
        form.modulename.choices = [(0, "请选择所属模块")]
        form.versionname.choices = [(0, "请选择所属版本")]
        if project_id:
            for m in Module.query.filter_by(project_id=project_id, status=1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=project_id, status=1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        module_id = form.modulename.data
        version_id = form.versionname.data
        form.api_id.choices = [(0, "请选择所属接口")]
        if module_id and version_id:
            for a in Api.query.filter_by(module_id=module_id, version_id=version_id):
                form.api_id.choices.append((a.id, "接口ID(" + str(a.id) + ")---" + a.apiname))
        if form.validate_on_submit():
            projectname = form.projectname.data
            module_id = form.modulename.data
            version_id = form.versionname.data
            api_id = form.api_id.data
            casename = form.casename.data
            beforecase = form.beforecase.data
            jsondata = form.jsondata.data
            if common.check_json_format(jsondata) == False:
                form.jsondata.errors = ['body参数格式不正确']
                return render_template('addcase.html', user=user, form=form)
            jsondata = jsondata.strip().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
            jsondata = json.dumps(eval(jsondata))
            # print(json.dumps(eval(jsondata)))
            comparemethod = form.comparemethod.data
            expectedResults = form.expectedResults.data
            note = form.note.data
            case = Case(api_id=api_id, casename=casename, beforecase=beforecase, jsondata=jsondata,
                        comparemethod=comparemethod, expectedResults=expectedResults, note=note, status="unsubmitted",
                        createtime=datetime.now(), modifytime=datetime.now(), locked=0, lastmodifier=user.id)
            db.session.add(case)
            db.session.commit()
            flash('测试用例添加成功', 'ok')
            form = CaseForm()
            return redirect(url_for('.copycase', id=id))
        else:
            return render_template('addcase.html', user=user, form=form)


@main.route('/apicaselist/<int:id>/', methods=['GET', 'POST'], endpoint='apicaselist')
@login_required
def apicaselist(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    company = getSection("env.conf", "company")
    apistatus = getSection("env.conf", "apistatus")
    casestatus = getSection("env.conf", "casestatus")
    comparemethod = getSection("env.conf", "comparemethod")
    if request.method == 'GET':
        caselist = db.session.query(Case, User).join(User, Case.lastmodifier == User.id).filter(Case.api_id == id).all()
        return render_template('caselist.html', user=user, caselist=caselist, company=company, apistatus=apistatus,
                               casestatus=casestatus, comparemethod=comparemethod)

@main.route('/testplanlist/', methods=['GET', 'POST'], endpoint='testplanlist')
@login_required
def testplanlist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    testplanstatus = getSection("env.conf", "testplanstatus")
    if request.method == 'GET':
        testplanlist = db.session.query(TestPlan, User, Project).join(User, TestPlan.lastmodifier == User.id).join(
            Project, TestPlan.project == Project.id).all()
        return render_template('testplanlist.html', user=user, testplanlist=testplanlist, modules=getmodulename,
                               versions=getversionname, apis=getapiname, testplanstatus=testplanstatus)

@main.route('/editsendemail/', methods=['GET', 'POST'], endpoint='editsendemail')
@login_required
def editsendemail():
    email = g.user
    user = User.query.filter_by(email=email).first()
    data = request.get_json()
    id = data.get('id')
    sendemail = data.get('sendemail')
    testplan = TestPlan.query.filter_by(id=id).first()
    testplan.sendemail = sendemail
    testplan.lastmodifier = user.id
    db.session.add(testplan)
    db.session.commit()
    return jsonify('{"msg":"测试计划是否发送邮件状态修改成功"}')

@main.route('/addtestplan/', methods=['GET', 'POST'], endpoint='addtestplan')
@login_required
def addtestplan():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        form = TestPlanForm()
        form.api_id.choices.remove((0, "请选择包含接口"))
        return render_template('addtestplan.html', user=user, form=form)
    else:
        form = TestPlanForm(request.form)
        project_id = form.projectname.data
        if project_id:
            form.modulename.choices = [(0, "全部模块")]
            form.versionname.choices = [(0, "全部版本")]
            for m in Module.query.filter_by(project_id=project_id, status = 1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=project_id, status = 1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        else:
            form.modulename.choices = [('', "请选择包含模块")]
            form.versionname.choices = [('', "请选择包含版本")]

        if form.modulename.data == None:
            form.modulename.data = None
        elif len(form.modulename.data) == 0:
            form.modulename.data = None
        module_id = form.modulename.data

        if form.versionname.data == None:
            form.versionname.data = None
        elif len(form.versionname.data) == 0:
            form.versionname.data = None
        version_id = form.versionname.data

        if form.modulename.data == None or form.versionname.data == None:
            form.api_id.choices.remove((0, "请选择包含接口"))
        elif len(form.modulename.data) == 0 and len(form.versionname.data) == 0:
            form.api_id.choices.remove((0, "请选择包含接口"))
        api_ids = getapis(project_id, module_id, version_id)
        for k, v in api_ids.items():
            form.api_id.choices.append((k, "接口ID(" + str(k) + ")---" + v))
        if form.api_id.data == None:
            form.api_id.data = None
        elif len(form.api_id.data) == 0:
            form.api_id.data = None
        api_id = form.api_id.data
        appointmentTime = form.appointmentTime.data
        note = form.note.data
        if form.validate_on_submit():
            planname = form.planname.data
            projectname = project_id
            if len(module_id) > 1:
                for index, item in enumerate(module_id):
                    if module_id[index] == 0:
                        form.errors['modulename'] = ['选择了全部，请勿选择单个模块']
                        return render_template('addtestplan.html', user=user, form=form)
                    module_id[index] = str(item)
                modules = ",".join(module_id)
            else:
                modules = module_id[0]

            if len(version_id) > 1:
                for index, item in enumerate(version_id):
                    if version_id[index] == 0:
                        form.errors['versionname'] = ['选择了全部，请勿选择单个版本']
                        return render_template('addtestplan.html', user=user, form=form)
                    version_id[index] = str(item)
                versions = ",".join(version_id)
            else:
                versions = version_id[0]

            if api_id == None:
                apis = ""
            elif len(api_id) > 1:
                for index, item in enumerate(api_id):
                    api_id[index] = str(item)
                apis = ",".join(api_id)
            else:
                apis = api_id[0]

            testplan = TestPlan(planname=planname, project=projectname, modules=modules, versions=versions, apis=apis,
                                appointmentTime=appointmentTime, note=note, status="create", createtime=datetime.now(),
                                modifytime=datetime.now(), lastmodifier=user.id)
            db.session.add(testplan)
            db.session.commit()
            flash('测试计划添加成功', 'ok')
            form = TestPlanForm()
            return redirect(url_for('.addtestplan'))
        else:
            return render_template('addtestplan.html', user=user, form=form)


@main.route('/edittestplan/<int:id>/', methods=['GET', 'POST'], endpoint='edittestplan')
@login_required
def edittestplan(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    plan = TestPlan.query.filter_by(id=id).first()
    if request.method == 'GET':
        form = TestPlanForm()
        form.planname.data = plan.planname
        form.projectname.data = plan.project
        form.modulename.choices = [(0, "全部模块")]
        form.versionname.choices = [(0, "全部版本")]
        if plan.project:
            for m in Module.query.filter_by(project_id=plan.project, status = 1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=plan.project, status = 1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        if plan.modules.find(",") >= 0:
            modules = [int(x) for x in plan.modules.split(",")]
        else:
            modules = [int(x) for x in plan.modules]
        form.modulename.data = modules
        if plan.versions.find(",") >= 0:
            versions = [int(x) for x in plan.versions.split(",")]
        else:
            versions = [int(x) for x in plan.versions]
        form.versionname.data = versions
        if plan.apis:
            if plan.apis.find(",") >= 0:
                apis = [int(x) for x in plan.apis.split(",")]
            else:
                apis = [int(x) for x in plan.apis]
            form.api_id.data = apis
        form.api_id.choices.remove((0, "请选择包含接口"))
        api_ids = getapis(plan.project, modules, versions)
        for k, v in api_ids.items():
            form.api_id.choices.append((k, "接口ID(" + str(k) + ")---" + v))
        form.appointmentTime.data = str(plan.appointmentTime)[:-3]
        form.note.data = plan.note
        return render_template('edittestplan.html', user=user, form=form)
    else:
        form = TestPlanForm(request.form)
        project_id = form.projectname.data
        if project_id:
            form.modulename.choices = [(0, "全部模块")]
            form.versionname.choices = [(0, "全部版本")]
            for m in Module.query.filter_by(project_id=project_id, status = 1).all():
                form.modulename.choices.append((m.id, m.modulename))
            for v in Version.query.filter_by(project_id=project_id, status = 1).order_by(db.desc(Version.id)).all():
                form.versionname.choices.append((v.id, v.versionname))
        else:
            form.modulename.choices = [('', "请选择包含模块")]
            form.versionname.choices = [('', "请选择包含版本")]

        if form.modulename.data == None:
            form.modulename.data = None
        elif len(form.modulename.data) == 0:
            form.modulename.data = None
        module_id = form.modulename.data

        if form.versionname.data == None:
            form.versionname.data = None
        elif len(form.versionname.data) == 0:
            form.versionname.data = None
        version_id = form.versionname.data

        if form.modulename.data == None or form.versionname.data == None:
            form.api_id.choices.remove((0, "请选择包含接口"))
        elif len(form.modulename.data) == 0 and len(form.versionname.data) == 0:
            form.api_id.choices.remove((0, "请选择包含接口"))
        api_ids = getapis(project_id, module_id, version_id)
        for k, v in api_ids.items():
            form.api_id.choices.append((k, "接口ID(" + str(k) + ")---" + v))
        if form.api_id.data == None:
            form.api_id.data = None
        elif len(form.api_id.data) == 0:
            form.api_id.data = None
        api_id = form.api_id.data
        plan.appointmentTime = form.appointmentTime.data
        plan.note = form.note.data
        if form.validate_on_submit():
            plan.planname = form.planname.data
            plan.projectname = project_id
            if len(module_id) > 1:
                for index, item in enumerate(module_id):
                    if module_id[index] == 0:
                        form.errors['modulename'] = ['选择了全部，请勿选择单个模块']
                        return render_template('addtestplan.html', user=user, form=form)
                    module_id[index] = str(item)
                plan.modules = ",".join(module_id)
            else:
                plan.modules = module_id[0]

            if len(version_id) > 1:
                for index, item in enumerate(version_id):
                    if version_id[index] == 0:
                        form.errors['versionname'] = ['选择了全部，请勿选择单个版本']
                        return render_template('addtestplan.html', user=user, form=form)
                    version_id[index] = str(item)
                plan.versions = ",".join(version_id)
            else:
                plan.versions = version_id[0]

            if api_id == None:
                plan.apis = ""
            elif len(api_id) > 1:
                for index, item in enumerate(api_id):
                    api_id[index] = str(item)
                plan.apis = ",".join(api_id)
            else:
                plan.apis = api_id[0]
            plan.modifytime = datetime.now()
            plan.lastmodifier = user.id
            db.session.add(plan)
            db.session.commit()
            flash('测试计划修改成功', 'ok')
            return redirect(url_for('.edittestplan', id=id))
        else:
            return render_template('edittestplan.html', user=user, form=form)

@main.route('/testresultlist/', methods=['GET'], endpoint='testresultlist')
@login_required
def testresultlist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        testresultlist = TestResult.query.filter_by(realcase=1).all()
        return render_template('testresultlist.html', user=user, testresultlist=testresultlist, beforeresult=getresultapiname)

@main.route('/batchnumberresult/<batchnumber>', methods=['GET'], endpoint='batchnumberresult')
@login_required
def batchnumberresult(batchnumber):
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        testresultlist = TestResult.query.filter_by(batchnumber=batchnumber,realcase=1).all()
        return render_template('testresultlist.html', user=user, testresultlist=testresultlist, beforeresult=getresultapiname)

@main.route('/caseresult/<int:id>', methods=['GET'], endpoint='caseresult')
@login_required
def caseresult(id):
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        caseresult = TestResult.query.filter_by(id=id).first()
        return render_template('caseresult.html', user=user, caseresult=caseresult, beforeresult=getresultapiname)

@main.route('/testplanreportlist/', methods=['GET'], endpoint='testplanreportlist')
@login_required
def testplanreportlist():
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        testreportlist = TestReport.query.filter_by().all()
        return render_template('testplanreport.html', user=user, testreportlist=testreportlist, apis=getapisname, cases=getcasesname)

@main.route('/testplanreport/<batchnumber>', methods=['GET'], endpoint='testplanreport')
@login_required
def testplanreport(batchnumber):
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        testreportlist = TestReport.query.filter_by(batchnumber=batchnumber).all()
        return render_template('testplanreport.html', user=user, testreportlist=testreportlist, apis=getapisname, cases=getcasesname)

@main.route('/reportdetail/<batchnumber>', methods=['GET'], endpoint='reportdetail')
@login_required
def reportdetail(batchnumber):
    email = g.user
    user = User.query.filter_by(email=email).first()
    if request.method == 'GET':
        testreport = TestReport.query.filter_by(batchnumber=batchnumber).first()
        testresultlist = TestResult.query.filter_by(batchnumber=batchnumber,realcase=1).all()
        with open(os.path.join(os.getcwd(),'report',batchnumber+'.html'), 'tw', encoding='utf8') as f:
            f.write(render_template('reportdetail.html', user=user, testreport=testreport, apis=getapisname, cases=getcasesname,
                        testresultlist=testresultlist, beforeresult=getresultapiname))
        return render_template('reportdetail.html', user=user, testreport=testreport, apis=getapisname, cases=getcasesname, testresultlist=testresultlist, beforeresult=getresultapiname)