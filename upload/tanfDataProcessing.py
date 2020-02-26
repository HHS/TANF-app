import json
import struct
import re
from datetime import datetime
from django.utils.timezone import make_aware
from upload.models import Family, Adult, Child, ClosedPerson, AggregatedData, ClosedCase, FamiliesByStratumData


##########################################################################
# This is where the record types are defined:  The keys are the json
# names for the fields, and the values are the size of the fields in bytes.
# The field sizes and names are derived from the documentation under
# https://www.acf.hhs.gov/ofa/resource/tanfedit/index

# header records
header_fields = {
    "title": 6,
    "calendarquarter": 5,
    "datatype": 1,
    "statefipscode": 2,
    "tribecode": 3,
    "programtype": 3,
    "editindicator": 1,
    "encryptionindicator": 1,
    "updateindicator": 1
}

# T1 records
section1_familydata_fields = {
    "recordtype": 2,
    "reportingmonth": 6,
    "casenumber": 11,
    "countyfipscode": 3,
    "stratum": 2,
    "zipcode": 5,
    "fundingstream": 1,
    "disposition": 1,
    "newapplicant": 1,
    "numfamilymembers": 2,
    "typeoffamilyforworkparticipation": 1,
    "receivessubsidizedhousing": 1,
    "receivesmedicalassistance": 1,
    "receivesfoodstamps": 1,
    "amtoffoodstampassistance": 4,
    "receivessubsidizedchildcare": 1,
    "amtofsubsidizedchildcare": 4,
    "amtofchildsupport": 4,
    "amtoffamilycashresources": 4,
    "cash_amount": 4,
    "cash_nbr_month": 3,
    "tanfchildcare_amount": 4,
    "tanfchildcare_children_covered": 2,
    "tanfchildcare_nbr_months": 3,
    "transportation_amount": 4,
    "transportation_nbr_months": 3,
    "transitionalservices_amount": 4,
    "transitionalservices_nbr_months": 3,
    "other_amount": 4,
    "other_nbr_months": 3,
    "sanctionsreduction_amt": 4,
    "workrequirementssanction": 1,
    "familysanctionforadultnohsdiploma": 1,
    "sanctionforteenparentnotattendingschool": 1,
    "noncooperatewithchildsupport": 1,
    "failuretocomploywithirp": 1,
    "othersanction": 1,
    "recoupmentofprioroverpayment": 4,
    "othertotalreductionamt": 4,
    "familycap": 1,
    "reductionbasedonlengthofreceiptofassistance": 1,
    "othernonsanction": 1,
    "waiver_evaluation_control_gprs": 1,
    "tanffamilyexemptfromtimelimits": 2,
    "tanffamilynewchildonlyfamily": 1,
    # "blank": 39
}

# T2 records
section1_adultdata_fields = {
    "recordtype": 2,
    "reportingmonth": 6,
    "casenumber": 11,
    "familyafilliation": 1,
    "noncustodialparent": 1,
    "dateofbirth": 8,
    "socialsecuritynumber": 9,
    "racehispanic": 1,
    "racenativeamerican": 1,
    "raceasian": 1,
    "raceblack": 1,
    "racewhite": 1,
    "gender": 1,
    "oasdibenefits": 1,
    "nonssabenefits": 1,
    "titlexivapdtbenefits": 1,
    "titlexviaabdbenefits": 1,
    "titlexvissibenefits": 1,
    "maritalstatus": 1,
    "relationshiptohh": 2,
    "parentminorchild": 1,
    "pregnantneeds": 1,
    "educationlevel": 2,
    "citizenship": 1,
    "coopwithchildsupport": 1,
    "countablemonths": 3,
    "countablemonthsremaining": 2,
    "currentmonthexempt": 1,
    "employmentstatus": 1,
    "workeligibleindicator": 2,
    "workparticipationstatus": 2,
    "unsubsidizedemployment": 2,
    "subsidizedprivateemployment": 2,
    "subsidizedpublicemployment": 2,
    "workexperiencehours": 2,
    "workexperienceexcusedabsences": 2,
    "workexperienceholidays": 2,
    "onthejobtraining": 2,
    "jobsearchhours": 2,
    "jobsearchexcusedabsences": 2,
    "jobsearchholidays": 2,
    "communitysvchours": 2,
    "communitysvcexcusedabsences": 2,
    "communitysvcholidays": 2,
    "vocationaltraininghours": 2,
    "vocationaltrainingexcusedabsences": 2,
    "vocationaltrainingholidays": 2,
    "jobskillshours": 2,
    "jobskillsexcusedabsences": 2,
    "jobskillsholidays": 2,
    "eduwithnodiplomahours": 2,
    "eduwithnodiplomaexcusedabsences": 2,
    "eduwithnodiplomaholidays": 2,
    "satisfactoryschoolhours": 2,
    "satisfactoryschoolexcusedabsences": 2,
    "satisfactoryschoolholidays": 2,
    "providingchildcarehours": 2,
    "providingchildcareexcusedabsences": 2,
    "providingchildcareholidays": 2,
    "otherwork": 2,
    "corehoursforoverallrate": 2,
    "corehoursfortwoparentrate": 2,
    "earnedincome": 4,
    "unearnedincomeincometaxcredit": 4,
    "unearnedincomesocialsecurity": 4,
    "unearnedincomessi": 4,
    "unearnedincomeworkerscomp": 4,
    "unearnedincomeother": 4,
}

