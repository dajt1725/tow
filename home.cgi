#!/usr/bin/python
#!C:\Python27\Python.exe
import sys, urllib
sys.path.insert(0,'/home/temple24/python')
import tow
div = '    <div style="background: beige; border-style: solid; border-width: 1">'
xdiv = '</div><br>\n'

person = ''
person_export = ''
person_report = ''
user = ''
donation_report = ''

script_var = None
#        <option value="addr">Address</option>
#        <option value="phone">Phone</option>
#        <option value="email">Email</option>
#        <option value="gender">Gender</option>
#        <option value="contact">Any Contact</option>
#        <option value="contNotes">Contact Notes</option>
#        <option value="ordained">Is Ordained</option>
#        <option value="ordOn">Ordination Date</option>
#        <option value="ordRenOn">Ordination Renewal Date</option>
#        <option value="ministries">Ministries</option>
#        <option value="notes">Notes</option>

mprt = ''

if 'person' in tow.permissions:
    person = div + tow.a('person', text = 'View/Edit people') + xdiv
    person_export = div + '<form action="' + tow.url('person-export') + '''" method="POST">
      <span class="c2a"><input type="submit" value="Export"/> people to CSV file</span>
      <span class="c2a"><label>Save As&nbsp;&nbsp;<input type="text" name="filename" value="person"/>.csv</label></span><br>
      <span class="c1"><label for="fields">Fields to export</label><span><input type="text" name="fields" value="first_name,last_name,any_email,any_phone,street_address_1,street_address_2,town_village_city,province_state,postal_code,country"/></span></span><br>
      <span class="c1"><label for="conditions">Only export people where</label><span><input type="text" name="conditions"/></span></span><br><br>
    </form>''' + xdiv

    person_report = div + '<form action="' + tow.url('person-report') + '''" method="POST">
      <span class="c1">
        <input style="float:left;width:auto;" type="submit" value="Find Person/People"/><label for="field">&nbsp;where&nbsp;</label><select name="field">
        <option value="" selected>(All People)</option>
        <option value="name">Name</option>
        <option value="fname">First Name</option>
        <option value="lname">Last Name</option>
        <option value="cname">Craft Name</option>
        <option value="contact">Contact Address</option>
        <option value="dob">Date of Birth</option>
        <option value="gender">Gender</option>
        <option value="status">Membership Status</option>
        <option value="since">Member Since</option>
        <option value="vs">Volunteer Status</option>
      </select><label for="value">&nbsp;is&nbsp;</label><span><input type="text" name="value"/></span></span><br>
    </form>''' + xdiv

    script_var = tow.script_common + tow.script_choose + 'var all_events_byname={'
    sep = ''
    for (i, n) in zip(tow.event_id_list, tow.event_list):
        script_var += sep + tow.var_text(n) + ':' + i
        sep = ','
    script_var += '};\n'

    mprt = div + \
'<form method=POST enctype=multipart/form-data action=' + tow.url('import') + '>' + '''
      <span class="c3a"><label><input type=submit value=Import>&nbsp;File</label></span>
      <span class="c3a"><input type=file name=file></span>
      <table><tbody><tr><td><label for=event>To Event&nbsp;&nbsp;</label><input type="hidden" name="event_id" value=""/><input type=text name=event onkeyup="setTimeout(function(){changed(event.target);},10);" onchange="changed(event.target);" id="name" choices="all_events_byname"></tbody></table><br>
    </form>''' + xdiv


text = 'View Events'
if 'event' in tow.permissions:
    text = 'View/Edit Events'
event = div + tow.a('event', text = text) + xdiv

if 'user' in tow.permissions:
    user = div + tow.a('user', text='View/Edit users') + xdiv

if 'donation' in tow.permissions:
    donation_report = div + '<form action="' + tow.url('donation') + '''" method="POST">
      <span class="c3a"><input type="submit" value="Donation"/>&nbsp;Report</span>
      <span class="c3"><label for="from">Start Date</label><span><input type="text" name="from" value=""/></span></span>
      <span class="c3"><label for="to">End Date</label><span><input type="text" name="to" value=""/></span></span><br>
    </form>''' + xdiv + \
    div + '<form action="' + tow.url('donation-export') + '''" method="POST">
      <span class="c2a"><input type="submit" value="Export"/> donations to CSV file</span>
      <span class="c2a"><label>Save As&nbsp;&nbsp;<input type="text" name="filename" value="donation"/>.csv</label></span><br>
      <span class="c1"><label for="fields">Fields to export</label><span><input type="text" name="fields" value="first_name,last_name,any_email,street_address_1,street_address_2,town_village_city,province_state,postal_code,country,total_donation"/></span></span><br>
      <span class="c1"><label for="conditions">Only export people where</label><span><input type="text" name="conditions"/></span></span><br><br>
      <span class="c3"><label for="from">Start Date</label><span><input type="text" name="from" value=""/></span></span>
      <span class="c3"><label for="to">End Date</label><span><input type="text" name="to" value=""/></span></span><br>
    </form>''' + xdiv


event_report = div + '<form action="' + tow.url('event-report') + '''" method="POST">
      <span class="c4a"><input type="submit" value="Event"/>&nbsp;Report</span>
      <span class="c4"><label for="name">Name</label><span><input type="text" name="name" value=""/></span></span>
      <span class="c4"><label for="from">Start Date</label><span><input type="text" name="from" value=""/></span></span>
      <span class="c4"><label for="to">End Date</label><span><input type="text" name="to" value=""/></span></span><br>
    </form>''' + xdiv


tow.start_page("ToW DB Home", text_title = 'Home Screen', style=tow.st, script = script_var, show_home = False)
print div + tow.a('user', text = 'Change your password', opts = {'Do': 'Show', 'us': tow.user}) + xdiv + event + person + user + person_report + person_export + donation_report + event_report + mprt
tow.end_page(show_home = False)
