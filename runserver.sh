source env/bin/activate
echo "In env $VIRTUAL_ENV"
if [ -e env_variables.sh ]
then
    echo "Initializing enviromental variables"

    . env_variables.sh

    echo "Starting gunicorn"

    cd project

    gunicorn -b 127.0.0.1:$PYHA_LISTEN_PORT --pid /run/pyha/pid wsgi &

    cd ..

    echo "To deactivate gunicorn use:"
    echo "ps ax | grep pyha"
    echo "kill <pid>"
    echo "<pid> = process pid determined by 'ps ax | grep pyha'"
    
else
    echo "Unable to find 'env_variables.sh'. Cannot start"
fi

deactivate