# T3 records
# These are the full fields as depicted in
# https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section1_10_2008.pdf
section1_childdata_fields = {
    "recordtype": 2,
    "reportingmonth": 6,
    "casenumber": 11,

    "familyafilliation_1": 1,
    "dateofbirth_1": 8,
    "socialsecuritynumber_1": 9,
    "racehispanic_1": 1,
    "racenativeamerican_1": 1,
    "raceasian_1": 1,
    "raceblack_1": 1,
    "racepacific_1": 1,
    "racewhite_1": 1,
    "gender_1": 1,
    "nonssabenefits_1": 1,
    "titlexvissibenefits_1": 1,
    "relationshiptohh_1": 2,
    "parentminorchild_1": 1,
    "educationlevel_1": 2,
    "citizenship_1": 1,
    "unearnedincomessi_1": 4,
    "unearnedincomeother_1": 4,

    "familyafilliation_2": 1,
    "dateofbirth_2": 8,
    "socialsecuritynumber_2": 9,
    "racehispanic_2": 1,
    "racenativeamerican_2": 1,
    "raceasian_2": 1,
    "raceblack_2": 1,
    "racepacific_2": 1,
    "racewhite_2": 1,
    "gender_2": 1,
    "nonssabenefits_2": 1,
    "titlexvissibenefits_2": 1,
    "relationshiptohh_2": 2,
    "parentminorchild_2": 1,
    "educationlevel_2": 2,
    "citizenship_2": 1,
    "unearnedincomessi_2": 4,
    "unearnedincomeother_2": 4,

    "blank": 55,

    "jobsearchhours": 2,
    "jobsearchexcusedabsences": 2,
    "jobsearchholidays": 2,
    "communitysvchours": 2,
    "communitysvcexcusedabsences": 2,
    "communitysvcholidays": 2,
    "vocationaltraininghours": 2,
    "vocationaltrainingexcusedabsences": 2,
    "vocationaltrainingholidays": 2,
    "jobskillshours": 2,
    "jobskillsexcusedabsences": 2,
    "jobskillsholidays": 2,
    "eduwithnodiplomahours": 2,
    "eduwithnodiplomaexcusedabsences": 2,
    "eduwithnodiplomaholidays": 2,
    "satisfactoryschoolhours": 2,
    "satisfactoryschoolexcusedabsences": 2,
    "satisfactoryschoolholidays": 2,
    "providingchildcarehours": 2,
    "providingchildcareexcusedabsences": 2,
    "providingchildcareholidays": 2,
    "otherwork": 2,
    "corehoursforoverallrate": 2,
    "corehoursfortwoparentrate": 2,
    "earnedincome": 4,
    "unearnedincomeincometaxcredit": 4,
    "unearnedincomesocialsecurity": 4,
    "unearnedincomessi": 4,
    "unearnedincomeworkerscomp": 4,
    "unearnedincomeother": 4,
}

