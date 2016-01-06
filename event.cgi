#!/usr/bin/python
import sys, urllib, string, traceback
sys.path.insert(0,'/home/temple24/python')
import mysql.connector, tow

td = tow.td

def del_p_e(i):
    cmd = "delete from tow_person_event where event_id = %(event_id)s and person_id = %(old_person_id)s"
    arg = i
    tow.cur.execute(cmd, arg)
    tow.check_warnings(cmd,arg)

def add_p_e(i):
    tow.add_person_event(i)
    i['old_person_id'] = i['person_id']
    i['old_type'] = i['type']
    i['old_status'] = i['status']
    i['old_payment_status'] = i['payment_status']
    i['old_enrolled'] = i['enrolled_s']


#    Event
# event_id integer unsigned primary key auto_increment,
# name varchar(32) not null unique,
# type enum ...
# starts_on date not null,
# ends_on date not null,
# base_cost integer not null,
# ceus integer
# notes text
#
#    person_event
# person_id integer unsigned not null references tow_person(person_id),
# event_id integer unsigned not null references tow_event(event_id),
# type enum ('Unknown', 'Teacher', 'Volunteer', 'Student', 'Auditor', 'Other') not null,
# status enum ('Unknown', 'Signed-Up', 'Cancelled', 'In-Progress', 'Completed') not null,
# payment_status enum ('Unknown', 'Paid', 'Not Paid', 'Scholarship', 'Donation Package', 'ISBE') not null,
# enrolled date

# t_e == 'Temple of Witchcraft Event'
empty_event = { 
 'event_id': None,
 'name': None,
 'type': 'Unknown',
 'starts_on': None,
 'ends_on': None,
 'base_cost': None, 
 'ceus': None,
 'notes': None }

def clear_event():
    global t_e
    global t_e_p
    t_e = dict(empty_event)
    t_e_p = []

clear_event()

##### slurp up the form data into form ########################################
# gather any data from form
# 'Add'		the cgi form data contains data for a new event to insert.
# 'Delete'	the cgi form data contains the id of an event to delete.
# 'Edit'	The cgi form data contains the id of an event to edit.
# 'List'	List events, allowing the user to show or edit (according to permissions) them.  This does not require any permissions.
# 'New'		Present an empty form, ready to be filled in.
# 'Show'	The cgi form data contains the id of an event to display, no editing allowed.  This does not require any permissions.
# 'Update'	the cgi form data contains data for an event to modify.
dowhat = tow.form.getfirst('Do')
if dowhat not in ('Add', 'Delete', 'Edit', 'New', 'Show', 'Update'):
    dowhat = 'List'

if dowhat not in ('List', 'Show'):
    tow.check_authorized("event")

if dowhat in ('Add', 'Update'):
    try:
        t_e['event_id'] = tow.form.getfirst('id')
        t_e['name'] = tow.form.getfirst('na')
        t_e['type'] = tow.form.getfirst('ty')
        t_e['starts_on'] = tow.form.getfirst('so')
        t_e['ends_on'] = tow.form.getfirst('eo')
        t_e['base_cost'] = tow.form.getfirst('bc')
        t_e['ceus'] = tow.form.getfirst('cu')
        t_e['notes'] = tow.form.getfirst('no')
        if t_e['ends_on'] is None:
            t_e['ends_on'] = t_e['starts_on']
        if t_e['ceus'] == '':
            t_e['ceus'] = None
        if t_e['notes'] == '':
            t_e['notes'] = None

