import sys, os, time, datetime, string, cgi, cgitb, Cookie, dateutil.parser, re, urllib
# they found tow.py, therefore this is not needed.
# sys.path.insert(0,'/home/temple24/python')
import mysql.connector

# Force input and outputs to utf8  Python is a kludge
import codecs
sys.stdin = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

if sys.version.startswith('2.7.12'):
    logfile = open('/local/tmp/db.log','a')
    _url_h = '/tow/'
    _url_t = '.cgi'
    image_url = '/Temple_Logo_72_small.jpg'
    db_conf = {'database': 'tow', 'user': 'tow', 'password': 'ScottJayDavid', 'charset': 'utf8'}
else:
    logfile = open('/home/temple24/jay/db.log','a')
    _url_h = '/'
    _url_t = '.cgi'
    image_url = '/Temple_Logo_72_small.jpg'
    db_conf = {'database': 'temple24_tow', 'user': 'temple24_dbase', 'password': 'l0vewi11wisd0m'}

td = '<td>'
div = '    <div style="background: beige; border-style: solid; border-width: 1">'
xdiv = '</div><br>\n'

# The default login cookie lasts an hour.
default_expire = '1h'

## connect to the database
conn = mysql.connector.connect(**db_conf)
conn.get_warnings = True
cur = conn.cursor()
conn2 = mysql.connector.connect(**db_conf)
conn2.get_warnings = True
cur2 = conn2.cursor()

## error handling variables
problems = []
# Not errors, just things to note.
messages = []

# What this user is allowed to do
user = None
permissions = None

form = cgi.FieldStorage()

# A convenient way to call cur.fetchone() in a "for X in ..." loop
def fetchrows():
    while True:
        ret = cur.fetchone()
        if ret is None:
            break
        yield ret

def get_enum_values(name):
    cmd = "select field from tow_enum_" + name
    arg = None
    cur.execute(cmd, arg)
    return tuple(x for x in fetchrows())

# Not currently used
#def get_re_enum_values(name):
#    cmd = "select field from tow_list_" + name
#    arg = None
#    cur.execute(cmd, arg)
#    ret = []
#    for resp in fetchrows():
#        ret.append(re.compile(resp[0]))
#    return ret

# Originally these were all hardcoded.  Now we're moving to storing them in
# subtables.  Try to make things work smoothly in all possible intermediate
# states.
# If these are hardcoded, they must match tow-schema.sql or doom will result
_enum_hash = {}
_enum_default_hash = {
    'contact_type':                ('Unknown', 'email', 'email/home', 'email/work', 'phone', 'phone/cell', 'phone/home', 'phone/work', 'other'),
    'donation_status':             ('Unknown', 'Pledged', 'Cancelled', 'Complete'),
    'donation_type':               ('Other', 'Money', 'Goods', 'Services'),
    'event_type':                  ('Unknown', 'Mystery School', 'Ritual', 'Workshop'),
    'person_event_payment_status': ('Unknown', 'Paid', 'Not Paid', 'Scholarship', 'Donation Package', 'ISBE'),
    'person_event_status':         ('Unknown', 'Signed-Up', 'Cancelled', 'In-Progress', 'Completed'),
    'person_event_type':           ('Unknown', 'Teacher', 'Volunteer', 'Student', 'Auditor', 'Other'),
    'person_gender':               ('Unknown', 'Male', 'Female', 'Other'),
    'person_membership':           ('Unknown', 'Other', 'Nonmember', 'General', 'Honored', 'Ministerial'),
    'person_volunteer':            ('Unknown', 'No', 'Pending', 'Former', 'Active'),
}

def enum(x):
    if x in _enum_hash:
        return _enum_hash[x]
    try:
        t = get_enum_values(x)
    except:
        t = _enum_default_hash[x]
    _enum_hash[x] = t
    return t

