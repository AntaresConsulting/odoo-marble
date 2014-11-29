#!/usr/bin/env python
from __future__ import print_function
import erppeek
import sys, os

total = len(sys.argv)
cmdargs = str(sys.argv)
#print ("1- The total numbers of args passed to the script: %d " % total)
#print ("2- Args list: %s " % cmdargs)
# Pharsing args one by one
#print ("3- Script name: %s" % str(sys.argv[0]))
#print ("4- First argument: %s" % str(sys.argv[1]))
#print ("5- Second argument: %s" % str(sys.argv[2]))

if len(sys.argv) == 1:
    print("""
    oe-model.sh <filter>
    > filter: "[(arg-1,operator,arg-2),..]"
    > ex: ./oe-model.sh "[('module','ilike','%product%')]"
    """)
    sys.exit(0)

# ----------------------------------------
path = str(sys.argv[0]).split('/')
file = path[len(path)-1].strip()
path = '/'.join(path[:len(path)-1]).strip() 
current_path = os.getcwd()

os.chdir(path)
client = erppeek.Client.from_config('db-00')
os.chdir(path)

# ----------------------------------------
proxy = client.model('ir.model.data')
arg = eval(sys.argv[1])

SIZE_ID     = 8
SIZE_MODULE = 20
SIZE_NAME   = 70
SIZE_MODEL  = 30
SIZE_RES_ID = 6 
SIZE_NAME2  = 10

title = {'id':'id','module':'module','name':'name','model':'model','res_id':'res_id','name2':'(model:id >> name)'}
head = "{id:"+str(SIZE_ID)+"} {module:"+str(SIZE_MODULE)+"} {name:"+str(SIZE_NAME)+"} {model:"+str(SIZE_MODEL)+"} {res_id:"+str(SIZE_RES_ID)+"}    {name2}"
print(head.format(**title))
print('-' * SIZE_ID + ' ' + '-' * SIZE_MODULE + ' ' +'-' * SIZE_NAME + ' ' +'-' * SIZE_MODEL + ' ' +'-' * SIZE_RES_ID + '    ' +'-' * SIZE_NAME2)

content = "{d.id:"+str(SIZE_ID)+"} {d.module:"+str(SIZE_MODULE)+"} {d.name:"+str(SIZE_NAME)+"} {d.model:"+str(SIZE_MODEL)+"} {d.res_id:"+str(SIZE_RES_ID)+"} >> {d2}"
datas = proxy.browse(arg)
for d in datas:
    d2 = client.model(d.model).browse([('id','=',d.res_id)])
    d2 = d2[0].name if len(d2) else ''
    # print("{id:SIZE_ID}  {module:SIZE_MODULE} {name:SIZE_NAME} {model:SIZE_MODEL} {res_id:SIZE_RES_ID} >> {name2}".format(d=d,d2=d2))
    print(content.format(d=d,d2=d2))

