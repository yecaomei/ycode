# coding=utf8
from functools import wraps
from flask import g, redirect, url_for
import os
from configparser import ConfigParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import zipfile

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('.login'))

    return wrapper

# def wapper(func):
#     def inner(*args,**kwargs):
#         if not session.get('user'):
#             return redirect(url_for('.login'))
#         return func(*args,**kwargs)
#     return inner

def getSection(file, section):
    # cur_path = os.path.abspath(os.curdir)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    configPath = os.path.join(cur_path,file)
    # print(configPath)
    conf = ConfigParser()
    conf.read(configPath, encoding='utf-8')
    sec_dict = {}
    for k,v in conf.items(section):
        if v != '':
            sec_dict[k] = v
    return  sec_dict

def zipfiles(batchnumber):
    z = zipfile.ZipFile(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), 'report', batchnumber + '.zip'), 'w', zipfile.ZIP_STORED)  # 打包，zipfile.ZIP_STORED是默认参数
    # z = zipfile.ZipFile('ss.zip', 'w', zipfile.ZIP_DEFLATED) #压缩
    file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), 'report', batchnumber + '.html')
    document = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), 'report', 'files')
    z.write(file, batchnumber + '.html')
    pre_len = len(os.path.dirname(document))
    for parent, dirnames, filenames in os.walk(document):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
            z.write(pathfile, arcname)
    z.close()

def send_mail(sender, psw, receiver, smtpserver, report_file, port):
    mail_body = """
                <html>
                  <head></head>
                  <body>
                        Hi，All<br>
                            &nbsp; &nbsp; &nbsp; &nbsp; 附件中是接口测试报告，请查收。
                    </p>
                  </body>
                </html>
                """
    # 定义邮件内容
    msg = MIMEMultipart()
    body = MIMEText(mail_body, _subtype='html', _charset='utf-8')
    msg['Subject'] = '接口测试报告'
    msg['From'] = sender
    msg['To'] = receiver
    msg.attach(body)
    # 添加附件
    att = MIMEText(open(report_file, "rb").read(),"base64","utf-8")
    att["Content-Type"] = "application/octet-stream"
    # att["Conten-Disposition"] = 'attachment;filename="report"'

    basename = os.path.basename(report_file)
    att.add_header('Content-Disposition','attachment',filename = basename)
    msg.attach(att)
    try:
        smtp = smtplib.SMTP_SSL(smtpserver,port)
    except:
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver, port)
    # 用户名密码
    smtp.starttls()
    smtp.login(sender, psw)
    smtp.sendmail(sender, receiver.split(";"),msg.as_string())
    smtp.quit()
    print("测试报告已发送")


if __name__ == "__main__":
    emailData = getSection("email.conf","email")
    # print(d)
    # print([(k, v) for k,v in d.items()])
    batchnumber = '20181010191314'
    zipfiles(batchnumber)
    sender = emailData['sender']
    psw = emailData['psw']
    smtp_server = emailData['smtp_server']
    port = emailData['port']
    receiver = "yulili@chehang168.com"
    report_file = os.path.join(os.path.abspath(os.path.join(os.getcwd(), "..")), 'report', batchnumber + '.zip')
    send_mail(sender, psw, receiver, smtp_server, report_file, port)  # 发送报告
