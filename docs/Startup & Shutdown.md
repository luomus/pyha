# Start and shutdown of the pyha service
In environmental development / For local experimentation: 

```shell
bash runserver.sh
```

or in the folder `/pyha/project`:

```shell
gunicorn -b ip:port luomuspyha.wsgi &
```

Run commands:

```shell
ps ax | grep pyha
kill <pid>
```
('pid' = process id for the pyha service)

or in the folder `/pyha`

```shell
source env/bin/activate
```

In the folder `/pyha/project` run:

```shell
python manage.py runserver <port>
```
(where 'port' is the service port for the process)

To stop the pyha service press:
```Ctrl+c```

and f.i. deactivate the virtualenv:

```shell
deactivate
```

On the server this can be done with:

```shell
systemctl status|stop|start pyha.service
```