# Now we can do things that might throw an exception
        t_e['starts_on'] = tow.store_date(t_e['starts_on'])
        t_e['ends_on'] = tow.store_date(t_e['ends_on'])
        t_e['base_cost'] = tow.store_cash(t_e['base_cost'])
        if t_e['type'] not in tow.enum('event_type'):
            tow.add_error("Invalid event type in form input ", t_e)

        t_e_p = tow.get_list(
  (('px', 'delete'), ('pi', 'person_id'), ('poi', 'old_person_id'),
  ('pn', 'name'),
  ('napn', 'new_address'), ('nppn', 'new_phone'), ('nepn', 'new_email'),
  ('pt', 'type', 'Unknown'), ('pot', 'old_type'),
  ('ps', 'status', 'Unknown'), ('pos', 'old_status'),
  ('pp', 'payment_status', 'Unknown'), ('pop', 'old_payment_status'),
  ('pe', 'enrolled_d'), ('poe', 'old_enrolled')))
        m = len(t_e_p)
        n = 0
        pete = tow.enum('person_event_type')
        pese = tow.enum('person_event_status')
        pepse = tow.enum(person_event_payment_status')
        while n < m:
            i = t_e_p[n]
            if i['person_id'] == '' and i['old_person_id'] == '' and i['name'] == '':
                del t_e_p[n]
                m -= 1
                continue
            if i['type'] not in pete or (i['old_type'] != '' and i['old_type'] not in pete:
                tow.add_error("Invalid type or old type in form input ", i)
            if i['status'] not in pese or (i['old_status'] != '' and i['old_status'] not in pese:
                tow.add_error("Invalid status or old status in form input ", i)
            if i['payment_status'] not in pepse or (i['old_payment_status'] != '' and i['old_payment_status'] not in pepse):
                tow.add_error("Invalid payment or old payment in form input ", i)
            i['enrolled_s'] = tow.store_date(i['enrolled_d'])
            n += 1

    except:
        tow.add_error('Invalid or missing data: ', traceback.format_exc().replace('\n','  '))
elif dowhat == 'Show' or dowhat == 'Edit':
    event_id = tow.form.getfirst('id')

    tow.cur.execute('select name, type, starts_on, ends_on, base_cost, ceus, event_notes from tow_event where event_id = %(event_id)s', {'event_id': event_id})
    resp = tow.cur.fetchall()
    if len(resp) != 1:
        tow.add_error("Event id ', event_id, ' not found")
    else:
        resp = resp[0]
        t_e = {
 'event_id': event_id,
 'name': resp[0],
 'type': resp[1],
 'starts_on': tow.store_date(resp[2]),
 'ends_on': tow.store_date(resp[3]),
 'base_cost': resp[4],
 'ceus': resp[5],
 'notes': resp[6] }

# FIXME: This is a horrible but self-contained kludge to get the attendees sorted by name
# Really we should use the tow.person_sort_by_id hash, but this is self-contained
        tow.cur.execute("select person_id, type, status, payment_status, enrolled from tow_person_event natural join tow_person where event_id = %(event_id)s order by type, last_name, first_name, craft_name", t_e)
        tow.check_warnings()
        for resp in tow.fetchrows():
            t_e_p.append({'person_id': tow.s(resp[0]), 'old_person_id': tow.s(resp[0]), 'name': tow.person_id_to_name(resp[0]), 'type': resp[1], 'old_type': resp[1], 'status': resp[2], 'old_status': resp[2], 'payment_status': resp[3], 'old_payment_status': resp[3], 'enrolled_s': resp[4], 'enrolled_d': tow.display_date(resp[4]), 'old_enrolled': resp[4]})

elif dowhat == 'Delete':
    t_e['event_id'] = tow.form.getfirst('id')

## if there is something to do, do it
if len(tow.problems) == 0:
    try:
        sys.stderr.write(tow.s('Attempting ', dowhat, ' on ', t_e, ' with ', t_e_p))
        if dowhat == 'Add':
            cmd = "insert into tow_event (name, type, starts_on, ends_on, base_cost, ceus, event_notes ) values ( %(name)s, %(type)s, %(starts_on)s, %(ends_on)s, %(base_cost)s, %(ceus)s, %(notes)s )"
            arg = t_e
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd, arg)
            event_id = tow.cur.lastrowid
            tow.conn.commit()
            t_e['event_id'] = event_id
            for i in t_e_p:
                if i['person_id'] == '':
                    i['person_id'] = tow.add_person({'name': i['name'], 'address': i['new_address'], 'phone': i['new_phone'], 'email': i['new_email']})
                    del i['new_address']
                    del i['new_phone']
                    del i['new_email']
                i['event_id'] = event_id
                add_p_e(i)
            tow.refresh_events()
            tow.add_note("Event ", tow.display_text(t_e['name']), " created with ", len(t_e_p), " attendees.")

        elif dowhat == 'Update':
            if 'event_id' not in t_e or t_e['event_id'] is None:
                raise ValueError("Unknown/missing event_id")
            cmd = "update tow_event set name = %(name)s, type =%(type)s, starts_on = %(starts_on)s, ends_on = %(ends_on)s, base_cost = %(base_cost)s, ceus = %(ceus)s, event_notes = %(notes)s where event_id = %(event_id)s"
            arg = t_e
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd, arg)

#  (('px', 'delete'), ('pi', 'person_id'), ('poi', 'old_person_id'),
#  ('pt', 'type', 'Unknown'), ('pot', 'old_type'),
#  ('ps', 'status', 'Unknown'), ('pos', 'old_status'),
#  ('pp', 'payment_status', 'Unknown'), ('pop', 'old_payment_status')))
#  ('pe', 'enrolled'), ('poe', 'old_enrolled')...
            n = 0
            m = len(t_e_p)
            while n < m:
                i = t_e_p[n]
                i['event_id'] = t_e['event_id']
                if i.get('delete') or (i['person_id'] == '' and i['name'] == ''):
                    if i['old_person_id'] != '':
                        del_p_e(i)
                        tow.add_note('Attendee ', tow.person_id_to_name(i['old_person_id']), ' deleted.')
                    else:
                        pass
                    del t_e_p[n]
                    m -= 1
                elif i['old_person_id'] == '':
                    if not i.get('person_id'):
                        i['person_id'] = tow.add_person({'name': i['name'], 'address': i['new_address'], 'phone': i['new_phone'], 'email': i['new_email']})
                        del i['new_address']
                        del i['new_phone']
                        del i['new_email']
                    add_p_e(i)
                    n += 1
                    tow.add_note("Attendee ", i['name'], ' added.')
                elif i['person_id'] != i['old_person_id']:
                    old_name = tow.person_id_to_name(i['old_person_id'])
                    del_p_e(i)
                    if i['person_id'] == '':
                        i['person_id'] = tow.add_person({'name': i['name'], 'address': i['new_address'], 'phone': i['new_phone'], 'email': i['new_email']})
                        del i['new_address']
                        del i['new_phone']
                        del i['new_email']
                    add_p_e(i)
                    n += 1
                    tow.add_note('Attendee ', old_name, ' replaced with ', i['name'], '.')
                elif \
 i['type'] == i['old_type'] and \
 i['status'] == i['old_status'] and \
 i['payment_status'] == i['old_payment_status'] and \
 ( i['enrolled_s'] == i['old_enrolled'] or ( i['enrolled_s'] is None and i['old_enrolled'] == '')):
                    n += 1
#                    tow.add_note("Skipping attendee ", i)
                else:
                    cmd = "update tow_person_event set type = %(type)s, status = %(status)s, payment_status = %(payment_status)s, enrolled = %(enrolled_s)s where event_id = %(event_id)s and person_id = %(person_id)s"
                    arg = i
                    tow.cur.execute(cmd, arg)
                    i['old_type'] = i['type']
                    i['old_status'] = i['status']
                    i['old_payment_status'] = i['payment_status']
                    i['old_enrolled'] = i['enrolled_s']
                    n += 1
                    tow.add_note("Attendee ", i['name'], ' updated.')
            tow.refresh_events()
            tow.add_note("Event ", tow.display_text(t_e['name']), ' updated.')

        elif dowhat == 'Delete':
            cmd = "delete from tow_person_event where event_id = %(event_id)s"
            arg = { 'event_id': t_e['event_id'] }
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd, arg)
            cmd = "delete from tow_event where event_id = %(event_id)s"
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd, arg)
            tow.add_note('Event ', tow.display_text(tow.event_id_to_name(t_e['event_id'])), ' deleted.')
            clear_event()
            tow.refresh_events()
    except mysql.connector.IntegrityError:
        tow.add_error('Database integrity error: ', traceback.format_exc().replace('\n','  '))

    except:
        tow.add_error('Error occurred: ', traceback.format_exc().replace('\n','  '))

