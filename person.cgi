#!/usr/bin/python
import sys, string, cgi, urllib, traceback
sys.path.insert(0,'/home/temple24/python')
import mysql.connector, tow

tow.check_authorized("person")

td = tow.td

# t_p == 'Temple of Witchcraft Person'
t_p = {}

# t_p_c == 'Temple of Witchcraft Person Contacts'
t_p_c = []
# t_p_d == 'Temple of Witchcraft Person Donations'
t_p_d = []
# t_p_e == 'Temple of Witchcraft Person Events'
t_p_e = []

empty_person = { 
 'person_id': None,
 'first_name': None,
 'last_name': None,
 'craft_name': None,
 'membership_status': 'Unknown', 
 'member_since': None,
 'ministries': '',
 'street_address_1': None,
 'street_address_2': None,
 'town_village_city': None,
 'province_state': None,
 'postal_code': None,
 'country': None,
 'date_of_birth': None,
 'gender': 'Unknown',
 'is_ordained': 0,
 'ordination_date': None,
 'ordination_renewal_date': None,
 'notes': None,
 'volunteer_status': 'Unknown' }

def clear_person():
    global t_p
    global t_p_c
    global t_p_d
    global t_p_e
    t_p = dict(empty_person)
    t_p_c = []
    t_p_d = []
    t_p_e = []

##### slurp up the form data into form ########################################
# gather any data from form
dowhat = tow.get_param('Do', oneof = ('Unknown',  'Add', 'Update', 'Delete', 'Show'))

clear_person()

if dowhat == 'Add' or dowhat == 'Update':
    t_p_c = tow.get_list((
 ('ct', 'type', 'Unknown'),
 ('cot', 'old_type', 'Unknown'),
 ('ca', 'address'),
 ('coa', 'old_address'),
 ('cn', 'notes'),
 ('con', 'old_notes'),
 ('cx', 'delete')))
    c_e = tow.enum('contact_type')
    for i in t_p_c:
        if i['type'] not in c_e or ( i['old_type'] != '' and i['old_type'] not in c_e ):
            tow.add_error('Unknown contact type ', i['type'], ':', i['old_type'], ' in form input')
        if i['notes'] == '':
            i['notes'] = None
        if i['old_notes'] == '':
            i['old_notes'] = None

    if 'donation' in tow.permissions:
        t_p_d = tow.get_list((
 ('di', 'donation_id'),
 ('dx', 'delete'),
 ('dd', 'date'),
 ('dod', 'old_date'),
 ('da', 'amount'),
 ('doa', 'old_amount'),
 ('ds', 'status', 'Complete'),
 ('dos', 'old_status', 'Complete'),
 ('dt', 'type', 'Other'),
 ('dot', 'old_type', 'Other'),
 ('dn', 'notes'),
 ('don', 'old_notes')))
        d_s_e = tow.enum('donation_status')
        d_t_e = tow.enum('donation_type')
        for i in t_p_d:
# FIXME: check donation id here?
            if i['status'] not in d_s_e or ( i['old_status'] != '' and i['old_status'] not in d_s_e ):
                tow.add_error('Unknown donation status ', i['status'], ':', i['old_status'], ' in form input, not ', repr(d_s_e))
            if i['type'] not in d_t_e or ( i['old_type'] != '' and i['old_type'] not in d_t_e ):
                tow.add_error('Unknown donation type ', i['type'], ':', i['old_type'], ' in form input, not ', repr(d_t_e))
            i['date'] = tow.store_date(i['date'])
            i['amount'] = tow.store_cash(i['amount'])

    t_p_e = tow.get_list((
 ('ee', 'event_id'), ('eoe', 'old_event_id'), ('en', 'name'),
 ('ex', 'delete'),
 ('et', 'type', 'Unknown'),
 ('eot', 'old_type', 'Unknown'),
 ('es', 'status', 'Unknown'),
 ('eos', 'old_status', 'Unknown'),
 ('ep', 'payment_status', 'Unknown'),
 ('eop', 'old_payment_status', 'Unknown'),
 ('ed', 'enrolled_d'),
 ('eod', 'old_enrolled')))
    pete = tow.enum('person_event_type')
    pese = tow.enum('person_event_status')
    pepse =tow.enum('person_event_payment_status')
    for i in t_p_e:
