Palvelimella:

K�ynnist� kansiossa "ohjelmakansio"/pyha/
gunicorn -b ip:port luomuspyha.wsgi &

Kaada komennoilla:
ps ax | grep pyha
kill <pid>
<pid> = prosessin id

Ymp�rist�nkehityksess�/Paikalliseen kokeiluun: 

K�ynnist� kansiossa "ohjelmakansio"/pyha/luomuspyha/
python manage.py runserver

Kaada painamalla: 
Ctrl+X
