#!/usr/bin/python
import sys, string, traceback
sys.path.insert(0,'/home/temple24/python')
import tow

##### slurp up the form data into form ########################################
# gather any data from form
event_id = tow.form.getfirst('id')
if event_id is None or event_id == '':
    tow.not_allowed('invalid paramater')
filename = tow.form.getfirst('filename')
if filename is None or filename == '':
    filename = tow.event_id_to_name(event_id)

people = {}
for i in tow.person_event_type_list:
    people[i] = {}
try:
    tow.cur.execute('select person_id, type, status, payment_status, enrolled from tow_person_event where event_id = %(event_id)s', {'event_id': event_id})
    for resp in tow.fetchrows():
        person_id = resp[0]
        person_name = tow.person_id_to_name(person_id)
        if '"' in person_name:
            person_name = '"'+person_name.replace('"', '""')+'"'
        elif ',' in person_name:
            person_name = '"'+person_name+'"'
        type = resp[1]
        people[type][tow.person_sort_by_id[person_id]] = string.join((person_name, type, resp[2] ,resp[3] ,tow.display_date(resp[4])), ',') + '\r'

except:
    tow.not_allowed('Error occurred: '+traceback.format_exc().replace('\n','  '))

print 'Content-type: text/csv\nContent-disposition: attachment; filename='+filename+'.csv\n'
for i in tow.person_event_type_list:
    for j in sorted(people[i].keys()):
        print people[i][j]
tow.fini()
