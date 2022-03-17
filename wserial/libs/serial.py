import sys
import glob
import serial

from wserial.libs.logger import get_logger

log = get_logger(module_name='serial')

def serial_ports():
	""" Lists serial port names

		:raises EnvironmentError:
				On unsupported or unknown platforms
		:returns:
				A list of the serial ports available on the system

		@credits: https://stackoverflow.com/a/14224477/11738218
	"""
	if sys.platform.startswith('win'):
		ports = ['COM%s' % (i + 1) for i in range(256)]
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		# this excludes your current terminal "/dev/tty"
		ports = glob.glob('/dev/tty[A-Za-z]*')
	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/tty.*')
	else:
		raise EnvironmentError('Unsupported platform')

	result = []
	for port in ports:
		try:
				s = serial.Serial(port)
				s.close()
				result.append(port)
		except (OSError, serial.SerialException):
				pass
	return result

def get_serial_port(name : str):
	log.info(f'opening port: `{name}`')
	serial_port = serial.Serial(name)
	if serial_port.is_open():
		serial_port.close()
	serial_port.open()
	return serial_port
