# -*- coding: utf-8 -*-
# Author: swstorage

import time, ldap 

LDAP_SERVER = null
BASE_DN = 'dc = sz'

def get_userdn(username):
    try:
        ldap_cxn  = ldap.initialize(LDAP_SERVER)
        ldap_cxn.protocol_version = ldap.VERSION3
        ldap_cxn.simple_bind(username)

        search_scope = ldap.SCOPE_SUBTREE
        search_filter = '(uid=' + username + ')'

        result_id = ldap_cxn.search(BASE_DN, search_scope, search_filter, None)
        result_type, result_data = ldap_cxn.result(result_id, 1)

        #print ldap_result_id
        #print result_type
        #print result_data

        if len(result_data) != 0:
            userdn = result_data[0][0]
            return 1, userdn # User exists
        else:
            return 0, 3 # Error: User is not found
    except ldap.LDAPError, e:
        print e
        return 0, 4 # Error: Server is busy
    finally:
        ldap_cxn.unbind()
        del ldap_cxn


def validate_user(username, passwd, trynum = 6):
    isfound = 0
    userdn = None
    for i in range(trynum):
        isfound, userdn = get_userdn(username)
        if(isfound):
            break

    if isfound == 1:
        try:
            ldap_cxn = ldap.initialize(LDAP_SERVER)
            ldap_cxn.simple_bind_s(userdn, passwd)
            return 1 # User authentication passed
        except Exception as e:
            return 2 # User password error
    else:
        return userdn # 3: User is not found  4: LDAP server error

if __name__ == '__main__':
    USER_NAME = null
    USER_passwd = null
    print validate_user(USER_NAME, USER_passwd)


