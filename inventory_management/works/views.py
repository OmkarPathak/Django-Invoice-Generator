from django.shortcuts import render, redirect
from .models import Work, HSCNumber, ChallanNumber, MeltChallanNumber, Report, QuantityRate, MeltReport
from .models import AddHSCForm, AddChallanForm, AddWorkForm, AssemblyReportForm, MeltReportForm, AddMeltChallanForm, StockReportForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import time, json, calendar, inflect
from django.db.models import Q
from xlsxwriter.workbook import Workbook
from django.conf import settings
import datetime
import os

num2words = inflect.engine()

def render_to_pdf(template_src, context_dict={}):
    '''
        Helper function to generate pdf from html
    '''
    context_dict['logo'] = os.path.join(settings.STATIC_ROOT, 'img', 'vew.jpeg')
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error Rendering PDF", status=400)

def fetch_resources(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

def generate_pdf(request):
    '''
        Helper function to generate pdf in case of ajax request
    '''
    context = request.GET.copy()
    request.session['context'] = context
    context['date'] = datetime.datetime.strptime(context.get('date'), '%Y-%m-%d').strftime('%d-%m-%Y')
    context['dated'] = datetime.datetime.strptime(context.get('dated'), '%Y-%m-%d').strftime('%d-%m-%Y')
    context['amount_in_words'] = num2words.number_to_words(round(float(context.get('grand_total')), 2)) + ' only'
    code            = request.GET.get('code1')
    particular      = request.GET.get('vendor_name1')
    challan_number  = request.GET.get('challan_number')
    date            = request.GET.get('date')
    quantity        = request.GET.get('quantity1')
    rate            = request.GET.get('rate1')
    amount          = request.GET.get('amount1')
    weight          = request.GET.get('weight1')
    scrap_weight    = request.GET.get('weight2')
    end_pieces      = request.GET.get('weight3')
    total_weight    = request.GET.get('total_weight')

    # If user enters the same challan number then the previous record for that paricular challan number
    # is deleted and new record is overriden onto the old one
    try:
        report = MeltReport(
                    code=code,
                    particular=particular,
                    challan_number=challan_number,
                    date=date,
                    quantity=quantity,
                    rate=rate,
                    amount=amount,
                    weight=weight,
                    scrap_weight=scrap_weight,
                    end_pieces=end_pieces,
                    total_weight=total_weight
                )
        report.save()

        challan = ChallanNumber.objects.first()
        challan.challan_number += 1
        challan.save()
    except:
        MeltReport.objects.filter(challan_number=challan_number).delete()
        report = MeltReport(
                    code=code,
                    particular=particular,
                    challan_number=challan_number,
                    date=date,
                    quantity=quantity,
                    rate=rate,
                    amount=amount,
                    weight=weight,
                    scrap_weight=scrap_weight,
                    end_pieces=end_pieces,
                    total_weight=total_weight
                )
        report.save()

        challan = ChallanNumber.objects.first()
        challan.challan_number += 1
        challan.save()

    return redirect('get_pdf')

def get_pdf(request):
    pdf = render_to_pdf('pdf/invoice_generator.html', request.session['context'])
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Melt_Invoice_{}.pdf".format(request.session.get('context').get('challan_number'))
        content = "inline; filename={}".format(filename)
        content = "attachment; filename={}".format(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

def generate_pdf_assembly(request):
    '''
        Helper function to generate pdf in case of ajax request
    '''
    context = request.GET.copy()
    context['works'] = json.loads(context['works'])
    context['amount_in_words'] = num2words.number_to_words(round(float(context.get('grand_total')), 2)) + ' only'
    challan_number = context.get('challan_number')
    hsc_number     = context.get('hsc_number')
    date           = context.get('date')
    cgst           = context.get('cgst_amount')
    sgst           = context.get('sgst_amount')
    total_amount   = context.get('grand_total')

    # If user enters the same challan number then the previous record for that paricular challan number
    # is deleted and new record is overriden onto the old one
    try:
        report = Report.objects.create(
                    challan_number=challan_number,
                    hsc_number=hsc_number,
                    date=date,
                    cgst=cgst,
                    sgst=sgst,
                    total_amount=total_amount
                )
        report.save()

        challan = ChallanNumber.objects.first()
        challan.challan_number += 1
        challan.save()
    except:
        QuantityRate.objects.filter(report__challan_number=challan_number).delete()
        Report.objects.filter(challan_number=challan_number).delete()
        report = Report.objects.create(
                    challan_number=challan_number,
                    hsc_number=hsc_number,
                    date=date,
                    cgst=cgst,
                    sgst=sgst,
                    total_amount=total_amount
                )
        report.save()

        challan = ChallanNumber.objects.first()
        challan.challan_number += 1
        challan.save()

    # Sometime user might delete a row dynamically and hence an empty dict is passed to server
    # Hence we will check if amount is present in the dict else we delete that particular dic record
    for index, work in enumerate(context.get('works')):
        if work.get('amount'):
            quant = QuantityRate.objects.create(
                        quantity=work.get('quantity'),
                        rate=work.get('rate'),
                        amount=work.get('amount')
                    )
            quant.save()
            quant.report.add(report)
        else:
            del context.get('works')[index]
    context['date'] = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
    context['dated'] = datetime.datetime.strptime(context.get('dated'), '%Y-%m-%d').strftime('%d-%m-%Y')
    request.session['context'] = context
    return redirect('get_pdf_assembly')

def get_pdf_assembly(request):
    pdf = render_to_pdf('pdf/invoice_generator_assembly.html', request.session['context'])
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Assembly_Invoice_{}.pdf".format(request.session.get('context').get('challan_number'))
        content = "inline; filename={}".format(filename)
        content = "attachment; filename={}".format(filename)
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
            'amount': work.amount,
            'po_number': work.po_number,
            'jc_number': work.jc_number
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
    return redirect('invoice_generator_assembly')

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
        To edit current entry of assembly challan number that is already created
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
        Get Current Challan Number of Assembly
    '''
    try:
        challan_number = ChallanNumber.objects.first()
    except ChallanNumber.DoesNotExist:
        ChallanNumber(challan_number=1).save()
        challan_number = ChallanNumber.objects.first()

    try:
        melt_challan_number = MeltChallanNumber.objects.first()
    except MeltChallanNumber.DoesNotExist:
        MeltChallanNumber(melt_challan_number=1).save()
        melt_challan_number = MeltChallanNumber.objects.first()

    return render(request, 'challan.html', {'challan_number': challan_number, 'melt_challan_number': melt_challan_number})

def melt_challan_no_edit(request, id):
    '''
        To edit current entry of melt challan number that is already created
    '''
    challan = get_object_or_404(MeltChallanNumber, id=id)
    if request.method == 'POST':
        form = AddMeltChallanForm(request.POST, instance=challan)
        if form.is_valid():
            form.save()
        messages.success(request, 'Entry Edited successfully')
        return redirect('challan_no')
    else:
        form = AddMeltChallanForm(initial={
                                'melt_challan_number'  : challan.melt_challan_number
                            }, instance=challan)
        return render(request, 'melt_challan_edit_modal.html', {'form': form})

def excel_export(reports, filename):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "attachment; filename=" + filename + ".xlsx"

    book = Workbook(response, {'in_memory': True})
    sheet = book.add_worksheet('Report')

    for col in range(50):
        sheet.set_column(col, col, 10)
    
    merge_format = book.add_format({
        'bold': 3,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 6
    })

    heading = book.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 6
    })

    data = book.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 6
    })

    # Table headings
    sheet.merge_range(
            'A1:I4', 
            'SALES\nVAIBHAV ENGINEERING WORKS\nS.No.15/11/3, \
             Old Warje Jakat Naka, Behind Kakde City, Karvanagar, \
             Pune-411052.', 
            merge_format)
    sheet.merge_range('A5:A6', 'HSN CODE', heading)
    sheet.merge_range('B5:B6', 'CHALLAN \n NUMBER', heading)
    sheet.merge_range('C5:C6', 'DATE', heading)
    sheet.merge_range('D5:D6', 'QUANTITY', heading)
    sheet.merge_range('E5:E6', 'RATE', heading)
    sheet.merge_range('F5:F6', 'BASIC AMOUNT', heading)
    sheet.merge_range('G5:G6', 'CGST', heading)
    sheet.merge_range('H5:H6', 'SGST', heading)
    sheet.merge_range('I5:I6', 'TOTAL', heading)

    row = 6

    # reports = Report.objects.filter(date__month=7)

    for report in reports:
        col = 0
        row += 1
        sheet.write(row, col, report.hsc_number, data)
        col += 1
        sheet.write(row, col, report.challan_number, data)
        col += 1
        sheet.write(row, col, report.date, data)
        col += 1
        for qr in QuantityRate.objects.filter(report=report):
            sheet.write(row, col, qr.quantity, data)
            col += 1
            sheet.write(row, col, qr.rate, data)
            col += 1
            sheet.write(row, col, qr.amount, data)
            row += 1    
            col -= 2
        col += 3
        row -= 1
        sheet.write(row, col, report.cgst, data)
        col += 1
        sheet.write(row, col, report.sgst, data)
        col += 1
        sheet.write(row, col, report.total_amount, data)

    sheet.conditional_format(6, 0, row, col, {'type': 'blanks', 'format' : data})
    book.close()

    return response

def report_assembly(request):
    if request.method == 'POST':
        form = AssemblyReportForm(request.POST)
        if form.is_valid():
            query = Q(
                        date__year=request.POST.get('year'),
                        date__month=request.POST.get('month')
                    )
            report = Report.objects.filter(query)
            return excel_export(report, 'Assembly_Report_' + calendar.month_name[int(request.POST.get('month'))] + '_' + request.POST.get('year'))
    else:
        form = AssemblyReportForm()
    return render(request, 'report_assembly.html', {'form': form})

def excel_export_melt(reports, filename):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "attachment; filename=" + filename + ".xlsx"

    book = Workbook(response, {'in_memory': True})
    sheet = book.add_worksheet('Report')

    for col in range(50):
        sheet.set_column(col, col, 6)
    
    merge_format = book.add_format({
        'bold': 3,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 6
    })

    heading = book.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 6
    })

    data = book.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 6
    })

    heading2 = book.add_format({
        'bold': 1,
        'border': 1,
        'font_size': 6
    })

    # Table headings
    sheet.merge_range(
            'A1:I4', 
            'DELIVERY CHALLAN / INVOICE \t \t \tMob:9423222798, 9881212348\n\
             VAIBHAV ENGINEERING WORKS\nS.No.15/11/3,\
             Old Warje Jakat Naka, Behind Kakde City, Karvanagar,\
             Pune-411052.', 
            merge_format)

    sheet.merge_range(
            'A5:F6', 
            'To, M/S Vanaz Engineers Ltd. 85/1, Paud road, Pune-38\n \
             GSTIN / Unique ID: 27AAACV6873B1ZA \t State Code:',
            heading2
            )

    sheet.merge_range(
            'G5:I6', 
            'GSTI-27APGPM-6700G1ZZ\n \
             \nPAN NO:-APGPM6700G',
            heading2
            )

    sheet.merge_range(
            'A7:D8', 
            'INVOICE Number: \t \t \tDate: \n\
             \nVendor Code: V0113',
            heading2
            )

    sheet.merge_range(
            'E7:I8', 
            'P.O. Number: \t \t \tDated:\
            \nJ.C. Number: \t \t \tDated:\n\
            \nOur Challan Number',
            heading2
            )

    sheet.merge_range('A9:A11', 'SR\nNO', heading)
    sheet.merge_range('B9:D11', 'PARTICULAR', heading)
    sheet.merge_range('E9:E11', 'OUR CHALLAN\nNUMBER', heading)
    sheet.merge_range('F9:F11', 'CHALLAN\nDATE', heading)
    sheet.merge_range('G9:G11', 'QUANTITY', heading)
    sheet.merge_range('H9:H11', 'RATE', heading)
    sheet.merge_range('I9:I11', 'AMOUNT', heading)

    row = 12
    total = 0
    for index, report in enumerate(reports):
        total += report.amount
        col = 0
        row += 1
        sheet.write(row, col, index + 1, data)
        col += 1
        sheet.merge_range(row, col, row, col + 2, report.particular, data)
        col += 3
        sheet.write(row, col, report.challan_number, data)
        col += 1
        sheet.write(row, col, report.date, data)
        col += 1
        sheet.write(row, col, report.quantity, data)
        col += 1
        sheet.write(row, col, report.rate, data)
        col += 1
        sheet.write(row, col, report.amount, data)

    # row += 2
    col -= 1

    cgst = (0.09 * total)
    sgst = (0.09 * total)
    grand_total = total + cgst + sgst
    words = num2words.number_to_words(round(grand_total, 2))
    row += 1
    sheet.write(row, col, 'Total: ', data)
    col += 1
    sheet.write(row, col, total, data)
    row += 1
    sheet.write(row, col - 1, 'CGST: ', data)
    sheet.write(row, col, cgst, data)
    row += 1
    sheet.write(row, col - 1, 'SGST: ', data)
    sheet.write(row, col, sgst, data)
    row += 2
    sheet.write(row, col - 1, 'Grand Total: ', heading)
    sheet.write(row, col, grand_total, data)
    row += 1
    sheet.merge_range(row, 0, row, 8, 'Rs. ' + words + ' only', data)
    row += 2
    sheet.merge_range(row, 0, row + 2, 5, 'Receives the above mentioned good in good working condition \n\n\nSend Through \t \t \tReceived By', data)
    sheet.merge_range(row, 6, row + 2, 8, ' For Vaibhav Engineering Works', data)

    sheet.conditional_format(9, 0, row, 8, {'type': 'blanks', 'format' : data})
    book.close()

    return response

def report_melt(request):
    if request.method == 'POST':
        form = MeltReportForm(request.POST)
        if form.is_valid():
            query = Q(
                        date__year=request.POST.get('year'),
                        date__month=request.POST.get('month')
                    )
            report = MeltReport.objects.filter(query)
            return excel_export_melt(report, 'Melt_Report_' + calendar.month_name[int(request.POST.get('month'))] + '_' + request.POST.get('year'))
    else:
        form = MeltReportForm()
    return render(request, 'report_melt.html', {'form': form})


def stock_report(reports, filename, month, year):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "attachment; filename=" + filename + ".xlsx"

    book = Workbook(response, {'in_memory': True})
    sheet = book.add_worksheet('Report')

    for col in range(50):
        sheet.set_column(col, col, 7)
        sheet.set_row(col, 30)
    
    merge_format = book.add_format({
        'bold': 3,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 8
    })

    heading = book.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 8
    })

    data = book.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 8
    })

    data2 = book.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 6
    })

    heading2 = book.add_format({
        'bold': 1,
        'border': 1,
        'font_size': 8
    })

    # Table headings
    sheet.merge_range(
            'A1:M3', 
            'Mob:9423222798, 9881212348\n\n\
             VAIBHAV ENGINEERING WORKS\n\
             S.No.15/11/3, Old Warje Jakat Naka, Behind Kakde City, Karvanagar, Pune-411052.\n\n\
             MONTHLY STOCK STATEMENTS FOR THE MONTH '  + month + ' ' + year, 
            merge_format)

    sheet.merge_range(
            'A4:F4',
             'REICEVED FROM VANAZ ENG. LTD.',
            heading
            )

    sheet.merge_range(
            'G4:M4', 
            'ISSUED FROM VAIBHAV ENG. WORKS',
            heading
            )

    sheet.merge_range('A5:A6', 'SR\nNO', heading)
    # sheet.merge_range('B5:B6', 'ITEM\nCODE\nNo', heading)
    sheet.merge_range('B5:B6', 'MELT OF\nBLANK', heading)
    sheet.merge_range('C5:C6', 'YOURS\nCHALLAN\nNUMBER', heading)
    sheet.merge_range('D5:D6', 'DATE', heading)
    sheet.merge_range('E5:E6', 'WEIGHT\n(KG)', heading)
    sheet.merge_range('F5:F6', 'QTY\nIN', heading)
    sheet.merge_range('G5:G6', 'OURS\nCHALLAN\nNUMBER', heading)
    sheet.merge_range('H5:H6', 'DATE', heading)
    sheet.merge_range('I5:I6', 'QTY\nOUT', heading)
    sheet.merge_range('J5:J6', 'WEIGHT\n(KG)', heading)
    sheet.merge_range('K5:K6', 'SCRAP\nWEIGHT\n(KG)', heading)
    sheet.merge_range('L5:L6', 'END\nPIECES\nWEIGHT', heading)
    sheet.merge_range('M5:M6', 'TOTAL\nWEIGHT', heading)

    row = 6
    for index, report in enumerate(reports):
        row += 1
        col = 0
        sheet.write(row, col, index + 1, data)
        col += 1
        sheet.write(row, col, str(report.code) + "\n" + str(report.particular), data)
        col += 5
        sheet.write(row, col, report.challan_number, data)
        col += 1
        sheet.write(row, col, report.date, data)
        col += 1
        sheet.write(row, col, report.quantity, data)
        col += 1
        sheet.write(row, col, report.weight, data)
        col += 1
        sheet.write(row, col, report.scrap_weight, data)
        col += 1
        sheet.write(row, col, report.end_pieces, data)
        col += 1
        sheet.write(row, col, report.total_weight, data)

    sheet.conditional_format(6, 0, row, 8, {'type': 'blanks', 'format' : data})
    book.close()

    return response

def stock_report_monthly(request):
    if request.method == 'POST':
        form = StockReportForm(request.POST)
        if form.is_valid():
            query = Q(
                        date__year=request.POST.get('year'),
                        date__month=request.POST.get('month')
                    )
            report = MeltReport.objects.filter(query)
            return stock_report(report, 'Stock_Report_' + calendar.month_name[int(request.POST.get('month'))] + '_' + request.POST.get('year'), calendar.month_name[int(request.POST.get('month'))], request.POST.get('year'))
    else:
        form = StockReportForm()
    return render(request, 'stock_report.html', {'form': form})

def test(request):
    from django.contrib.staticfiles.templatetags.staticfiles import static
    context_dict = {}
    context_dict['logo'] = static('vew.jpeg')
    return render(request, 'pdf/invoice_generator_assembly.html', context_dict)