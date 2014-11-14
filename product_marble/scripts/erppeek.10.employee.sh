#!/usr/bin/env python
from __future__ import print_function
import erppeek

for src in ['origen', 'destino']:
    client = erppeek.Client.from_config(src)

    proxy = client.model('hr.employee')
    employees = proxy.browse([])

    print('> ' + src + ':')
    for empl in employees:
            print("\t {emp.id} {emp.name}".format(emp=empl))

