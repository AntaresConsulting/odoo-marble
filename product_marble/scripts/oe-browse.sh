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

# constants -------------------------------------------------

DEFAULTS_FIELDS = ['id', 'name']
# DISCARD_FILEDS = ['create_date','create_uid','write_date','write_uid', '__last_update']
DISCARD_FIELDS = ['__last_update']
MAX_SIZE = 20
MAX_ROW = 50
MORE_ROW = False
NO_DATA = False
NO_DATA_SIZE_COL = 25
NO_DATA_COUNT_COL = 4

# functions -------------------------------------------------

def _check_argum():
    fields = ''
    model  = ''
    filter = ''

    size_arg = len(sys.argv) - 1
    if size_arg == 2: # <fields> <model> -> info fields
        fields = str(sys.argv[1])
        model  = str(sys.argv[2])
       
    elif size_arg == 3: # <fields> <model> <filter> -> to process data
        fields = str(sys.argv[1])
        model  = str(sys.argv[2])
        filter = eval(sys.argv[3])

    else:
        print("""
        oe-browse.sh <fields> <model> <filter>

        > fields: '?' = give info columns, is not nesesary <filter>, or
                  'field-1, .., field-N' = column to load,
                  '' = by defount info columns 'id, name',
        > model: model name to load,
        > filter: "[(arg-1,operator,arg-2),..]"
        
        > ex-1: ./oe-browse.sh '?' 'hr.employee' 
        > ex-2: ./oe-browse.sh 'notes, color, compani_id' 'hr.employee' "[('id','=',1)]"
        """)
        sys.exit(0)

    fields =[f.strip() for f in fields.split(',')]

    # print('arg = %s - %s - %s' % (fields, model, str(filter)))
    return fields, model, filter

def _exists_model(client, model_name):
    proxy = client.model('ir.model')
    ids = proxy.search([('model', '=', model_name)])
    # print('ids = %s' % ids)
    return (len(ids) > 0)

def _load_fields(proxy, lfields):
    global NO_DATA

    fields = DEFAULTS_FIELDS
    fields = [fname for fname, field in sorted(proxy.fields().items())]

    if '?' in lfields:
        NO_DATA = True
        return fields

    elif lfields:
        fields = [name for name in fields if name in lfields]

    for name in fields:
        if name in DISCARD_FIELDS:
            fields.remove(name)

    # print('\n >> fields = ',fields)
    return fields 

def _load_datas(proxy, fields, filter):
    global MORE_ROW
    global NO_DATA

    if NO_DATA:
        return []
    
    data =[] 
    for d in proxy.browse(filter):
        MORE_ROW = (len(data) == MAX_ROW)
        if MORE_ROW:
            break
        line = {}
        for f in fields:
            val = eval('d.' + f)
            val = str(val) if not ('class' in str(type(val))) else str(val.id or val.ids or "")
            val = val[:MAX_SIZE]
            line.update({f:val})
            # print('\n >> line = ',line)

        data.append(line)
    # print('\n >> data = ',data)
    return data

def _size_fields(fields, data):
    col_size = {}
    for f in fields:
        size = 0
        lis = [f] + [d.get(f) for d in data]
        # print('>> ' + str(lis))

        for r in lis:
            # size = len(r) if (len(r) > size) and (len(r) < MAX_SIZE) else size
            size = len(r) if (len(r) > size) and (len(r) < MAX_SIZE) else size
            
        col_size.update({f:size})
    # print('\n >> col = ',col_size)
    return col_size


def _print_data(col_size, fields, data):
    # global MORE_ROW

    fields_sintax = ["{" + name[:col_size.get(name)] + ":" + str(col_size.get(name)) + "}" for name in fields]
    fields_sintax = " ".join(fields_sintax)
    
    # header = ["{" + name + ":" + col_size.get(name) + "}" for name in fields]
    header = [name + (" " * (col_size.get(name) - len(name))) for name in fields]
    separator = [('-' * col_size.get(name)) for name in fields]

    to_print = []
    to_print.append('\n- - - Start - - -')

    to_print.append(" ".join(header)) # header
    # to_print.append(header.format(**fields)) # header
    to_print.append(" ".join(separator)) # separator

    for d in data:
        # print(d)
        to_print.append(fields_sintax.format(**d)) # data

    if MORE_ROW:
        to_print.append('- - - End - More records for process - - -\n') # foot
    else:
        to_print.append('- - - End - - -\n')

    for p in to_print:
        print(p)
    
    return


def _print_fields(col_size, fields):
    to_print = []
    to_print.append('\n- - - Start - - -')
    
    fcount = len(fields)
    rcount = fcount // NO_DATA_COUNT_COL
    
    row = 0
    to_print = [' ' for i in range(rcount)]
    print(to_print)
    for f in fields:
        row = 0 if row > rcount else row 

        fname = f + ' ' * (NO_DATA_SIZE_COL - len(f)) 

        print('1- to_print = %s, row = %s' % (to_print, row))
        
        to_print[row] += fname 
        # if row == 0:
        #     to_print.append(fname)
        # else:
        #     to_print[row] = to_print[row] + ' ' + fname

        row += 1
        # print('2- %s' % to_print)

        # to_print[row] = (to_print[row] + ' ' + fname) if (row > 0) else fname
        # to_print[k] += ' ' + fname

    to_print.append('- - - End - - -\n')

    for p in to_print:
        print(p)
    
    return

# to process...
def _to_process(proxy, lfields, filter):
#    global NO_DATA

    fields = _load_fields(proxy, lfields)
    data = _load_datas(proxy, fields, filter) 
    col_size = _size_fields(fields, data) 

    if NO_DATA:
        _print_fields(col_size,fields)
    else:
        _print_data(col_size,fields, data)

    return 

# main -------------------------------------------------------

if __name__ != "__main__":
    sys.exit(1)

# check arguments
lfields, model, filter = _check_argum()

# check if exisist model
client = erppeek.Client.from_config('db-00')
if not _exists_model(client, model):
    print('\t >> Do not exist model \'' + model + '\'')
    sys.exit(1)

# to process...
proxy = client.model(model)
_to_process(proxy, lfields, filter)

#
sys.exit(0)