# FIXME: check event id here?
        if i['type'] not in pete or ( i['old_type'] != '' and i['old_type'] not in pete ):
            tow.add_error('Unknown attendee type ', i['type'], ':', i['old_type'], ' in form input')
        if i['status'] not in pese or ( i['old_status'] != '' and i['old_status'] not in pese ):
            tow.add_error('Unknown attendee status ', i['status'], ':', i['old_status'], ' in form input')
        if i['payment_status'] not in pepse or ( i['old_payment_status'] != '' and i['old_payment_status'] not in pepse ):
            tow.add_error('Unknown attendee payment ', i['payment_status'], ':', i['old_payment_status'], ' in form input')
        i['enrolled_s'] = tow.store_date(i['enrolled_d'])
    io = 0
    if tow.get_param('io') is not None:
        io = 1
    t_p = { 
 'person_id': tow.get_param('id'),
 'first_name': tow.get_param('fn'),
 'last_name': tow.get_param('ln'),
 'craft_name': tow.get_param('cn'),
 'membership_status': tow.get_param('ms'), 
 'member_since': tow.get_param('sn'),
 'ministries': tow.get_param('mn'),
 'street_address_1': tow.get_param('s1'),
 'street_address_2': tow.get_param('s2'),
 'town_village_city': tow.get_param('tv'),
 'province_state': tow.get_param('ps'),
 'postal_code': tow.get_param('zp'),
 'country': tow.get_param('ct'),
 'date_of_birth': tow.get_param('db'),
 'gender': tow.get_param('gd'),
 'is_ordained': io,
 'ordination_date': tow.get_param('od'),
 'ordination_renewal_date': tow.get_param('or'),
 'notes': tow.get_param('no'),
 'volunteer_status': tow.get_param('vs') }
# FIXME: check person_id here?
    if t_p['ministries'] is None:
        t_p['ministries'] = ''
    for n in ('member_since', 'date_of_birth', 'ordination_date', 'ordination_renewal_date'):
        t_p[n] = tow.store_date(t_p[n])
    if t_p['membership_status'] not in tow.enum('person_membership'):
        tow.add_error('Unknown membership status ', t_p['membership_status'], ' in form input')
    if t_p['gender'] not in tow.enum('person_gender'):
        tow.add_error('Unknown gender ', t_p['gender'], ' in form input')
    if t_p['volunteer_status'] not in tow.enum('person_volunteer'):
        tow.add_error('Unknown volunteer status ', t_p['volunteer_status'], ' in form input')
elif dowhat == 'Show':
    t_p = { 'person_id': tow.get_param('id') }
    tow.cur.execute("select type, address, contact_notes from tow_contact where person_id = %(person_id)s", t_p)
    tow.check_warnings()
    for resp in tow.fetchrows():
        t_p_c.append({'type': resp[0], 'old_type': resp[0], 'address': resp[1], 'old_address': resp[1], 'notes': resp[2], 'old_notes': resp[2]})

    if 'donation' in tow.permissions:
        tow.cur.execute("select donation_id, donation_date, donation_amount, donation_status, donation_type, donation_notes from tow_donation where person_id = %(person_id)s", t_p)
        tow.check_warnings()
        for resp in tow.fetchrows():
            date = tow.store_date(resp[1])
            t_p_d.append({'donation_id': tow.s(resp[0]), 'date': date, 'old_date': date, 'amount': resp[2], 'old_amount': resp[2], 'status': resp[3], 'old_status': resp[3], 'type': resp[4], 'old_type': resp[4], 'notes': resp[5], 'old_notes': resp[5]})

    tow.cur.execute("select event_id, type, status, payment_status, enrolled from tow_person_event where person_id = %(person_id)s", t_p)
    tow.check_warnings()
    for resp in tow.fetchrows():
        enrolled_d = tow.display_date(resp[4])
        t_p_e.append({'event_id': tow.s(resp[0]), 'old_event_id': tow.s(resp[0]), 'name': tow.event_id_to_name(resp[0]),  'type': resp[1], 'old_type': resp[1], 'status': resp[2], 'old_status': resp[2], 'payment_status': resp[3], 'old_payment_status': resp[3], 'enrolled_s': resp[4], 'enrolled_d': enrolled_d, 'old_enrolled': enrolled_d})

    tow.cur.execute("""select first_name, last_name, craft_name, membership_status,
 member_since, ministries, street_address_1, street_address_2, town_village_city,
 province_state, postal_code, country, date_of_birth, gender,
 is_ordained, ordination_date, ordination_renewal_date, person_notes,
 volunteer_status from tow_person where person_id = %(person_id)s""", t_p)
    resp = tow.cur.fetchall()
    if len(resp) != 1:
        tow.add_error('Person id ',t_p['person_id'], ' not found')
    else:
        resp = resp[0]
        t_p = {
 'person_id': t_p['person_id'],
 'first_name': resp[0],
 'last_name': resp[1],
 'craft_name': resp[2],
 'membership_status': resp[3],
 'member_since': tow.store_date(resp[4]),
 'ministries': tow.display_set(resp[5]),
 'street_address_1': resp[6],
 'street_address_2': resp[7],
 'town_village_city': resp[8],
 'province_state': resp[9],
 'postal_code': resp[10],
 'country': resp[11],
 'date_of_birth': tow.store_date(resp[12]),
 'gender': resp[13],
 'is_ordained': resp[14],
 'ordination_date': tow.store_date(resp[15]),
 'ordination_renewal_date': tow.store_date(resp[16]),
 'notes': resp[17],
 'volunteer_status': resp[18] }