# T3 records:  Our example data seems to be missing a character and is otherwise truncated,
#      so let's hope that 3 chars for the last field is OK.
section1_childdata_fields_exampledata = {
    "recordtype": 2,
    "reportingmonth": 6,
    "casenumber": 11,

    "familyafilliation_1": 1,
    "dateofbirth_1": 8,
    "socialsecuritynumber_1": 9,
    "racehispanic_1": 1,
    "racenativeamerican_1": 1,
    "raceasian_1": 1,
    "raceblack_1": 1,
    "racepacific_1": 1,
    "racewhite_1": 1,
    "gender_1": 1,
    "nonssabenefits_1": 1,
    "titlexvissibenefits_1": 1,
    "relationshiptohh_1": 2,
    "parentminorchild_1": 1,
    "educationlevel_1": 2,
    "citizenship_1": 1,
    "unearnedincomessi_1": 4,
    "unearnedincomeother_1": 3,
}

# T3 records:  Our example data seems to be missing a character, sometimes
#      has 2 children in it and is also truncated,
#      so let's hope that 3 chars for the last field of the first child is OK.
section1_childdata_fields_twochild = {
    "recordtype": 2,
    "reportingmonth": 6,
    "casenumber": 11,

    "familyafilliation_1": 1,
    "dateofbirth_1": 8,
    "socialsecuritynumber_1": 9,
    "racehispanic_1": 1,
    "racenativeamerican_1": 1,
    "raceasian_1": 1,
    "raceblack_1": 1,
    "racepacific_1": 1,
    "racewhite_1": 1,
    "gender_1": 1,
    "nonssabenefits_1": 1,
    "titlexvissibenefits_1": 1,
    "relationshiptohh_1": 2,
    "parentminorchild_1": 1,
    "educationlevel_1": 2,
    "citizenship_1": 1,
    "unearnedincomessi_1": 4,
    "unearnedincomeother_1": 3,

    "familyafilliation_2": 1,
    "dateofbirth_2": 8,
    "socialsecuritynumber_2": 9,
    "racehispanic_2": 1,
    "racenativeamerican_2": 1,
    "raceasian_2": 1,
    "raceblack_2": 1,
    "racepacific_2": 1,
    "racewhite_2": 1,
    "gender_2": 1,
    "nonssabenefits_2": 1,
    "titlexvissibenefits_2": 1,
    "relationshiptohh_2": 2,
    "parentminorchild_2": 1,
    "educationlevel_2": 2,
    "citizenship_2": 1,
    "unearnedincomessi_2": 4,
    "unearnedincomeother_2": 4,
}


# T4 records
section2_closedcase_fields = {
    "recordtype": 2,
    "reportingmonth": 6,
    "casenumber": 11,
    "countyfipscode": 3,
    "stratum": 2,
    "zipcode": 5,
    "disposition": 1,
    "reason": 2,
    "receivessubsidizedhousing": 1,
    "receivesmedicalassistance": 1,
    "receivesfoodstamps": 1,
    "receivessubsidizedchildcare": 1,
}

# T5 records
section2_closedperson_fields = {
    "recordtype": 2,
    "reportingmonth": 6,
    "casenumber": 11,
    "familyafilliation": 1,
    "dateofbirth": 8,
    "socialsecuritynumber": 9,
    "racehispanic": 1,
    "racenativeamerican": 1,
    "raceasian": 1,
    "raceblack": 1,
    "racepacific": 1,
    "racewhite": 1,
    "gender": 1,
    "oasdibenefits": 1,
    "nonssabenefits": 1,
    "titlexivapdtbenefits": 1,
    "titlexviaabdbenefits": 1,
    "titlexvissibenefits": 1,
    "maritalstatus": 1,
    "relationshiptohh": 2,
    "parentminorchild": 1,
    "pregnantneeds": 1,
    "educationlevel": 2,
    "citizenship": 1,
    "countablemonths": 3,
    "countablemonthsremaining": 2,
    "employmentstatus": 1,
    "earnedincome": 4,
    "unearnedincome": 4,
}

# T6 records
section3_aggregatedata_fields = {
    "recordtype": 2,
    # XXX many more fields need to be added here
}

# T7 records
section4_familiesbystratum_fields = {
    "recordtype": 2,
    # XXX many more fields need to be added here
}

# trailer records
trailer_fields = {
    "title": 7,
    "numrecords": 7,
    # "blank": 9
}

