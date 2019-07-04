# coding=utf8
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField,SubmitField,SelectField,RadioField,TextAreaField,SelectMultipleField,DateTimeField,FileField,IntegerField
from wtforms.validators import Length, Email,InputRequired,DataRequired,EqualTo,ValidationError,Regexp,AnyOf,NumberRange
from ..tools import getSection
from ..models import TestCaseProject,TestCaseModule,TestCaseSubModule,TestCase

class TestCaseProjectForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    projectname = StringField(
        # 标签
        label='测试项目名称',
        # 验证器
        validators=[
            InputRequired('请输入测试项目名称')
        ],
        description="测试项目名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试项目名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )

    note = TextAreaField(
        # 标签
        label='测试项目描述',
        description="测试项目描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试项目描述",
            "autocomplete": "off",
            "rows": 6
        }
    )


class TestCaseModuleForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    modulename = StringField(
        # 标签
        label='测试用例模块名称',
        # 验证器
        validators=[
            InputRequired('请输入测试用例模块名称')
        ],
        description="测试用例模块名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试用例模块名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )
    projectname = SelectField(
        # 标签
        label='测试项目名称',
        # 验证器
        validators=[
            InputRequired('请选择测试项目名称'),
            NumberRange(min=1, message="请选择测试项目名称")
        ],
        description="测试项目名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(0, "请选择测试项目名称")],
        coerce=int
    )
    note = TextAreaField(
        # 标签
        label='测试用例模块描述',
        description="测试用例模块描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试用例模块描述",
            "autocomplete": "off",
            "rows": 6
        }
    )

    def __init__(self, *args, **kwargs):
        super(TestCaseModuleForm, self).__init__(*args, **kwargs)
        # self.projectname.choices = [(0, "请选择测试项目名称")]
        for project in TestCaseProject.query.filter_by(status=1).all():
            self.projectname.choices.append((project.id, project.projectname))

class TestCaseSubModuleForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    projectname = SelectField(
        # 标签
        label='测试项目名称',
        # 验证器
        validators=[
            InputRequired('请选择测试项目名称'),
            NumberRange(min=1, message="请选择测试项目名称")
        ],
        description="测试项目名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange": "selectproject()",
            "required": "required"
        },
        # choices=[(0, "请选择测试项目名称")],
        coerce=int
    )
    modulename = SelectField(
        # 标签
        label='测试用例模块',
        # 验证器
        validators=[
            InputRequired('请选择测试用例模块'),
            NumberRange(min=1, message="请选择测试用例模块")
        ],
        description="测试用例模块",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(0, "请选择测试用例模块")],
        coerce=int
    )

    submodulename = StringField(
        # 标签
        label='测试用例子模块名称',
        # 验证器
        validators=[
            InputRequired('请输入测试用例子模块名称')
        ],
        description="测试用例子模块名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试用例子模块名称",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )

    note = TextAreaField(
        # 标签
        label='测试用例子模块名称描述',
        description="测试用例子模块名称描述",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试用例子模块名称描述",
            "autocomplete": "off",
            "rows": 6
        }

    )

    def __init__(self, *args, **kwargs):
        super(TestCaseSubModuleForm, self).__init__(*args, **kwargs)
        self.projectname.choices = [(0, "请选择项目")]
        for project in TestCaseProject.query.filter_by(status=1).all():
            self.projectname.choices.append((project.id, project.projectname))


class TestCaseForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    projectname = SelectField(
        # 标签
        label='测试项目名称',
        # 验证器
        validators=[
            InputRequired('请选择测试项目名称'),
            NumberRange(min=1, message="请选择测试项目名称")
        ],
        description="测试项目名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange": "selectproject()",
            "required": "required"
        },
        # choices=[(0, "请选择测试项目名称")],
        coerce=int
    )
    modulename = SelectField(
        # 标签
        label='测试用例模块',
        # 验证器
        validators=[
            InputRequired('请选择测试用例模块'),
            NumberRange(min=1, message="请选择测试用例模块")
        ],
        description="测试用例模块",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange": "selectmodule()",
            "required": "required"
        },
        choices=[(0, "请选择测试用例模块")],
        coerce=int
    )

    submodulename = SelectField(
        # 标签
        label='测试用例子模块',
        # 验证器
        validators=[
            InputRequired('请选择测试用例子模块'),
            NumberRange(min=1, message="请选择测试用例子模块")
        ],
        description="测试用例子模块",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[(0, "请选择测试用例子模块")],
        coerce=int
    )

    caseNo = StringField(
        # 标签
        label='测试用例序号',
        # 验证器
        validators=[
            InputRequired('请输入测试用例序号'),
            Regexp(regex="^[1-9]\d*$", message='请输入正确的测试用例序号啊')
        ],
        description="测试用例序号",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试用例序号",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )

    testcasename = StringField(
        # 标签
        label='测试用例标题',
        # 验证器
        validators=[
            InputRequired('请输入测试用例标题')
        ],
        description="测试用例子标题",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入测试用例子标题",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
        }
    )

    precondition = TextAreaField(
        # 标签
        label='前置条件',
        description="前置条件",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入用例名称",
            "autocomplete": "off",
            "rows": 3
        }
    )

    steps = TextAreaField(
        # 标签
        label='操作步骤',
        # 验证器
        validators=[
            InputRequired('请输入操作步骤')
        ],
        description="操作步骤",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入用例描述",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
            "rows": 4
        }
    )

    logicalresult = TextAreaField(
        # 标签
        label='页面逻辑结果',
        # 验证器
        validators=[
            InputRequired('请输入页面逻辑结果')
        ],
        description="页面逻辑结果",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入页面逻辑结果",
            "autocomplete": "off",
            "required": "required",  # 表示输入框不能为空
            "rows": 4
        }
    )

    databaseresult = TextAreaField(
        # 标签
        label='数据库结果',
        description="数据库结果",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入数据库结果",
            "autocomplete": "off",
            "rows": 3
        }
    )

    priority = SelectField(
        # 标签
        label='用例级别',
        # 验证器
        validators=[
            InputRequired('请选择用例级别'),
        ],
        description="用例级别",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "required": "required"
        },
        choices=[("P1", "P1"), ("P2", "P2"), ("P3", "P3"), ("P4", "P4")]
    )

    version = StringField(
        # 标签
        label='所属版本',
        description="所属版本",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "placeholder": "请输入所属版本",
            "autocomplete": "off",
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
        super(TestCaseForm, self).__init__(*args, **kwargs)
        self.projectname.choices = [(0,"请选择测试项目")]
        for project in TestCaseProject.query.filter_by(status = 1).all():
            self.projectname.choices.append((project.id, project.projectname))

class UploadExcelForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    excelfile = FileField(
        # 标签
        label='上传测试用例excel文档',
        description = "上传测试用例excel文档",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "default",
            "placeholder": "请上传测试用例excel文档",
        }
    )

class DownloadExcelForm(FlaskForm):  # 注意如果单独使用功能时要继承Form，如果在Flask框架中使用是要继承FlaskForm
    projectname = SelectField(
        # 标签
        label='测试项目名称',
        # 验证器
        validators=[
            InputRequired('请选择测试项目名称'),
            NumberRange(min=1, message="请选择测试项目名称")
        ],
        description="测试项目名称",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "onchange": "selectproject()",
            "required": "required"
        },
        coerce=int
    )
    modulename = SelectMultipleField(
        # 标签
        label='测试用例模块',
        description="测试用例模块",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "form-control",
            "multiple": "multiple",
            "onchange": "selectmodule()",
            "required": "required"
        },
        choices=[('', "请选择测试用例模块")],
        coerce=int
    )

    submodulename = SelectMultipleField(
        # 标签
        label='测试用例子模块',
        description="测试用例子模块",
        # 附加选项,会自动在前端判别
        render_kw={
            "class": "multi-select",
            "multiple":"multiple",
            "required": "required"
        },
        choices=[(0, "请选择测试用例子模块")],
        coerce=int
    )

    def __init__(self, *args, **kwargs):
        super(DownloadExcelForm, self).__init__(*args, **kwargs)
        self.projectname.choices = [(0,"请选择测试项目")]
        for project in TestCaseProject.query.filter_by(status = 1).all():
            self.projectname.choices.append((project.id, project.projectname))