# Upgrading pyha
These upgrade instructions are written for Ubuntu, and for the remote Oracle database server.
The instructions require that all user-specific (non-sudo) commands be executed by your own user created for the Holy System.
For example, the Holy User and the Holy Group.

(June 12, 2019) The most significant changes that require upgrade commands are:

- Database changes.
- NO changes to the environment variable.
- New python library to install (schedule)
- Language changes.
- Static network elements.

#### Database updates may cause anomalies if users are able to use the service during the update.

## 0 - Start

In the terminal, go to the root directory of the Pyha git project.

Download the latest version of git:

```shell
git pull
```

## 1 - Automated updating

Run in the terminal:

```shell
bash updateserver.sh
```

Restart the service.

### If step 1 was successful until the end, you're done.

## 2 - Manual update

Examine the commands inside `updateserver.sh`.

Open the python virtual environment:

```shell
source env/bin/activate
```

Set the environment variables in the virtual environment.
Run the following commands:

```shell
pip install -r Requirements.txt (Python libraries)
```

and / or

```shell
pip3 install -r Requirements.txt (Python libraries)
```

```shell
rm -r project / Static (static network elements)

python project/manage.py collectstatic (static network elements)

python project/manage.py makemigrations (Database Changes)

python project/manage.py migrate (Database Changes)

python project/manage.py createcachetable (Database changes)

python project/manage.py makemessages -a (Language changes)

python project/manage.py compilemessages (Language changes)
```

Restart the service.
