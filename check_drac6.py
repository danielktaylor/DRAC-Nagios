#!/usr/bin/python
import re, optparse, sys, paramiko, socket

# Return codes expected by Nagios
nagios_codes = {'OK': 0, 
                'WARNING': 1, 
                'CRITICAL': 2,
                'UNKNOWN': 3,
                'DEPENDENT': 4}

def nagios_return(exit_code, response):
	''' 
	prints the response message and exits the script with one
	of the defined exit codes
	'''
	print exit_code + ': ' + response
	sys.exit(nagios_codes[exit_code])

healthy_status = r'.*HealthState = 5 \(OK\)\n\s+OperationalStatus\[0\] = 2 \(OK\).*'

if __name__=='__main__':
	# Parse options
	parser = optparse.OptionParser(usage='Usage: %prog [options]')
	parser.add_option('-H', '--host', action="store", dest="host", help="DRAC Hostname")
	parser.add_option('-u', '--username', action="store", dest="username", help="Username")
	parser.add_option('-p', '--password', action="store", dest="password", help="Password")
	(options, args) = parser.parse_args()
	
	mandatory = ['host', 'username', 'password']
	for m in mandatory:
		if not options.__dict__[m]:
			parser.error("Incorrect number of arguments ('--help' to see list)")

	# Test components
	ssh = paramiko.SSHClient()
	try:
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(options.host,username=options.username,password=options.password)
		
		# Check status
		stdin, stdout, stderr = ssh.exec_command('show system1')
		output = ''.join(stdout.readlines())
		
		if not re.match(healthy_status,output,re.DOTALL):
			nagios_return('CRITICAL', 'Health or operational status failure detected.')
		
		nagios_return('OK', 'All checks passed.')
	except socket.gaierror, e:
		nagios_return('CRITICAL', 'Cannot connect to host: ' + str(e))
	except socket.error, e:
		nagios_return('CRITICAL', 'Cannot connect to host: ' + str(e))
	finally:
		ssh.close()
