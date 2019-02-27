# -*- coding: utf-8 -*-
__author__ = 'fan'
import MySQLdb
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#源数据库配置
SourceUserDB='xxx'
SourcePasswdDB='xxx'
SourceHostDB='xxx'

#目标数据库配置
TargetUserDB='xxx'
TargetPasswdDB='xxx'
TargetHostDB='xxx'

# 邮件配置
MailHost = 'xxx'
MailUser = 'xxx'
MailPasswd = 'xxx'
Subject="xxx环境数据同步报告"
Addressees =  ['xxx','xxx']

# 同步表配置
Tables={
    "Database1":["Table1","Table2","Table3","Table4"],
    "Database2":["Table1","Table2","Table3","Table4"],
}
def SendMail(to_list,subject,content):
    me = MailUser
    msg = MIMEText(content,_charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = me
    msg['to'] = to_list
    try:
        s = smtplib.SMTP()
        s.connect(MailHost)

        s.login(MailUser,MailPasswd)
        s.sendmail(me,to_list,msg.as_string( ))
        s.close()
        return True
    except Exception,e:
        print str(e)
        return False
class Sdb():
    def _connect(self,dbname):
        try:
            self.conn =  MySQLdb.connect(host = SourceHostDB,user = SourceUserDB,passwd = SourcePasswdDB,db = dbname,connect_timeout = 2,charset="utf8")
            self.cursor = self.conn.cursor()
            return True
        except MySQLdb.OperationalError:
            self.conn = No
            self.cursor = None
            return False
    def _dconnect(self,dbname):
        try:
            self.dconn =  MySQLdb.connect (host = TargetHostDB,user = TargetUserDB,passwd = TargetPasswdDB,db = dbname,connect_timeout = 2,charset="utf8")
            self.dcursor = self.dconn.cursor()
            return True
        except MySQLdb.OperationalError:
            self.dconn = None
            self.dcursor = None
            return False
    def _get(self,dbname,tablename):
        if not self._connect(dbname):
            return False,str("sdb connection failed ")
        else:
            if not self._dconnect(dbname):
                return False,str("ddb connection failed")
            try:
                self.dcursor.execute("TRUNCATE TABLE  %s"%(tablename))
                agr = self.query(tablename,dbname)
                if len(agr) != 0:
                    for sql in agr:
                        self.dcursor.execute(sql)
                        self.dconn.commit()
                return True,str(len(agr))
            except Exception,error:
                return False,str(error)
    def query(self,tablename,dbname):
        sql = "SELECT * FROM %s"%(tablename)
        self.cursor.execute(sql)
        index = self.cursor.description
        Index = ''
        result = []
        for i in range(len(index)):
            Index+=(tablename+'.'+index[i][0])
            if i < len(index)-1:
                Index+=","
        for res in self.cursor.fetchall():
            Value = ''
            for i in range(len(index)):
                Value += "'"+str(res[i])+"'"
                if i < len(res)-1:
                    Value += ','
            Insert = "INSERT INTO %s.%s (%s) VALUES (%s);"%(dbname,tablename,Index,Value.replace('\\','\\\\'))
            result.append(Insert)
        return result
s = Sdb()
info=''
for  db in Tables:
    for table in Tables[db]:
        stauts , value = s._get(db,table)
        if not stauts:
            info += db+'.'+table+":同步失败:%s\n"%(str(value))
        else:
            info += db+'.'+table+":同步成功,处理数据%s条\n"%(str(value))
for Email in Addressees:
    SendMail(Email,Subject,info)
