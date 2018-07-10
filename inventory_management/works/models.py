from django.db import models

class Melt(models.Model):
	code 		= models.CharField(max_length=200, null=True, blank=True)
	amount 		= models.IntegerField()
	date_added	= models.DateTimeField(auto_now_add=True)


class Assembly(models.Model):
	code 		= models.CharField(max_length=200, null=True, blank=True)
	amount 		= models.IntegerField()
	date_added	= models.DateTimeField(auto_now_add=True)


class Challan(models.Model):
	date_added	= models.DateTimeField(auto_now_add=True)
	cgst		= models.IntegerField()
	sgst		= models.IntegerField()
	amount 		= models.IntegerField()

class Report(models.Model):
	invoice_of 	= models.CharField(max_length=200, null=True, blank=True)
	challan 	= models.OneToOneField(Challan, null=True,blank=True, on_delete=models.CASCADE)