# ArPI Server

The server part of the ArPI Home Security system written in python running mainly on the Raspberry PI Zero device. It has three components:

* database: PostgreSQL database for storing the configuration
* server: Flask application for hosting the webapplication and implementing REST API
* monitor: multithreaded python application for managing the security system and notifying the client

The server and monitor can communicate with file socket based IPC. Clients can connect to the monitor service for getting notifications with socket-io.


## Starting the application in development mode on your machine

Before starting the components you need to build the "development" [web application](https://github.com/ArPIHomeSecurity/arpi_webapplication).


1. Starting the database:

    ```bash
    ./scripts/start_database.sh dev

    # prepare the database (only if you start the database container first time)
    # add structure
    ./scripts/update_database_struct.sh dev
    # add example data
    ./scripts/update_database_data.sh dev test_01
    ```

2. Starting the server (REST API):

    ```bash
    ./script/start_server.sh dev
    ```

3. Starting the monitoring service:

    ```bash
    ./script/start_monitor.sh dev
    ```

## Running the server on the Raspberry PI Zero

The component of the security system are managed by systemd services.

```bash
sudo systemctl <status|start|stop> <nginx|argus_server|argus_monitor>
```

* nginx: for hosting the webapplication
* argus_server
* argus_monitor

You can read the logs of the system in the journal.

```bash
journalctl -f -u <argus_server|argus_monitor>
```

---

<a href="https://www.paypal.me/gkovacs81/">
  <img alt="Support via PayPal" src="https://cdn.rawgit.com/twolfson/paypal-github-button/1.0.0/dist/button.svg"/>
</a>
