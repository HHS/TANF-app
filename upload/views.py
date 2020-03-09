from django.shortcuts import render, redirect
from upload.tasks import importRecords
from django.core.files.storage import default_storage
import datetime
import json
from json import JSONDecodeError
from django.apps import apps
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core import serializers
from django.http import HttpResponse, Http404
from upload.querysetchain import QuerySetChain
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.


def about(request):
    return render(request, "about.html")


@login_required
def upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        user = str(request.user)
        datestr = datetime.datetime.now().strftime('%Y%m%d%H%M%SZ')
        originalname = myfile.name

        # save a copy for processing
        originalfilename = '_'.join([user, datestr, originalname, '.txt'])
        default_storage.save(originalfilename, myfile)

        # process file (validate and store records)
        importRecords(originalfilename, user)

        # redirect to status page
        return redirect('status')

    return render(request, 'upload.html')


@login_required
def status(request):
    statusmap = {}
    try:
        for i in default_storage.listdir('')[1]:
            # only show files that are owned by the requestor
            if i.endswith('.txt') and i.startswith(str(request.user)):
                statusfile = i + '.status'
                try:
                    with default_storage.open(statusfile, 'r') as f:
                        status = json.load(f)
                        statusmap[i] = status['status']
                except (FileNotFoundError, OSError):
                    statusmap[i] = 'Queued'
    except (FileNotFoundError, OSError) as e:
        print('FileNotFoundError:  hopefully this is local dev env', e)

    files = sorted(statusmap.items())

    context = {
        'filelist': files,
    }
    return render(request, "status.html", context)


@login_required
def download(request, file=None, json=None):
    # XXX probably ought to think about this one to make sure there
    #     is no way that somebody can download system files or things
    #     like that.
    if file.endswith('.txt') and file.startswith(str(request.user)):
        if json is not None:
            file = file + '.json'
        try:
            with default_storage.open(file, 'r') as f:
                response = HttpResponse(f.read(), content_type="text/plain")
                response['Content-Disposition'] = 'inline; filename=' + file
                return response
        except (FileNotFoundError, OSError):
            raise Http404
    return redirect('status')


# This is where we should be able to delve in and edit data that needs fixing.
# For now, we will just show the issues, so they can reupload.  Maybe this is
# better, because this will enforce good data hygiene on the STT end?
@login_required
def fileinfo(request, file=None):
    status = []
    statusfile = file + '.status'
    invalidfile = file + '.invalid'
    try:
        with default_storage.open(statusfile, 'r') as f:
            statusdata = json.load(f)
            status = [statusdata['status']]
    except (FileNotFoundError, OSError):
        status = ['No status yet.  This probably means the file was interrupted during processing and thus is stuck.',
                  'You will probably want to delete and re-import this file.']
    try:
        with default_storage.open(invalidfile, 'r') as f:
            # invalidata = json.load(f)
            invalidata = f.read()
    except (FileNotFoundError, OSError):
        invalidata = []

    context = {
        'status': status,
        'invalidata': invalidata
    }
    return render(request, "fileinfo.html", context)


@login_required
def deletesuccessful(request):
    files = []
    for i in default_storage.listdir('')[1]:
        # only look at files that are json and owned by the requestor
        if i.endswith('.txt') and i.startswith(str(request.user)):
            statusfile = i + '.status'
            try:
                with default_storage.open(statusfile, 'r') as f:
                    status = json.load(f)
                    # if there are no issues, add it to the list
                    if status['status'] != 'Failed Validation':
                        files.append(i)
            except (FileNotFoundError, OSError):
                pass
    for file in files:
        statusfile = file + '.status'
        if default_storage.exists(file) and default_storage.exists(statusfile):
            default_storage.delete(file)
            default_storage.delete(statusfile)
    return redirect('status')