if dowhat == 'Show':
    tmp = tow.display_text(t_e['name'])
    tow.start_page('Show Event ' + tmp, style = tow.st)
    s_s = '<h2>' + t_e['type']
    if t_e['starts_on'] == t_e['ends_on']:
        s_s += ' on ' + tow.display_date(t_e['starts_on'])
    else:
        s_s += ' from '+tow.display_date(t_e['starts_on'])+' to '+tow.display_date(t_e['ends_on'])
    if t_e['base_cost']:
        s_s += ' donation '+tow.display_cash(t_e['base_cost'])
    if t_e['ceus']:
        s_s += ' '+tow.display_text(t_e['ceus'])+' CEUs'
    if t_e['notes']:
        s_s += ' notes: '+tow.display_text(t_e['notes'])
    s_s += '</h2><br>'
    print s_s
    if len(t_e_p) > 0:
        n = 0
        print '<table style="margin:0px auto" border="2"><caption>Attendees</caption><thead><tr><th>##<th>Attendee<th>As<th>Status<th>Payment<th>Enrolled On</thead><tbody>'
        for i in t_e_p:
            name = tow.display_text(i['name'])
            if 'person' in tow.permissions:
                person = tow.a('person', text = name, opts = {'Do': 'Show', 'id': i['person_id']})
            else:
                person = name
            print tow.s('        <tr><td>', n, td, person, td, i['type'], td, i['status'], td, i['payment_status'], td, i['enrolled_d'])
            n += 1
        print '</tbody></table>'
        if 'event' in tow.permissions:
            print tow.s(
'      <span class="b3">\n',
'        <form action="', tow.url('event'), '" method="GET">\n',
'          <input type="submit" name="Do" value="Edit" />\n',
'          <input type="hidden" name="id", value="', t_e['event_id'], '"/>\n',
'        </form>\n',
'      </span><br><br>\n')

