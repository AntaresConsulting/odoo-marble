#!/usr/bin/env python
from __future__ import print_function
import erppeek

DEFAULTS = dict(help='', string='Unknown')

client = erppeek.Client.from_config('db-00')
user_model = client.model('res.users')

#for fname, field in sorted(user_model.fields().items()):
#    values = dict(DEFAULTS, name=fname, **field)
#    print("{name:30} {type:10} {string}".format(**values))

i = 0
for fname, field in sorted(user_model.fields().items()):
    values = dict(DEFAULTS, name=fname, **field)
    print("{name:30} {type:10} {string}".format(**values))

    i += 1
    if i == 3:
        break
   