# The record type definitions end here.
##########################################################################


# This parses a particular record and gives back a dictionary
def parseFields(fieldinfo, linestring):
    fields = list(fieldinfo.keys())
    fieldwidths = list(fieldinfo.values())
    fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's')
                         for fw in fieldwidths)
    fieldstruct = struct.Struct(fmtstring)
    unpack = fieldstruct.unpack_from
    parse = lambda line: tuple(s.decode() for s in unpack(line.encode()))
    return dict(zip(fields, parse(linestring)))


# This is the simple subtitution cipher
encryptmap = {
    '1': '@',
    '2': '9',
    '3': 'Z',
    '4': 'P',
    '5': '0',
    '6': '#',
    '7': 'Y',
    '8': 'B',
    '9': 'W',
    '0': 'T',
}
decryptmap = {}
for k, v in encryptmap.items():
    decryptmap[v] = k


# This decrypts the ssn using the silly substitution cipher
def decryptSsn(ssn):
    result = ''
    for z in ssn:
        try:
            result = result + decryptmap[z]
        except Exception:
            result = result + z
    # # Put dashes into SSN
    # if len(result) == 9:
    #   result = result[:5] + '-' + result[5:]
    #   result = result[:3] + '-' + result[3:]
    return result


#
# This function parses the txt files that are sent by STT people to the TDRS
# app and returns a json document.
#
# Possible tricky bits:
#  1) We do not parse the fields at all, but just pull them
#     in as strings.  So we don't do any type parsing or anything.  That might
#     better be done by code that consumes the json doc and stores it.
#  2) The social security numbers do not have dashes put into them, which may
#     not be the way they are parsed/stored in the existing system.
#
# This code must be run with python 3.6 or above, because it preserves
# the order of dictionaries, which we need for this to work.
#
#
# XXX The fields here are incomplete.  More work is required to
#     make this parse all record types and all sections.
#
def tanf2json(f):
    # This is the TANF data structure which we fill up with data and convert
    # into json at the end.
    tanfdata = {
        'header': {},
        'section1_familydata': [],
        'section1_adultdata': [],
        'section1_childdata': [],
        'section2_closedcasedata': [],
        'section2_closedpersondata': [],
        'section3_aggregatedata': [],
        'section4_familiesbystratumdata': [],
        'trailer': ()
    }

    # This is the list of lines that we couldn't figure out what to do with
    errorlines = []

    # XXX really need to make this write to a stream rather than memory
    #     Write records into db or files, then serialize into json?
    for line in f:
        line = line.decode('utf-8')

        # skip blank lines
        if line in ['\n', '\r\n']:
            continue

        if re.match(r'^T1', line):
            tanfdata['section1_familydata'].append(parseFields(section1_familydata_fields, line))

        elif re.match(r'^T2', line):
            adult = parseFields(section1_adultdata_fields, line)
            if tanfdata['header']['encryptionindicator'] == 'E':
                adult['socialsecuritynumber'] = decryptSsn(adult['socialsecuritynumber'])
            tanfdata['section1_adultdata'].append(adult)

        elif re.match(r'^T3', line):
            child = parseFields(section1_childdata_fields, line)
            if tanfdata['header']['encryptionindicator'] == 'E':
                child['socialsecuritynumber_1'] = decryptSsn(child['socialsecuritynumber_1'])
                try:
                    child['socialsecuritynumber_2'] = decryptSsn(child['socialsecuritynumber_2'])
                except KeyError:
                    # This is because our sample data seems not to have all the fields we ought to have,
                    # so we are just handling the situation in case it gets put in later.
                    pass
            tanfdata['section1_childdata'].append(child)

        elif re.match(r'^T4', line):
            tanfdata['section2_closedcasedata'].append(parseFields(section2_closedcase_fields, line))

        elif re.match(r'^T5', line):
            person = parseFields(section2_closedperson_fields, line)
            if tanfdata['header']['encryptionindicator'] == 'E':
                person['socialsecuritynumber'] = decryptSsn(person['socialsecuritynumber'])
            tanfdata['section2_closedpersondata'].append(person)

        elif re.match(r'^T6', line):
            tanfdata['section3_aggregatedata'].append(parseFields(section3_aggregatedata_fields, line))

        elif re.match(r'^T7', line):
            tanfdata['section4_familiesbystratumdata'].append(parseFields(section4_familiesbystratum_fields, line))

        elif re.match(r'^HEADER', line):
            tanfdata['header'] = parseFields(header_fields, line)

        elif re.match(r'^TRAILER', line):
            tanfdata['trailer'] = parseFields(trailer_fields, line)

        else:
            errorlines.append(line)

    if len(errorlines) > 0:
        raise Exception('could not parse lines', errorlines)

    # return what we found out as a json document
    return json.dumps(tanfdata)