elif dowhat == 'Delete':
    t_p = { 'person_id': tow.get_param('id') }
else:
    clear_person()

## if there is something to do, do it
if len(tow.problems) == 0:
    tmp = ''
    if 'donation' in tow.permissions:
        tmp = tow.s(' donations ', t_p_d)
    tow.log('Attempting ', dowhat, ' on ', t_p, ', contacts ', t_p_c, tmp, ', events ', t_p_e)
    cmd = None
    try:
        if dowhat == 'Add':
            person_id = tow.add_person(t_p)
            tow.conn.commit()
            t_p['person_id'] = person_id
            for i in t_p_c:
                i['person_id'] = person_id
                tow.add_contact(i)
            if 'donation' in tow.permissions:
                for i in t_p_d:
                    i['person_id'] = person_id
                    tow.add_donation(i)
            for i in t_p_e:
                i['person_id'] = person_id
                tow.add_person_event(i)
            clear_person()
            tow.refresh_people()

        elif dowhat == 'Update':
            if t_p.get('person_id') is None:
                raise ValueError("Unknown person id")
# 'delete', 'type', 'old_type', 'address', 'old_address', 'notes'
            n = 0
            m = len(t_p_c)
            while n < m:
                i = t_p_c[n]
                i['person_id'] = t_p['person_id']
                if i.get('delete'):
                    if i['type'] != '' and i['type'] == i['old_type'] and i['address'] is not None and i['address'] == i['old_address']:
                        cmd = 'delete from tow_contact where person_id = %(person_id)s and type = %(type)s and address = %(address)s'
                        arg = i
                        tow.cur.execute(cmd, arg)
                    else:
# Deleting an entry that isn't actually in the database?  That's easy
                        pass
                    del t_p_c[n]
                    m -= 1
                elif ( i['type'] == i['old_type'] or ( i['type'] == 'Unknown' and i['old_type'] == '' ) ) and i['address'] == i['old_address'] and i['notes'] == i['old_notes']:
# Updating an entry that hasn't changed is easy
                    n += 1
                elif ( i['old_type'] is not None and i['old_address'] is not None ) and i['address'] is not None:
                    tow.add_contact(i)
                    i['old_type'] = i['type']
                    i['old_address'] = i['address']
                    i['old_notes'] = i['notes']
                    n += 1
                else:
                    cmd = 'update tow_contact set type = %(type)s, address = %(address)s, contact_notes = %(notes)s where person_id = %(person_id)s and type = %(old_type)s and address = %(old_address)s'
                    arg = i
                    tow.cur.execute(cmd, arg)
                    i['old_type'] = i['type']
                    i['old_address'] = i['address']
                    i['old_notes'] = i['notes']
                    n += 1

# {'status': 'Unknown', 'donation_id': '', 'old_date': '', 'person_id': '5', 'amount': '', 'date': '', 'old_status': '', 'old_amount': '', 'delete': ''}
            if 'donation' in tow.permissions:
                n = 0
                m = len(t_p_d)
                while n < m:
                    i = t_p_d[n]
                    i['person_id'] = t_p['person_id']
                    if i.get('delete'):
                        if i['donation_id'] != '':
                            cmd = 'delete from tow_donation where donation_id = %(donation_id)s'
                            arg = {'donation_id': i['donation_id']}
                            tow.cur.execute(cmd, arg)
                        else:
