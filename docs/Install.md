# Installation of pyha

These instructions are written for Ubuntu, and for the remote Oracle database server.
The instructions require that all user-specific (non-sudo) commands be executed by user created for runing this service.
For example user `pyha` and group `pyha`.

## 1 - Oracle client

Follow the steps below to install:
- Download the following Oracle clients [here](https://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html):
  * Oracle Instant Client Basic Linux 12.1.0.2.0
  * Instant Client SDK Linux 12.1.0.2.0

- Extract the archives (they will be extracted to the same folder).
  Then add the following lines to the file `~ / .bashrc`:

   ```shell
   export ORACLE_HOME=path/to/instantclient_12_1  
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME
   ```
  
  Enter in a terminal:

   ```shell
   source ~/.bashrc
   ```

  or restart the terminal for the `~/.bashrc` installed environment variables to take effect.


- Then do the following:

   cd path/to/instantclient_12_1
   ```shell
   ln -s libclntsh.so.12.1 libclntsh.so  
   ln -s libocci.so.12.1 libocci.so
   ```

## 2 - To get started

Install the following packages

```shell
sudo apt-get install && sudo apt-get update
sudo apt-get install build-essential python3 python-pip python3-pip python-virtualenv git libaio1
```

Create a folder where you plan to install the environment, f.i. and clone the `pyha` repository in it:

```shell
mkdir ~/pyha
```

Navigate to the folder

```shell
cd ~/pyha
```

clone repository:

```git clone https://bitbucket.org/luomus/pyha.git```

Navigate to the folder created after this called `pyha`:
```shell
cd pyha
```

## 3 - Automated installation

Make sure that all cloned files and the `pyha` folder have the rights of the user created for the `pyha` system,
as well as the execution rights of the shell scripts (*.sh files).

```shell
chmod u+x *.sh
```

Run the script created for automatic installation:

```shell
./install.sh
```

If the automatic installation was successful, you can skip step 4.

## 4 - Manual installation

The following line creates a new `virtualenv` environment with python 3 in its own folder env:

```shell
virtualenv -p python3 env
```

Open the python virtual environment:

```shell
source env/bin/activate
```

Install the programs required by the python virtual environment:

```shell
pip install -r Requirements.txt
```
	
and / or
	
```shell
pip3 install -r Requirements.txt
```

Create a file:

```shell
touch env_variables.sh
```

Add all environment variables to the template here (see the list of variables with examples in the `install.sh` file):

    export ENVAR='content'
    ...
    export ENVARx-1='contentx-1'
    export ENVARx='contentx'


ENVAR Names are listed in the KEYS variable, as well as the correct type of content values in the string commenting on the ENVAR variable name.

## 5 - Starting the service

### After successful step 3 
If step 3 was successful, you can transfer the files:

    pyha.service 
    pyha.socket 

from the `services` folder to the `/etc/systemd/system` service folder.

If you use the `pyha` service via Apache at: `hostdomain / pyha`, put:
`services/pyha.conf` in folder `/etc/httpd/conf.d/`.

Add `services/pyha.cron` to the user's crontab file directory (usually `/var/spool/cron`) for scheduled functionality, 
or preferably edit the user's crontab file with the command below and add the `pyha.cron` file's content.

```shell
crontab -e
```

### Step 3 unsuccessful
If step 3 was not successful, create a file (pyha.service):
	
    /etc/systemd/system/pyha.service

with contents:

	[Unit]
	Description=pyha
	Requires=pyha.socket
	After=network.target

	[Service]
	PIDFile=/run/pyha/pid
	User=pyha
	Group=pyha
	WorkingDirectory=<path/to/folder/pyha project>

Add all environment variables to the template (see list and example from install.sh): #

	Environment=ENVAR='content'
	...
	Environment=ENVARx='contentx'

	ExecStart=path/to/folder/env/bin/gunicorn --threads 3 --timeout 600 --pid /run/pyha/pid wsgi
	ExecReload=/bin/kill -s HUP $MAINPID
	ExecStop=/bin/kill -s TERM $MAINPID
	PrivateTmp=true

	[Install]
	WantedBy=multi-user.target

Create another file (pyha.socket):

	/etc/systemd/system/pyha.socket

with contents:

	[Unit]
	Description=pyha socket
	
	[Socket]
	ListenStream=/run/pyha/socket
	
	[Install]
	WantedBy=sockets.target

If you use Apache webserver with: 'hostdomain/pyha', create a file:

	/etc/httpd/conf.d/pyha.conf

with the following contents:

	#Pyha
	<Directory "path/to/project/static">
	    AllowOverride None
	    Require all granted
	</Directory>
	ProxyPass               /pyha/static !
	ProxyPass               /pyha http://localhost:port
	ProxyPassReverse        /pyha http://localhost:port
	Alias /pyha/static     path/to/project/static
	
The timers work as internal threads, so there is no need to use crontab.

## 6 - Finally

Make sure that all of the above files and the `pyha` folder have the rights of the user created for the `pyha` system,
as well as the permissions on the shell scripts (*.sh) files.
For example, for the user `pyha` and the group `pyha`.
