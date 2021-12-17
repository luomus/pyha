# Environment update
General script for updating the environment

in the folder `/pyha`:

```shell
bash updateserver.sh
```

or if changes have been made to the `/static/` folder alone you can do, 
in the folder `/pyha`:

```shell
source env/bin/activate
```

Start in the `/pyha/project` folder

```shell
python manage.py collectstatic
```

And to leave the virtualenv run:

```shell
deactivate
```