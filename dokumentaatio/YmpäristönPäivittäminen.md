Yleinen skripti ympäristön päivittämiseen

kansiossa /pyha

bash updateserver.sh

tai

Mikäli tehty muutoksia pelkässä `/static/` kansiossa. Voi suorittaa:

kansiossa /pyha

source env/bin/activate

Käynnistä kansiossa /pyha/project

python manage.py collectstatic

deactivate