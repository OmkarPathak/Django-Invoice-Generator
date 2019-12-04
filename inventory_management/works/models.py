from django.db import models
from django.forms import ModelForm
import datetime, calendar
from django import forms

class Work(models.Model):
	code 		= models.CharField(max_length=200, unique=True)
	name 		= models.CharField(max_length=200)
	amount 		= models.FloatField()
	date_added	= models.DateTimeField(auto_now_add=True)
	po_number	= models.CharField(max_length=1000, blank=True, null=True)
	jc_number	= models.CharField(max_length=1000, blank=True, null=True)


	def __str__(self):
		return 'Code: ' + self.code + ', Name: ' + self.name

class ChallanNumber(models.Model):
	'''
		Assembly Challan Number
	'''
	challan_number = models.IntegerField(default=0)

	def __str__(self):
		return str(self.challan_number)

class MeltChallanNumber(models.Model):
	melt_challan_number = models.IntegerField(default=0)

	def __str__(self):
		return str(self.melt_challan_number)

class HSCNumber(models.Model):
	hsc_number  = models.CharField(('HSN Code'), max_length=200)
	cgst 		= models.FloatField(('CGST (in %)'))
	sgst 		= models.FloatField(('SGST (in %)'))
	date_added	= models.DateTimeField(auto_now_add=True)

class Report(models.Model):
	challan_number 	= models.IntegerField(unique=True)
	date			= models.DateField()
	hsc_number		= models.CharField(max_length=200)
	cgst			= models.FloatField()
	sgst			= models.FloatField()
	total_amount	= models.FloatField()
	date_added		= models.DateTimeField(auto_now_add=True)

class MeltReport(models.Model):
	code			= models.CharField(max_length=200, blank=True, null=True)
	particular		= models.CharField(max_length=200)
	challan_number	= models.IntegerField(unique=True)
	date			= models.DateField()
	quantity		= models.FloatField()
	rate			= models.FloatField()
	amount			= models.FloatField()
	weight			= models.CharField(max_length=100, blank=True, null=True)
	scrap_weight	= models.CharField(max_length=100, blank=True, null=True)
	end_pieces		= models.CharField(max_length=100, blank=True, null=True)
	total_weight	= models.CharField(max_length=100, blank=True, null=True)

class QuantityRate(models.Model):
	report 			= models.ManyToManyField(Report)
	quantity 		= models.FloatField()
	rate 			= models.FloatField()
	amount 			= models.FloatField()

class AddWorkForm(ModelForm):
	class Meta:
		model  = Work
		fields = ['code', 'name', 'amount', 'po_number', 'jc_number']

class AddHSCForm(ModelForm):
	class Meta:
		model  = HSCNumber
		fields = ['hsc_number', 'cgst', 'sgst']

class AddChallanForm(ModelForm):
	class Meta:
		model  = ChallanNumber
		fields = ['challan_number']

class AddMeltChallanForm(ModelForm):
	class Meta:
		model  = MeltChallanNumber
		fields = ['melt_challan_number']

YEAR_CHOICES = []
for year in range(2018, datetime.datetime.now().year + 1):
    YEAR_CHOICES.append((year, year))

MONTHS_CHOICES = tuple(zip(range(1,13), (calendar.month_name[i] for i in range(1,13))))

class AssemblyReportForm(forms.Form):
	month = forms.ChoiceField(choices=MONTHS_CHOICES)
	year = forms.ChoiceField(choices=YEAR_CHOICES)

class MeltReportForm(forms.Form):
	month = forms.ChoiceField(choices=MONTHS_CHOICES)
	year = forms.ChoiceField(choices=YEAR_CHOICES)

class StockReportForm(forms.Form):
	month = forms.ChoiceField(choices=MONTHS_CHOICES)
	year = forms.ChoiceField(choices=YEAR_CHOICES)