# How to make resizing text boxes
#
# add padding to the inner span to have it not go directly to the edges
#
#  <span style="float:left;display:block;width:33%;overflow:hidden">
#             <label for="a" style="float:left"> Person Name </label>
#             <span style="display:block;overflow:hidden"><input style="width:100%" type="text" id="a"/></span>
#          </span>
#
#
st = '''.c1 { float: left; display: block; width: 100%; overflow: hidden; }
.c1 label { float: left; }
.c1 select { float: left; }
.c1 span { display: block; overflow: hidden; }
.c1 input { width: 100%; }
.c2a { float: left; display: block; width: 50%; overflow: hidden; }
.c2 { float: left; display: block; width: 50%; overflow: hidden; }
.c2 label { float: left; }
.c2 span { display: block; overflow: hidden; }
.c2 input { width: 100%; }
.c23a { float: left; display: block; width: 66.67%; overflow: hidden; }
.c23 { float: left; display: block; width: 66.67%; overflow: hidden; }
.c23 label { float: left; }
.c23 span { display: block; overflow: hidden; }
.c23 input { width: 100%; }
.b3 { float: left; width: 33%; text-align: center; }
.c3a { float: left; display: block; width: 33.33%; text-align: center; overflow: hidden; }
.c3 { float: left; display: block; width: 33.33%; overflow: hidden; }
.c3 label { float: left; }
.c3 span { display: block; overflow: hidden; }
.c3 input { width: 100%; }
.c4a { float: left; display: block; width: 25%; text-align: center; overflow: hidden; }
.c4 { float: left; display: block; width: 25%; overflow: hidden; }
.c4 label { float: left; }
.c4 span { display: block; overflow: hidden; }
.c4 input { width: 100%; }
.c6a { float: left; display: block; width: 16.66%; text-align: center; overflow: hidden; }
.c6 { float: left; display: block; width: 16.66%; overflow: hidden; }
.c6 label { float: left; }
.c6 span { display: block; overflow: hidden; }
.c6 input { width: 100%; }
caption {font-weight:bold;font-size:1.5em;}
'''

#
# Currently unused at the moment.
#
#
#
#      function merge_attrs(o1,o2){
#        var r={};
#        for(var a in o1){r[a]=o1[a];}
#        for(var a in o2){r[a]=o2[a];}
#        return r;
#      }
#
# function mk_td() {
#   return mk_ele('td', null, Array.prototype.slice.call(arguments));
# }
#
#

script_common = '''

function mk_text(t) {
  return document.createTextNode(t);
}


function mk_ele(t, a) {
  var ret = document.createElement(t);
  if (a) { for (var i in a) { ret.setAttribute(i, a[i]); } }
  if (arguments.length > 2) {
    for (var i = 2; i < arguments.length; i++) {
      var z = arguments[i];
      if (z instanceof Array) {
        for (var j = 0; j < z.length; j++) {
          ret.appendChild(z[j]);
        }
      } else {
        ret.appendChild(z);
      }
    }
  }
  return ret;
}

'''

script_add_row = '''

String.prototype.replaceAll=function(s,r){
  if(r==undefined){
    return this.toString();
  }
  return this.split(s).join(r)
}

function do_quote(s) {
  s=s.replaceAll('\\\\','\\\\\\\\');
  s=s.replaceAll('"','\\\\"');
  s=s.replaceAll("'","\\\\'");
  return s;
}

function strify(l) {
  if (l == null) {
    return l;
  }
  var ret = '[';
  var sep = '';
  for (var i in l) {
    ret = ret + sep + '"' + do_quote(l[i]) + '"'
    sep = ',';
  }
  return ret + ']';
}


function mk_tr(a) {
  var ret = document.createElement('tr');
  if (a != null) {
    for (var i in a) { ret.setAttribute(i, a[i]); }
  }
  for (var i = 1; i < arguments.length; i++) {
    var d = document.createElement('td');
    var z = arguments[i];
    if (z != null) {
      if (z instanceof Array) {
        for (var j = 0; j < z.length; j++) {
          d.appendChild(z[j]);
        }
      } else {
        d.appendChild(z);
      }
    }
    ret.appendChild(d);
  }
  return ret;
}


function mk_input_checkbox(n, c) {
  var t = {'name': n, 'type': 'checkbox'};
  if (c != '0') { t.checked = ''; }
  return mk_ele('input', t);
}


function mk_input_text(n,v) {
  return mk_ele('input', {'name': n, 'type': 'text', 'value': v});
}


function mk_input_hidden(n, v) {
  return mk_ele('input', {'name': n, 'type': 'hidden', 'value': v});
}


function mk_input_select(n,v,d,l) {
  if (l == null) {
    l = v;
  }
  var s = mk_ele('select', {'name': n});
  for (var i = 0; i < v.length; i += 1) {
      var a = {'value': v[i], 'label': l[i]};
      if (d == v[i]) { a.selected = ''; }
      s.appendChild(mk_ele('option', a, mk_text(l[i])));
  }
  return s;
}


function add_row(f,fun,l) {
  var m = Number(f.getAttribute('max'));
  var c = fun+'('+m+','+strify(l)+')';
  c = eval(c);
  f.appendChild(c);
  m += 1;
  f.setAttribute('max', m);
}


function row_changed(t,fun,e) {
  t.removeAttribute('onkeydown');
  t.removeAttribute('onchange');
  add_row(t.parentNode, fun, null);
}

'''

