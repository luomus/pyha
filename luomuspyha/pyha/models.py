from __future__ import unicode_literals

from django.db import models

class Collection(models.Model):
	collection_id = models.CharField(max_length=100)
	count = models.IntegerField()
	status = models.IntegerField()
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	# termsOfUse = models.CharField(max_length=1000
	# decision = models.CharField(max_length=100)
	# decisionDate = models.DateTimeField()
	# decisionExplanation = models.CharField(max_length=1000)
	# collectionContact
	# collectionLicense 

	def __str__(self):
		return self.collection_id

class Request(models.Model):
	id = models.CharField(max_length=100, primary_key=True)
	order = models.IntegerField()
	date = models.DateTimeField()
	source = models.CharField(max_length=30)
	email = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	downloadFormat = models.CharField(max_length=20)
	downloadIncludes = models.CharField(max_length=1000)
	status = models.IntegerField()	
	filter_list = models.CharField(max_length=1000)
	requests = models.Manager()
	# reason = models.CharField(max_length=1000)	

	def __str__(self):
		return self.id