# FIXME?    ...
elif dowhat != 'List':
    script_var = tow.var_list('attendee_types',tow.enum('person_event_type')) + \
 tow.var_list('attendee_statuses', tow.enum('person_event_status') + \
 tow.var_list('attendee_payments', tow.enum('person_event_payment_status')) + \
 'var the_people=['
    sep = ''
    n = 1
    for i in t_e_p:
        pn = 'New'
        if i['old_status'] != '':
            pn = n
            n += 1
        checked = 0
        if i.get('delete'):
            checked = 1
        j = { 'pn': pn, 'checked': checked}
        for e in ('person_id', 'old_person_id', 'name', 'type', 'old_type', 'status', 'old_status', 'payment_status', 'old_payment_status', 'enrolled_d', 'old_enrolled', 'new_address', 'new_phone', 'new_email'):
            j[e] = i.get(e)
        script_var += sep + tow.var_hash(j, ('pn', 'old_person_id', 'old_type', 'old_status', 'old_payment_status', 'old_enrolled', 'checked', 'person_id', 'name', 'type', 'status', 'payment_status', 'enrolled_d', 'new_address', 'new_phone', 'new_email'))
        sep = ','
    script_var += sep + 'null];\nvar all_people_byname={'
    sep = ''
    for (i, n) in zip(tow.person_id_list, tow.person_list):
        script_var += sep + tow.var_text(n) + ':' + i
        sep = ','
    script_var += '};\n'

    script_var += '''

function new_n_p_e(i,l){
  if(l==null){
    l=['','',''];
  }
  return mk_ele('tr',{'id': 'n'+i},mk_ele('td',{'colspan':7},mk_text('Address'),mk_input_text('na'+i,l[0]),mk_text('Phone'),mk_input_text('np'+i,l[1]),mk_text('Email'),mk_input_text('ne'+i,l[2])));
}

function add_new_person(e) {
  e.parentNode.parentNode.removeChild(e.parentNode);
  var t=document.getElementById(e.getAttribute('choose_in'));
  var n=new_n_p_e(t.id,null);
  t.parentNode.parentNode.parentNode.insertBefore(n,t.parentNode.parentNode.nextSibling);
  t.setAttribute('has_new',n.id);
  t.removeAttribute('has_menu');
}

function new_p_e(m,l) {
  var a=null;
  if (l==null){
    l=['New','','','','','',0,'','','Unknown','Unknown','Unknown',''];
    a={'onchange':'row_changed(this,"new_p_e",event);',
       'onkeydown':'row_changed(this,"new_p_e",event);'};
  }
  return mk_tr(a,
[ mk_text(l[0]),
  mk_input_hidden('poi'+m,l[1]),
  mk_input_hidden('pot'+m,l[2]),
  mk_input_hidden('pos'+m,l[3]),
  mk_input_hidden('pop'+m,l[4]),
  mk_input_hidden('poe'+m,l[5])],
mk_input_checkbox('px'+m,l[6]),
[ 
  mk_input_hidden('pi'+m,l[7]),
  mk_ele('input', {
    'id':'pn'+m,
    'choices':'all_people_byname',
    'allow_new':'add_new_person',
    'name':'pn'+m,
    'type':'text',
    'value':l[8],
    'onkeyup':'setTimeout(function(){changed(event.target);},2);',
    'onchange':'changed(event.target);'})],
mk_input_select('pt'+m,attendee_types,l[9]),
mk_input_select('ps'+m,attendee_statuses,l[10]),
mk_input_select('pp'+m,attendee_payments,l[11]),
mk_input_text('pe'+m,l[12]));
}

function setup() {
  for(var i=0;i<the_people.length;i++){
    var m = people.getAttribute('max');
    add_row(people,'new_p_e',the_people[i]);
    if (the_people[i][13] != '' || the_people[i][14] != '' || the_people[i][15] != '') {
      var tmp=new_n_p_e(m,[the_people[i][13], the_people[i][14], the_people[i][15]]);
      people.lastChild.setAttribute('has_new',tmp.getAttribute('id'));
      people.appendChild(tmp);
    }
  }
}
'''
    if t_e['name']:
        tmp = 'Edit Event ' + tow.display_text(t_e['name'])
    else:
        tmp = 'Add New Event'

    tow.start_page(tmp, style = tow.st, script = tow.script_common + tow.script_add_row + tow.script_choose + script_var, onload='setup();')
    print '      <form action="' + tow.url('event') + '" method="POST">\n' + \
 '        <span class="c1"><label for="na">Event&nbsp;</label><span>' + \
   '<input type="text" name="na" value="' +  tow.display_text(t_e['name']) + \
   '"/></span></span><br>\n' + \
 '        <span class="c6a">' + tow.dropdown("ty", tow.enum('event_type'), \
    title = "Type", default = t_e['type']) + '</span>\n' + \
 '        <span class="c6"><label for="so">Starts On&nbsp;</label><span>' + \
    '<input type="text" name="so" value="' +  tow.display_date(t_e['starts_on']) + \
    '"/></span></span>\n' + \
 '        <span class="c6"><label for="eo">&nbsp;&nbsp;Ends On&nbsp;</label><span>' + \
    '<input type="text" name="eo" value="' +  tow.display_date(t_e['ends_on']) + \
 '"/></span></span>\n' + \
 '        <span class="c6"><label for="bc">&nbsp;&nbsp;Base Cost&nbsp;</label>' + \
     '<span><input type="text" name="bc" value="' + tow.display_cash(t_e['base_cost']) + \
     '" /></span></span>\n' + \
 '        <span class="c6"><label for="cu">&nbsp;&nbsp;CEUs&nbsp;</label><span>' + \
    '<input type="text" name="cu" value="' + tow.display_text(t_e['ceus']) + \
    '" /></span></span><br>\n' + \
 '        <span class="c1"><label for="no">&nbsp;&nbsp;Notes&nbsp;</label><span>' + \
    '<input type="text" name="no" value="' + tow.display_text(t_e['notes']) + '" />' + \
    '</span></span>\n' + \
 '        <br><br>'

    # 'px': 'delete', 'pi': 'person_id', 'pt': 'type', 'ps': 'status', 'pp': 'payment_status'
    n = 0
    print '<table style="margin:0px auto" border="2"><caption>Attendees</caption><thead><tr><th>##<th>[Delete]<th>Attendee<th>As<th>Status<th>Payment<th>Enrolled On</thead><tbody id="people" max="0">'
    print '        </tbody></table>'

    print '        <span class="b3"><input type="submit" name="Do" value="New" /></span>'
    if t_e.get('event_id'):
        print tow.s('        <input type="hidden" name="id", value="', t_e['event_id'], """" />
        <span class="b3"><input type="submit" name="Do" value="Update" /></span>
        <span class="b3"><input type="submit" name="Do" value="Delete" /></span>""")
    else:
        print '        <span class="b3"><input type="submit" name="Do" value="Add" /></span>'
    print '      </form><br><br>'

else:
    tow.start_page("List Events", 'List Events', style = tow.st)
    if 'event' in tow.permissions:
        print '      <span class="b3"><form action="' + tow.url('event') + '" method="POST">\n        <input type="submit" name="Do" value="New" />\n      </form></span><br><br>'

##### Report Section #########################################################
# FIXME: How to specify not past events, only past events, etc?
tow.cur.execute('select event_id, name, starts_on, ends_on from tow_event order by event_id desc limit 20')

h1 = '      <hr style="color:#c00;background-color:#c00;height:4"/>'
h2 = '      <table style="margin:0px auto" border="1"><caption>Recently Added Events</caption><thead><tr><th>Event<th>Starts on<th>Ends on<th>Export to CSV</thead><tbody>'
t1 = None

if 'event' in tow.permissions:
    cmd = 'Edit'
else:
    cmd = 'Show'

for resp in tow.fetchrows():
    if h1 is not None:
        print h1
        print h2
        h1 = None
        t1 = '      </tbody></table>'
    (event_id, name, starts_on, ends_on) = resp
    print '<tr><td>' + tow.a('event', text = tow.display_text(name), opts = {'Do': cmd, 'id': event_id}) + '<td>' + tow.display_date(starts_on)+'<td>'+tow.display_date(ends_on)+'<td>' + tow.a('event-export', text = 'Export', opts = {'id': event_id})
    resp = tow.cur.fetchone()
if t1 is not None:
    print t1

tow.end_page()
