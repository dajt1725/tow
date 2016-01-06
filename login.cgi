#!/usr/bin/python
import sys, os, string, cgi, random, datetime, Cookie
sys.path.insert(0,'/home/temple24/python')
import hashlib, tow

tow.user = tow.form.getfirst('id')
password = tow.form.getfirst('pw')

if tow.user is None or tow.user == '' or not password:
    tow.start_page('Log In',text_title = '', show_logout = False, show_home = False)
    if tow.user is None:
        tow.user = ''
    print string.Template("""    <form action="${login_url}" method="POST">
      <input type="text" name="id", value="${user}" /><br>
      <input type="password" name="pw", value="" /><br>
      <input type="submit" value="Login" />
    </form>""").substitute({'login_url': tow.url('login'), 'user': tow.user})
    tow.end_page(show_logout = False, show_home = False)
    sys.exit(0)


tow.cur.execute("select salt, password, permissions, expiration from tow_user where user = %(user)s", {'user': tow.user})
resp = tow.cur.fetchall()
if len(resp) != 1:
    tow.not_logged_in('User ' + tow.user + ' not found.')
m = hashlib.sha256()
m.update(str(resp[0][0]))
if password:
    m.update(password)
if m.digest() != resp[0][1]:
    tow.not_logged_in("Password mismatch")
tow.permissions = resp[0][2]
id = random.SystemRandom().randint(0,4294967296L)
now = datetime.datetime.now()
expires = now + datetime.timedelta(seconds = resp[0][3])
tow.log('logged in')
tow.cur.execute("delete from tow_session where expires < %(now)s", {'now': now})
tow.cur.execute("insert into tow_session (user, id, host, expires, permissions) values (%(user)s, %(id)s, %(host)s, %(expires)s, %(permissions)s)", {'user': tow.user, 'id': id, 'host': os.environ.get("REMOTE_ADDR"), 'expires': expires, 'permissions': tow.display_set(tow.permissions)})
tow.check_warnings()
cookie = Cookie.SimpleCookie()
cookie['id'] = str(id)

tow.fini()
tow.print_results('Logged In Redirect', 'home', 'You are logged in', headers = cookie.output() + '\n', timeout = 0)
