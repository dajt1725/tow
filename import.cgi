#!/usr/bin/python

import sys, string, traceback, StringIO, csv, types, re
sys.path.insert(0,'/home/temple24/python')
import tow

def strip_time(s):
    return s.split(' ')[0]

tow.check_authorized('person')

ignored_fields = (
  '1', 
  'guest(s)',
  'timestamp',
  'are you applying for the in-person or online class?',
  'emergency contact',
  'you must indicate your agreement to apply',
  'guest of first name',
  'guest of last name',
  'payment type',
  'fee type',
  'promo code',
  'code type',
  'discount percent',
  'discount amount',
  'minimum donation quantity',
  'minimum donation price',
  'registered for afternoon workshop quantity',
  'registered for afternoon workshop price',
  'suggested donation quantity',
  'suggested donation price',
  'workshop donation quantity',
  'workshop donation price',
  'workshop & evening ritual price',
  'workshop & evening ritual quantity',
  'minimum donation quantity',
  'minimum donation price',
  'suggested donation quantity',
  'suggested donation price',
  'attending evening ritual quantity',
  'attending evening ritual price',
  'event fee price',
  'event fee quantity',
  'total',
  'total price',
  'children (age 6 and under) price',
  'children (age 6 and under) quantity',
  'children (ages 7 to 12) price',
  'children (ages 7 to 12) quantity',
  'child (ages 7 to 12) price',
  'child (ages 7 to 12) quantity',)

ignored_re = (
  re.compile('witchcraft iii is a prerequisite for this course'),
  re.compile('witchcraft iv requires a regular '),
  re.compile('witchcraft iv is a purposely intellectually challenging course'),
  re.compile('what do you think will be '),
  re.compile('do you currently or in the past '),
  re.compile('have you ever experienced or suffered from '),
  re.compile('are you prepared to make a commitment of study '),
  re.compile('have you ever registered for this course before '),
  re.compile('did you have a mentor in the previous level of study'),
  re.compile('do you have any questions'),
  re.compile('legal name'),
  re.compile('i understand that submission of the above information '),)

_person_membership_status = ('person', 'membership_status', {
      'honored (mystery school student or graduate)': 'Honored',
      'honored (mystery school student)': 'Honored',
      'general (three or more events)': 'General',
      'general (three or more events attended)': 'General',
      'ministerial (seminary graduate)': 'Ministerial',
      'none': 'Nonmember',
    })

_reg_status = ('event', 'status', {
    'registered': 'Signed-Up',
    'cancelled': 'Cancelled',
    'abandoned': 'Error',
   })

_payment_status = ('event', 'payment_status', {
    'paid': 'Paid',
    'pending': 'Not Paid',
    'na': 'Unknown',
    'incomplete': 'Error',
    'refunded': 'Not Paid',
  })

mapping = {
  'first name': ('person', 'first_name'),
  'first name:': ('person', 'first_name'),
  '\xef\xbb\xbffirst name:': ('person', 'first_name'),
  '???first name:': ('person', 'first_name'),

  'last name':  ('person', 'last_name'),
  'last name:': ('person', 'last_name'),

  'craft name': ('person', 'craft_name'),
  'magickal/craft name (if any)': ('person', 'craft_name'),

  'email address:': ('person', 'email'),
  'email address': ('person', 'email'),
  'e-mail address': ('person', 'email'),
  'email': ('person', 'email'),

  'what is your level of temple membership?': _person_membership_status,
  'level of temple membership': _person_membership_status,

  'phone number': ('person', 'phone'),

  'street address': ('person', 'street_address_1'),
  'city': ('person', 'town_village_city'),
  'state/province': ('person', 'province_state'),
  'mailing code': ('person', 'postal_code'),
  'country': ('person', 'country'),

  'birth date': ('person', 'date_of_birth'),
  'astrological Information': ('person', 'date_of_birth'),

  'gender': ('person', 'gender'),

  'registration date': ('event', 'enrolled_d', strip_time),
  'date submitted': ('event', 'enrolled_d', strip_time),
  'reg date': ('event', 'enrolled_d', strip_time),

  'registration status': _reg_status,
  'reg status': _reg_status,

  'payment status': _payment_status,
  'pay status': _payment_status,
 }

