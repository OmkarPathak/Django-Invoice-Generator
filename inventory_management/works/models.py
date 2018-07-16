from django.db import models
from django.forms import ModelForm

class Work(models.Model):
	code 		= models.CharField(max_length=200, unique=True)
	name 		= models.CharField(max_length=200)
	amount 		= models.IntegerField()
	date_added	= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return 'Code: ' + self.code + ', Name: ' + self.name


class Challan(models.Model):
	date_added	= models.DateTimeField(auto_now_add=True)
	cgst		= models.IntegerField()
	sgst		= models.IntegerField()
	amount 		= models.IntegerField()

class Report(models.Model):
	invoice_of 	= models.CharField(max_length=200, null=True, blank=True)
	challan 	= models.OneToOneField(Challan, null=True,blank=True, on_delete=models.CASCADE)

class AddWorkForm(ModelForm):
	class Meta:
		model  = Work
		fields = ['code', 'name', 'amount']