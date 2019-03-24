# -*-coding:utf-8-*-

import os
import sys
import time
import shutil

# 清理临时文件
backupdir="/data/backup/file/%s"%(time.strftime("%Y-%m-%d",time.localtime()))
bday=604800
path='/data/images/img/temporary'

if os.path.exists(backupdir) is False:
  os.makedirs(backupdir)

cday=int(time.time())

for i in os.walk(path):
  # 判断目录是否为空,且创建时间大于 bday
  if i[1] == [] and i [2] == [] and (cday - int(os.stat(i[0]).st_mtime)) > bday:
      print "删除空目录:  %s"%(str(i[0]))
      os.rmdir(i[0])
  else:
      for j in  i[2]:
          # 判断大于 bday 的文件
          if (cday - int(os.stat(i[0]+'/'+j).st_mtime)) > bday:
              print "移动文件:  %s"%(str(i[0]+'/'+j))
              shutil.move(str(i[0]+'/'+j),backupdir+'/'+j)
