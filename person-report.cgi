#!/usr/bin/python
import sys, string, urllib, re
sys.path.insert(0,'/home/temple24/python')
import tow

tow.check_authorized('person')
td = tow.td
a = ' and '
##### slurp up the form data into form ########################################
# gather any data from form
field_txt = ''
field = tow.form.getfirst('field')
if field is not None:
    field_txt = '<input type="hidden" name="field" value="' + field + '"/>'
value_txt = ''
value = tow.form.getfirst('value')
if value is not None:
    value_txt = '<input type="hidden" name="value" value="' + value + '"/>'

label = ''
people = []
if field == 'name':
    r = re.compile(value,flags=re.IGNORECASE)
    for (name, id) in zip(tow.person_list, tow.person_id_list):
        if r.search(name):
            people.append(int(id))
        label = 'whose names contain ' + value
else:
    clause = ''
    conj = ' where '
    if field == 'fname':
        clause += conj + 'first_name like %(value)s'
        conj = a
        label = 'whose first name is ' + value
    elif field == 'lname':
        clause += conj + 'last_name like %(value)s'
        conj = a
        label = 'whose last name is ' + value
    elif field == 'cname':
        clause += conj + 'craft_name like %(value)s'
        conj = a
        label = 'whose craft name is ' + value
    elif field == 'dob':
        clause += conj + 'date_of_birth = cast(%(value)s as date)'
        conj = a
        label = 'who were born on ' + value
        value = tow.store_date(value)
    elif field == 'since':
        clause += conj + 'member_since = cast(%(value)s as date)'
        conj = a
        label = 'who have been members since ' + value
        value = tow.store_date(value)
    elif field == 'gender':
        clause += conj + 'gender = %(value)s'
        conj = a
        label = 'whose gender is ' + value
    elif field == 'status':
        clause += conj + 'membership_status = %(value)s'
        conj = a
        label = 'whose membership status is ' + value
    elif field == 'vs':
        clause += conj + 'volunteer_status = %(value)s'
        conj = a
        label = 'whose volunteer status is ' + value
    elif field is None:
        pass
    else:
        tow.add_error('Ignoring unknown field ', field)

    tow.cur.execute('select person_id from tow_person natural left join tow_contact ' + clause , {'value': value})
    for resp in tow.fetchrows():
        people.append(resp[0])

tow.start_page("People Report", "People Report")
print '      <h3>People ' + label + '</h3><br>'
if len(people) == 0:
    print '      <h4>No people found</h4>'
else:
    print '      <form action="' + tow.url('merge') + '">' + field_txt + value_txt + '<input type="submit" value="Merge"><br><table style="margin:0px auto" border="1"><thead><tr><th>Left<th>Right<th>Name<th>Address<th>Contact<th>Status<th>Since<th>DoB<th>Gender</thead><tbody>'
    sorted_people = {}
    for person_id in people:
        sorted_people[tow.person_sort_by_id[person_id]] = person_id
    for i in sorted(sorted_people.keys()):
        person_id = sorted_people[i]

        tow.cur.execute('select membership_status,member_since,date_of_birth,gender,street_address_1,street_address_2,town_village_city,province_state,postal_code,country from tow_person where person_id = %(person_id)s', {'person_id': person_id})
        resp = tow.cur.fetchall()
        if len(resp)!=1:
            status = 'Unknown'
            since = ''
            dob = ''
            gender = 'Unknown'
            addr = ''
# Log error?
        else:
            resp = resp[0]
            status = resp[0]
            since = tow.display_date(resp[1])
            dob = tow.display_date(resp[2])
            gender = resp[3]
            addr = ''
            sep = ''
            if resp[4]:
                addr += sep + tow.display_text(resp[4])
                sep = '<br>'
            if resp[5]:
                addr += sep + tow.display_text(resp[5])
                sep = '<br>'
            if resp[6]:
                addr += sep + tow.display_text(resp[6])
                sep = ', '
            if resp[7]:
                addr += sep + tow.display_text(resp[7])
                sep = '  '
            if resp[8]:
                addr += sep + tow.display_text(resp[8])
                sep = '  '
            if resp[9]:
                addr += sep + tow.display_text(resp[9])
                sep = '  '

        contact = ''
        sep = ''
        tow.cur.execute('select type, address from tow_contact where person_id = %(person_id)s', {'person_id': person_id})
        for resp in tow.fetchrows():
            contact += sep + resp[0] + ': '+tow.display_text(resp[1])
            sep = '<br>'

        name = tow.a('person', text = tow.display_text(tow.person_id_to_name(person_id)), opts = {'Do': 'Show', 'id': tow.s(person_id)})
        a = '      <tr><td><input type="radio" name="left" value="'+tow.s(person_id)+'">'+td+'<input type="radio" name="right" value="'+tow.s(person_id)+'">'+td+name+td+addr+td+contact+td+status+td+since+td+dob+td+gender
        print a
    print '</tbody></table><input type="submit" value="Merge"></form>'
tow.end_page()
