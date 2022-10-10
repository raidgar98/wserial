#!/usr/bin/python3

from argparse import ArgumentParser
from concurrent.futures import Future, ProcessPoolExecutor
from functools import partial
from pathlib import Path
from sys import argv

from ordered_set import OrderedSet
from serial import Serial

from wserial.libs.logger import get_logger
from wserial.libs.serial import get_serial_port, serial_ports
from wserial.libs.server import ENCODING, Handler, run_http_server, run_ws_server

# CONSTS
BOOL_PARAM = dict(nargs='?', type=bool, const=True, default=False)
print = partial(print, flush=True)
log = get_logger(module_name='main')

# ARGUMENT PARSING
arg_engine = ArgumentParser(prog='wserial', description='forwards data from websocket/http to serial port')
arg_engine.add_argument('-l','--list-serial-ports', dest='list_only', help='if given, prrogram just list avaiable sockets and closes itself', **BOOL_PARAM)
arg_engine.add_argument('-s', '--serial-port', type=str, dest='serial_port', help='serial port to forward communications')
arg_engine.add_argument('-p', '--port', type=int, dest='ws_port', default=8090, help='websocket port to listen on (if <=0 disabled) [= 8090]')
arg_engine.add_argument('--http-port', type=int, dest='http_port', default=-1, help='http port to listen on, responds and works same as websocket, handy for debug (if <=0 disabled) [= -1]')
arg_engine.add_argument('-w', '--whitelist', type=str, dest='whitelist', default=None, help='path to file with allowed commands to forward (one command per line, no separators) [= Not set]')
args = arg_engine.parse_args(argv[1:])

# HANDLE LISTING
if args.list_only:
	ports = serial_ports()
	if len(ports):
		print('Found serial ports:\n' + '\n - '.join(ports))
	else:
		print('Found no serial ports')
	exit(0)


# ALIAS USER INPUT
SERIAL_PORT : str = args.serial_port
WS_PORT : int = args.ws_port
HTTP_PORT : int = args.http_port
WHITELIST : list = Path(args.whitelist) if args.whitelist is not None else None

# VALIDATE INPUT
assert WS_PORT != HTTP_PORT, f'{WS_PORT} != {HTTP_PORT}'
assert SERIAL_PORT is not None and len(SERIAL_PORT) > 0, f'serial port (-s flag) has to be defined. re-run with -l flag to get avaiable options'

# LOADING WHITELIST
if WHITELIST is not None:
	allowed_commands = []
	with WHITELIST.open('rt') as file:
		allowed_commands = [x.strip('\n') for x in file.readlines()]
	WHITELIST = OrderedSet(allowed_commands)

# HANDLER FOR SERVERS
def handler(port : Serial, data : str):
	ok_result = None
	try:

		if data.startswith('!'):
			ok_result = (200, 'OK')
			data = data[1:]

		if WHITELIST is None or data in WHITELIST:
			log.debug(f'writing to port: `{data}`')
			port.write(data.encode(ENCODING))
	except Exception as e:
		return (500, f'exception occured while writing to serial port: {e}')
	return ok_result

def handler_destructor():
	if Handler.context is not None and Handler.context.is_open:
		Handler.context.close()

# SETTING UP HANDLER CLASS
Handler.context = get_serial_port(SERIAL_PORT)
Handler.handle_function = handler
Handler.close_function = handler_destructor

# RUN SERVERS IN THREADS
with Handler():
	futures = []
	with ProcessPoolExecutor(max_workers=2) as executor:
		if WS_PORT > 0:
			futures.append(executor.submit(run_ws_server, port=WS_PORT))
		if HTTP_PORT > 0:
			futures.append(executor.submit(run_http_server, port=HTTP_PORT))

		# JOIN TASKS
		for fut in futures:
			fut : Future = fut
			exc = fut.exception()
			if exc is not None:
				print(f'got exception: {exc}')

