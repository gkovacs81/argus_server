# Server part

It has three components:

* server: hosting the webapplication and implementing REST API
* monitor: handling of sensors, syren, GSM/email communication

## Start

To start the server in development mode on your machinde:

```bash
./script/start_server.sh dev
```

To start the monitor in development mode on your machinde:

```bash
./script/start_monitor.sh dev
```