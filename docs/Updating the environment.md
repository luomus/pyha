# Environment update
General script for updating the environment

in the `folder/Pyha`:

```shell
bash updateserver.sh
```

or if changes have been made to the `/Static/` folder alone you can do, 
in the folder `/Pyha`:

```shell
source env / bin / activate
```

Start in the /Pyha/project` folder

```shell
python manage.py collectstatic
```

And to leave the virtualenv run:

```shell
deactivate
```