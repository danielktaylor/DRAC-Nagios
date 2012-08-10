#!/usr/bin/python
import re, optparse, sys, paramiko, socket

# DRAC Command prefix
cmd_prefix = 'smclp show system1/'

# Ignore these errors
# Key: host
# Value: list of components to skip
ignore = {
	'mymachine.mycompany.com':['fans1/tachsensor4'],
}

# Component sensors to check
components = [
	# Batteries
	'batteries1/sensor1',
	'batteries1/sensor2',
	# Voltage
	'voltages1/voltsensor1',
	'voltages1/voltsensor2',
	'voltages1/voltsensor3',
	'voltages1/voltsensor4',
	'voltages1/voltsensor5',
	'voltages1/voltsensor6',
	'voltages1/voltsensor7',
	'voltages1/voltsensor8',
	'voltages1/voltsensor9',
	'voltages1/voltsensor10',
	'voltages1/voltsensor11',
	'voltages1/voltsensor12',
	'voltages1/voltsensor13',
	'voltages1/voltsensor14',
	# Numeric voltage
	'voltages1/numericsensor1',
	'voltages1/numericsensor2',
	# Temperature
	'temperatures1/tempsensor1',
	'temperatures1/tempsensor2',
	# Fans
	'fans1/tachsensor1',
	'fans1/tachsensor2',
	'fans1/tachsensor3',
	'fans1/tachsensor4',
	'fans1/tachsensor5',
	'fans1/tachsensor6',
	'fans1/tachsensor7',
	'fans1/tachsensor8',
	'fans1/tachsensor9',
	'fans1/tachsensor10',
	'fans1/tachsensor11',
	'fans1/tachsensor12',
	'fans1/tachsensor13',
	'fans1/tachsensor14',
	'fans1/tachsensor15',
	'fans1/tachsensor16',
	# Fan redundancy
	'fans1/redundancyset1',
	# Power supplies
	'powersupplies1/pwrsupply1',
	'powersupplies1/pwrsupply2',
	# Power supply redundancy
	'powersupplies1/redundancyset1',
	# Power monitors
	'powermonitor1/numericsensor1',
	'powermonitor1/numericsensor2',
	# Hardware performance
	'hardwareperformance1/sensor1',
]

# Missing component string
missing_component = r'ERROR: Invalid target specified'

# Strings to look for in return status from the DRAC
# Newer versions of firmware capitalize first letter
success_strings = [
	r'.*CurrentState\s+= [Gg]ood.*',
	r'.*CurrentState\s+= [Nn]ormal.*',
	r'.*HealthState\s+= [Nn]ormal.*',
	r'.*RedundancyStatus\s+= [Ff]ull.*',
]

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

def test_component(ssh_handle, component):
	global cmd_prefix, missing_component, success_strings

	stdin, stdout, stderr = ssh.exec_command(cmd_prefix + component)
	output = ''.join(stdout.readlines())
	
	for expected_value in success_strings:
		if re.match(expected_value, output,re.DOTALL):
			# Component is in a good state
			return
	if re.match(missing_component, output,re.DOTALL):
		# Component not configured for this system, not a failure condition
		return
	else:
		nagios_return('CRITICAL', 'Component failure: ' + component)

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

		for device in components:
			if options.host in ignore and device in ignore[options.host]:
				continue
			test_component(ssh, device)

		nagios_return('OK', 'All checks passed.')
	except socket.gaierror, e:
		nagios_return('CRITICAL', 'Cannot connect to host: ' + str(e))
	except socket.error, e:
		nagios_return('CRITICAL', 'Cannot connect to host: ' + str(e))
	finally:
		ssh.close()
