if [ -e env_variables.sh ]
then
    echo "Initializing enviromental variables"

    . env_variables.sh

    echo "Updating server..."
    rm -r project/static
	env/bin/pip install -r Requirements.txt
	env/bin/pip3 install -r Requirements.txt
    env/bin/python project/manage.py collectstatic
    env/bin/python project/manage.py makemigrations
    env/bin/python project/manage.py migrate
    env/bin/python project/manage.py createcachetable
    cd project/pyha
    django-admin makemessages -a
    django-admin compilemessages
    cd ../..

else
    echo "Unable to find 'env_variables.sh'. Cannot start"
fi
echo "Completed"