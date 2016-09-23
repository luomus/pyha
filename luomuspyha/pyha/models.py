from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Collection(models.Model):
	collection_name = models.CharField(max_length=200)
	collection_id = models.CharField(max_length=100)
	collection_count = models.IntegerField()
	# collection_contact
	# collection_license

	def __str__(self):
		return self.collection_name

class Filter(models.Model):
	target_list = []
	time_list = []
	place_list = []

class Request(models.Model):
	request_id = models.CharField(max_length=100)
	request_source = models.CharField(max_length=10)
	request_email = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	filter_list = []
	collection_list = []
	request_status
	
