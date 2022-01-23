import xml.etree.ElementTree as ET

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import ScanForm
from .models import Host, Scan, ScanPolicy, Service


def index(request):
    context = {
        'item_list': Scan.objects.order_by('date_created')[:],
    }
    return render(request, 'scans/index.html', context)


def policies(request):
    item_list = ScanPolicy.objects.all()
    return render(request, 'scans/policies.html', context={'item_list': item_list})


def scan_detail(request, pk):
    pg = get_object_or_404(Scan, pk=pk)
    context = {
        'title': pg.name,
        'record': pg,
        'dataset': Scan.objects.all(),
    }
    return render(request, 'scans/scan_detail.html', context)


def upload(request):
    submitted = False
    if request.method == 'POST' and request.FILES['xmlfile']:
        form = ScanForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            # Do all the parsing here

            final_data = cleaned
            scan = final_data.save()
            return HttpResponseRedirect(reverse('index'))
            # Once built, redirect to the scan detail page that will show # live hosts, and table of services
            #return HttpResponseRedirect(reverse('scans:detail', args=(scan.pk,)))
    else:
        form = ScanForm()
    if 'submitted' in request:
        submitted = True
    return render(request, 'scans/upload.html', {'form': form, 'submitted': submitted})