script_choose = '''

function mk_br() {
  return document.createElement('br');
}

function matches(s,l) {
  if (s==''){return[];}
  var ret=[];
  var r=new RegExp('\\\\b'+s,'i');
  var k=Object.keys(l);
  var a;
  for (var i=0;i<k.length;i++){
    a=k[i];
    if(r.test(a)){
      ret.push([l[a], a]);
    }
  }
  return ret;
}


function chose(e) {
  var t=document.getElementById(e.getAttribute('choose_in'));
  t.value = e.firstChild.nodeValue;
  t.previousSibling.value = e.getAttribute('setto');
  t.removeAttribute('has_menu');
  e.parentNode.parentNode.removeChild(e.parentNode);
}

function changed(t){
  if (!t.hasAttribute('choices')){
    return;
  }
  if (t.hasAttribute('has_menu')){
    var e=document.getElementById(t.getAttribute('has_menu'));
    e.parentNode.removeChild(e);
    t.removeAttribute('has_menu');
  }
  if (t.hasAttribute('has_new')){
    var e=document.getElementById(t.getAttribute('has_new'));
    e.parentNode.removeChild(e);
    t.removeAttribute('has_new');
  }
  t.previousSibling.value='';
  if(t.value.length==0) {
    return;
  }
  var r=mk_ele('div', {'id':'m'+t.id});
  if (t.hasAttribute('allow_new')){
    r.appendChild(mk_ele('input',{'type':'button','onclick':t.getAttribute('allow_new')+'(this);','choose_in':t.id,'value':'New'}));
    r.appendChild(mk_br());
  }
  var m=matches(t.value,eval(t.getAttribute('choices')));
  if(m.length==0){
    r.appendChild(mk_ele('span',{'style':'font-weight:bold;color:red;'},mk_text('Not Found')));
  }else if(m.length>8){
    r.appendChild(mk_ele('span',{'style':'font-weight:bold;color:red;'},mk_text('Too Many To List')));
  }else{
    for(var i=0;i<m.length;i++){
      r.appendChild(mk_ele('span',{'onclick':'chose(this);','choose_in':t.id,'setto':m[i][0]},mk_text(m[i][1]),mk_br()));
    }
  }
  if(t.nextSibling){
    t.parentNode.insertBefore(r,t.nextSibling);
  } else {
    t.parentNode.appendChild(r);
  }
  t.setAttribute('has_menu','m'+t.id)
}
'''

# Encode a url, rather like urllib.urlencode, but don't chock on unicode
# and be horribly inefficient about it, because I'm lazy.
always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'              
	       'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')

def quote(s, safe):
    """quote('abc def') -> 'abc%20def'

    Each part of a URL, e.g. the path info, the query, etc., has a
    different set of reserved characters that must be quoted.     

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters.

    reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
	          "$" | ","                                      

    Each of these characters is reserved in some component of a URL,
    but not necessarily in all of them.

    By default, the quote function is intended for quoting the path
    section of a URL.  Thus, it will not encode '/'.  This character
    is reserved, but in typical usage the quote function is being
    called on a path where the existing slash characters are used as
    reserved characters.
    """
    if not s.rstrip(safe):
        return s
    safe_map = {}
    for i in range(256):
        c = chr(i)
        safe_map[i] = (c in safe) and c or ('%%%02X' % i)

    return ''.join(map(safe_map.__getitem__, bytearray(unicode(s), 'UTF-8')))

def quote_plus(s):
    """Quote the query fragment of a URL; replacing ' ' with '+'"""
    if type(s) == int or type(s) == float:
        s = str(s)
    if ' ' in s:
        s = quote(s, ' ' + always_safe)
        return unicode(s.replace(' ', '+'))
    return unicode(quote(s, always_safe))


def urlencode(b, q):
    if q is None:
        return b
    t = []
    for k, v in q.items():
        t.append(quote_plus(k) + '=' + quote_plus(v))
    return b + '?' + '&'.join(t)


