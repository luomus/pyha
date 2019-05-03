echo date
source env/bin/activate
echo "In env $VIRTUAL_ENV"
if [ -e env_variables.sh ]
then
    echo "Initializing enviromental variables"

    . env_variables.sh

    echo "Starting missing_handlers_mail"

    cd project

    python manage.py missing_handlers

    cd ..

    echo "Finished missing_handlers_mail"
    
else
    echo "Unable to find 'env_variables.sh'. Cannot start"
fi

deactivate
