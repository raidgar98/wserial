from cgitb import handler
from http.server import BaseHTTPRequestHandler, HTTPServer
from simple_websocket_server import WebSocketServer, WebSocket

from wserial.libs.logger import get_logger

log = get_logger(module_name='Handler')
wlog = get_logger(module_name='WS Server')
hlog = get_logger(module_name='HTTP Server')

ENCODING = 'ascii'

class Handler:
	context = None
	handle_function = None
	close_function = None

	def handle(data) -> tuple:
		return Handler.handle_function(Handler.context, data)

	def __enter__(self):
		return self

	def __exit__(self, exception_type, exception_value, exception_traceback):
		if Handler.close_function:
			Handler.close_function()

		if exception_type == KeyboardInterrupt:
			log.info('closing on user request')
			return True
		elif exception_type is not None:
			log.error(f'cought error `{exception_type.__name__}`, with value: `{exception_value}`')
			log.error(f'traceback: {exception_traceback}')
			return False

		return True


class HttpHandler(BaseHTTPRequestHandler):

	def do_POST(self):
		length = int(self.headers['Content-length'])
		result = Handler.handle(self.rfile.read(length).decode(ENCODING))
		if result is not None:
			if result[0] != 200:
				hlog.error(f'Non 200 response with code {result[0]}: {result[1]}')
			resp = result[1].encode(ENCODING)
			self.send_response(result[0])
			self.send_header('Content-length', len(resp))
			self.send_header('Content-type', 'text; charset=ascii')
			self.end_headers()
			self.wfile.write(resp)


	def log_request(self, *args, **kwargs) -> None:
		hlog.debug(f'finished handling request with address {self.address_string()} with {args[0]} status code')
		pass

class WebsocketHandler(WebSocket):
	def handle(self):
		data = self.data
		if isinstance(data, (bytes, bytearray)):
			data = data.decode(ENCODING)
		result = Handler.handle(data)
		if result is not None:
			if result[0] != 200:
				wlog.error(f'Non 200 response with code {result[0]}: {result[1]}')
			self.send_message(result[1])

	def connected(self):
		wlog.debug(f'opened websocket for {self.address}')

	def handle_close(self):
		wlog.debug(f'closed websocket with {self.address}')

def run_http_server(port : int):
	hlog.info(f'starting HTTP server on 0.0.0.0:{port}')
	try:
		HTTPServer(('0.0.0.0', port), HttpHandler).serve_forever()
	except KeyboardInterrupt:
		hlog.info('stopping on user request')

def run_ws_server(port : int):
	wlog.info(f'starting WS server on 0.0.0.0:{port}')
	try:
		WebSocketServer(host='0.0.0.0', port=port, websocketclass=WebsocketHandler).serve_forever()
	except KeyboardInterrupt:
		wlog.info('stopping on user request')
