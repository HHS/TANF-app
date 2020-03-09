import json
from django.core import serializers
from django.core.files.storage import default_storage
from upload.models import Family, Adult, Child, ClosedPerson, AggregatedData, FamiliesByStratumData
from django.db import transaction
from background_task import background
from upload.tanfDataProcessing import tanf2db
from django.core.files.base import ContentFile


# This is for tasks that need to be run in the background.
class TANFDataImport(Exception):
    pass


@background
def importRecords(file=None, user=None):
    print('starting to process', file)
    statusfile = file + '.status'
    status = {'status': 'Importing'}
    default_storage.save(statusfile, ContentFile(json.dumps(status).encode()))
    invalidcount = 0

    # wrap this whole thing in a transaction.  If we encounter problems
    # importing data, or we have invalid records, store the invalid records
    # and then rollback.
    try:
        with transaction.atomic():
            try:
                with default_storage.open(file, 'r') as f:
                    tanf2db(f, user)
            except (FileNotFoundError, OSError):
                print('missing file, assuming job was deleted before we could process it:', file)
                return
            except Exception as e:
                print('Import Error:', e)
                status = {'status': 'Error While Importing'}
                default_storage.delete(statusfile)
                default_storage.save(statusfile, ContentFile(json.dumps(status).encode()))
                raise TANFDataImport('Error While Importing ' + repr(e))

            print('finished importing', file)

            # check if we had any invalid things
            invalidcount = Family.objects.filter(valid=False).count()
            invalidcount += Adult.objects.filter(valid=False).count()
            invalidcount += Child.objects.filter(valid=False).count()
            invalidcount += ClosedPerson.objects.filter(valid=False).count()
            invalidcount += AggregatedData.objects.filter(valid=False).count()
            invalidcount += FamiliesByStratumData.objects.filter(valid=False).count()
            if invalidcount > 0:
                status = {'status': 'Failed Validation'}
                default_storage.delete(statusfile)
                default_storage.save(statusfile, ContentFile(json.dumps(status).encode()))

                # Write out an invalid file with all the invalid stuff.
                invalidfile = file + '.invalid'
                with default_storage.open(invalidfile, 'w') as f:
                    # invalidstring = '["invalid: ' + str(invalidcount) + '"]'
                    # f.write(invalidstring)
                    # XXX write out the invalid records
                    f.write('[')

                    tmplist = Family.objects.filter(valid=False)
                    tmpjson = serializers.serialize('json', tmplist)
                    f.write(json.loads(tmpjson))
                    f.write(',')

                    tmplist = Adult.objects.filter(valid=False)
                    tmpjson = serializers.serialize('json', tmplist)
                    f.write(json.loads(tmpjson))
                    f.write(',')

                    tmplist = Child.objects.filter(valid=False)
                    tmpjson = serializers.serialize('json', tmplist)
                    f.write(json.loads(tmpjson))
                    f.write(',')

                    tmplist = ClosedPerson.objects.filter(valid=False)
                    tmpjson = serializers.serialize('json', tmplist)
                    f.write(json.loads(tmpjson))
                    f.write(',')

                    tmplist = AggregatedData.objects.filter(valid=False)
                    tmpjson = serializers.serialize('json', tmplist)
                    f.write(json.loads(tmpjson))
                    f.write(',')

                    tmplist = FamiliesByStratumData.objects.filter(valid=False)
                    tmpjson = serializers.serialize('json', tmplist)
                    f.write(json.loads(tmpjson))

                    f.write(']')
                raise TANFDataImport('invalid records: rolling back')
            else:
                status = {'status': 'Imported'}
                default_storage.delete(statusfile)
                default_storage.save(statusfile, ContentFile(json.dumps(status).encode()))
    except TANFDataImport as e:
        # if we have a data import/validation problem, it should be rolled
        # back and then we should exit the job cleanly so that we don't
        # reschedule the job and run it again.
        print('Data import/validation did not succeed:', e)
        pass
    return