# Deleting an entry that isn't actually in the database?  That's easy
                            pass
                        del t_p_d[n]
                        m -= 1
                    elif \
     ( i['status'] == i['old_status'] or ( i['status'] == 'Complete' and i['old_status'] == '' ) ) \
 and ( i['type'] == i['old_type'] or ( i['type'] == 'Other' and i['old_type'] == '' ) ) \
 and   i['date'] == i['old_date'] \
 and   i['amount'] == i['old_amount'] \
 and   i['notes'] == i['old_notes']:
# Updating an entry that hasn't changed is easy
                        n += 1
                    else:
                        if i['donation_id'] == '':
                            i['donation_id'] = tow.add_donation(i)
                        else:
                            cmd = 'update tow_donation set donation_date = %(date)s, donation_amount = %(amount)s, donation_status = %(status)s, donation_type = %(type)s, donation_notes = %(notes)s where donation_id = %(donation_id)s'
                            arg = i
                            tow.cur.execute(cmd, arg)
                        i['old_date'] = i['date']
                        i['old_amount'] = i['amount']
                        i['old_status'] = i['status']
                        i['old_type'] = i['type']
                        i['old_notes'] = i['notes']
                        n += 1

            n = 0
            m = len(t_p_e)
            while n < m:
                i = t_p_e[n]
# {'status': 'Unknown', 'old_type': '', 'event_id': '',
#  'payment_status': 'Unknown', 'old_payment_status': '',
#  'person_id': '5', 'old_status': '', 'type': 'Unknown', 'delete': ''}
                i['person_id'] = t_p['person_id']
                if i.get('delete'):
                    if i['event_id'] != '':
                        cmd = 'delete from tow_person_event where person_id = %(person_id)s and event_id = %(event_id)s'
                        arg = {'person_id': i['person_id'], 'event_id': i['event_id']}
                        tow.cur.execute(cmd, arg)
                    else:
# Deleting an entry that isn't actually in the database?  That's easy
                        pass
                    del t_p_e[n]
                    m -= 1
                elif (    i['status'] == i['old_status'] \
       or ( i['status'] == 'Unknown' and i['old_status'] == '' ) ) \
 and (     i['type'] == i['old_type'] \
      or ( i['type'] == 'Unknown' and i['old_type'] == '') ) \
 and (     i['payment_status'] == i['old_payment_status'] \
       or ( i['payment_status'] == 'Unknown' and i['old_payment_status'] == '' ) ) \
 and (i['enrolled_d'] == i['old_enrolled'] or ( i['enrolled_d'] == '' and i['old_enrolled'] is None)):
# Updating an entry that hasn't changed is easy
                    n += 1
                elif i['old_type'] == '' or i['old_status'] == '' or i['old_payment_status'] == '':
                    tow.add_person_event(i)
                    i['old_type'] = i['type']
                    i['old_status'] = i['status']
                    i['old_payment_status'] = i['payment_status']
                    i['old_enrolled'] = i['enrolled_d']
                    n += 1
                else:
                    cmd = 'update tow_person_event set type = %(type)s, status = %(status)s, payment_status = %(payment_status)s, enrolled = %(enrolled_s)s where person_id = %(person_id)s and event_id = %(event_id)s'
                    arg = i
                    tow.cur.execute(cmd, arg)
                    i['old_type'] = i['type']
                    i['old_status'] = i['status']
                    i['old_payment_status'] = i['payment_status']
                    i['old_enrolled'] = i['enrolled_d']
                    n += 1


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
            arg = t_p
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd,arg)
            tow.refresh_people()
        elif dowhat == 'Delete':
            arg = { 'person_id': t_p['person_id'] }
            cmd = 'delete from tow_person_event where person_id = %(person_id)s'
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd,arg)
            cmd = 'delete from tow_donation where person_id = %(person_id)s'
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd,arg)
            cmd = 'delete from tow_contact where person_id = %(person_id)s'
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd,arg)
            cmd = 'delete from tow_person where person_id = %(person_id)s'
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd,arg)
            clear_person()
            tow.refresh_people()
        elif dowhat == 'Show':
            pass
        else:
