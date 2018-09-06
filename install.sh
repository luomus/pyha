virtualenv -p python3 env

source env/bin/activate
pip install django
pip install requests
pip install cx_Oracle 
pip install gunicorn

cd pyha/luomuspyha/

python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable

echo "Installation has finished"
