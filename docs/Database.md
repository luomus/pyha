# Database

## In general

Uses Oracle database (12c).
In the case you want to see create table statements, you can do the following:

In the `folder/pyha` activate the virtualenv (with all Python dependencies installed):

```shell
source env/bin/activate
```

Start the service in the `/pyha/project` folder:

```shell
python manage.py sqlmigrate Pyha 0001
...
python manage.py sqlmigrate Pyha <XXXX>

deactivate
```

where <XXXX> is the largest number in the `/pyha/project/pyha/migrations/` folder.



## Data model
NOTE: These might not be up-to-date. The latest models can be found in the file `/pyha/project/pyha/models.py`.

### Request:
A single data request.

```
id = models.AutoField (primary_key = True) #id starts at one and goes up
lajiId = models.CharField (max_length = 200) #id given by laji.api
description = models.CharField (max_length = 400) #description given by the requester for his request

#for status
#status 0: Awaiting requestor approval
#status 1: Waiting for the editor to process it
#status 2: Partially accepted
#status 3: Rejected
#status 4: Approved
#status 5: Unknown
#status 6: Awaiting answer to additional questions
#status 7: Waiting for the download to complete
#status 8: Downloadable

status = models.IntegerField ()

date = models.DateTimeField ()
source = models.CharField (max_length = 60)
user = models.CharField (max_length = 100)
approximateMatches = models.IntegerField ()
downloadFormat = models.CharField (max_length = 40)
downloadIncludes = models.CharField (max_length = 1000)
downloadDate = models.CharField (max_length = 400, null = True)
filter_list = models.CharField (max_length = 2000)
personName = models.CharField (max_length = 100, null = True)
personStreetAddress = models.CharField (max_length = 100, null = True)
personPostOfficeName = models.CharField (max_length = 100, null = True)
personPostalCode = models.CharField (max_length = 100, null = True)
personCountry = models.CharField (max_length = 100, null = True)
personEmail = models.CharField (max_length = 100, null = True)
personPhoneNumber = models.CharField (max_length = 100, null = True)
personOrganizationName = models.CharField (max_length = 100, null = True)
personCorporationId = models.CharField (max_length = 100, null = True)
reason = models.CharField (max_length = 16000, null = True)
lang = models.CharField (max_length = 10, default = 'en')
changedBy = models.CharField (max_length = 100) #Last instance variable as tag + name of the function used for the change
```

### Collection: 
Decision for a specific collection of a data request  

```
address = models.CharField (max_length = 500) #Collection ID api.laji.fi:ss  
count = models.IntegerField () #Number of roughened observations

#for collection.status
#status 0: Awaiting requestor approval
#status 1: Waiting for the editor to process it
#status 3: Rejected
#status 4: Approved
#status 6: Awaiting answer to additional questions

status = models.IntegerField () # The status of the decision, which is described as a numeric value
request = models.ForeignKey ('Request', on_delete = models.CASCADE)
taxonSecured = models.IntegerField (default = 0) # Number of sensitive observations
customSecured = models.IntegerField (default = 0) #Number of data-restricted observations
downloadRequestHandler = models.CharField (max_length = 500, null = True) # Identifiers of material owners at api.laji.fi at the moment the request is processed.
decisionExplanation = models.CharField (max_length = 1000, null = True) # Justification of the decision in text
changedBy = models.CharField (max_length = 100) #Last instance variable as tag + name of the function used for the change
```

### RequestContact: 
Contains additional contacts if one of the contacts in the Request table was not sufficient.

```
id = models.AutoField (primary_key = True)
request = models.ForeignKey ('Request', on_delete = models.CASCADE)
personName = models.CharField (max_length = 100, null = True)
personStreetAddress = models.CharField (max_length = 100, null = True)
personPostOfficeName = models.CharField (max_length = 100, null = True)
personPostalCode = models.CharField (max_length = 100, null = True)
personCountry = models.CharField (max_length = 100, null = True)
personEmail = models.CharField (max_length = 100, null = True)
personPhoneNumber = models.CharField (max_length = 100, null = True)
personOrganizationName = models.CharField (max_length = 100, null = True)
personCorporationId = models.CharField (max_length = 100, null = True)
changedBy = models.CharField (max_length = 100) #Last instance variable as tag + name of the function used for the change
```

### RequestLogEntry:
Contains a log of events related to requests

```
VIEW = 'VIEW'
ACCEPT = 'ACC'
DECISION_POSITIVE = 'POS'
DECISION_NEGATIVE = 'NEG'
ACTION = (
(VIEW, 'views request'),
(ACCEPT, 'accepts terms of use'),
(DECISION_POSITIVE, 'accepts use of data'),
(DECISION_NEGATIVE, 'declines use of data'),
)
request = models.ForeignKey (Request, on_delete = models.CASCADE)
collection = models.ForeignKey (Collection, on_delete = models.SET_NULL, blank = True, null = True)
date = models.DateTimeField (auto_now_add = True)
user = models.CharField (max_length = 100)
role = models.CharField (max_length = 100)
action = models.CharField (max_length = 5, choices = ACTION)
changedBy = models.CharField (max_length = 100) #Last instance variable as tag + name of the function used for the change
```

### RequestSensitiveChatEntry: 
Includes government discussions NOTE: NOT USED ANYMORE? Sensitive data is no longer approved separately.

```
request = models.ForeignKey (Request, on_delete = models.CASCADE)
date = models.DateTimeField (auto_now_add = True)
user = models.CharField (max_length = 100)
message = models.CharField (max_length = 2000)
changedBy = models.CharField (max_length = 100) #Last instance variable as tag + name of the function used for the change
```

### RequestHandlerChatEntry: 
Includes discussions between data owners/decision makers

```
request = models.ForeignKey (Request, on_delete = models.CASCADE)
date = models.DateTimeField (auto_now_add = True)
user = models.CharField (max_length = 100)
message = models.CharField (max_length = 2000)
target = models.CharField (max_length = 200)
changedBy = models.CharField (max_length = 100) #Last instance variable as tag + name of the function used for the change
```

### RequestInformationChatEntry: 
Contains discussions between data owners and the applicant

```
request = models.ForeignKey (Request, on_delete = models.CASCADE)
date = models.DateTimeField (auto_now_add = True)
user = models.CharField (max_length = 100)
question = models.BooleanField ()
message = models.CharField (max_length = 2000)
target = models.CharField (max_length = 200) # Subject of the request for additional information, eg material identifier or 'sens' for sensitive
changedBy = models.CharField (max_length = 100) #Last instance variable as tag + name of the function used for the change
```

### ContactPreset: 
Contains contacts previously filled in by the user.

```
user = models.CharField (primary_key = True, max_length = 100)
requestPersonName = models.CharField (max_length = 100, null = True)
requestPersonStreetAddress = models.CharField (max_length = 100, null = True)
requestPersonPostOfficeName = models.CharField (max_length = 100, null = True)
requestPersonPostalCode = models.CharField (max_length = 100, null = True)
requestPersonCountry = models.CharField (max_length = 100, null = True)
requestPersonEmail = models.CharField (max_length = 100, null = True)
requestPersonPhoneNumber = models.CharField (max_length = 100, null = True)
requestPersonOrganizationName = models.CharField (max_length = 100, null = True)
requestPersonCorporationId = models.CharField (max_length = 100, null = True)
changedBy = models.CharField (max_length = 100) #Last instance variable as tag + name of the function used for the change
```
