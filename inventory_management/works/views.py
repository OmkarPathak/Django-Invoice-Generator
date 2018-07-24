from django.shortcuts import render, redirect
from .models import Work, AddWorkForm, HSCNumber, AddHSCForm, ChallanNumber, AddChallanForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import time, json

def render_to_pdf(template_src, context_dict={}):
    '''
        Helper function to generate pdf from html
    '''
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error Rendering PDF", status=400)

def generate_pdf(request):
    '''
        Helper function to generate pdf in case of ajax request
    '''
    context = request.GET
    request.session['context'] = context
    return redirect('get_pdf')

def get_pdf(request):
    pdf = render_to_pdf('pdf/invoice_generator.html', request.session['context'])
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_{}.pdf".format(time.strftime("%Y%m%d"))
        content = "inline; filename='{}'".format(filename)
        content = "attachment; filename='{}'".format(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

def generate_pdf_assembly(request):
    '''
        Helper function to generate pdf in case of ajax request
    '''
    context = request.GET.copy()
    context['works'] = json.loads(context['works'])
    request.session['context'] = context
    return redirect('get_pdf_assembly')

def get_pdf_assembly(request):
    pdf = render_to_pdf('pdf/invoice_generator_assembly.html', request.session['context'])
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_{}.pdf".format(time.strftime("%Y%m%d"))
        content = "inline; filename='{}'".format(filename)
        content = "attachment; filename='{}'".format(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

def get_code_values(request):
    if request.method == 'GET':
        code = request.GET.get('code')
        work = Work.objects.get(code=code)
        data = {
            'id': work.id,
            'code': work.code,
            'name': work.name,
            'amount': work.amount
        }
        return JsonResponse(data)

def get_hsc_values(request):
    if request.method == 'GET':
        code = request.GET.get('code')
        hsc = HSCNumber.objects.get(hsc_number=code)
        data = {
            'id'  : hsc.id,
            'cgst': hsc.cgst,
            'sgst': hsc.sgst
        }
        return JsonResponse(data)

def homepage(request):
    return render(request, 'base.html')

def invoice_generator_melt(request):
    challan_number = ChallanNumber.objects.get(id=1)
    works = Work.objects.all().order_by('code')
    hsc   = HSCNumber.objects.all()
    context = {
        'works'         : works, 
        'hsc'           : hsc,
        'challan_number': challan_number
    }
    return render(request, 'invoice.html', context)

def invoice_generator_assembly(request):
    challan_number = ChallanNumber.objects.get(id=1)
    works = Work.objects.all().order_by('code')
    hsc   = HSCNumber.objects.all()
    context = {
        'works'         : works, 
        'hsc'           : hsc,
        'challan_number': challan_number
    }
    return render(request, 'invoice_assembly.html', context)

def admin(request):
    '''
        To add new work entry.
        User can add a new entry with Work Code, Work Name and Work Rate/Amount
    '''
    form = AddWorkForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New Entry Added successfully')
        return redirect('admin')
    works = Work.objects.all().order_by('-date_added')
    return render(request, 'admin.html', {'form': form, 'works': works})

def admin_edit(request, id):
    '''
        To edit a single work entry that is already created
    '''
    work = get_object_or_404(Work, id=id)
    if request.method == 'POST':
        form = AddWorkForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
        messages.success(request, 'Entry Edited successfully')
        return redirect('admin')
    else:
        form = AddWorkForm(initial={
                                'code'  : work.code,
                                'name'  : work.name,
                                'amount': work.amount 
                            }, instance=work)
        return render(request, 'admin_edit_modal.html', {'form': form})

def admin_delete(request, id):
    '''
        To delete a single entry already created
    '''
    work = get_object_or_404(Work, id=id)
    work.delete()
    messages.success(request, 'Entry Deleted successfully')
    return redirect('admin')

def hsc(request):
    '''
        To add new HSC entry.
        User can add a new HSC Code with respective CGST and SGST amounts
    '''
    form = AddHSCForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New Entry Added successfully')
        return redirect('hsc')
    hsc = HSCNumber.objects.all()
    return render(request, 'hsc.html', {'form': form, 'hsc': hsc})

def hsc_edit(request, id):
    '''
        To edit a single hsc code entry that is already created
    '''
    hsc = get_object_or_404(HSCNumber, id=id)
    if request.method == 'POST':
        form = AddHSCForm(request.POST, instance=hsc)
        if form.is_valid():
            form.save()
        messages.success(request, 'Entry Edited successfully')
        return redirect('hsc')
    else:
        form = AddHSCForm(initial={
                                'hsc_number'  : hsc.hsc_number,
                                'cgst'        : hsc.cgst,
                                'sgst'        : hsc.sgst 
                            }, instance=hsc)
        return render(request, 'hsc_edit_modal.html', {'form': form})
        
def hsc_delete(request, id):
    '''
        To delete a single entry already created
    '''
    hsc = get_object_or_404(HSCNumber, id=id)
    hsc.delete()
    messages.success(request, 'Entry Deleted successfully')
    return redirect('hsc')

def challan_no_edit(request, id):
    '''
        To edit current entry of challan number that is already created
    '''
    challan = get_object_or_404(ChallanNumber, id=id)
    if request.method == 'POST':
        form = AddChallanForm(request.POST, instance=challan)
        if form.is_valid():
            form.save()
        messages.success(request, 'Entry Edited successfully')
        return redirect('challan_no')
    else:
        form = AddChallanForm(initial={
                                'challan_number'  : challan.challan_number
                            }, instance=challan)
        return render(request, 'challan_edit_modal.html', {'form': form})

def challan_no(request):
    '''
        Get Current Challan Number
    '''
    try:
        challan_number = ChallanNumber.objects.get(id=1)
    except ChallanNumber.DoesNotExist:
        ChallanNumber(challan_number=1).save()
        challan_number = ChallanNumber.objects.get(id=1)
    return render(request, 'challan.html', {'challan_number': challan_number})