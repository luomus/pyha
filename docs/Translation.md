# Translations
The contents of the e-mails and their translations can be found in the `project/pyha/templates/pyha/email` folder as text files in UTF-8 format.

The terms and their translations can be found in the `project/pyha/templates/pyha/requestform/terms` folder as html files.

* In the templates, translation strings look like `{% trans" Hello "%}`
    * If the template has translations, it must always have `{% load i18n%}` first
* In Python code, translation strings look like:
   ```
   from django.utils.translation import ugettext
   ...
   myMessage = ugettext ('Hello')
   ```

You can take the existing translations as a model.

----

The translations process goes like this:
1. Translation strings are collected into translation files with
   ```
   cd project
   python manage.py makemessages -a
   ```        
2. Finnish is used as a source language for the translations so you should add those translations manually to the file:
   ```
   project/pyha/locale/fi/LC_MESSAGES/django.po
   ```
   You can take the old translations as a model. Every "msgstr" field should have a value, empty strings are not taken into account when they are send to Crowdin.
3. Send translations to Crowdin with
   ```
   bash crowdin-update.sh
   ```
   The script requires Docker to be installed. You can also find "Crowdin Pyha" task in the CI service that does the same thing.
4. Make translations in the Crowdin service, then call the Crowdin update script again to fetch the translations.
5. Compile translations with
   ```
   cd project
   python manage.py compilemessages
   ```

Start the test server and check the translations which should now appear. You can also use the command `bash updateserver.sh` in the first and last step as it includes the collection and compilation of the translations.

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
