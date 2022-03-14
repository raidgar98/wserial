# WSERIAL

Listen on ws or http, and forward everythink to selected serial port

## Usage

here is `./main.py --help`

```
usage: wserial [-h] [-l [LIST_ONLY]] [-s SERIAL_PORT] [-p WS_PORT] [--http-port HTTP_PORT] [-w WHITELIST]

forwards data from websocket/http to serial port

options:
-h, --help            show this help message and exit
-l [LIST_ONLY], --list-serial-ports [LIST_ONLY]
								if given, prrogram just list avaiable sockets and closes itself
-s SERIAL_PORT, --serial-port SERIAL_PORT
								serial port to forward communications
-p WS_PORT, --port WS_PORT
								websocket port to listen on (if <=0 disabled) [= 8090]
--http-port HTTP_PORT
								http port to listen on, responds and works same as websocket, handy for debug (if <=0 disabled)
								[= -1]
-w WHITELIST, --whitelist WHITELIST
								path to file with allowed commands to forward (one command per line, no separators) [= Not set]
```

### Listing avaiable serial ports

`./main.py -l`

If found, there will be displayed list of them, if not:

```
Found no serial ports
```

### Starting server

<br>

#### HTTP
---

This method is not recommended, because it requires reconnecting call affter call, recommended is to use websocket.

To start HTTP server:

`./main.py -s COM1 --http-port 8090`

<br>

#### WS
---

To start WS server

`./main.py -s COM1 -p 8091`

<br>

#### WS + HTTP
---

`./main.py -s COM1 -p 8091 --http-port 8090`

Note: This program is not thread-safe it is not recommend to use (or even call) two servers at once. This is avaiable because of development proceess

<br>

#### Whitelisting
---

To narrow commands to 3 e.x.: `STOP` `START` `N` create file (here allow.txt):

```
STOP
START
N
```

and run:

`./main.py -s COM1 -p 8091 -w allow.txt`


---

## Communication

Format used for communication is simple: body is forwarded to serial port as is

Note: For HTTP use POST method

If confiramtion is required add exclamation at the begining. Send `!STOP` instead of `STOP`, and `STOP` will be forwarded to serial port

<br><br>

In following examples server is started as:

`./main.py --http-port 8090 -p 8091 -s 'COM1'`

Example curls:

```
$ curl -s -d 'START' http://localhost:8090 -vvv

*   Trying 127.0.0.1:8090...
* Connected to localhost (127.0.0.1) port 8090 (#0)
> POST / HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/7.81.0
> Accept: */*
> Content-Length: 5
> Content-Type: application/x-www-form-urlencoded
>
* Empty reply from server
* Closing connection 0
```


```
$ curl -s -d '!START' http://localhost:8090 -vvv

*   Trying 127.0.0.1:8090...
* Connected to localhost (127.0.0.1) port 8090 (#0)
> POST / HTTP/1.1
> Host: localhost:8090
> User-Agent: curl/7.81.0
> Accept: */*
> Content-Length: 6
> Content-Type: application/x-www-form-urlencoded
>
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: BaseHTTP/0.6 Python/3.10.2
< Date: Mon, 14 Mar 2022 18:12:24 GMT
< Content-length: 2
< Content-type: text; charset=ascii
<
* Closing connection 0
```

Example [wscat](https://github.com/websockets/wscat) (websocket communication):

```
$ wscat -c ws://localhost:8091
Connected (press CTRL+C to quit)
> STOP
> START
> !STOP
< OK
> !START
< OK
> STOP
> N
> !N
< OK
>
```
