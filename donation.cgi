#!/usr/bin/python
import sys, string
sys.path.insert(0,'/home/temple24/python')
import tow

tow.check_authorized("donation")

td = tow.td

##### slurp up the form data into form ########################################
clause = ' where '
from_text = ''
to_text = ''
# gather any data from form
try:
    d_from = tow.form.getfirst('from')
    if d_from == '':
        d_from = None
    if d_from is not None:
        d_from = tow.store_date(d_from)
        from_text = clause + 'donation_date >= %(d_from)s'
        clause = ' and '
except:
    tow.not_allowed('invalid paramater: from ' + d_from)

try:
    d_to = tow.form.getfirst('to')
    if d_to == '':
        d_to = None
    if d_to is not None:
        d_to = tow.store_date(d_to)
        to_text = clause + "donation_date <= %(d_to)s"
        clause = ' and '
except:
    tow.not_allowed('invalid paramater: to ' + d_to)

total = {'Complete': 0, 'Pledged': 0, 'Cancelled': 0, 'Unknown': 0}
people = {}
s = {}
tow.cur.execute("select person_id, donation_date, donation_amount, donation_status, donation_type, donation_notes from tow_donation" + from_text + to_text + " order by donation_date", {'d_from': d_from, 'd_to': d_to})
for resp in tow.fetchrows():
    (person_id, date, amount, status, typ, notes) = resp
    entry = {'date': date, 'amount': amount, 'status': status, 'type': typ, 'notes': notes}
    if person_id not in people:
        people[person_id] = {'name': tow.person_id_to_name(person_id), 'Unknown': 0, 'Complete': 0, 'Pledged': 0, 'Cancelled': 0, 'donations': []}
        s[tow.person_sort_by_id[person_id]] = person_id
    people[person_id]['donations'].append(entry)
    people[person_id][status] += amount
    total[status] += amount

if len(s) == 0:
    tow.not_allowed('no donations to report')

num = 0
for i in s:
    num += len(people[s[i]]['donations'])

if num == 1:
    tmp = 'One Donation'
else:
    tmp = tow.s(num, ' Donations')

if len(s) == 1:
    tmp += ' by One Person'
else:
    tmp += tow.s(' by ', len(s), ' People')

if d_from is None and d_to is None:
    d_text = ''
elif d_from is None:
    d_text = 'To ' + tow.display_date(d_to)
elif d_to is None:
    d_text = 'From ' + tow.display_date(d_from)
elif d_from == d_to:
    d_text = 'On ' + tow.display_date(d_from)
else:
    d_text = 'From ' + tow.display_date(d_from) + ' to ' + tow.display_date(d_to)
tow.start_page("Donations Report", "Donations Report " + d_text)
print '      <h3>'+tmp+'</h3><br><table border="1"><tr><th>Person<th>Status<th>Type<th>Date<th>Amount<th>Notes<th>Subtotal'
for sequence in sorted(s.keys()):
    person = people[s[sequence]]
    if len(person['donations']) > 1:
# Add a subtotal row
        print '        <tr><td colspan="6">' + person['name'] + td + tow.display_cash(person['Complete'] + person['Unknown'])
        for donation in person['donations']:
            print '        <tr><td colspan="2" style="text-align: right">' + donation['status'] + td + donation['type'] + td + tow.display_date(donation['date']) + td + tow.display_cash(donation['amount']) + td + tow.display_text(donation['notes']) + td
    else:
        donation = person['donations'][0]
        amount = tow.display_cash(donation['amount'])
        print '        <tr><td>' + person['name'] + '<td style="text-align: right">' + donation['status'] + td + donation['type'] + td + tow.display_date(donation['date']) + td + amount + td + tow.display_text(donation['notes']) + td + amount

print '      </table><br>Total Unknown ' + tow.display_cash(total['Unknown']) + '<br>Total Cancelled ' + tow.display_cash(total['Cancelled']) + '<br>Total Pledged ' + tow.display_cash(total['Pledged']) + '<br>Total Complete '+ tow.display_cash(total['Complete'])
tow.end_page()