# Return a form parameter as valid utf-8
def get_param(name, empty = None, oneof = None, notfound = None):
    ret = form.getfirst(name)
    if oneof is not None and ret not in oneof:
        ret = oneof[0]
    if ret == '':
        ret = empty
    if ret is None:
        ret = notfound
    if ret is not None:
        try:
            ret = ret.encode('raw_unicode_escape')
        except:
            pass
        ret = ret.decode('utf-8')
    return ret


def url(base, opts = None):
    if opts is None:
        return _url_h + base + _url_t
    else:
        return urlencode(_url_h + base + _url_t, opts)

# Create a URL, 
def a(base, img = None, alt = None, text = None, opts = None):
    if text is None and img is None:
        text = base
    elif text is None:
        if alt is None:
            alt = ''
        else:
            alt = ' alt="' + alt + '"'
        text = '<img src="' + img + '"' + alt + ' align="center" style="border:0px" />'
    return '<a href="' + urlencode(url(base), opts) + '">' + text + '</a>'


# Lazy helper function to convert things to printable strings.
# Life would be easier if str(unicode-string) didn't throw an error.
def s(*l):
    r = ''
    for i in l:
        if type(i) in (str, unicode, int, float):
            r += unicode(i)
        else:
            r += repr(i)
    return r


def log(*l):
    if logfile != sys.stderr:
        text = s(datetime.datetime.now().isoformat(), ': ', user, ': ', *l)
    else:
        text = s(user, ': ', *l)
    logfile.write(text + '\n')

def add_error(*l):
    problems.append(s(*l))

def add_note(*l):
    messages.append(s(*l))

# print stub pages
def print_results(title, to_where, text, opts = None, to_do = 'continue', headers = '', timeout = 3):
    to_url = url(to_where, opts)
    if timeout == 0:
        tt = 'window.location = "' + to_url + '";'
    else:
        tt = 'setTimeout(function() { window.location = "' + to_url + '";}, ' + s(timeout) + '000);'

    print s("""Content-Type: text/html;charset=UTF-8
Cache-Control: no-cache
""", headers, """
<html>
  <head>
    <title>""", title, """</title>
    <meta http-equiv="refresh" content=""", s(timeout), """; url=""", to_url, """" />
    <META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
    <script language="javascript">
      """, tt, """
    </script>
  </head>
  <body>""")
    if len(problems) > 0:
        log('Problems: ', problems, '\n')
        print """    <table style="margin: 0px auto;border: 2px solid red;">
      <caption style="border=2px solid red;color:#900;">Errors Have Occured:</caption><thead><tr><th>##<th>Error</thead>
      <tbody>
"""
        n = 0
        for err in problems:
            print s('      <tr><td>', n, '<td style="border:1px solid red;color:#900;">', display_text(err))
            n += 1
        print """    </tbody></table>
    <hr />"""

    if len(messages) > 0:
        log('Messages: ', messages, '\n')
        print """    <table style="margin: 0px auto;border: 1px solid black;">
      <caption>Messages</caption><thead><tr><th>##<th>Msg</thead>
      <tbody>
"""
        n = 0
        for m in messages:
            print s('      <tr><td>', n, '<td style="border:1px solid black;">', display_text(m))
            n += 1
        print """    </tbody></table>
    <hr />"""

    print s(text, '<br>Go to ', a(to_where), ' to ', to_do, """.
  </body>
</html>""")
    sys.exit(0)

def not_allowed(reason):
    log('not_allowed: ', reason)
    time.sleep(3)
    print_results('Not Allowed', 'home', 'You are not allowed to do that '+ reason)


def not_logged_in(reason):
    log('not_logged_in: ', reason)
    time.sleep(3)
    print_results('Not Logged In', 'login', 'You are not logged in ' + reason, to_do = 'log in')

def format_name(f, l, c):
    if c is not None:
        if l is not None:
            n = c + ' (' + f + ' ' + l + ')'
        else:
            n = c + ' (' + f + ')'
    elif l is not None:
        n = f + ' ' + l
    else:
        n = f
    return n

def refresh_people():
    global person_id_list
    global person_list
    global person_sort_by_id

    person_id_list = []
    person_list = []
    person_sort_by_id = {}
    cur.execute("select person_id, first_name, last_name, craft_name from tow_person order by last_name, first_name, craft_name")
    n = 0
    for resp in fetchrows():
        (i, f, l, c) = resp
        person_id_list.append(s(i))
        person_list.append(format_name(f, l, c))
        person_sort_by_id[i] = n
        n += 1