#            tow.add_error("Dunno what to do")
            clear_person()
    except mysql.connector.IntegrityError:
        if cmd is not None:
            tow.add_error("On command ", cmd, " with ", arg)
        tow.add_error('Database integrity error: ', traceback.format_exc().replace('\n','  '))

    except:
        if cmd is not None:
            tow.add_error("On command ", cmd, " with ", arg)
        tow.add_error('Error thrown: ', traceback.format_exc().replace('\n','  '))

if t_p.get('person_id'):
    text = "Edit Person " + tow.display_text(tow.person_id_to_name(t_p.get('person_id')))
else:
    text = "Add New Person"

script_var = tow.var_list('contact_types',tow.enum('contact_type')) + 'var the_contacts = ['
n = 1
sep = ''
for i in t_p_c:
    i['pn'] = 'New'
    if i['old_type'] != '':
        i['pn'] = n
        n += 1
    i['checked'] = 0
    if i.get('delete'):
        i['checked'] = 1
    script_var += sep + tow.var_hash(i, ('pn', 'old_type', 'old_address', 'old_notes', 'checked', 'type', 'address', 'notes'))
    sep = ','
script_var += sep + 'null];\n'

if 'donation' in tow.permissions:
    script_var += \
 tow.var_list('donation_statuses', tow.enum('donation_status')) + \
 tow.var_list('donation_types', tow.enum('donation_type')) + \
 'var the_donations = ['
    n = 1
    sep = ''
    for i in t_p_d:
        i['pn'] = 'New'
        if i['donation_id'] != '':
            i['pn'] = n
            n += 1
        i['checked'] = 0
        if i.get('delete'):
            i['checked'] = 1
        i['date'] = tow.display_date(i['date'])
        i['amount'] = tow.display_cash(i['amount'])
        script_var += sep + tow.var_hash(i, ('pn', 'donation_id', 'old_date', 'old_amount', 'old_status', 'checked', 'date', 'amount', 'status', 'type', 'notes'));
        sep = ','
    script_var += sep + 'null];\n'

if len(tow.event_list) > 0:
    script_var += tow.var_list('attendee_types',tow.enum('person_event_type')) + \
 tow.var_list('attendee_statuses',tow.enum('person_event_status')) + \
 tow.var_list('attendee_payments',tow.enum('person_event_payment_status')) + \
 'var the_events = ['
    n = 1
    sep = ''
    for i in t_p_e:
        i['pn'] = 'New'
        if i['old_status'] != '':
            i['pn'] = n
            n += 1
        i['checked'] = 0
        if i.get('delete'):
            i['checked'] = 1
        script_var += sep + tow.var_hash(i, ('pn', 'old_event_id', 'old_type', 'old_status', 'old_payment_status', 'old_enrolled', 'checked', 'event_id', 'name', 'type', 'status', 'payment_status', 'enrolled_d'))
        sep = ','

    script_var += sep + 'null];\nvar all_events_byname={'
    sep = ''
    for (i, n) in zip(tow.event_id_list, tow.event_list):
        script_var += sep + tow.var_text(n) + ':' + i
        sep = ','
    script_var += '};\n'

