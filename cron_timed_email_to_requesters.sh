echo date
source env/bin/activate
echo "In env $VIRTUAL_ENV"
if [ -e env_variables.sh ]
then
    echo "Initializing enviromental variables"

    . env_variables.sh

    echo "Starting mail to requesters"

    cd project

    python manage.py timed_email_to_requesters

    cd ..

    echo "Finished mail to requesters"

else
    echo "Unable to find 'env_variables.sh'. Cannot start"
fi

deactivate
