source /envi/bin/activate
echo "In env $VIRTUAL_ENV"
echo "Starting gunicorn"

gunicorn -b 127.0.0.1:$PYHA_LISTEN_PORT luomuspyha.wsgi &