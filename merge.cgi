#!/usr/bin/python
import os, sys, string, cgi, urllib, traceback
sys.path.insert(0,'/home/temple24/python')
import mysql.connector, tow

tow.check_authorized("person")
tow.check_authorized("donation")

tr = '<tr>'
td = tow.td
div = '    <div style="background: beige; border-style: solid; border-width: 1">'
xdiv = '</div><br>\n'

all_fields = (
 ('fn', 'first_name',       'First Name', ),
 ('ln', 'last_name',        'Last Name', ),
 ('cn', 'craft_name',       'Craft Name', ),
 ('s1', 'street_address_1', 'Street Address 1', ),
 ('s2', 'street_address_2', 'Street Address 2', ),
 ('tv', 'town_village_city','City', ),
 ('ps', 'province_state',   'State', ),
 ('zp', 'postal_code',      'Zip', ),
 ('ct', 'country',          'Country', ),
 ('db', 'date_of_birth',    'Date of Birth', ),
 ('gd', 'gender',           'Gender', ),
 ('ms', 'membership_status','Status', ),
 ('sn', 'member_since',     'Member Since', ),
 ('vs', 'volunteer_status', 'Volunteer Status', ),
 ('io', 'is_ordained',      'Is Ordained', ),
 ('od', 'ordination_date',  'Ordination Date', ),
 ('or', 'ordination_renewal_date', 'Ordination Renewal Date', ),
 ('mn', 'ministries',       'Ministries of Interest', ),
 ('no', 'notes',            'Notes', ),
)

def failed():
    o = report_opts
    if o is None:
        o = {}
    o['left'] = l_id
    o['right'] = r_id

    tow.print_results('Merge Failed', 'merge', 'The merge failed.', opts = o, timeout = 10, to_do = 'try again')


def get_person(id):
    p = {}

    i = { 'person_id': id }

    tow.cur.execute("""select first_name, last_name, craft_name, membership_status,
 member_since, ministries, street_address_1, street_address_2, town_village_city,
 province_state, postal_code, country, date_of_birth, gender,
 is_ordained, ordination_date, ordination_renewal_date, person_notes,
 volunteer_status from tow_person where person_id = %(person_id)s""", i)
    resp = tow.cur.fetchall()
    if len(resp) != 1:
        tow.add_error("person id ", id, " not found")
        failed()
    resp = resp[0]
    p = {
 'person_id': id,
 'first_name': tow.display_text(resp[0]),
 'last_name': tow.display_text(resp[1]),
 'craft_name': tow.display_text(resp[2]),
 'membership_status': tow.display_text(resp[3]),
 'member_since': tow.display_date(resp[4]),
 'ministries': tow.display_set(resp[5]),
 'street_address_1': tow.display_text(resp[6]),
 'street_address_2': tow.display_text(resp[7]),
 'town_village_city': tow.display_text(resp[8]),
 'province_state': tow.display_text(resp[9]),
 'postal_code': tow.display_text(resp[10]),
 'country': tow.display_text(resp[11]),
 'date_of_birth': tow.display_date(resp[12]),
 'gender': tow.display_text(resp[13]),
 'is_ordained': resp[14],
 'ordination_date': tow.display_date(resp[15]),
 'ordination_renewal_date': tow.display_date(resp[16]),
 'notes': tow.display_text(resp[17]),
 'volunteer_status': tow.display_text(resp[18]) }

    tow.cur.execute("select type, address, contact_notes from tow_contact where person_id = %(person_id)s", i)
    tow.check_warnings()
    c = [{'type': tow.display_text(x[0]), 'address': tow.display_text(x[1]), 'notes': tow.display_text(x[2])} for x in tow.fetchrows()]

    tow.cur.execute("select donation_date, donation_amount, donation_status, donation_type, donation_notes from tow_donation where person_id = %(person_id)s", i)
    tow.check_warnings()
    d = [{ 'date': tow.display_date(x[0]), 'amount': tow.display_cash(x[1]), 'status': tow.display_text(x[2]), 'type': tow.display_text(x[3]), 'notes': tow.display_text(x[4])} for x in tow.fetchrows()]

    tow.cur.execute("select event_id, type, status, payment_status, enrolled from tow_person_event where person_id = %(person_id)s", i)
    tow.check_warnings()
    e = [{'event_id': tow.s(x[0]), 'name': tow.display_text(tow.event_id_to_name(x[0])),  'type': tow.display_text(x[1]), 'status': tow.display_text(x[2]), 'payment_status': tow.display_text(x[3]), 'enrolled': tow.display_date(x[4])} for x in tow.fetchrows()]
    return (p, c, d, e)

