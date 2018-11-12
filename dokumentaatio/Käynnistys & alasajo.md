Ympäristönkehityksessä/Paikalliseen kokeiluun: 

bash runserver.sh

tai

Käynnistä kansiossa /pyha/project
gunicorn -b ip:port luomuspyha.wsgi &

Kaada komennoilla:
ps ax | grep pyha
kill <pid>
<pid> = prosessin id

tai

kansiossa /pyha

source env/bin/activate

Käynnistä kansiossa /pyha/project
python manage.py runserver port

Kaada painamalla: 
Ctrl+X

deactivate

Palvelimella:

systemctl status|stop|start pyha.service
