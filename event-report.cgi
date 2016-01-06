#!/usr/bin/python
import sys, string, urllib
sys.path.insert(0,'/home/temple24/python')
import tow

td = tow.td
##### slurp up the form data into form ########################################
# gather any data from form
name = tow.form.getfirst('name')
d_from = tow.form.getfirst('from')
d_to = tow.form.getfirst('to')
if d_from and d_to and d_to < d_from:
    tow.not_allowed('invalid paramater')

clause = ''
conj = ' where '
if name:
    clause += conj + 'name like %(name)s'
    conj = ' and '
if d_to:
    clause += conj + 'starts_on <= cast(%(d_to)s as date)'
    conj = ' and '
if d_from:
    clause += conj + 'ends_on >= cast(%(d_from)s as date)'
    conj = ' and '

tow.cur.execute('select event_id, name, type, starts_on, ends_on, base_cost, ceus from tow_event ' + clause + ' order by starts_on', {'name': name, 'd_from': tow.store_date(d_from), 'd_to': tow.store_date(d_to)})
events = []
for resp in tow.cur.fetchall():
    ceus = resp[6]
    if ceus is None:
        ceus = ''
    events.append({'event_id': resp[0], 'name': resp[1], 'type': resp[2], 'starts_on': tow.display_date(resp[3]), 'ends_on': tow.display_date(resp[4]), 'base_cost': tow.display_cash(resp[5]), 'ceus': tow.s(ceus)})
tow.start_page("Event Report", "Event Report")
if not name and not d_from and not d_to:
    label = 'All events'
else:
    label = 'Events'
    if name:
        label += ' matching ' + tow.display_text(name)
    if d_from:
        if not d_to:
            label += ' from ' + d_from
        elif d_to == d_from:
            label += ' on ' + d_from
        else:
            label += ' from ' + d_from + ' to ' + d_to
    elif d_to:
        label += ' up to ' + d_to

print '      <h3>' + label + '</h3><br>'
if len(events) == 0:
    print '      <h4>No events found</h4>'
else:
    print '      <table style="margin:0px auto" border="1"><thead><tr><th>Event<th>Type<th>Start<th>End<th>Cost<th>CEUs<th>Headcount<th>Teacher</thead><tbody>'
    for event in events:
        t = {}
        tow.cur.execute('select person_id from tow_person_event where event_id = %(event_id)s and type="Teacher"', {'event_id': event['event_id']})
        for resp in tow.cur.fetchall():
            person_id = resp[0]
            name = tow.display_text(tow.person_id_to_name(person_id))
            if 'person' in tow.permissions:
                name = tow.a('person', text = name, opts = {'Do': 'Show', 'id': tow.s(person_id)})
            t[tow.person_sort_by_id[person_id]] = name
        if len(t) == 0:
            teacher = ''
        elif len(t) == 1:
            teacher = t[t.keys()[0]]
        else:
            l = sorted(t.keys())
            last = t[l.pop()]
            n = []
            for i in l:
                n.append(t[i])
            teacher = string.join(n, ', ')+' and '+last

        tow.cur.execute('select count(person_id) from tow_person_event where event_id = %(event_id)s', {'event_id': event['event_id']})
        resp = tow.cur.fetchall()
        if event['starts_on'] == event['ends_on']:
            dates = '<td colspan="2" style="text-align: center">' + event['starts_on']
        else:
            dates = td + event['starts_on'] + td + event['ends_on']
        a = '      <tr><td>' + tow.a('event', text = tow.display_text(event['name']), opts = {'Do': 'Show', 'id': tow.s(event['event_id'])})
        a += td + event['type']
        a += dates
        a += td + event['base_cost']
        a += td + event['ceus']
        a += td + tow.s(resp[0][0])
        a += td + teacher
        print a
    print '</tbody></table>'
tow.end_page()
