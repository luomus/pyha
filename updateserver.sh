if [ -e env_variables.sh ]
then
    echo "Initializing enviromental variables"

    . env_variables.sh

    echo "Updating server..."

    env/bin/python luomuspyha/manage.py collectstatic
    env/bin/python luomuspyha/manage.py makemigrations
    env/bin/python luomuspyha/manage.py migrate
    env/bin/python luomuspyha/manage.py createcachetable

else
    echo "Unable to find 'env_variables.sh'. Cannot start"
fi
echo "Completed"