def make_choice(text, n, lv, rv):
    lv = tow.s(lv)
    rv = tow.s(rv)
    if (lv == rv):
        ret = tr + td + text + '<td colspan=2><input type="radio" name="'+n+'" value="'+lv+'" checked>' + lv
    else:
        l_checked = ''
        r_checked = ''
        if lv == '' or lv == 'Unknown' or lv == '0':
            r_checked = ' checked'
        if rv == '' or rv == 'Unknown' or rv == '0':
            l_checked = ' checked'
        ret = tr + td + text
        ret += td + '<input type="radio" name="' + n + '" value="' + lv + '"' + l_checked + '>' + lv
        ret += td + '<input type="radio" name="' + n + '" value="' + rv + '"' + r_checked + '>' + rv
    ret += td + '<input type="radio" name="' + n + '" value="_man_' + n + '"><input type="text" name="_man_' + n + '" value="">'
    return ret + '<br>'

def print_contact(i,s, n):
    n = tow.s(n)
    print tr + td + s + '<input type="hidden" name="ct' + n + '" value="' + i['type'] + '"><input type="hidden" name="ca' + n + '" value="' + i['address'] + '"><input type="hidden" name="cn' + n + '" value="' + i['notes'] + '">' + td + i['type'] + td + i['address'] + td + i['notes']

def print_donation(i,s, n):
    n = tow.s(n)
    print tr + td + s + '<input type="hidden" name="dd' + n + '" value="' + i['date'] + '"><input type="hidden" name="da' + n + '" value="' + i['amount'] + '"><input type="hidden" name="ds' + n + '" value="' + i['status'] + '"><input type="hidden" name="dt' + n + '" value="' + i['type'] + '"><input type="hidden" name="dn' + n + '" value="' + i['notes'] + '">' + td + i['date'] + td + i['amount'] + td + i['status'] + td + i['type'] + td + i['notes']

def print_event(i,s, n):
    n = tow.s(n)
    print tr + td + s + '<input type="hidden" name="ee' + n + '" value="' + i['event_id'] + '"><input type="hidden" name="et' + n + '" value="' + i['type'] + '"><input type="hidden" name="es' + n + '" value="' + i['status'] + '"><input type="hidden" name="ep' + n + '" value="' + i['payment_status'] + '"><input type="hidden" name="ed'+n+'" value="'+i['enrolled']+'">' + td + i['name'] + td + i['type'] + td + i['status'] + td + i['payment_status'] + td + i['enrolled']

##### slurp up the form data into form ########################################
# gather any data from form
l_id = tow.form.getfirst('left')
r_id = tow.form.getfirst('right')

field = tow.form.getfirst('field')
value = tow.form.getfirst('value')
commit_cmd = tow.form.getfirst('commit')

report_opts = None
if field is not None or value is not None:
    report_opts = {}
    if field is not None:
        report_opts['field'] = field
    if value is not None:
        report_opts['value'] = value