script_var += '''


      function new_contact(m, l) {
        var a = null;
        if (l == null) {
          l = ['New', '', '', '', 0, 'Unknown', '', ''];
          a = {'onchange': 'row_changed(this,"new_contact",event);',
                 'onkeydown': 'row_changed(this,"new_contact",event)'};
        }
        return mk_tr(a,
[ mk_text(l[0]), mk_input_hidden('cot'+m,l[1]), mk_input_hidden('coa'+m,l[2]), mk_input_hidden('con'+m,l[3]) ],
mk_input_checkbox('cx'+m,l[4]),
mk_input_select('ct'+m,contact_types,l[5]),
mk_input_text('ca'+m,l[6]),
mk_input_text('cn'+m,l[7]));
      }


      function new_donation(m, l) {
        var a = null;
        if (l == null) {
          l = ['New', '', '', '', '', 0, '', '', 'Complete', 'Other', ''];
          a = {'onchange': 'row_changed(this,"new_donation",event);',
                 'onkeydown': 'row_changed(this,"new_donation",event)'};
        }
        return mk_tr(a,
[ mk_text(l[0]), mk_input_hidden('di'+m,l[1]), mk_input_hidden('dod'+m,l[2]), mk_input_hidden('doa',l[3]), mk_input_hidden('dos'+m,l[4]) ],
mk_input_checkbox('dx'+m,l[5]),
mk_input_text('dd'+m,l[6]),
mk_input_text('da'+m,l[7]),
mk_input_select('ds'+m,donation_statuses,l[8]),
mk_input_select('dt'+m,donation_types,l[9]),
mk_input_text('dn'+m,l[10]));
      }


      function new_event(m, l) {
        var a = null;
        if (l == null) {
          l = ['New', '', '', '', '', '', 0, '', '', 'Unknown', 'Unknown', 'Unknown', ''];
          a = {'onchange': 'row_changed(this,"new_event",event);',
                 'onkeydown': 'row_changed(this,"new_event",event)'};
        }
        var ret = mk_tr(a,
 [ mk_text(l[0]), mk_input_hidden('eoe'+m,l[1]), mk_input_hidden('eot'+m,l[2]), mk_input_hidden('eos'+m, l[3]), mk_input_hidden('eop'+m, l[4]), mk_input_hidden('eod'+m, l[5])],
 mk_input_checkbox('ex'+m,l[6]),
 [mk_input_hidden('ee'+m,l[7]), mk_ele('input',{'name':'en'+m,'type':'text','value':l[8],'onkeyup':'setTimeout(function(){changed(event.target);},10);','onchange':'changed(event.target);','id':'en'+m,'choices':'all_events_byname'})],
 mk_input_select('et'+m,attendee_types,l[9]),
 mk_input_select('es'+m,attendee_statuses,l[10]),
 mk_input_select('ep'+m,attendee_payments,l[11]),
 mk_input_text('ed'+m,l[12]));
        return ret;
      }


      function setup() {
        for (var i = 0; i < the_contacts.length; i++) {
          add_row(contacts, 'new_contact', the_contacts[i]);
        }
        for (var i = 0; i < the_donations.length; i++) {
          add_row(donations, 'new_donation', the_donations[i]);
        }
        for (var i = 0; i < the_events.length; i++) {
          add_row(events, 'new_event', the_events[i]);
        }
      }
'''

tow.start_page(text, style = tow.st, script = tow.script_common + tow.script_add_row + tow.script_choose + script_var, onload = "setup();")
tmp = {'person_url': tow.url('person'), 'ministries': t_p['ministries']}
for i in ('membership_status', 'gender', 'volunteer_status'):
    if t_p.get(i) is None:
        tmp[i] = 'Unknown'
    else:
        tmp[i] = t_p[i]
tmp['status_options'] = tow.dropdown("ms", tow.enum('person_membership'), title = "Status", default = tmp['membership_status'])
tmp['gender_options'] = tow.dropdown("gd", tow.enum('person_gender'), title = "Gender", default = tmp['gender'])
tmp['volunteer_options'] = tow.dropdown("vs", tow.enum('person_volunteer'), title = "Volunteer Status", default = tmp['volunteer_status'] )
tmp['io_checked'] = ''
if t_p.get('is_ordained'):
    tmp['io_checked'] = 'checked'
for i in ('first_name', 'last_name', 'craft_name', 'street_address_1', 'street_address_2', 'town_village_city', 'province_state', 'postal_code', 'country', 'notes'):
    tmp[i] = tow.display_text(t_p.get(i))
for i in ('member_since', 'date_of_birth', 'ordination_date', 'ordination_renewal_date'):
    tmp[i] = tow.display_date(t_p[i])

