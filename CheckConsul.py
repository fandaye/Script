# -*-coding:utf-8-*-
import redis
import urllib2
import json
import smtplib
import time
from qcloudsms_py import SmsMultiSender
from qcloudsms_py.httpclient import HTTPError
from email.mime.text import MIMEText
from email.header import Header

# consul 配置
Url='http://10.100.4.36:8500/v1/health/state/any'
Token='e38f0c3e-69a2-4fca-baec-e4b0cf677dc5'

# 腾讯短信配置
appid = xxxxxxx
appkey = "xxxxxxx"
phone_numbers = ["xxxxxxx", "xxxxxxx"]
template_id = xxxxxxx

# redis配置
redis_host='127.0.0.1'
redis_port=6379
redis_db=1
redis_sms_key='96ca8302-7b68-11e8-bc4a-1e00b000003e'
redis_email_key='7203896e-7b69-11e8-abd0-1e00b000003e'

# 收件人列表
to_list=["xxxxxxx","xxxxxxx"]
# 邮件主题
title="%s  Consul异常通知"%(time.strftime('%Y-%m-%d', time.localtime(time.time())))

# 邮件配置
MailHost = 'xxx'
MailUser = 'xxx'
MailPasswd = 'xxx'

# 初始化短信
ssender = SmsMultiSender(appid, appkey)
# 初始化redis
redis_connect = redis.Redis(host=redis_host, port=redis_port,db=redis_db)
# 连接consul api
req = urllib2.Request(Url)
resp = urllib2.urlopen(req)

def send_mail(to_list,subject,content):
    me = MailUser
    msg = MIMEText(content,'html',_charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = me
    msg['to'] = to_list
    try:
        s = smtplib.SMTP_SSL(MailHost, 465)
        s.connect(MailHost)
        s.login(MailUser,MailPasswd)
        s.sendmail(me,to_list,msg.as_string())
        s.close()
        return True
    except Exception,e:
        print str(e)
        return False

data=[]
for server in json.loads(resp.read()):
    if server['Name'] != 'Serf Health Status'  and server['Status'] != 'passing':
        data.append({"Node":server['Node'],"Service":server['Name'].replace('Service \'','').replace('\' check',''),"Status":server['Status']})


html='''
<style type="text/css">
table.gridtable {
    font-family: verdana,arial,sans-serif;
    font-size:15px;
    color:#333333;
    border-width: 1px;
    border-color: #666666;
    border-collapse: collapse;
}
table.gridtable th {
    border-width: 1px;
    padding: 12px;
    border-style: solid;
    border-color: #666666;
    background-color: #dedede;
}
table.gridtable td {
    border-width: 1px;
    padding: 12px;
    border-style: solid;
    border-color: #666666;
    background-color: #ffffff;
}
</style>
<div>
<table class="gridtable">
<tr><th> host </th>  <th> service </th> <th> status </th>
<tr>

'''

for i in data:
    html = html + u"""
        <tr>
        <td>%s</td>  <td>%s</td>  <td>%s</td>
        </tr>
        """%(i['Node'],i['Service'],i['Status'])

html+='</table>  </div> '

if len(data) >=1:
    if redis_connect.get(redis_sms_key) is None:
        result = ssender.send_with_param(86, phone_numbers,template_id, [])
        redis_connect.set(redis_sms_key,"")
        redis_connect.expire(redis_sms_key,60*60*24)

    if redis_connect.get(redis_email_key) is None:
        redis_connect.set(redis_email_key,"")
        redis_connect.expire(redis_email_key,60*60)
        for i in to_list:
            print i
            send_mail(i,title,html)
