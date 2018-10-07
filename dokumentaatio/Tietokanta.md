# Tietokanta

## Yleisesti

K�ytt�� Oracle-tietokantaa.
Mik�li djangon luomat kent�t haluaa SQL kielell�. 

env/bin/python project/manage.py sqlmigrate pyha 0001

Olettaen ett� olet asettanut ymp�rist�muuttujat terminaaliin [Asennus](Asennus.md).

env_variables.sh

## Taulut

Collection: #Sis�lt�� tietyst� kokoelmasta aineistopyynn�ss� haluttujen tietojen yleist� dataa, sek� siihen liittyv�n p��t�ksen ja p��t�stekstin

	address = CharField(max_length=500) #Kokoelman tunniste api.laji.fi:ss�
	count = IntegerField()  #Karkeistettujen havaintojen m��r�
	
	#for status
	#status 1: Odottaa aineiston toimittajan k�sittely�
	#status 2: Osittain hyv�ksytty
	#status 3: Hyl�tty
	#status 4: Hyv�ksytty
	#status 5: Tuntematon

	status = models.IntegerField() #P��t�ksen tila, mit� kuvataan numeroarvona
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	taxonSecured = models.IntegerField(default=0) #Sensitiivisten havaintojen m��r�
	customSecured = models.IntegerField(default=0)  #Ainestokohtaisesti rajoitettujen havaintojen m��r�
	downloadRequestHandler = models.CharField(max_length=500,null=True) #Aineistonomistajien tunnisteet api.laji.fi:ss� hetkell�, kun pyynt� annetaan k�sitelt�v�ksi.
	decisionExplanation = models.CharField(max_length=1000,null=True) #P��t�ksen perustelut tekstin�	

Request: #Sis�lt�� aineistopyynn�n tietoja, sen sensitiivisiin aineistoihin liittyv�n p��t�ksen ja p��t�stekstin
	
	id = models.AutoField(primary_key=True) #id alkaa ykk�sest� ja nousee
	lajiId = models.CharField(max_length=200) #id given by laji.api
	description = models.CharField(max_length=400)  #description given by the requester for his request
	
	#for status
	#status 0: Ei sensitiivist� tietoa
	#status 1: Odottaa aineiston toimittajan k�sittely�
	#status 2: Osittain hyv�ksytty
	#status 3: Hyl�tty
	#status 4: Hyv�ksytty
	#status 5: Tuntematon
	#status 6: Odottaa vastausta lis�kysymyksiin
	#status 7: Odottaa latauksen valmistumista
	#status 8: Ladattava
	
	status = models.IntegerField()
	
	#for sensstatus
	#status 0: Ei sensitiivist� tietoa
	#status 1: Odottaa aineiston toimittajan k�sittely�
	#status 3: Hyl�tty
	#status 4: Hyv�ksytty
	#status 5: Tuntematon
	#status 99: Ohitettu
	
	sensstatus = models.IntegerField()
	sensDecisionExplanation = models.CharField(max_length=1000,null=True)
	sensComment = models.CharField(max_length=1000,null=True)
	date = models.DateTimeField()
	source = models.CharField(max_length=60)
	user = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	downloadFormat = models.CharField(max_length=40)
	downloadIncludes = models.CharField(max_length=1000)
	downloadDate = models.CharField(max_length=400,null=True)
	filter_list = models.CharField(max_length=2000)
	personName = models.CharField(max_length=100,null=True)
	personStreetAddress = models.CharField(max_length=100,null=True)
	personPostOfficeName = models.CharField(max_length=100,null=True)
	personPostalCode = models.CharField(max_length=100,null=True)
	personCountry = models.CharField(max_length=100,null=True)
	personEmail = models.CharField(max_length=100,null=True)
	personPhoneNumber = models.CharField(max_length=100,null=True)
	personOrganizationName = models.CharField(max_length=100,null=True)
	personCorporationId = models.CharField(max_length=100,null=True)
	reason = models.CharField(max_length=16000,null=True)

RequestContact: #Sis�lt�� lis�� yhteystietoja, mik�li Request taulun yhteystiedot eiv�t riitt�neet.

	id = models.AutoField(primary_key=True)
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	personName = models.CharField(max_length=100,null=True)
	personStreetAddress = models.CharField(max_length=100,null=True)
	personPostOfficeName = models.CharField(max_length=100,null=True)
	personPostalCode = models.CharField(max_length=100,null=True)
	personCountry = models.CharField(max_length=100,null=True)
	personEmail = models.CharField(max_length=100,null=True)
	personPhoneNumber = models.CharField(max_length=100,null=True)
	personOrganizationName = models.CharField(max_length=100,null=True)
	personCorporationId = models.CharField(max_length=100,null=True)

RequestLogEntry: #Sis�lt�� pyynt�ihin liittyvien tapahtumien lokin

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
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, blank=True, null=True)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	role = models.CharField(max_length=100)
	action = models.CharField(max_length=5, choices=ACTION)

RequestChatEntry: #Sis�lt�� viranomaisten keskustelut

	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	message = models.CharField(max_length=2000)

RequestInformationChatEntry: #Sis�lt�� lis�tietopyynt�jen keskustelut

	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	question = models.BooleanField()
	message = models.CharField(max_length=2000)
	target = models.CharField(max_length=200) #Lis�tietopyynt�keskustelun kohde esim. aineiston tunniste tai sens

ContactPreset: #Sis�lt�� muistissa k�ytt�j�n aikaisemmin t�ytt�m�t yhteystiedot.

	user = models.CharField(primary_key=True, max_length=100)
	requestPersonName = models.CharField(max_length=100,null=True)
	requestPersonStreetAddress = models.CharField(max_length=100,null=True)
	requestPersonPostOfficeName = models.CharField(max_length=100,null=True)
	requestPersonPostalCode = models.CharField(max_length=100,null=True)
	requestPersonCountry = models.CharField(max_length=100,null=True)
	requestPersonEmail = models.CharField(max_length=100,null=True)
	requestPersonPhoneNumber = models.CharField(max_length=100,null=True)
	requestPersonOrganizationName = models.CharField(max_length=100,null=True)
	requestPersonCorporationId = models.CharField(max_length=100,null=True)