def refresh_events():
    global event_list
    global event_id_list
    event_id_list = []
    event_list = []
    cur.execute("select event_id, name from tow_event order by name")
    for resp in fetchrows():
        (i, n) = resp
        event_id_list.append(s(i))
        event_list.append(n)



# extract information from the database
expires = None
if os.environ.get("REQUEST_URI") != url('login'):
    log('not logged in "', os.environ.get("REQUEST_URI"), '" != "', url('login'), '"')
    host = os.environ.get("REMOTE_ADDR")
    cookie_string = os.environ.get("HTTP_COOKIE")
    if cookie_string is None or cookie_string == '':
        not_logged_in("No Cookie.")
    cookie = Cookie.SimpleCookie()
    cookie.load(cookie_string)
    id = cookie.get('id')
    if id is None or id.value is None:
        not_logged_in("No id in cookie.")
    id = id.value
    cur.execute("select user, host, expires, permissions from tow_session where id = %(id)s", {'id': id})
    resp = cur.fetchall()
    if len(resp) != 1:
        not_logged_in(s('Response ', resp))
    resp = resp[0]
    if resp[1] != host:
        not_logged_in('host ' + resp[1] + ' != ' + host)
    expires = resp[2]
    if expires < datetime.datetime.now():
        not_logged_in(s('Cookie expired ', expires.isoformat(), ' < ', datetime.datetime.now().isoformat()))
    user = resp[0]
    permissions = resp[3]
    if 'debug' in permissions:
        cgitb.enable()
# They presented a valid ID from the correct host.  They're logged in.


refresh_people()
refresh_events()

# Code, some of this is obsolete and not used

def check_authorized(what):
    if what not in permissions:
        not_allowed(what + ' not in permission list' + display_set(permissions))


def var_text(t):
    if t is None:
        t = ''
    t = s(t)
    # Must be first
    t = t.replace('\\','\\x5c')
    t = t.replace('"', '\\"')
    t = t.replace('&', '\\&')
    t = t.replace("'", "\\'")
    t = t.replace('<', '\\x3c')
    t = t.replace('>', '\\x3e')
    return '"' + t + '"'


def var_hash(i, l):
    ret = '['
    sep = ''
    for v in l:
        ret += sep + var_text(i[v])
        sep = ','
    ret += ']'
    return ret


def var_list(v, l, p = None):
    ret = 'var '+ v + '=['
    sep = ''
    if p is not None:
        ret += p
        sep = ','
    for t in l:
        ret += sep + var_text(t)
        sep = ','
    return ret + '];\n'


def store_date(d):
    if d == '' or d is None:
        return None
    if type(d) == str or type(d) == unicode:
        d = dateutil.parser.parse(d).date()
    ret = d.isoformat()
    return ret


def store_cash(c):
    if c == '' or c is None:
        return None
    if c[0] == '$':
        c = c[1:]
    return s(int((float(c) + .005 ) * 100))


def store_text(t):
    if t == '':
        return None
    t = string.replace(s(t),'&amp;','&')
    t = string.replace(t,'&lt;', '<')
    t = string.replace(t,'&gt;', '>')
    t = string.replace(t,'&apos;', "'")
    t = string.replace(t,'&quot;', '"')
    return t


def display_date(d):
    if d is None:
        return ''
    if type(d) == str:
        d = dateutil.parser.parse(d).date()
    if d.year < 1900:
        return repr(d)
    return d.strftime("%x")


def display_cash(m):
    if m is None:
        return ''
    d = s(int(m) / 100)
    c = int(m) % 100
    if c < 10:
        c = '0' + s(c)
    else:
        c = s(c)
    ret = '$' + d + '.' + c
    return ret


def display_text(t):
    if t is None:
        return ''
    t = cgi.escape(s(t), True)
    t = string.replace(t, "'", '&apos;')
    return t


def display_set(s):
    sep = ','
    ret = ''
    ss = ''
    for i in s:
        ret += ss + i
        ss = sep
    return ret

# s is in seconds
def display_timedelta(s):
    d = s / 86400
    if d > 0:
        d = unicode(d) + u'd'
    else:
        d = u''
    s %= 86400

    h = s / 3600
    if h > 0:
        h = unicode(h) + u'h'
    else:
        h = u''
    s %= 3600

    m = s / 60
    if m > 0:
        m = unicode(m) + u'm'
    else:
        m = u''
    s %= 60

    if s > 0:
        s = unicode(s) + u's'
    else:
        s = u''

    return d + h + m + s