if l_id is None or r_id is None:
    tow.start_page("Find Potential Duplicates", style = tow.st, script = tow.script_common)
    print div + '<table style="margin:0px auto" border="1"><caption>Possible Duplicates</caption><thead><tr><th>Left<th>Right<th>Address<th>Merge?</thead><tbody>'
    cmd = 'select l.person_id, r.person_id, l.address from tow_contact as l join tow_contact as r where l.person_id < r.person_id and l.address = r.address'
    arg = {}
    tow.cur.execute(cmd, arg)
    tow.check_warnings(cmd,arg)
    for resp in tow.fetchrows():
        print tr \
 + td + tow.a('person', text=tow.person_id_to_name(resp[0]), opts={'Do': 'Show', 'id': resp[0]}) \
 + td + tow.a('person', text=tow.person_id_to_name(resp[1]), opts={'Do': 'Show', 'id': resp[1]}) \
 + td + tow.display_text(resp[2]) \
 + td + '<form style="display:inline" action="' + tow.url('merge') + '" method="POST">' \
      + '<input type="hidden" name="left" value="' + tow.s(resp[0]) + '">' \
      + '<input type="hidden" name="right" value="' + tow.s(resp[1]) + '">' \
      + '<input type="submit" name="commit" value="Merge"></form>'
    print '</tbody></table>'
    tow.end_page()
    sys.exit(0)

# if not committing, show left/right page with commit button
if commit_cmd != 'Commit':
    (l, l_c, l_d, l_e) = get_person(l_id)
    (r, r_c, r_d, r_e) = get_person(r_id)
    tow.start_page("Merge two people", style = tow.st, script = tow.script_common)
    tow.log('Left ', l, l_c, l_d, l_e)
    tow.log('Right ', r, r_c, r_d, r_e)

    print div + '<form style="display:inline" action="' + tow.url('merge') + '" method="POST"><input type="hidden" name="left" value="'+tow.s(l_id)+'"><input type="hidden" name="right" value="'+tow.s(r_id)+'"><br><table style="margin:0px auto" border="1"><caption>Person</caption><thead><tr><th>Datum<th>Left<th>Right<th>Manual</thead><tbody>'
    for i in all_fields:
        print make_choice(i[2], i[0], l[i[1]], r[i[1]])

    print '</tbody></table><br>'
    if len(l_c) > 0 or len(r_c) > 0:
        print '        <table style="margin:0px auto" border="1"><caption>Contact Methods</caption><thead><tr><th>Person<th>[Include?]<th>Type<th>@<th>Notes</thead><tbody>'
        n = 0
        for i in l_c:
            if i in r_c:
                s = 'Both' + td
                r_c.remove(i)
            else:
                s = tow.s('Left', td, '<input type="checkbox" name="ci', n, '" checked>')
            print_contact(i, s, n)
            n += 1
        for i in r_c:
            s = tow.s('Right', td, '<input type="checkbox" name="ci', n, '" checked>')
            print_contact(i, s, n)
            n += 1
        print '        </tbody></table>'

    if len(l_d) > 0 or len(r_d) > 0:
        print '        <table style="margin:0px auto" border="1"><caption>Donations</caption><thead><tr><th>Person<th>[Include?]<th>Date<th>Amount<th>Status<th>Type<th>Notes</thead><tbody>'
        n = 0
        for i in l_d:
            if i in r_d:
                s = 'Both' + td
                r_d.remove(i)
            else:
                s = tow.s('Left', td, '<input type="checkbox" name="di', n, '" checked>')
            print_donation(i, s, n)
            n += 1
        for i in r_d:
            s = tow.s('Right', td, '<input type="checkbox" name="di', n, '" checked>')
            print_donation(i, s, n)
            n += 1
        print '        </tbody></table>'

    if len(l_e) > 0 or len(r_e) > 0:
        print '        <table style="margin:0px auto" border="1"><caption>Events</caption><thead><tr><th>Person<th>[Include?]<th>Event<th>Attending As<th>Status<th>Payment<th>Enrolled On</thead><tbody>'
        n = 0
        for i in l_e:
            if i in r_e:
                s = 'Both' + td
                r_e.remove(i)
            else:
                s = tow.s('Left', td, '<input type="checkbox" name="ei', n, '" checked>')
            print_event(i, s, n)
            n += 1
        for i in r_e:
            s = tow.s('Right', td, '<input type="checkbox" name="ei', n, '" checked>')
            print_event(i, s, n)
            n += 1
        print '        </tbody></table>'

    print '        <br><input type="submit" name="commit" value="Commit"><br>'
    print "      </form>" + xdiv
    print div + tow.a('person-report', text="Redo Search", opts = report_opts) + xdiv
    tow.end_page()
    sys.exit(0)


