from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Collection(models.Model):
	collection_name = models.CharField(max_length=200)
	collection_id = models.CharField(max_length=100)
	collection_count = models.IntegerField()
	request = models.ForeignKey('Request', on_delete=models.CASCADE)
	# collection_contact
	# collection_license

	def __str__(self):
		return self.collection_name

class Request(models.Model):
	request_id = models.CharField(max_length=100, primary_key=True)
	request_source = models.CharField(max_length=10)
	request_email = models.CharField(max_length=100)
	approximateMatches = models.IntegerField()
	filter_list = models.CharField(max_length=1000)
	request_status = models.CharField(max_length=100)

	def __str__(self):
		return self.request_id
