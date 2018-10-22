echo date
source env/bin/activate
echo "In env $VIRTUAL_ENV"
if [ -e env_variables.sh ]
then
    echo "Initializing enviromental variables"

    . env_variables.sh

    echo "Starting handlermail"

    cd project

    python manage.py handlermail

    cd ..

    echo "Finished handlermail"
    
else
    echo "Unable to find 'env_variables.sh'. Cannot start"
fi

deactivate
