# Translations
Email headers and translations are currently found in the project/pyha/email.py file.
The contents of the e-mails and their translations can be found in the project/pyha/templates/pyha/email folder as text files in UTF-8 format.

The terms and their translations can be found in the project/pyha/templates/pyha/requestform/terms folder as html files.

* In the templates, translation strings look like `{% trans" Hello "%}`
    * If the template has translations, it must always have `{% load i18n%}` first
* In Python code, translation strings look like:
```
from django.utils.translation import ugettext
...
myMessage = ugettext ('Hello')
```

You can take the existing translations as a model.

Once you've processed the code as described above, you can use the command:

     bash updateserver.sh

or:

    ./manage.py makemessages -a

It collects the translation strings from templates and `*.py` files into `django.po` files.

Then edit the translation files in the following locations:

* `path/to/project/pyha/locale/en/LC_MESSAGES/django.po` <- template & py texts

Write the translations manually in these `.po` files (take the old translations as a model).

Then give the command:

    ./manage.py compilemessages

Start the test server by doing `bash runserver.sh` - and check the translations which should now appear.

----
If the text change you made is not displayed. Check the .po file above the translation line for the following:
```
#, fuzzy
# | msgid "secured_collections_in_request"
```
, it forces the translation to use msgid "secured_collections_in_request" instead of the translation you want.

If you don't have the language selector enabled, you can test different languages by changing your Chrome preferred language as follows:

* Settings -> search for "language" -> "Language and input settings". Rearrange / add languages. The top language is what Chrome prefers the most. Done.

Then F5 (refresh) and the language should be changed.
