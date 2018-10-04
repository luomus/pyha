# Tietokanta

## Yleisesti

Käyttää Oracle-tietokantaa

## Taulut


Collection: #Sisältää aineistopyynnön tietystä kokoelmasta haluttujen tietojen yleistä dataa, sekä siihen liittyvän päätöksen ja päätöstekstin
	address = CharField(max_length=500) #Kokoelman tunniste api.laji.fi:ssä
	count = IntegerField()  #Karkeistettujen havaintojen määrä
	status = models.IntegerField() #Päätöksen tila, mitä kuvataan numeroarvona
	request = models.ForeignKey('Request', on_delete=models.CASCADE) #FOREIGNKEY aineistopyynnön numero, mihin aineistokokoelma kuuluu
	taxonSecured = models.IntegerField(default=0) #Sensitiivisten havaintojen määrä
	customSecured = models.IntegerField(default=0)  #Ainestokohtaisesti rajoitettujen havaintojen määrä
	downloadRequestHandler = models.CharField(max_length=500,null=True) #Aineistonomistajien tunnisteet api.laji.fi:ssä 
	decisionExplanation = models.CharField(max_length=1000,null=True) #Päätöksen perustelut tekstinä
	

@python_2_unicode_compatible
class Request(models.Model):
	#id alkaa ykkösestä ja nousee
	id = models.AutoField(primary_key=True)
	lajiId = models.CharField(max_length=200) #id given by laji.api
	description = models.CharField(max_length=400)  #description given by the requester for his request
	
	#for status
	#status 0: Ei sensitiivistä tietoa
	#status 1: Odottaa aineiston toimittajan käsittelyä
	#status 2: Osittain hyväksytty
	#status 3: Hylätty
	#status 4: Hyväksytty
	#status 5: Tuntematon
	#status 6: Odottaa vastausta lisäkysymyksiin
	#status 7: Odottaa latauksen valmistumista
	#status 8: Ladattava
	
	status = models.IntegerField()
	
	#for sensstatus
	#status 0: Ei sensitiivistä tietoa
	#status 1: Odottaa aineiston toimittajan käsittelyä
	#status 3: Hylätty
	#status 4: Hyväksytty
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
	requests = models.Manager()

	def __str__(self):
		return self.id

@python_2_unicode_compatible
class RequestContact(models.Model):
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
	
	def __str__(self):
		return self.id

@python_2_unicode_compatible
class RequestLogEntry(models.Model):
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
	requestLog = models.Manager()
	
	def __str__(self):
		return '%s (role: %s): %s (request: %d, collection: %s)' %(self.user, self.role, self.get_action_display(), self.request.id, self.collection )

@python_2_unicode_compatible		
class RequestChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	message = models.CharField(max_length=2000)
	requestChat = models.Manager()
	
	def __str__(self):
		return self.message

@python_2_unicode_compatible
class RequestInformationChatEntry(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=100)
	question = models.BooleanField()
	message = models.CharField(max_length=2000)
	target = models.CharField(max_length=200)
	requestInformationChat = models.Manager()
	
	def __str__(self):
		return self.message

@python_2_unicode_compatible
class ContactPreset(models.Model):
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

	def __str__(self):
		return self.user

