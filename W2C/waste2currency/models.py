from django.db import models

# Create your models here.
class Customer(models.Model):
	address = models.CharField(max_length=200,primary_key=True,default="")
	name = models.CharField(max_length=200,default="")
	phone = models.CharField(max_length=200,default="")
	email = models.CharField(max_length=200,default="")
	password = models.CharField(max_length=200,default="")
	Ecoins = models.IntegerField(default=0)
	Fcoins = models.IntegerField(default=0)
	
	def __str__(self):
		return self.name


class Waste(models.Model):
	uuid = models.CharField(max_length=200,primary_key=True,default="")
	wtype = models.CharField(max_length=200,default="")
	weight = models.IntegerField(default=0)
	Createdby = models.CharField(max_length=200,default="")
	Ownedby = models.CharField(max_length=200,default="")


		