print string.Template("""      <form style="display:inline" action="${person_url}" method="POST">
        <span class="c3"><label for="fn">First Name&nbsp;</label><span><input type="text" name="fn" value="${first_name}"/></span></span>
        <span class="c3"><label for="ln">&nbsp;&nbsp;Last Name&nbsp;</label><span><input type="text" name="ln" value="${last_name}"/></span></span>
        <span class="c3"><label for="cn">&nbsp;&nbsp;Craft Name&nbsp;</label><span><input type="text" name="cn" value="${craft_name}"/></span></span><br>
        <span class="c1"><label for="s1">Street Address 1&nbsp;</label><span><input type="text" name="s1" value="${street_address_1}" /></span></span><br>

        <span class="c1"><label for="s2">Street Address 2&nbsp;</label><span><input type="text" name="s2" value="${street_address_2}" /></span></span><br>

        <span class="c3"><label for="tv">City&nbsp;</label><span><input type="text" name="tv" value="${town_village_city}" /></span></span>
        <span class="c3"><label for="ps">&nbsp;&nbsp;State&nbsp;</label><span><input type="text" name="ps" value="${province_state}" /></span></span>
        <span class="c6"><label for="zp">&nbsp;&nbsp;Zip&nbsp;</label><span><input type="text" name="zp" value="${postal_code}" /></span></span>
        <span class="c6"><label for="ct">&nbsp;&nbsp;Country&nbsp;</label><span><input type="text" name="ct" value="${country}" /></span></span><br>

        <span class="c3"><label for="db">Date of Birth&nbsp;</label><span><input type="text" name="db" value="${date_of_birth}" /></span></span>
        <span class="c3a">${gender_options}</span>&nbsp;<br><br>

        <span class="c3"><label for="sn">Member Since&nbsp;</label><span><input type="text" name="sn" value="${member_since}" /></span></span>
        <span class="c3a">${status_options}</span>
        <span class="c3a">${volunteer_options}</span><br><br>

        <span class="c3a"><label>Is Ordained<input type="checkbox" name="io" ${io_checked}/></label></span>
        <span class="c3"><label for="od">Ordination Date&nbsp;</label><span><input type="text" name="od" value="${ordination_date}"/></span></span>
        <span class="c3"><label for="or">&nbsp;&nbsp;Ordination Renewal Date&nbsp;</label><span><input type="text" name="or" value="${ordination_renewal_date}"/></span></span><br>

        <span class="c1"><label for="mn">Ministries of Interest&nbsp;</label><span><input type="text" name="mn" value="${ministries}"/></span></span><br>

        <span class="c1"><label for="no">Notes&nbsp;</label><span><input type="text" name="no" value="${notes}"/></span></span><br>""").substitute(tmp)
print '        <br><table style="margin:0px auto" border="1"><caption>Contact Methods</caption><thead><tr><th>##<th>[Delete]<th>Type<th>@<th>Notes</thead><tbody id="contacts" max="0">'
print '        </tbody></table>'
if 'donation' in tow.permissions:
#  'delete', 'donation_id', 'date', 'amount', 'status'
    print '        <table style="margin:0px auto" border="1"><caption>Donations</caption><thead><tr><th>##<th>[Delete]<th>Date<th>Amount<th>Status<th>Type<th>Notes</thead><tbody id="donations" max="0">'
    print '        </tbody></table>'

if len(tow.event_list) > 0:
    # 'ex': 'delete', 'ee': 'event_id', 'et': 'type', 'es': 'status', 'ep': 'payment_status'
    print '        <table style="margin:0px auto" border="1"><caption>Events</caption><thead><tr><th>##<th>[Delete]<th>Event<th>Attending As<th>Status<th>Payment<th>Enrolled On</thead><tbody id="events" max="0">'
    print '        </tbody></table><br>'

print '        <span class="b3"><input type="submit" name="Do" value="New"/></span>'
if t_p.get('person_id'):
    print string.Template("""        <span class="b3"><input type="submit" name="Do" value="Update" />
        <input type="hidden" name="id", value="${person_id}" /></span>""").substitute({'person_id': t_p['person_id']})
else:
    print '        <span class="b3"><input type="submit" name="Do" value="Add" /></span>'

print """      </form>"""
if t_p.get('person_id'):
    print string.Template("""      <span class="b3"><form action="${person_url}" method="POST">
        <input type="submit" name="Do" value="Delete" />
        <input type="hidden" name="id", value="${person_id}" />
      </form></span>""").substitute({'person_url': tow.url('person'), 'person_id': t_p['person_id']})
print '      <br><br>'
##### Report Section #########################################################
print '      <hr style="color:#c00;background-color:#c00;height:4"/>'
print '      <table style="margin:0px auto" border="1"><caption>Recently Added People</caption><thead><tr><th>Name<th>Status<th>Since</thead><tbody>'

people = {}
tow.cur.execute("""select person_id, membership_status, member_since from tow_person order by person_id desc limit 20""")
for resp in tow.fetchrows():
    (person_id, status, since) = resp
    people[tow.person_sort_by_id[person_id]] = '<tr><td>' + tow.a('person', text = tow.display_text(tow.person_id_to_name(person_id)), opts = {'Do': 'Show', 'id': person_id}) + td + status + td + tow.display_date(since)
for i in sorted(people.keys()):
    print people[i]
print '      </tbody></table><br>'
tow.end_page()
