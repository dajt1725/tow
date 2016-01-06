#!/usr/bin/python
import sys, string, traceback
sys.path.insert(0,'/home/temple24/python')
import tow

tow.check_authorized('person')

def quote(s):
    if s is None:
        return ''
    if '"' in s:
        return '"'+s.replace('"','""')+'"'
    elif ',' in s:
        return '"'+s+'"'
    else:
        return s

filename = tow.form.getfirst('filename')
if filename is None or filename == '':
    filename = 'person'
template = tow.form.getfirst('fields')
if template is None or template == '':
    template = ('first_name', 'last_name', 'email', 'phone', 'street_address_1', 'street_address_2', 'town_village_city', 'province_state', 'postal_code', 'country')
else:
    template = template.split(',')
condition = tow.form.getfirst('conditions')
if condition is None or condition == '':
    condition = 'True'

to_print = []
try:
    tow.cur.execute("""select
 p.first_name,
 p.last_name,
 p.craft_name,
 p.membership_status,
 p.member_since,
 p.street_address_1,
 p.street_address_2,
 p.town_village_city,
 p.province_state,
 p.postal_code,
 p.country,
 p.date_of_birth,
 p.gender,
 p.is_ordained,
 p.ordination_date,
 p.ordination_renewal_date,
 p.person_notes,
 p.volunteer_status,
 p.ministries,
 any_em.any_email,
 em.email,
 em_h.email_home,
 em_w.email_work,
 any_ph.any_phone,
 ph.phone,
 ph_c.phone_cell,
 ph_h.phone_home,
 ph_w.phone_work
    from tow_person as p
       natural left join (select person_id, max(address) as any_email from tow_contact where type in ('email','email/home','email/work') group by person_id) as any_em
       natural left join (select person_id, max(address) as email from tow_contact where type = 'email' group by person_id) as em
       natural left join (select person_id, max(address) as email_home from tow_contact where type = 'email/home' group by person_id) as em_h
       natural left join (select person_id, max(address) as email_work from tow_contact where type = 'email/work' group by person_id) as em_w
       natural left join (select person_id, max(address) as any_phone from tow_contact where type in ('phone','phone/cell','phone/home','phone/work') group by person_id) as any_ph
       natural left join (select person_id, max(address) as phone from tow_contact where type = 'phone' group by person_id) as ph
       natural left join (select person_id, max(address) as phone_cell from tow_contact where type = 'phone/cell' group by person_id) as ph_c
       natural left join (select person_id, max(address) as phone_home from tow_contact where type = 'phone/home' group by person_id) as ph_h
       natural left join (select person_id, max(address) as phone_work from tow_contact where type = 'phone/work' group by person_id) as ph_w""", {})
    for resp in tow.fetchrows():
        person = {}
        person['first_name'] = quote(resp[0])
        person['last_name'] = quote(resp[1])
        person['craft_name'] = quote(resp[2])
        person['membership_status'] = resp[3]
        person['member_since'] = tow.display_date(resp[4])
        person['street_address_1'] = quote(resp[5])
        person['street_address_2'] = quote(resp[6])
        person['town_village_city'] = quote(resp[7])
        person['province_state'] = quote(resp[8])
        person['postal_code'] = quote(resp[9])
        person['country'] = quote(resp[10])
        person['date_of_birth'] = tow.display_date(resp[11])
        person['gender'] = resp[12]
        person['is_ordained'] = resp[13]
        person['ordination_date'] = tow.display_date(resp[14])
        person['ordination_renewal_date'] = tow.display_date(resp[15])
        person['notes'] = quote(resp[16])
        person['volunteer_status'] = resp[17]
        person['ministries'] = tow.display_set(resp[18])
        person['any_email'] = quote(resp[19])
        person['email'] = quote(resp[20])
        person['email_home'] = quote(resp[21])
        person['email_work'] = quote(resp[22])
        person['any_phone'] = quote(resp[23])
        person['phone'] = quote(resp[24])
        person['phone_cell'] = quote(resp[25])
        person['phone_home'] = quote(resp[26])
        person['phone_work'] = quote(resp[27])

        do_print = eval(condition, person)
        if do_print is True:
            val = []
            for field in template:
                val.append(person[field])
            val = string.join(val,',')+'\r'
            to_print.append(val)
    print 'Content-type: text/csv\nContent-disposition: attachment; filename='+filename+'.csv\n'
    for i in to_print:
        print i
    tow.fini()

except:
    tow.add_error('Error occurred: ', traceback.format_exc().replace('\n','  '))
    tow.start_page('People Export Error','People Export Error', redir_to = 'home')
    tow.end_page()