tow.log('Committting merge of ', l_id, ' and ', r_id)
m_c = tow.get_list((
 ('ct', 'type', 'Unknown'),
 ('ci', 'include'),
 ('ca', 'address'),
 ('cn', 'notes')))
c_t = tow.enum('contact_type')
for i in m_c:
    if i['type'] not in c_t:
        tow.add_error('Unknown contact type ', i['type'], ' in form input, not in ', repr(c_t))
    if i['notes'] == '':
        i['notes'] = None

m_d = tow.get_list((
 ('di', 'include'),
 ('dd', 'date'),
 ('da', 'amount'),
 ('ds', 'status', 'Unknown'),
 ('dt', 'type', 'Other'),
 ('dn', 'notes')))
d_s = tow.enum('donation_status')
d_t = tow.enum('donation_type')
for i in m_d:
# FIXME: check donation id here?
    if i['status'] not in d_s:
        tow.add_error('Unknown donation status ', i['status'], ' in form input, not in ', repr(d_s))
    if i['type'] not in d_t:
        tow.add_error('Unknown donation type ', i['type'], ' in form input, not in ', repr(d_t))
    i['date'] = tow.store_date(i['date'])
    i['amount'] = tow.store_cash(i['amount'])

m_e = tow.get_list((
 ('ei', 'include'),
 ('ee', 'event_id'),
 ('et', 'type', 'Unknown'),
 ('es', 'status', 'Unknown'),
 ('ep', 'payment_status', 'Unknown'),
 ('ed', 'enrolled')))
e_t = tow.enum('person_event_type')
e_s = tow.enum('person_event_status')
e_p = tow.enum('person_event_payment_status')
for i in m_e:
# FIXME: check event id here?
    if i['type'] not in e_t:
        tow.add_error('Unknown attendee type ', i['type'], ' in form input, not in ', repr(e_t))
    if i['status'] not in e_s:
        tow.add_error('Unknown attendee status ', i['status'], ' in form input, not in ', repr(e_s))
    if i['payment_status'] not in e_p:
        tow.add_error('Unknown attendee payment ', i['payment_status'], ' in form input, not in ', repr(e_p))

m = {'person_id': l_id}
for i in all_fields:
    tmp = tow.form.getfirst(i[0])
    if tmp == '_man_' + i[0]:
        tmp = tow.form.getfirst('_man_' + i[0])
    m[i[1]] = tmp

if m['first_name'] is None:
    tow.add_error('Missing required first name, setting it to Unknown')
    m['first_name'] = 'Unknown'
if m['gender'] is None:
    tow.add_error('Missing required gender, setting it to Unknown')
    m['gender'] = 'Unknown'
if m['is_ordained'] is None:
    tow.add_error('Missing required is ordained, setting it to 0')
    m['is_ordained'] = 0
if m['volunteer_status'] is None:
    tow.add_error('Missing required volunteer status, setting it to Unknown')
    m['volunteer_status'] = 'Unknown'
# FIXME: check person_id here?
if m['ministries'] is None:
    m['ministries'] = ''
for n in ('member_since', 'date_of_birth', 'ordination_date', 'ordination_renewal_date'):
    m[n] = tow.store_date(m[n])