@login_required
def delete(request, file=None):
    confirmed = request.GET.get('confirmed')
    statusfile = file + '.status'
    invalidfile = file + '.invalid'

    try:
        with default_storage.open(statusfile, 'r') as f:
            status = json.load(f)
    except (FileNotFoundError, OSError):
        # no status, so probably stuck.  Clean everything.
        try:
            default_storage.delete(file)
        except (FileNotFoundError, OSError):
            pass
        try:
            default_storage.delete(invalidfile)
        except (FileNotFoundError, OSError):
            pass
        return redirect('status')

    try:
        with default_storage.open(invalidfile, 'r') as f:
            invaliditems = json.load(f)
    except (FileNotFoundError, OSError):
        invaliditems = []
    except JSONDecodeError:
        invaliditems = ['could not decode json:  may be in the process of dumping issues']

    # Get a confirmation if we still have issues with the upload.
    # Otherwise, the import went well, so delete without prompting.
    if confirmed is None and status['status'] != 'Imported':
        return render(request, "delete.html", {'file': file, 'invaliditems': len(invaliditems)})

    if default_storage.exists(file) and default_storage.exists(statusfile):
        default_storage.delete(file)
        default_storage.delete(statusfile)
        try:
            default_storage.delete(invalidfile)
        except (FileNotFoundError, OSError):
            pass

    return redirect('status')


# Look at various things in the tables
@login_required
def viewTables(request):
    # choose what table to view
    tablelist = []
    for model in apps.all_models['upload']:
        tablelist.append(model)
    table = request.GET.get('table')
    if table is None:
        table = tablelist[0]

    # Get the model for the selected table and get all the data from it.
    mymodel = apps.get_model('upload', table)
    alldata = mymodel.objects.all()

    # set up pagination here
    hitsperpagelist = ['All', '20', '100', '200', '500']
    hitsperpage = request.GET.get('hitsperpage')
    if hitsperpage is None:
        hitsperpage = hitsperpagelist[1]
    page_no = request.GET.get('page')
    if hitsperpage == 'All':
        # really don't get all of them.  That could be bad.
        paginator = Paginator(alldata, 1000000)
    else:
        paginator = Paginator(alldata, int(hitsperpage))
    try:
        page = paginator.get_page(page_no)
    except PageNotAnInteger:
        page = paginator.get_page(1)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)
    data = serializers.serialize("python", page)
    fields = []
    for field in mymodel._meta.get_fields():
        # XXX this seems messy, but the serializer doesn't emit this field
        # So we need to get rid of it to make the fields align in the table.
        if field.verbose_name != 'ID':
            fields.append(field.verbose_name)

    context = {
        'tablelist': tablelist,
        'selected_table': table,
        'data': data,
        'page': page,
        'fields': fields,
        'hitsperpagelist': hitsperpagelist,
        'selected_hitsperpage': hitsperpage,
    }
    return render(request, "viewData.html", context)


def uniquelist(list):
    newlist = []
    for i in list:
        if i not in newlist:
            newlist.append(i)
    return newlist


@login_required
def viewquarter(request):
    # enumerate all the available calendarquarters in all tables.
    calquarters = []
    for model in apps.all_models['upload']:
        mymodel = apps.get_model('upload', model)
        for cq in mymodel.objects.values('calendar_quarter').distinct():
            calquarters.append(cq['calendar_quarter'])
    calquarters = uniquelist(calquarters)
    calquarters.sort()
    calquarter = request.GET.get('calquarter')
    if calquarter is None:
        try:
            calquarter = calquarters[0]
        except IndexError:
            calquarter = 0
    else:
        calquarter = int(calquarter)

    # select all data for the selected calquarter
    qslist = []
    for model in apps.all_models['upload']:
        mymodel = apps.get_model('upload', model)
        newdata = mymodel.objects.filter(calendar_quarter=calquarter)
        qslist.append(newdata)
    # XXX I am suspicious of this approach.  Not sure that this will
    # actually introduce some sort of background "pull everything into
    # memory" thing.  It does seem to be doing a full table scan locally.
    qs = QuerySetChain(qslist)

    # set up pagination here
    hitsperpagelist = ['All', '20', '100', '200', '500']
    hitsperpage = request.GET.get('hitsperpage')
    if hitsperpage is None:
        hitsperpage = hitsperpagelist[1]
    page_no = request.GET.get('page')
    if hitsperpage == 'All':
        # really don't get all of them.  That could be bad.
        paginator = Paginator(qs, 1000000)
    else:
        paginator = Paginator(qs, int(hitsperpage))
    try:
        page = paginator.get_page(page_no)
    except PageNotAnInteger:
        page = paginator.get_page(1)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)

    data = serializers.serialize("python", page)

    context = {
        'calquarters': calquarters,
        'selected_calquarter': int(calquarter),
        'page': page,
        'data': data,
        'hitsperpagelist': hitsperpagelist,
        'selected_hitsperpage': hitsperpage,
    }
    return render(request, "viewcalquarter.html", context)


@staff_member_required
def useradmin(request):
    return redirect('/admin/users/tanfuser/')
