#!/usr/bin/env python
from __future__ import print_function
import erppeek

#------------------------------------------------------------------------------
def _exists_model(client, model_name):
    proxy = client.model('ir.model')
    ids = proxy.search([('model', '=', model_name)])
    return (len(ids) > 0)

def _create_mapping(client):

    proxy = client.model('ir.model')
    values = {
        'model' : 'migra_map',
        'name'  : 'Migration Mapping',
        'state' : 'manual',
    }
    model = proxy.create(values)

    proxy = client.model('ir.model.fields')
    values = {
        'name': 'origin',
        'ttype': 'char',
        'size': 64,
        'field_description': 'Source Data Base',
        'model_id': model.id,
        'model': model.model,
        'domain': '[]',
    }
    model = proxy.create(values)


#------------------------------------------------------------------------------
client_ori = erppeek.Client.from_config('origen')
client_des = erppeek.Client.from_config('destino')

proxy_ori = client_ori.model('product.uom.categ')
proxy_des = client_des.model('product.uom.categ')

descarte = ['id','create_date','create_uid','write_date','write_uid']

print('Origen:')

objs = proxy_ori.browse([8])
for obj in objs:
    print("\t {o.id} {o.name}".format(o=obj))

    #[data[e] for e inj data.keys()]
    #print(obj)

    val = {}
    for key in proxy_ori.keys():
        if key not in descarte:
            v = {key : eval('obj.' + key)}
            val.update(v)

    print(val)
    proxy_des.create(val)

print('Destino:')

objs = proxy_des.browse([])
for obj in objs:
    print("\t {o.id} {o.name}".format(o=obj))


