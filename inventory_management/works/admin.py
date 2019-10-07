from django.contrib import admin
from .models import Work, ChallanNumber, HSCNumber, Report, QuantityRate, MeltReport, MeltChallanNumber

admin.site.register(Work)
admin.site.register(ChallanNumber)
admin.site.register(MeltChallanNumber)
admin.site.register(HSCNumber)
admin.site.register(Report)
admin.site.register(MeltReport)
admin.site.register(QuantityRate)