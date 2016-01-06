#!/usr/bin/python
import sys, cgi, urllib, random, traceback
sys.path.insert(0,'/home/temple24/python')
import hashlib, mysql.connector, tow

td = tow.td

def get_password_hash(pw, salt = None, r = random.SystemRandom()):
    if salt is None:
        salt = r.randint(0,4294967296L)
    m = hashlib.sha256()
    m.update(str(salt))
    m.update(pw)
    return (m.digest(), salt)

def clear_user():
    global user
    global permissions
    global permissions_old
    global notes
    global notes_old
    global expire
    global expire_old

    user = None
    permissions = ''
    permissions_old = ''
    notes = None
    notes_old = None
    expire = tow.default_expire
    expire_old = tow.default_expire

def do_change():
    if new_password_1 != new_password_2 or new_password_1 == '' or new_password_1 is None:
        tow.add_error("Invalid new password")
        return
    tow.cur.execute("select password, salt from tow_user where user = %(user)s", {'user': tow.user})
    resp = tow.cur.fetchall()
    if len(resp) != 1:
        tow.add_error('Active user not found')
        return
    (password_hash, tmp) = get_password_hash(old_password, resp[0][1])
    if password_hash != resp[0][0]:
        tow.add_error("Invalid old password")
        return
    (password_hash, salt) = get_password_hash(new_password_1, None)
    cmd = "update tow_user set password = %(password)s, salt = %(salt)s where user= %(user)s"
    arg = {'password': password_hash, 'salt': salt, 'user': tow.user}
    tow.cur.execute(cmd, arg)
    tow.check_warnings(cmd, arg)
    if len(tow.problems) == 0:
        tow.add_note('Your pasword has been changed.')
    cmd = "delete from tow_session where user=%(user)s"
    arg = {'user': tow.user}
    tow.cur.execute(cmd, arg)
    tow.check_warnings(cmd, arg)
    tow.start_page("Change Password", style=tow.st, redir_to = 'login')
    tow.end_page()
    sys.exit(0)


##### slurp up the form data into form ########################################
# gather any data from form
dowhat = tow.form.getfirst('Do')
if dowhat not in ('Add', 'Change', 'Delete', 'List', 'New', 'Show', 'Update'):
    dowhat = 'List'
user = tow.form.getfirst('us')
if user == '':
    user = None

old_password = tow.form.getfirst('op')
new_password_1 = tow.form.getfirst('np1')
new_password_2 = tow.form.getfirst('np2')
permissions = tow.form.getfirst('pm')
if permissions is None:
    permissions = ''
permissions_old = tow.form.getfirst('opm')
if permissions_old is None:
    permissions_old = ''
notes = tow.form.getfirst('no')
if notes == '':
    notes = None
notes_old = tow.form.getfirst('ono')
if notes_old == '':
    notes_old = None
expire = tow.form.getfirst('ex')
if expire is None:
    expire = tow.default_expire
expire_old = tow.form.getfirst('oex')
if expire_old is None:
    expire_old = tow.default_expire

cmd = None
arg = None

if dowhat == 'Change' or (dowhat == 'Show' and (user is None or user == tow.user)):
    if dowhat == 'Change':
        do_change()

    tow.start_page("Change Password", style=tow.st)
    print '      <form action="' + tow.url('user') + '" method="POST">\n' + \
 '        <span class="c1"><label for="op">Current Password&nbsp;</label><span><input type="password" name="op" value=""/></span></span><br>\n' + \
 '        <span class="c2"><label for="np1">New Password&nbsp;</label><span><input type="password" name="np1" value=""/></span></span>\n' + \
 '        <span class="c2"><label for="np2">&nbsp;&nbsp;Reenter New Password&nbsp;</label><span><input type="password" name="np2" value=""/></span></span><br>\n' + \
 '        <input type="submit" name="Do" value="Change" />\n' + \
 '      </form>'
    tow.end_page()
    sys.exit(0)

tow.check_authorized("user")
if dowhat not in ('List', 'New') and user is None:
    tow.add_error('Missing username')

new_user = False
if dowhat == 'New':
    clear_user()

elif dowhat == 'Add':
    new_user = True
    if new_password_1 != new_password_2:
        tow.add_error('New password mismatch')
    elif new_password_1 is None or new_password_1 == '':
         tow.add_error("empty password")
    else:
        try:
            (password_hash, salt) = get_password_hash(new_password_1, None)
            cmd = "insert into tow_user (user, password, salt, permissions, user_notes, expiration) values (%(user)s, %(password_hash)s, %(salt)s, %(permissions)s, %(notes)s, %(expire)s)"
            arg = {'user': user, 'password_hash': password_hash, 'salt': salt, 'permissions': permissions, 'notes': notes, 'expire': tow.store_timedelta(expire)}
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd, arg)
        except:
            tow.add_error('Adding new user failed', traceback.format_exc().replace('\n','  '))
        if len(tow.problems) == 0:
            tow.add_note('User ', tow.display_text(user), ' successfully added.')
            clear_user()

