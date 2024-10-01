import os
from tinydb import TinyDB, Query
from datetime import datetime

from const import *

# TODO: use args here
name = 'brainfuck'

query = Query()
db = TinyDB(f'{loc}tinydb.json')

unmark = True

try:
    q = query._type == 'machine' and query.name == name
    # UNMARK AS DONE
    if unmark:
        machine = {'doneDate': ''}
        updateResult = db.update(machine, q)
        if len(updateResult) > 0:
            print(f'machine {name} successfully unmarked as done')
        else:
            print(f'machine {name} not found')
    # MARK AS DONE
    else:
        machineResult = db.search(q)
        if machineResult and len(machineResult) >= 1:
            machine = machineResult[0]
            if machine['doneDate'] == '':
                machine['doneDate'] = str(datetime.now())
                db.update(machine, q)
                print(f'machine {name} successfully marked as done')
            else:
                print(f'machine {name} already marked as done on {machine["doneDate"]}')
        else:
            print(f'machine {name} not found')
except Exception as err:
    print('ERROR', err)

