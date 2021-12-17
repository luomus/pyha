# Start and shutdown of the pyha service

## For local experimentation:

### Option 1

In the folder `/pyha`

```shell
source env/bin/activate
```

In the folder `/pyha/project` run:

```shell
python manage.py runserver <port>
```
(where 'port' is the service port for the process, can be left empty)

To stop the pyha service press:
```Ctrl+c```

and deactivate the virtualenv:

```shell
deactivate
```

### Option 2

```shell
bash runserver.sh
```

or in the folder `/pyha/project`:

```shell
gunicorn -b ip:port luomuspyha.wsgi &
```

You can kill the process with:

```shell
ps ax | grep pyha
kill <pid>
```
('pid' = process id for the pyha service)


## On the server

```shell
systemctl status|stop|start pyha.service
```