elif dowhat == 'Update':
    if new_password_1 != new_password_2:
        tow.add_error('New password mismatch')
    else:
        if new_password_1 is not None and new_password_1 != '':
            try:
                (password_hash, salt) = get_password_hash(new_password_1, None)
                cmd = "update tow_user set password = %(password)s, salt = %(salt)s where user= %(user)s"
                arg = {'password': password_hash, 'salt': salt, 'user': user}
                tow.cur.execute(cmd, arg)
                tow.check_warnings(cmd, arg)
            except:
                tow.add_error('Updating password failed')
        if permissions != permissions_old:
            try:
                cmd = "update tow_user set permissions = %(permissions)s where user= %(user)s"
                arg = {'permissions': permissions, 'user': user}
                tow.cur.execute(cmd, arg)
                tow.check_warnings(cmd, arg)
                permissions_old = permissions
            except:
                tow.add_error('Updating permissions failed')
        if notes != notes_old:
            try:
                cmd = 'update tow_user set user_notes = %(notes)s where user = %(user)s'
                arg = {'notes': notes, 'user': user}
                tow.cur.execute(cmd, arg)
                tow.check_warnings(cmd, arg)
                notes_old = notes
            except:
                tow.add_error('Updating notes failed')
        if expire != expire_old:
            try:
                cmd = 'update tow_user set expiration = %(expire)s where user = %(user)s'
                arg = {'expire': tow.store_timedelta(expire), 'user': user}
                tow.cur.execute(cmd, arg)
                tow.check_warnings(cmd, arg)
                expire_old = expire
            except:
                tow.add_error('Updating expiration failed')
        try:
            cmd = "delete from tow_session where user=%(user)s"
            arg = {'user': user}
            tow.cur.execute(cmd, arg)
            tow.check_warnings(cmd, arg)
        except:
            tow.add_error('Removing old sessions failed')
        if len(tow.problems) == 0:
            tow.add_note('User ', tow.display_text(user), ' successfully updated.')
            clear_user()

elif dowhat == 'Delete':
    cmd = "delete from tow_session where user=%(user)s"
    arg = {'user': user}
    try:
        tow.cur.execute(cmd, arg)
        tow.check_warnings(cmd, arg)
    except:
        tow.add_error('Removing old sessions failed.')
    cmd = "delete from tow_user where user=%(user)s"
    try:
        tow.cur.execute(cmd, arg)
        tow.check_warnings(cmd, arg)
    except:
        tow.add_error('Deleting user failed.')
    if len(tow.problems) == 0:
        tow.add_note('User ', tow.display_text(user), ' successfully deleted.')
        clear_user()

elif dowhat == 'Show':
    tow.cur.execute("select permissions, user_notes, expiration from tow_user where user = %(user)s", {'user': user})
    resp = tow.cur.fetchall()
    if len(resp) != 1:
        tow.add_error('user ', user, ' not found')
    else:
        permissions = tow.display_set(resp[0][0])
        permissions_old = permissions
        notes = resp[0][1]
        notes_old = notes
        expire = tow.display_timedelta(resp[0][2])
        expire_old = expire
elif dowhat == 'List':
    pass
else:
    tow.add_error("Unknown to-do ", dowhat)

if user is None:
    new_user = True
if new_user:
    title = "Add new user"
    n = 'New '
else:
    title = 'Edit user ' + tow.display_text(user)
    n = ''
if user is None:
    d = ''
    v = ''
else:
    d = ' readonly'
    v = tow.display_text(user) 

tow.start_page(title, style=tow.st)
print '      <form action="' + tow.url('user') + '" method="POST">'
print '        <span class="c1"><label for="us">' + n + 'User&nbsp;</label><span><input type="text"' + d + ' name="us" value="' + v + '"/></span></span><br>'
print '        <span class="c2"><label for="np1">New Password&nbsp;</label><span><input type="password" name="np1" value=""/></span></span>\n' + \
 '        <span class="c2"><label for="np2">&nbsp;&nbsp;Reenter New Password&nbsp;</label><span><input type="password" name="np2" value=""/></span></span><br>\n' + \
 '        <span class="c1"><label for="pm">Permissions&nbsp;</label><span><input type="text" name="pm" value="' + permissions + '"/></span></span>\n' + \
 '        <input type="hidden" name="opm" value="' + permissions_old + '" /><br>\n' + \
 '        <span class="c1"><label for="ex">Expire&nbsp;</label><span><input type="text" name="ex" value="' + expire + '"/></span></span>\n' + \
 '        <input type="hidden" name="oex" value="' + expire_old + '" /><br>' + \
 '        <span class="c1"><label for="no">Notes&nbsp;</label><span><input type="text" name="no" value="' + tow.display_text(notes) + '"/></span></span>\n' + \
 '        <input type="hidden" name="ono" value="' + tow.display_text(notes_old) + '" /><br>'
print '        <span class="b3"><input type="submit" name="Do" value="New" /></span>'
if new_user:
    print '        <span class="b3"><input type="submit" name="Do" value="Add" /></span>'
else:
    print '        <span class="b3"><input type="submit" name="Do" value="Update" /></span>\n' + \
 '        <span class="b3"><input type=submit name=Do value="Delete"/></span>\n'
print '      </form><br><br>'

##### Report Section #########################################################
print '      <hr style="color:#c00;background-color:#c00;height:4"/>'
print '      <table style="margin:0px auto;" border="1"><caption>All Users</caption><thead><tr><th><th>User<th>Permissions<th>Notes<th>Expire</thead><tbody>'
tow.cur.execute('select user, permissions, user_notes, expiration from tow_user order by user')
for resp in tow.fetchrows():
    (user, permissions, notes, expire) = resp
    print '        <tr><td>' + tow.a('user', text='Delete', opts = {'Do': 'Delete', 'us': user}) + td + tow.a('user', text = tow.display_text(user), opts = {'Do': 'Show', 'us': user}) + td + tow.display_set(permissions) + td + tow.display_text(notes) + td + tow.display_timedelta(expire)
print '      </tbody></table>'
print '      <hr style="color:#c00;background-color:#c00;height:4"/>'
tow.end_page()
