Ympäristönkehityksessä/Paikalliseen kokeiluun: 

Käynnistä kansiossa /pyha/project
gunicorn -b ip:port luomuspyha.wsgi &

Kaada komennoilla:
ps ax | grep pyha
kill <pid>
<pid> = prosessin id

tai

Käynnistä kansiossa /pyha/project
python manage.py runserver port

Kaada painamalla: 
Ctrl+X

Palvelimella:

systemctl status|stop|start pyha.service
