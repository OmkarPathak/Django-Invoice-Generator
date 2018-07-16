from django.shortcuts import render, redirect
from .models import Work, AddWorkForm
from django.contrib import messages
from django.shortcuts import get_object_or_404

# Create your views here.
def homepage(request):
    return render(request, 'base.html')

def admin(request):
    form = AddWorkForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New Entry Added successfully')
        form = AddWorkForm()
    works = Work.objects.all().order_by('-date_added')
    return render(request, 'admin.html', {'form': form, 'works': works})

def admin_edit(request, id):
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
    work = get_object_or_404(Work, id=id)
    work.delete()
    messages.success(request, 'Entry Deleted successfully')
    return redirect('admin')