* Templateissa käännökset tyylillä `{% trans "Moikka" %}` 
    * Jos templatessa on käännettävää, sen alkupuolella pitää aina olla `{% load i18n %}`
* Python-koodissa käännökset tyylillä:
````
    from django.utils.translation import ugettext as _
    # ...
    myMessage = _('Moikka')
````
* Javascript-koodissa käännökset tyylillä `var myMessage = gettext('Moikka');` 

Ota mallia valmiista käännöksistä.

Kun olet käsitellyt koodin ylläolevan mukaisesti, voit käyttää komentoa:

     bash updateserver.sh

tai:

    ./manage.py makemessages -a

Se kerää käännettävät templateista ja .py -tiedostoista django.po -tiedostoihin. Ja sitten:

    ./manage.py makemessages -a -d djangojs

Se kerää .js -tiedostoista.

Sitten editoi käännöstiedostoja, jotka ovat seuraavan näköisissä paikoissa:

* `pyha/locale/en/LC_MESSAGES/django.po`   <- template & py -tekstit
* `pyha/locale/en/LC_MESSAGES/djangojs.po`  <- js-tekstit

Kirjoita käännökset käsin näihin `.po` tiedostoihin (ota mallia vanhoista käännöksistä).

Sitten tee

    ./manage.py compilemessages

Ja sitten käynnistä testiserveri tekemällä `bash runserver.sh` -- nyt käännösten pitäisi näkyä.

----

Jos kielivalitsinta ei ole käytössä, voit testata eri kieliä muuttamalla Chromen preferred languagea seuraavasti:

* Settings -> etsi "language" -> "Language and input settings". Uudelleenjärjestä/lisää kieliä. Ylimmäksi vedetty kieli on se mitä Chrome preferoi eniten. Done. 

Sitten F5 ja kielen pitäisi olla vaihtunut.