# s is '{%d days?, } hh:mm:ss' as generated by display_timedelta()
def store_timedelta(s):
    m = re.match(r'^(?:(?P<d>\d+)d)?\s*(?:(?P<h>\d+)h)?\s*(?:(?P<m>\d+)m)?\s*(?:(?P<s>\d+)s)?$', s)
    if m is None:
        raise ValueError('Invalid timedelta '+repr(s))
    d = m.groupdict()
    ret = 0
    if d['d'] is not None:
        ret += int(d['d']) * 86400
    if d['h'] is not None:
        ret += int(d['h']) * 3600
    if d['m'] is not None:
        ret += int(d['m']) * 60
    if d['s'] is not None:
        ret += int(d['s'])
    return ret


def get_list(l):
    ret = []
    n = 0
    while True:
        tmp = {}
        foundone = False
        nonempty = False
        for v in l:
            if len(v) > 2:
                (v1, v2, v3) = v
            else:
                (v1, v2) = v
                v3 = None
            t = form.getfirst(v1 + s(n))
            if t is not None and t != 'None':
                tmp[v2] = t
                foundone = True
                if t != '' and t != v3:
                    nonempty =True
            else:
                tmp[v2] = ''
        if not foundone:
            break
        if nonempty:
            ret.append(tmp)
        n += 1
    return ret


def event_id_to_name(id):
    if id in event_id_list:
        return event_list[event_id_list.index(id)]
    cur2.execute("select name from tow_event where event_id = %(event_id)s", {'event_id': id })
    resp = cur2.fetchall()
    if len(resp) != 1:
        raise ValueError(s('Unknown event_id ', id))
    return resp[0][0]


def find_event(e):
    if 'name' in e:
        name = e['name']
        if name in event_list:
            return event_id_list[event_list.index(name)]
        cur2.execute("select event_id from tow_event where name = %(name)s", {'name': name})
        resp = cur2.fetchall()
        if len(resp) != 1:
            raise ValueError('Unknown or ambiguous event '+name)
        return resp[0][0]
    raise ValueError(s("Don't know how to find event ", e))


def person_id_to_name(id):
    if id in person_id_list:
        return person_list[person_id_list.index(id)]
    cur2.execute("select first_name, last_name, craft_name from tow_person where person_id = %(person_id)s", {'person_id': id })
    resp = cur2.fetchall()
    if len(resp) != 1:
        raise ValueError(s('Unknown person_id ', id))
    (fn, ln, cn) = resp[0]
    return format_name(fn, ln, cn)

def find_people(p):
    ret = []
    for i in p:
        p[i] = p[i].strip()
    cmd = "select p.person_id from tow_person as p"
    clause = ' where '
    sep = ''
    nsep = ' and '
    if p.get('first_name'):
        clause += sep + 'p.first_name = %(first_name)s'
        sep = nsep

    if p.get('last_name'):
        clause += sep + 'p.last_name = %(last_name)s'
        sep = nsep

    if p.get('craft_name'):
        clause += sep + 'p.craft_name = %(craft_name)s'
        sep = nsep

    if p.get('membership_status'):
        clause += sep + 'p.membership_status = %(membership_status)s'
        sep = nsep

    if p.get('email'):
        cmd += ' left join tow_contact as ce using(person_id)'
        clause += sep + 'ce.type in ("email", "email/home", "email/work") and ce.address = %(email)s'
        sep = nsep

    if p.get('phone'):
        cmd += ' left join tow_contact as cp using(person_id)'
        clause += sep + 'cp.type in ("phone", "phone/home", "phone/work", "phone/cell") and cp.address = %(phone)s'
        sep = nsep

    log('find_people', cmd, clause, ': ', p)
    cur.execute(cmd+clause, p)
    resp = cur.fetchall()
    if len(resp) == 0:
        return None
    for e in resp:
        ret.append(e[0])
    return ret


def add_person(p):
    t = {}
    for i in ('first_name', 'last_name', 'craft_name', 'member_since', 'street_address_1', 'street_address_2', 'town_village_city', 'province_state', 'postal_code', 'country',
'date_of_birth', 'ordination_date', 'ordination_renewal_date', 'notes'):
        t[i] = p.get(i)
        if t[i]:
            t[i] = t[i].strip()
    if 'name' in p:
