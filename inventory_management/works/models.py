from django.db import models
from django.forms import ModelForm

class Work(models.Model):
	code 		= models.CharField(max_length=200, unique=True)
	name 		= models.CharField(max_length=200)
	amount 		= models.FloatField()
	date_added	= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return 'Code: ' + self.code + ', Name: ' + self.name


class Challan(models.Model):
	date_added	= models.DateTimeField(auto_now_add=True)
	cgst		= models.FloatField()
	sgst		= models.FloatField()
	amount 		= models.FloatField()

class ChallanNumber(models.Model):
	challan_number = models.IntegerField()

	def __str__(self):
		return str(self.challan_number)

class HSCNumber(models.Model):
	hsc_number  = models.CharField(max_length=200)
	cgst 		= models.FloatField(('CGST (in %)'))
	sgst 		= models.FloatField(('SGST (in %)'))
	date_added	= models.DateTimeField(auto_now_add=True)

class Report(models.Model):
	challan_number 	= models.IntegerField()
	date			= models.DateField()
	hsc_number		= models.CharField(max_length=200)
	cgst			= models.FloatField()
	sgst			= models.FloatField()
	amount			= models.FloatField()

class AddWorkForm(ModelForm):
	class Meta:
		model  = Work
		fields = ['code', 'name', 'amount']

class AddHSCForm(ModelForm):
	class Meta:
		model  = HSCNumber
		fields = ['hsc_number', 'cgst', 'sgst']

class AddChallanForm(ModelForm):
	class Meta:
		model  = ChallanNumber
		fields = ['challan_number']