if m['membership_status'] is None:
    tow.add_error('Missing required membership status, setting it to Unknown')
    m['membership_status'] = 'Unknown'
tmp = tow.enum('person_membership')
if m['membership_status'] not in tmp:
    tow.add_error('Unknown membership status ', m['membership_status'], ' in form input, not in ', repr(tmp))
tmp = tow.enum('person_gender')
if m['gender'] not in tmp:
    tow.add_error('Unknown gender ', m['gender'], ' in form input, not in ', repr(tmp))
tmp = tow.enum('person_volunteer')
if m['volunteer_status'] not in tmp:
    tow.add_error('Unknown volunteer status ' + m['volunteer_status'] + ' in form input, not in ', repr(tmp))
tow.log('merged ', m, m_c, m_d, m_e)
cmd = """
 update tow_person set
  first_name = %(first_name)s,
  last_name = %(last_name)s,
  craft_name = %(craft_name)s,
  membership_status = %(membership_status)s,
  member_since = %(member_since)s,
  ministries = %(ministries)s,
  street_address_1 = %(street_address_1)s,
  street_address_2 = %(street_address_2)s,
  town_village_city = %(town_village_city)s,
  province_state = %(province_state)s,
  postal_code = %(postal_code)s,
  country = %(country)s,
  date_of_birth = %(date_of_birth)s,
  gender = %(gender)s,
  is_ordained = %(is_ordained)s,
  ordination_date = %(ordination_date)s,
  ordination_renewal_date = %(ordination_renewal_date)s,
  person_notes = %(notes)s,
  volunteer_status = %(volunteer_status)s
 where person_id = %(person_id)s"""
arg = m
tow.cur.execute(cmd, arg)
tow.check_warnings(cmd,arg)

cmd = 'delete from tow_contact where person_id = %(l_id)s or person_id = %(r_id)s'
arg = { 'l_id': l_id, 'r_id': r_id }
tow.cur.execute(cmd, arg)
tow.check_warnings(cmd, arg)
cmd = 'delete from tow_donation where person_id = %(l_id)s or person_id = %(r_id)s'
arg = { 'l_id': l_id, 'r_id': r_id }
tow.cur.execute(cmd, arg)
tow.check_warnings(cmd, arg)

cmd = 'delete from tow_person_event where person_id = %(l_id)s or person_id = %(r_id)s'
arg = { 'l_id': l_id, 'r_id': r_id }
tow.cur.execute(cmd, arg)
tow.check_warnings(cmd, arg)

for i in m_c:
    if i['include'] == 'on':
        i['person_id'] = l_id
        try:
            tow.add_contact(i)
        except:
            tow.add_error('Adding contact ', repr(i), ' failed!')

for i in m_d:
    if i['include'] == 'on':
        j = {}
        j['person_id'] = l_id
        j['date'] = i['date']
        j['amount'] = i['amount']
        j['status'] = i['status']
        j['type'] = i['type']
        j['notes'] = i['notes']
        try:
            i['donation_id'] = tow.add_donation(j)
        except:
            tow.add_error('Adding donation ', repr(j), ' failed!')

for i in m_e:
    if i['include'] == 'on':
        i['person_id'] = l_id
        i['enrolled_s'] = tow.store_date(i['enrolled'])
        try:
            tow.add_person_event(i)
        except:
            tow.add_error('Adding event ', repr(i), ' failed!')

try:
    cmd = 'delete from tow_person where person_id = %(r_id)s'
    arg = {'r_id': r_id}
    tow.cur.execute(cmd, arg)
    tow.check_warnings(cmd, arg)
except:
    tow.add_error('Deleting duplicate person failed.')

if len(tow.problems) > 0:
    failed()

tow.log('Merge completed')
tow.fini()

tow.print_results('Merge Complete', 'person-report', 'Merge completed sucessfully.', opts = report_opts, timeout = 10)
