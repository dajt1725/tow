#!/usr/bin/python
import sys, string
sys.path.insert(0,'/home/temple24/python')
import tow

##### slurp up the form data into form ########################################
tow.log('logged out')
tow.cur.execute("delete from tow_session where id = %(id)s", {'id': tow.cookie.get('id').value})
tow.check_warnings()
tow.fini()
tow.print_results('Logged Out', tow.url('login'), 'You are logged out.', to_do = 'log in')
