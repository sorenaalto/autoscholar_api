# to be able to import ldap run pip install python-ldap 

import ldap
import sys
 
if __name__ == "__main__":
  	ldap_server="10.0.4.101"
	username = "sorena"
	password= "somepassword"
	# the following is the user_dn format provided by the ldap server
	user_dn = "uid="+username+",ou=someou,dc=somedc,dc=local"
	# adjust this to your base dn for searching
#	base_dn = "dc=somedc,dc=local"
	base_dn = "OU=Staff,OU=Users,OU=DUT Resources,DC=dut,DC=ac,DC=za"
	connect = ldap.open(ldap_server)
	search_filter = "sAMAccountName="+username
	try:
		#if authentication successful, get the full user data
		connect.bind_s(user_dn,password)
		result = connect.search_s(base_dn,ldap.SCOPE_SUBTREE,search_filter)
		# return all user data results
		connect.unbind_s()
		print result
	except ldap.LDAPError:
		connect.unbind_s()
		print "authentication error"

