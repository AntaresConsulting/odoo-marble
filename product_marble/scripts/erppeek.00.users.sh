#!/usr/bin/env python
from __future__ import print_function
import erppeek

#SERVER = 'http://localhost:8069'
#DATABASE = 'v80-05'
#USERNAME = 'admin'
#PASSWORD = 'admin'
#
#client = erppeek.Client(SERVER, DATABASE, USERNAME, PASSWORD)
client = erppeek.Client.from_config('destino')

proxy = client.model('res.users')
# No need to use the model.search method, the model.browse method accepts a
# domain
users = proxy.browse([])

for user in users:
        print("{user.id} {user.name}".format(user=user))

