Ymp�rist�nkehityksess�/Paikalliseen kokeiluun: 

bash runserver.sh

tai

K�ynnist� kansiossa /pyha/project
gunicorn -b ip:port luomuspyha.wsgi &

Kaada komennoilla:
ps ax | grep pyha
kill <pid>
<pid> = prosessin id

tai

kansiossa /pyha

source env/bin/activate

K�ynnist� kansiossa /pyha/project
python manage.py runserver port

Kaada painamalla: 
Ctrl+X

deactivate

Palvelimella:

systemctl status|stop|start pyha.service
