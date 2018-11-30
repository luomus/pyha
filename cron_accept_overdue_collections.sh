echo date
source env/bin/activate
echo "In env $VIRTUAL_ENV"
if [ -e env_variables.sh ]
then
    echo "Initializing enviromental variables"

    . env_variables.sh

    echo "Starting auto-accepting overdue collections"
	
    cd project

    python manage.py accept_overdue_collections

    cd ..

    echo "Finished auto-accepting overdue collections"
    
else
    echo "Unable to find 'env_variables.sh'. Cannot start"
fi

deactivate