# FIXME, handle craft names here too
        tmp = re.match('^\\s*(.+)\\s+\\(([^ ]+)\\s+(.+)\\)\\s*$',p['name'])
        if tmp:
            t['first_name'] = tmp.group(2)
            t['last_name'] = tmp.group(3)
            t['craft_name'] = tmp.group(1)
        else:
            tmp = re.match('^\\s*([^\\s]+)\\s+(.+)\\s*$',p['name'])
            if tmp:
                t['first_name'] = tmp.group(1)
                t['last_name'] = tmp.group(2)
            else:
                t['first_name'] = p['name']
    if 'address' in p:
# FIXME, do better splitting here
        tmp = re.match('^\\s*([^,]*)\\s*(,\\s*([^,]*)\\s*(,\\s*([^,]*\\s*(,\\s*([^,]*)\\s*(,\\s*([^,]*)\\s*(,\\s*([^,]*))?)?)?)?)?)?$',p['address'])
        if tmp:
            t['street_address_1'] = tmp.group(1)
            t['street_address_2'] = tmp.group(3)
            t['town_village_city'] = tmp.group(5)
            t['province_state'] = tmp.group(7)
            t['postal_code'] = tmp.group(9)
            t['country'] = tmp.group(11)
        else:
            t['street_address_1'] = p['address']

    for i in ('membership_status', 'gender', 'volunteer_status'):
        t[i] = p.get(i, 'Unknown')

    t['ministries'] = p.get('ministries','')
    t['is_ordained'] = p.get('is_ordained', 0)
    cmd = """insert into
 tow_person (first_name, last_name, craft_name, membership_status,
  member_since, ministries, street_address_1, street_address_2,
  town_village_city, province_state, postal_code, country,
  date_of_birth, gender, is_ordained, ordination_date,
  ordination_renewal_date, person_notes, volunteer_status )
 values ( %(first_name)s, %(last_name)s, %(craft_name)s, %(membership_status)s,
  %(member_since)s, %(ministries)s, %(street_address_1)s, %(street_address_2)s,
  %(town_village_city)s, %(province_state)s, %(postal_code)s, %(country)s,
  %(date_of_birth)s, %(gender)s, %(is_ordained)s, %(ordination_date)s,
  %(ordination_renewal_date)s, %(notes)s, %(volunteer_status)s )"""
    arg = t
    cur.execute(cmd, arg)
    check_warnings(cmd,arg)
    person_id = cur.lastrowid
    for i in ('email', 'phone'):
        if p.get(i):
            cmd = 'insert into tow_contact (person_id, type, address) values (%(person_id)s, %(type)s, %(address)s)'
            arg = { 'person_id': person_id, 'type': i, 'address': p[i] }
            cur.execute(cmd, arg)
            check_warnings(cmd,arg)
    refresh_people()
    add_note('Attempting to create person ', format_name(t['first_name'], t['last_name'], t['craft_name']), '.')
    return person_id

def add_contact(c):
    if 'notes' not in c:
        c['notes'] = None
    cmd = 'insert into tow_contact (person_id, type, address, contact_notes) values (%(person_id)s, %(type)s, %(address)s, %(notes)s )'
    arg = c
    cur.execute(cmd, arg)
    check_warnings(cmd,arg)

def add_donation(d):
    cmd = 'insert into tow_donation (person_id, donation_date, donation_amount, donation_status, donation_type, donation_notes) values (%(person_id)s, %(date)s, %(amount)s, %(status)s, %(type)s, %(notes)s )'
    arg = d
    cur.execute(cmd, arg)
    check_warnings(cmd,arg)
    return cur.lastrowid

def add_person_event(pe):
    cmd = 'insert into tow_person_event (person_id, event_id, type, status, payment_status, enrolled) values (%(person_id)s, %(event_id)s, %(type)s, %(status)s, %(payment_status)s, %(enrolled_s)s)'
    arg = pe
    cur.execute(cmd, arg)
    check_warnings(cmd, arg)