def section1_familydata_check(data):
    # XXX need to check stuff actually here!
    reasons = []
    status = {
        'check': True,
        'reasons': ", ".join(reasons)
    }
    return status


def section1_adultdata_check(data):
    # XXX need to check stuff actually here!
    reasons = []
    status = {
        'check': True,
        'reasons': ", ".join(reasons)
    }
    return status


def section1_childdata_check(data):
    # XXX need to check stuff actually here!
    reasons = []
    status = {
        'check': True,
        'reasons': ", ".join(reasons)
    }
    return status


# Read the data, parse the different line types, put it into the db
def tanf2db(f, user):
    # This is the list of lines that we couldn't figure out what to do with
    errorlines = []

    now = make_aware(datetime.now())
    header = {}
    trailer = {}

    for line in f:
        # different environments can result in a string or bytes, so decode if we need to
        try:
            line = line.decode().rstrip()
        except (UnicodeDecodeError, AttributeError):
            line = line.rstrip()

        # skip blank lines
        if line in ['\n', '\r\n']:
            continue

        if re.match(r'^T1', line):
            try:
                data = parseFields(section1_familydata_fields, line)
            except Exception as e:
                print('Parsing T1:', e, line)
                raise e

            # clean up data
            try:
                del data['blank']
            except KeyError:
                pass
            data['countyfipscode'] = int(data['countyfipscode'])

            # store data
            check = section1_familydata_check(data)
            try:
                family = Family.objects.create(
                    imported_at=now,
                    imported_by=user,
                    valid=check['check'],
                    invalidreason=check['reasons'],
                    calendar_quarter=header['calendarquarter'],
                    state_code=header['statefipscode'],
                    tribe_code=header['tribecode'],
                    **data)
            except Exception as e:
                print('Creating Family object:', e, line)
                raise e
            family.save()

        elif re.match(r'^T2', line):
            try:
                data = parseFields(section1_adultdata_fields, line)
            except Exception as e:
                print('Parsing T2:', e, line)
                raise e

            # clean up data
            data['dateofbirth'] = make_aware(datetime.strptime(data['dateofbirth'], '%Y%m%d')).strftime('%Y-%m-%d')
            if header['encryptionindicator'] == 'E':
                data['socialsecuritynumber'] = decryptSsn(data['socialsecuritynumber'])

            # store data
            check = section1_adultdata_check(data)
            try:
                adult = Adult.objects.create(
                    imported_at=now,
                    imported_by=user,
                    valid=check['check'],
                    invalidreason=check['reasons'],
                    calendar_quarter=header['calendarquarter'],
                    state_code=header['statefipscode'],
                    tribe_code=header['tribecode'],
                    **data)
            except Exception as e:
                print('Creating Adult object:', e, '"', line, '"')
                raise e
            adult.save()

        elif re.match(r'^T3', line):
            # Child fields seem to be strangely variable, and in our example data, not
            # compliant with the spec.  Thus, we try a few different field configs.
            try:
                # This is the full spec with all the fields
                data = parseFields(section1_childdata_fields, line)
            except Exception:
                try:
                    # This is truncated at 59 characters (should be 60) so seems to be for one child
                    data = parseFields(section1_childdata_fields_exampledata, line)
                except Exception:
                    try:
                        # This is truncated at 100 chars.  For 2 children, it seems?
                        data = parseFields(section1_childdata_fields_twochild, line)
                    except Exception as e:
                        # Default:  throw up our hands in exasperation.
                        print('Parsing T3:', e, line)
                        raise e

            # clean up data
            data['dateofbirth_1'] = make_aware(datetime.strptime(data['dateofbirth_1'], '%Y%m%d')).strftime('%Y-%m-%d')
            try:
                data['dateofbirth_2'] = make_aware(datetime.strptime(data['dateofbirth_2'], '%Y%m%d')).strftime('%Y-%m-%d')
            except KeyError:
                # This is because our sample data seems not to have all the fields we ought to have,
                # so we are just handling the situation in case it gets put in later.
                pass
            if header['encryptionindicator'] == 'E':
                data['socialsecuritynumber_1'] = decryptSsn(data['socialsecuritynumber_1'])
                try:
                    data['socialsecuritynumber_2'] = decryptSsn(data['socialsecuritynumber_2'])
                except KeyError:
                    # This is because our sample data seems not to have all the fields we ought to have,
                    # so we are just handling the situation in case it gets put in later.
                    pass
            try:
                del data['blank']
            except KeyError:
                pass

            check = section1_childdata_check(data)
            try:
                child = Child.objects.create(
                    imported_at=now,
                    imported_by=user,
                    valid=check['check'],
                    invalidreason=check['reasons'],
                    calendar_quarter=header['calendarquarter'],
                    state_code=header['statefipscode'],
                    tribe_code=header['tribecode'],
                    # This is where all the json data gets added in
                    **data)
            except Exception as e:
                print('Creating Child object:', e, line)
                raise e
            child.save()

        elif re.match(r'^T4', line):
            try:
                data = parseFields(section2_closedcase_fields, line)
            except Exception as e:
                print('Parsing T4:', e, line)
                raise e
            try:
                closedcase = ClosedCase.objects.create(
                    imported_at=now,
                    imported_by=user,
                    calendar_quarter=header['calendarquarter'],
                    state_code=header['statefipscode'],
                    tribe_code=header['tribecode'],
                    **data)
            except Exception as e:
                print('Creating ClosedCase object:', e, line)
                raise e
            closedcase.save()

            Family.objects.filter(calendar_quarter=header['calendarquarter'], casenumber=data['casenumber'], countyfipscode=data['countyfipscode'], zipcode=data['zipcode']).delete()

            # # XXX do we delete associated person records too?
            # Adult.objects.filter(calendar_quarter=header['calendarquarter'], casenumber=data['casenumber']).delete()
            # Child.objects.filter(calendar_quarter=header['calendarquarter'], casenumber=data['casenumber']).delete()

        elif re.match(r'^T5', line):
            data = parseFields(section2_closedperson_fields, line)

            if header['encryptionindicator'] == 'E':
                data['socialsecuritynumber'] = decryptSsn(data['socialsecuritynumber'])

            closedperson = ClosedPerson.objects.create(
                imported_at=now,
                imported_by=user,
                calendar_quarter=header['calendarquarter'],
                state_code=header['statefipscode'],
                tribe_code=header['tribecode'],
                **data)
            closedperson.save()

            Adult.objects.filter(calendar_quarter=header['calendarquarter'], casenumber=data['casenumber'], socialsecuritynumber=data['socialsecuritynumber']).delete()
            Child.objects.filter(calendar_quarter=header['calendarquarter'], casenumber=data['casenumber'], socialsecuritynumber=data['socialsecuritynumber']).delete()

        elif re.match(r'^T6', line):
            data = parseFields(section3_aggregatedata_fields, line)
            aggregatedata = AggregatedData.objects.create(
                imported_at=now,
                imported_by=user,
                calendar_quarter=header['calendarquarter'],
                state_code=header['statefipscode'],
                tribe_code=header['tribecode'],
                **data)
            aggregatedata.save()

        elif re.match(r'^T7', line):
            data = parseFields(section4_familiesbystratum_fields, line)
            stratumdata = FamiliesByStratumData.objects.create(
                imported_at=now,
                imported_by=user,
                calendar_quarter=header['calendarquarter'],
                state_code=header['statefipscode'],
                tribe_code=header['tribecode'],
                **data)
            stratumdata.save()

        elif re.match(r'^HEADER', line):
            header = parseFields(header_fields, line)

        elif re.match(r'^TRAILER', line):
            trailer = parseFields(trailer_fields, line)

        else:
            errorlines.append(line)

    if len(errorlines) > 0:
        raise Exception('could not parse lines', errorlines)

    return