people = []
unknown = []
unknown_fields = []
try:
    event_name = tow.form.getfirst('event')
    event_id = tow.find_event({'name': event_name})

    attending = {}
    tow.cur.execute("select person_id, type, status, payment_status, enrolled from tow_person_event where event_id = %(event_id)s", {'event_id': event_id})
    tow.check_warnings()
    for resp in tow.fetchrows():
        attending[resp[0]] = { 'type': resp[1], 'status': resp[2], 'payment_status': resp[3], 'enrolled_s': resp[4]}
    file = tow.form.getfirst('file')
    if file is None or file == '':
        raise ValueError('Invalid or missing file uploaded')
    infile = StringIO.StringIO(file)
    reader = csv.DictReader(infile)
#    unknown.append(repr(reader.fieldnames))
    for row in reader:
        line = { 'person': {}, 'event': {}, 'ignored': {}}
        a = row.keys()
        for i in a:
            v = row[i]
            if v == '':
                del row[i]
                continue
            ii = i.lower()
            if ii not in mapping:
                if ii not in ignored_fields:
                    found = False
                    for j in ignored_re:
                       if j.search(ii):
                           found = True
                           break
                    if not found and i not in unknown_fields:
                        unknown_fields.append(i)
                del row[i]
                continue
            j = mapping[ii]
            if len(j) > 2:
                k = j[2]
                if type(k) == dict:
                    vv = v.lower()
                    if vv not in k:
                        unknown.append(tow.s('Entry ', v, ' not found in ', k))
                        v = None
                    else:
                        v = k[vv]
                elif type(k) == types.FunctionType:
                    v = k(v)
                else:
                    v = k
            line[j[0]][j[1]] = v
            del row[i]
        if len(row) > 0:
            unknown.append(row)
        if len(line['person']) > 0 or len(line['event']) > 0 or len(line['ignored']) > 0:
            people.append(line)

    if len(unknown_fields) > 0:
        tow.add_error("Unknown fields found: ", repr(unknown_fields))
    for i in unknown:
        tow.add_error("Unknown fields in ", i)

    people_added = 0
    added_to_event = 0
    for line in people:
        if line['event'].get('status') == 'Error' or line['event'].get('payment_status') == 'Error':
            continue
        person = line['person']
        person_id_list = tow.find_people(person)
        if person_id_list is None:
            try:
                person_id = tow.add_person(person)
                people_added += 1
#                tow.add_note("Attempting to add person ", repr(person))
            except:
                tow.add_note("Could not add person: ", person)
                person_id = None
        else:
            if len(person_id_list) > 1:
                tow.add_note("Found multiple people for ", person, ", picking one at random")
            person_id = person_id_list[0]
        if person_id:
            if person_id in attending:
                tow.add_note(tow.person_id_to_name(person_id), ' is already entened as attending ', line['event'], ' vs ', attending[person_id])
# FIXME: add error checknig here, see if imported version of attendence matches
# the version already in the database.
            else:
                event = line['event']
                event['person_id'] = person_id
                event['event_id'] = event_id
                event['type'] = 'Student'
                if not 'status' in event:
                    event['status'] = 'Signed-Up'
                    tow.add_note('Attempting to add status to event for ', person)
                if not 'payment_status' in event:
                    event['payment_status'] = 'Unknown'
                    tow.add_note('Attempting to add payment status to event for ', person)
                if not 'enrolled_d' in event:
                    event['enrolled_s'] = None
                else:
                    event['enrolled_s'] = tow.store_date(event['enrolled_d'])
                try:
                    tow.add_person_event(event)
                    added_to_event += 1
                except:
                    tow.add_error("Failed to add ", tow.person_id_to_name(person_id), " to event ", event)

    tow.add_note("Attempting to add ", people_added, " people")
    tow.add_note("Attempting to add ", added_to_event, " attendees to ", event_name)

except:
    tow.add_error('Error occurred: ', traceback.format_exc().replace('\n','  '))

tow.start_page('Import Results')
print tow.a('event', text="View/Edit Event "+event_name, opts = { 'Do': 'Edit', 'id': event_id }) + '<br>'
tow.end_page()

