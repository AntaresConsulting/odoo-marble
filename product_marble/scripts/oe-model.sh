#!/usr/bin/env python
from __future__ import print_function
import erppeek
import sys

#total = len(sys.argv)
#cmdargs = str(sys.argv)
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


arg = eval(sys.argv[1])

client = erppeek.Client.from_config('db-00')
proxy = client.model('ir.model.data')

datas = proxy.browse(arg)
for d in datas:
    d2 = client.model(d.model).browse([('id','=',d.res_id)])
    d2 = d2[0].name if len(d2) else ''
    print("{d.id:8}  {d.module:20} {d.name:70} {d.model:30} {d.res_id:5} >> {d2}".format(d=d,d2=d2))

