from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Collection(models.Model):
	name = models.CharField(max_length=200)
	collection_id = models.CharField(max_length=100)
	count = models.IntegerField()
	status = models.CharField(max_length=100)
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	# decision = models.CharField(max_length=100)
	# decision_date = models.DateTimeField()
	# decision_explanation = models.CharField(max_length=1000)
	# collection_contact
	# collection_license 

	def __str__(self):
		return self.collection_id

class Request(models.Model):
	id = models.CharField(max_length=100, primary_key=True)
	order = models.IntegerField()
	date = models.DateTimeField()
	source = models.CharField(max_length=10)
	email = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	# downloadFormat = CharField(max_lenght=20)
	# downloadIncludes = []	
	filter_list = models.CharField(max_length=1000)
	requests = models.Manager()
	# reason = models.CharField(max_length=1000)	

	def __str__(self):
		return self.id
