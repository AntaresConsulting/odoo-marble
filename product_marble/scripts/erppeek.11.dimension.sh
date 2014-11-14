#!/usr/bin/env python
from __future__ import print_function
import erppeek

def _exists_model(client, model_name):
    proxy = client.model('ir.model')
    ids = proxy.search([('model', '=', model_name)])
    # print('ids = %s' % ids)
    return (len(ids) > 0)

for src in ['origen', 'destino']:
    print('> ' + src + ':')

    client = erppeek.Client.from_config(src)
    model_name = 'product.marble.dimension'
    if not _exists_model(client, model_name):
        continue

    proxy = client.model(model_name)
    objs = proxy.browse([])
    for obj in objs:
        print("\t {o.id} {o.dimension}".format(o=obj))

