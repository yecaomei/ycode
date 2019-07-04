# coding=utf8
from flask import request
from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField,SelectField,RadioField,TextAreaField,SelectMultipleField,DateTimeField,FileField
from wtforms.validators import Length, Email,InputRequired,DataRequired,EqualTo,ValidationError,Regexp,AnyOf,NumberRange
from wtforms.fields import core
from ..tools import getSection
from wtforms import widgets
from ..models import User,Role,Project,Module,Version,Api,Case

class LoginForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    email = StringField(
        # 标签
        label='邮箱',
        # 验证器
        validators=[
            # DataRequired('请输入邮箱'),
            InputRequired('邮箱不能为空'),
            # Email('邮箱格式错误')
        ],
        description = "邮箱",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱",
            "autocomplete":"off",
            "required": "required",  # 表示输入框不能为空
            "autofocus":"autofocus"
        }
    )
    password = PasswordField(
        label='密码',
        validators=[
            InputRequired('密码不能为空'),
            # Length(6, 16, '密码长度是6到16')
        ],
        render_kw = {
            "class": "form-control",
            "placeholder": "请输入密码",
    }
    )
    remember = BooleanField(
        label='7天有效',
        default=False
    )

class RegistrationForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    email = StringField(
        # 标签
        label='邮箱',
        # 验证器
        validators=[
            InputRequired('邮箱不能为空'),
            Email('邮箱格式错误')
        ],
        description = "邮箱",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱",
            "autocomplete":"off",
            "required": "required",  # 表示输入框不能为空
            "autofocus":"autofocus"
        }
    )
    username = StringField(
        # 标签
        label='用户名',
        # 验证器
        validators=[
            InputRequired('用户名不能为空'),
            Length(2, 10, '用户名长度是2到10')
        ],
        description="用户名",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入用户名",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    password = PasswordField(
        label='密码',
        validators=[
            InputRequired('密码不能为空'),
            Length(8, 20, '密码长度是8到20'),
            Regexp(regex="^(?![A-Za-z]+$)(?![A-Z\\d]+$)(?![A-Z\\W]+$)(?![a-z\\d]+$)(?![a-z\\W]+$)(?![\\d\\W]+$)\\S{8,20}$",
                              message='密码必须符合由数字,大写字母,小写字母,特殊符,至少其中三种组成的8至20位字符')
        ],
        description="密码",
        render_kw = {
            "class": "form-control",
            "placeholder": "请输入密码",
        }
    )
    repassword = PasswordField(
        label='密码',
        validators=[
            InputRequired('确认密码不能为空'),
            EqualTo('password', message="两次密码输入不一致")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入确认密码",
        }
    )

    def validate_email(self, filed):
        email = filed.data
        account = User.query.filter_by(email=email).count()
        if account > 0:
            raise ValidationError("此邮箱已经注册")

class UserForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    images = FileField(
        # 标签
        label='头像',
        description = "头像",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "default",
            "placeholder": "请上传头像",
        }
    )
    username = StringField(
        # 标签
        label='用户名',
        # 验证器
        validators=[
            InputRequired('请输入用户名'),
            Length(2, 10, '用户名长度是2到10')
        ],
        description="用户名",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入用户名",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    password = StringField(
        # 标签
        label='密码',
        description="密码",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    telephone = StringField(
        # 标签
        label='手机号',
        description="手机号",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机号",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    role_id = SelectField(
        # 标签
        label='所属角色',
        # 验证器
        validators=[
            InputRequired('请选择所属角色'),
            NumberRange(min=1, message="请选择所属角色")
        ],
        description="所属角色",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(0, "请选择所属角色")],
        coerce=int
    )
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for role in Role.query.all():
            self.role_id.choices.append((role.id, role.rolename))

class PasswordForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    password = PasswordField(
        label='密码',
        validators=[
            InputRequired('密码不能为空'),
            Length(8, 20, '密码长度是8到20'),
            Regexp(regex="^(?![A-Za-z]+$)(?![A-Z\\d]+$)(?![A-Z\\W]+$)(?![a-z\\d]+$)(?![a-z\\W]+$)(?![\\d\\W]+$)\\S{8,20}$",
                              message='密码必须符合由数字,大写字母,小写字母,特殊符,至少其中三种组成的8至20位字符')
        ],
        description="密码",
        render_kw = {
            "class": "form-control",
            "placeholder": "请输入密码",
        }
    )

class ResetpwdForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    useremail = StringField(
        # 标签
        label='邮箱',
        # 验证器
        validators=[
            InputRequired('邮箱不能为空'),
            Email('邮箱格式错误')
        ],
        description="邮箱",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
            "autofocus": "autofocus"
        }
    )

class RoleForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    rolename = StringField(
        # 标签
        label='角色名称',
        # 验证器
        validators=[
            InputRequired('请输入角色名称')
        ],
        description="角色名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入角色名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )

class ProjectForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    projectname = StringField(
        # 标签
        label='项目名称',
        # 验证器
        validators=[
            InputRequired('请输入项目名称')
        ],
        description="项目名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入项目名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    role_id = SelectMultipleField(
        # 标签
        label='所属角色',
        # 验证器
        validators=[
            InputRequired('请勾选所属角色')
        ],
        description="所属角色",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "col-lg-10",
            "style":"list-style:none;float:left;",
            "required": "required"
        },
        choices=[],
        coerce=int,
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
    )
    users = SelectMultipleField(
        # 标签
        label='项目人员',
        # 验证器
        validators=[
            InputRequired('请选择项目人员')
        ],
        description="项目人员",
        # 附加选项,会自动在前端判别
        render_kw={
            # "class": "form-control",
            "class": "multi-select",
            "multiple": "multiple",
            "required": "required"
        },
        choices=[],
        coerce=int
    )
    note = TextAreaField(
        # 标签
        label='项目描述',
        description="项目描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入项目描述",
            "autocomplete": "off",
            "rows": 6
        }
    )
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for role in Role.query.all():
            self.role_id.choices.append((role.id, role.rolename))
        for user in User.query.all():
            self.users.choices.append((user.id, user.username+"("+user.email+")"))

class ModuleForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    modulename = StringField(
        # 标签
        label='模块名称',
        # 验证器
        validators=[
            InputRequired('请输入模块名称')
        ],
        description="模块名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入模块名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    projectname = SelectField(
        # 标签
        label='项目名称',
        # 验证器
        validators=[
            InputRequired('请选择项目名称'),
            NumberRange(min=1, message="请选择项目名称")
        ],
        description="项目名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(0, "请选择项目名称")],
        coerce=int
    )
    note = TextAreaField(
        # 标签
        label='模块描述',
        description="模块描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入模块描述",
            "autocomplete": "off",
            "rows": 6
        }
    )

    def __init__(self, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)
        for project in Project.query.all():
            self.projectname.choices.append((project.id, project.projectname))

class VersionForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    versionname = StringField(
        # 标签
        label='接口版本名称',
        # 验证器
        validators=[
            InputRequired('请输入接口版本名称')
        ],
        description="接口版本名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入接口版本名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    projectname = SelectField(
        # 标签
        label='项目名称',
        # 验证器
        validators=[
            InputRequired('请选择项目名称'),
            NumberRange(min=1, message="请选择项目名称")
        ],
        description="项目名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(0, "请选择项目名称")],
        coerce=int
    )
    note = TextAreaField(
        # 标签
        label='接口版本描述',
        description="接口版本描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "接口版本描述",
            "autocomplete": "off",
            "rows": 6
        }
    )

    def __init__(self, *args, **kwargs):
        super(VersionForm, self).__init__(*args, **kwargs)
        for project in Project.query.all():
            self.projectname.choices.append((project.id, project.projectname))

class ApiForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    projectname = SelectField(
        # 标签
        label='所属项目',
        # 验证器
        validators=[
            InputRequired('请选择项目'),
            NumberRange(min=1,message="请选择项目")
        ],
        description = "所属项目",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange":"selectproject()",
            "required": "required"
        },
        choices=[(0, "请选择项目")],
        coerce=int
    )
    modulename = SelectField(
        # 标签
        label='所属模块',
        # 验证器
        validators=[
            InputRequired('请选择所属模块'),
            NumberRange(min=1, message="请选择所属模块")
        ],
        description="所属模块",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(0, "请选择所属模块")],
        coerce=int
    )
    versionname = SelectField(
        # 标签
        label='所属版本',
        # 验证器
        validators=[
            InputRequired('请选择所属版本'),
            NumberRange(min=1, message="请选择所属版本")
        ],
        description="所属版本",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(0, "请选择所属版本")],
        coerce=int
    )

    apiname = StringField(
        # 标签
        label='接口名称',
        # 验证器
        validators=[
            InputRequired('请输入接口名称')
        ],
        description="接口名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入接口名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )

    method = SelectField(
        # 标签
        label='请求方式',
        # 验证器
        validators=[
            InputRequired('请选择请求方式'),
        ],
        description="请求方式",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[("GET", "GET"),("POST","POST"),("PUT","PUT"),("DELETE","DELETE")]
    )

    domain = SelectField(
        # 标签
        label='接口域名',
        # 验证器
        validators=[
            InputRequired('请选择接口域名'),
        ],
        description="接口域名",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(k, v) for k,v in getSection("env.conf","company").items()]
    )

    url = StringField(
        # 标签
        label='接口地址',
        # 验证器
        validators=[
            InputRequired('请输入接口地址')
        ],
        description="接口地址",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入接口地址",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )

    protocol = SelectField(
        # 标签
        label='接口协议',
        # 验证器
        validators=[
            InputRequired('请选择接口协议'),
        ],
        description="接口协议",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[("HTTP", "HTTP"), ("HTTPS", "HTTPS")]
    )

    transmethod = RadioField(
        # 标签
        label='传参方式',
        # 验证器
        validators=[
            InputRequired('请选择传参方式')
        ],
        description="传参方式",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[("form-data", "form-data"), ("x-www-form-urlencoded", "x-www-form-urlencoded"), ("raw", "raw")],
        # choices=[("form-data", "form-data"), ("x-www-form-urlencoded", "x-www-form-urlencoded"), ("raw", "raw"), ("binary", "binary")],
        default="x-www-form-urlencoded"
    )

    jsondata = TextAreaField(
        # 标签
        label='body传参',
        # 验证器
        validators=[
            InputRequired('请输入body传参')
        ],
        description="body传参",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入接口地址",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
            "rows": 6
        }
    )

    note = TextAreaField(
        # 标签
        label='接口描述',
        description="接口描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入接口描述",
            "autocomplete": "off",
            "rows": 6
        }

    )

    def __init__(self, *args, **kwargs):
        super(ApiForm, self).__init__(*args, **kwargs)
        self.projectname.choices = [(0,"请选择项目")]
        for project in Project.query.filter_by(status = 1).all():
            self.projectname.choices.append((project.id, project.projectname))

class CaseForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    projectname = SelectField(
        # 标签
        label='所属项目',
        # 验证器
        validators=[
            InputRequired('请选择项目'),
            NumberRange(min=1,message="请选择项目")
        ],
        description = "所属项目",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange":"selectproject()",
            "required": "required"
        },
        choices=[(0, "请选择项目")],
        coerce=int
    )
    modulename = SelectField(
        # 标签
        label='所属模块',
        # 验证器
        validators=[
            InputRequired('请选择所属模块'),
            NumberRange(min=1, message="请选择所属模块")
        ],
        description="所属模块",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange": "changemodule()",
            "required": "required"
        },
        choices=[(0, "请选择所属模块")],
        coerce=int
    )
    versionname = SelectField(
        # 标签
        label='所属版本',
        # 验证器
        validators=[
            InputRequired('请选择所属版本'),
            NumberRange(min=1, message="请选择所属版本")
        ],
        description="所属版本",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange": "changeversion()",
            "required": "required"
        },
        choices=[(0, "请选择所属版本")],
        coerce=int
    )

    api_id = SelectField(
        # 标签
        label='所属接口',
        # 验证器
        validators=[
            InputRequired('请选择所属接口'),
            NumberRange(min=1, message="请选择所属接口")
        ],
        description="所属接口",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange": "selectapi()",
            "required": "required"
        },
        choices=[(0, "请选择所属接口")],
        coerce=int
    )

    casename = StringField(
        # 标签
        label='用例名称',
        # 验证器
        validators=[
            InputRequired('请输入用例名称')
        ],
        description="用例名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入用例名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    beforecase = TextAreaField(
        # 标签
        label='前置用例及其获取的参数',
        description="前置用例及其获取的参数",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入前置用例及其获取的参数",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
            "rows": 6
        }
    )

    jsondata = TextAreaField(
        # 标签
        label='body传参',
        # 验证器
        validators=[
            InputRequired('请输入body传参')
        ],
        description="body传参",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入接口地址",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
            "rows": 6
        }
    )
    comparemethod = SelectField(
        # 标签
        label='结果对比方式',
        # 验证器
        validators=[
            InputRequired('请选择结果对比方式'),
        ],
        description="结果对比方式",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(k, v) for k, v in getSection("env.conf", "comparemethod").items()]
    )
    expectedResults = TextAreaField(
        # 标签
        label='期望结果',
        # 验证器
        validators=[
            InputRequired('请输入期望结果')
        ],
        description="期望结果",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入期望结果",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
            "rows": 6
        }
    )

    note = TextAreaField(
        # 标签
        label='用例描述',
        description="用例描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入用例描述",
            "autocomplete": "off",
            "rows": 6
        }

    )

    def __init__(self, *args, **kwargs):
        super(CaseForm, self).__init__(*args, **kwargs)
        self.projectname.choices = [(0,"请选择项目")]
        for project in Project.query.filter_by(status = 1).all():
            self.projectname.choices.append((project.id, project.projectname))

class TestPlanForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    planname = StringField(
        # 标签
        label='测试计划名称',
        # 验证器
        validators=[
            InputRequired('请输入测试计划名称')
        ],
        description="测试计划名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试计划名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    projectname = SelectField(
        # 标签
        label='所属项目',
        # 验证器
        validators=[
            InputRequired('请选择所属项目'),
            NumberRange(min=1,message="请选择所属项目")
        ],
        description = "所属项目",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange":"selectproject()",
            "required": "required"
        },
        choices=[(0, "请选择所属项目")],
        coerce=int
    )
    modulename = SelectMultipleField(
        # 标签
        label='包含模块',
        validators=[
            InputRequired('请选择包含模块'),
        ],
        description="包含模块",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "multiple":"multiple",
            "onchange": "selectmodule()",
            "required": "required"
        },
        choices=[('', "请选择包含模块")],
        coerce=int
    )
    versionname = SelectMultipleField(
        # 标签
        label='包含版本',
        validators=[
            InputRequired('请选择包含版本'),
        ],
        description="包含版本",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "multiple": "multiple",
            "onchange": "selectversion()",
            "required": "required"
        },
        choices=[('', "请选择包含版本")],
        coerce=int
    )

    api_id = SelectMultipleField(
        # 标签
        label='包含接口',
        description="包含接口",
        # 附加选项,会自动在前端判别
        render_kw={
            # "class": "form-control",
            "class": "multi-select",
            "multiple":"multiple",
            "required": "required"
        },
        choices=[(0, "请选择包含接口")],
        coerce=int
    )

    appointmentTime = StringField(
        # 标签
        label='预定执行时间',
        # 验证器
        validators=[
            InputRequired('请选择预定执行时间'),
            Regexp(regex='^[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s+(20|21|22|23|[0-1]\d):[0-5]\d$',message='请输入正确格式的日期时间')
        ],
        description="预定执行时间",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form_datetime form-control",
            "autocomplete": "off",
            "required": "required"
        }
    )

    note = TextAreaField(
        # 标签
        label='测试计划描述',
        description="测试计划描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试计划描述",
            "autocomplete": "off",
            "rows": 6
        }

    )

    def __init__(self, *args, **kwargs):
        super(TestPlanForm, self).__init__(*args, **kwargs)
        self.projectname.choices = [(0,"请选择所属项目")]
        for project in Project.query.filter_by(status = 1).all():
            self.projectname.choices.append((project.id, project.projectname))
