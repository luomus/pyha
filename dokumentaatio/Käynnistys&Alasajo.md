Palvelimella:

Käynnistä kansiossa "ohjelmakansio"/pyha/
gunicorn -b ip:port luomuspyha.wsgi &

Kaada komennoilla:
ps ax | grep pyha
kill <pid>
<pid> = prosessin id

Ympäristönkehityksessä/Paikalliseen kokeiluun: 

Käynnistä kansiossa "ohjelmakansio"/pyha/luomuspyha/
python manage.py runserver

Kaada painamalla: 
Ctrl+X
