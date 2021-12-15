# Translations
Email headers and translations are currently found in the project / Pyha / email.py file.
The contents of the e-mails and their translations can be found in the project / Pyha / templates / Pyha / email folder as text files in UTF-8 format.

The terms and their translations can be found in the project / Pyha / templates / Pyha / skipofficial / terms folder as html files.

* Templates have translations of `{% trans" Hello "%}`
    * If the template has a compiler, it must always have `{% load i18n%}` first
* Python code translations in style:
```
from django.utils.translation import ugettext
...
myMessage = ugettext ('Hello')
```

Take a sample of the completed translations.

Once you've processed the code as described above, you can use the command:

     bash updateserver.sh

or:

    ./manage.py makemessages -a

It collects compilers from templates and `*.py` files into `django.po` files.

Then edit the translation files in the following locations:

* `path / to / project / Pyha / locale / en / LC_MESSAGES / django.po` <- template & py texts

Write the translations manually in these `.po` files (take a sample of the old translations).

Then give the command:

    ./manage.py compilemessages

Start the test server by doing `bash runserver.sh` - and check the translations which should now appear.

----
If the text change you made is not displayed. Check the .po file above the translation line for the following:
    #, fuzzy
    # | msgid "secured_collections_in_request"
, it forces the translation to use msgid "secured_collections_in_request" instead of the translation you want.

If you don't have the language selector enabled, you can test different languages by changing your Chrome preferred language as follows:

* Settings -> search for "language" -> "Language and input settings". Rearrange / add languages. The top language is what Chrome prefers the most. Done.

Then F5 (refresh) and the language should be changed.