def start_page(page_title, text_title = None, show_logout = True, show_home = True, style = None, script = None, redir_to = None, onload = None):
    titletxt = ''
    logouttxt = ''
    hometxt = ''
    styletxt = ''
    scripttxt = ''
    redirtxt = ''
    usertxt = ''
    onloadtxt = ''

    if text_title is None:
        text_title = page_title

    if text_title != '':
        titletxt = '    <h2>' + text_title + '</h2>\n'

    if show_logout:
        logouttxt = div + a('logout', text = 'Log Out') + xdiv

    if show_home:
        hometxt = div + a('home', text = 'Return Home') + xdiv

    if style is not None:
        styletxt = '    <style>\n' + style + '    </style>\n'
    else:
        styletxt = '    <style>\ncaption {font-weight:bold;font-size:1.5em;}\n    </style>\n'

    if script is not None:
        scripttxt = '    <script language="javascript">\n' + script + '    </script>\n'

    if redir_to is not None:
        redirtxt = string.Template("""    <meta http-equiv="refresh" content="3; url=${redir_to}" />
    <script language="javascript">
      setTimeout(function() { window.location = "${redir_to}";}, 3000);
    </script>
""").substitute({'redir_to': url(redir_to)})

    if user is not None and permissions is not None and 'debug' in permissions:
        tmp = display_set(permissions)
        if tmp:
            tmp = ' with permissions ' + tmp
        if expires:
            tmp += '.<br>Your cookie will expire at ' + expires.isoformat()
        usertxt = '    You are logged in as ' + user + tmp + '.<br><br>\n'
    if onload is not None:
        onloadtxt = 'onload = "' + onload + '"'

    print """Content-Type: text/html;charset=UTF-8
Cache-Control: no-cache

<html>
  <head>
    <title>""" + page_title + """</title>
""" + redirtxt + styletxt + scripttxt + '''    <META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
  </head>
  <body style="text-align:center;"''' + onloadtxt + '>'+a('home', img = image_url, alt='Temple of Witchcraft') + '<br>' + titletxt + usertxt + hometxt + logouttxt + '    <hr />\n'

    if len(problems) > 0:
        log('Problems: ', problems, '\n')
        print """    <table style="margin: 0px auto;border: 2px solid red;">
      <caption style="border=2px solid red;color:#900;">Errors Have Occured:</caption><thead><tr><th>##<th>Error</thead>
      <tbody>
"""
        n = 0
        for err in problems:
            print s('      <tr><td>', n, '<td style="border:1px solid red;color:#900;">', display_text(err))
            n += 1
        print """    </tbody></table>
    <hr />"""
        conn.rollback()
    else:
        conn.commit()

    if len(messages) > 0:
        log(s('Messages: ', messages, '\n'))
        print """    <table style="margin: 0px auto;border: 1px solid black;">
      <caption>Messages</caption><thead><tr><th>##<th>Msg</thead>
      <tbody>
"""
        n = 0
        for m in messages:
            print s('      <tr><td>', n, '<td style="border:1px solid black;">', display_text(m))
            n += 1
        print """    </tbody></table>
    <hr />"""


def fini():
    conn.commit()
    cur.close()
    conn.close()
    cur2.close()
    conn2.close()


def end_page(show_logout = True, show_home = True):
    logouttxt = ''
    if show_logout:
        logouttxt = div + a('logout', text = 'Log Out') + xdiv
    hometxt = ''
    if show_home:
        hometxt = div + a('home', text = 'Return Home') + xdiv
    print '''    <hr />
''' + logouttxt + hometxt + '''  </body>
</html>
'''
    fini()


def check_warnings(cmd = None, arg = None):
    """see if the database threw any warnings
    Exiting is never an acceptable way to handle errors in a CGI script.
    """
    warnings = cur.fetchwarnings()
    if warnings:
        l = len(warnings)
        if l > 1:
            v = s(l, ' database warnings ')
        else:
            v = 'Database warning '
        if cmd is not None:
            add_error(v, "on command ", cmd, " with ", arg)
            v = ''
        for i in warnings:
            add_error(v, i)
            v = ''


def dropdown(id, values, default = None, labels = None, title = None, has_none = False):
    """create a dropdown named 'id' with label 'title' and values from 'values' and options from 'labels', with 'default' listed as selected """
    if title is not None:
      r = '        <label for="' + id + '">' + title + '</label>\n        '
    else:
        r = '        <td>'
    r += '<select name="' + id + '">\n'
    if has_none:
        s = ''
        if default is None:
            s = ' selected'
        r += '          <option value="" label="None"' + s +'> -- None -- </option>\n'
    if labels is None:
        labels = values
    for (v1, l1) in zip(values, labels):
        s = ''
        if v1 == default:
            s = ' selected'
        r += '          <option value="' + v1 +'" label="' + l1 + '"' + s + '>' + l1 + '</option>\n'
    r += '        </select>'
    return r
