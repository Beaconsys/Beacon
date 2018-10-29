import ldap3

ldap_server = 'ldap://10.0.2.1:389'
baseDN = 'dc=sz'
ldap_user = 'uid=swstorage, ou=People, dc=sz'
ldap_pwd ='nAGmH4rlll'

user_list = []
#get user's dn


def authorize(host=None, user=None, password=None):
    if not host:
        return False, 'no host'

    server = ldap3.Server(host, get_info=ldap3.ALL)
    conn = None
    auto_bind = False

    try:
        if user:
            if password:
                auto_bind = True
        conn = ldap3.Connection(server, user=user, password=password, auto_bind=auto_bind)
        if not auto_bind:
            succ = conn.bind()
        else:
            succ = True

        msg = conn.result
        conn.unbind()
        return succ, msg
    except Exception as e:
        if conn:
            conn.unbind()
        return False, e

if __name__ == '__main__':
    print authorize(ldap_server, ldap_user, ldap_pwd)
    #server = ldap3.Server(ldap_server, get_info=ldap3.ALL)
    #conn = ldap3.Connection(server, user='uid=' + ldap_user + ', ou=People, dc=sz', password=ldap_pwd, auto_bind=True)
    #print conn
    #conn = ldap3.Connection(server, auto_bind=True)
    #print server.info
