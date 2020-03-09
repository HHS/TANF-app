from django.db import models
import datetime


# Create your models here.

# NOTE:  These fields are kinda lame, in that some of them probably ought to be
# parsed into integers or something like that rather than being strings.

# T1: https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section1_10_2008.pdf
class Family(models.Model):
    # metadata
    imported_at = models.DateTimeField('time record was imported (metadata)')
    imported_by = models.CharField('who record was imported by (metadata)', max_length=64)
    valid = models.BooleanField('has record passed validation checks', default=True)
    invalidreason = models.CharField('Reason(s) why record did not pass validation. (metadata)', max_length=1024, default='')

    # header data
    calendar_quarter = models.IntegerField('calendar quarter (header)')
    state_code = models.CharField('state fips code (header)', max_length=3)
    tribe_code = models.CharField('tribe code (header)', max_length=3)

    # record data
    recordtype = models.CharField('record type (T1)', max_length=2)
    reportingmonth = models.CharField('reporting month (item 4)', max_length=6)
    casenumber = models.CharField('case number (item 6)', max_length=11)
    countyfipscode = models.IntegerField('county fips code (item 2)')
    stratum = models.IntegerField('stratum (item 5)')
    zipcode = models.CharField('zipcode (item 7)', max_length=5)
    fundingstream = models.IntegerField('funding stream (item 8)')
    disposition = models.IntegerField('disposition (item 9)')
    newapplicant = models.IntegerField('new applicant (item 10)')
    numfamilymembers = models.IntegerField('number family members (item 11)')
    typeoffamilyforworkparticipation = models.IntegerField('type of family for work participation (item 12)')
    receivessubsidizedhousing = models.CharField('receives subsidized housing (item 13)', max_length=1)
    receivesmedicalassistance = models.CharField('receives medical assistance (item 14)', max_length=1)
    receivesfoodstamps = models.CharField('receives food stamps (item 15)', max_length=1)
    amtoffoodstampassistance = models.IntegerField('amount of food stamp assistance (item 16)')
    receivessubsidizedchildcare = models.CharField('receives food stamps (item 17)', max_length=1)
    amtofsubsidizedchildcare = models.IntegerField('amount of subsidized child care (item 18)')
    amtofchildsupport = models.IntegerField('amount of child support (item 19)')
    amtoffamilycashresources = models.IntegerField('amount of familys cash resources (item 20)')
    cash_amount = models.IntegerField('cash and cash equivalents amount (item 21a)')
    cash_nbr_month = models.IntegerField('cash and cash equivalents number of months (item 21b)')
    tanfchildcare_amount = models.IntegerField('TANF child care amount (item 22a)')
    tanfchildcare_children_covered = models.IntegerField('TANF child care children covered (item 22b)')
    tanfchildcare_nbr_months = models.IntegerField('TANF child care number of months (item 22c)')
    transportation_amount = models.IntegerField('transportation amount (item 23a)')
    transportation_nbr_months = models.IntegerField('transportation number of months (item 23b)')
    transitionalservices_amount = models.IntegerField('transitional services amount (item 24a')
    transitionalservices_nbr_months = models.IntegerField('transitional services number of months (item 24b)')
    other_amount = models.IntegerField('other amount (item 25a')
    other_nbr_months = models.IntegerField('other number of months (item 25b)')
    sanctionsreduction_amt = models.IntegerField('reason for and amount of assistance reduction: sanctions reduction_amount (item 26a)')
    workrequirementssanction = models.CharField('reason for and amount of assistance reduction: work requirements sanction (item 26a)', max_length=4)
    familysanctionforadultnohsdiploma = models.CharField('reason for and amount of assistance reduction: family sanction for adult, no high school diploma (item 26a)', max_length=1)
    sanctionforteenparentnotattendingschool = models.CharField('reason for and amount of assistance reduction: sanction for teen parent not attending school (item 26a)', max_length=1)
    noncooperatewithchildsupport = models.CharField('reason for and amount of assistance reduction: non-cooperation with child support (item 26a)', max_length=1)
    failuretocomploywithirp = models.CharField('reason for and amount of assistance reduction: failure to comply with individual responsibility plan (item 26a)', max_length=1)
    othersanction = models.CharField('reason for and amount of assistance reduction: other sanction (item 26a)', max_length=1)
    recoupmentofprioroverpayment = models.CharField('reason for and amount of assistance reduction: recourpment of prior overpayment (item 26b)', max_length=4)
    othertotalreductionamt = models.CharField('reason for and amount of assistance reduction: other total reduction amount (item 26c)', max_length=4)
    familycap = models.CharField('reason for and amount of assistance reduction: family cap (item 26c)', max_length=1)
    reductionbasedonlengthofreceiptofassistance = models.CharField('reason for and amount of assistance reduction: reduction based on length of receipt of assistance (item 26c)', max_length=1)
    othernonsanction = models.CharField('reason for and amount of assistance reduction: other, non-sanction (item 26c)', max_length=1)
    waiver_evaluation_control_gprs = models.CharField('waiver_evaluation_control_gprs (item 27)', max_length=1)
    tanffamilyexemptfromtimelimits = models.IntegerField('TANF family exempt from time_limits (item 28)')
    tanffamilynewchildonlyfamily = models.IntegerField('TANF family new child only family (item 29)')


# T2: https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section1_10_2008.pdf
class Adult(models.Model):
    # metadata
    imported_at = models.DateTimeField('time record was imported (metadata)')
    imported_by = models.CharField('who record was imported by (metadata)', max_length=64)
    valid = models.BooleanField('has record passed validation checks', default=True)
    invalidreason = models.CharField('Reason(s) why record did not pass validation. (metadata)', max_length=1024, default='')

    # header data
    calendar_quarter = models.IntegerField('calendar quarter (header)')
    state_code = models.CharField('state fips code (header)', max_length=3)
    tribe_code = models.CharField('tribe code (header)', max_length=3)

    # record data
    recordtype = models.CharField('record type (T2)', max_length=2)
    reportingmonth = models.CharField('reporting month (item 4)', max_length=6)
    casenumber = models.CharField('case number (item 6)', max_length=11)
    familyafilliation = models.IntegerField('family affiliation (item 30)')
    noncustodialparent = models.IntegerField('noncustodial parent (item 31)')
    dateofbirth = models.DateField('date of birth (item 32)')
    socialsecuritynumber = models.CharField('social security number (item 33)', max_length=9)
    racehispanic = models.CharField('race/ethnicity: hispanic or latino (item 34a)', max_length=1)
    racenativeamerican = models.CharField('race/ethnicity: american indian or alaska native (item 34b)', max_length=1)
    raceasian = models.CharField('race/ethnicity: asian (item 34c)', max_length=1, default='')
    raceblack = models.CharField('race/ethnicity: black or african american (item 34d)', max_length=1, default='')
    raceislander = models.CharField('race/ethnicity: islander (item 34e)', max_length=1, default='')
    racewhite = models.CharField('race/ethnicity: white (item 34f)', max_length=1, default='')
    gender = models.IntegerField('gender (item 35)', default=0)
    oasdibenefits = models.CharField('receives disability benefits: received federal disability insurance benefits under the oasdi program (item 36a)', max_length=1, default='')
    nonssabenefits = models.CharField('receives disability benefits: receives benefits based on federal disability status under non-ssa programs (item 36b)', max_length=1, default='')
    titlexivapdtbenefits = models.CharField('receives disability benefits: received aid to the permanently and totally disabled under title xiv-apdt (item 36c)', max_length=1, default='')
    titlexviaabdbenefits = models.CharField('receives disability benefits: received aid to the aged, blind, and disabled under title xvi-aabd (item 36d)', max_length=1, default='')
    titlexvissibenefits = models.CharField('receives disability benefits: received ssi under title xvi-ssi (item 36e)', max_length=1, default='')
    maritalstatus = models.CharField('marital status (item 37)', max_length=1, default='')
    relationshiptohh = models.IntegerField('relationship to head of household (item 38)', default=0)
    parentminorchild = models.CharField('parent with minor child in the family (item 39)', max_length=1, default='')
    pregnantneeds = models.CharField('needs of a pregnant woman (item 40)', max_length=1, default='')
    educationlevel = models.CharField('education level (item 41)', max_length=2, default='')
    citizenship = models.CharField('citizenship/alienage (item 42)', max_length=1, default='')
    coopwithchildsupport = models.CharField('cooperation with child support (item 43)', max_length=1, default='')
    countablemonths = models.CharField('number of countable months toward federal time limit (item 44)', default='', max_length=3)
    countablemonthsremaining = models.CharField('number of countable months remaining under state/tribe limit (item 45)', default='', max_length=2)
    currentmonthexempt = models.CharField('current month exempt from state tribe time-limit (item 46)', max_length=1, default='')
    employmentstatus = models.CharField('employment status (item 47)', max_length=1, default='')
    workeligibleindicator = models.CharField('work eligible individual indicator (item 48)', max_length=2, default='')
    workparticipationstatus = models.CharField('work participation status (item 49)', max_length=2, default='')
    unsubsidizedemployment = models.CharField('unsubsidized employment (item 50)', max_length=2, default='')
    subsidizedprivateemployment = models.CharField('subsidized private employment (item 51)', max_length=2, default='')
    subsidizedpublicemployment = models.CharField('subsidized public employment (item 52)', max_length=2, default='')
    workexperiencehours = models.CharField('work experience: hours of participation (item 53a)', max_length=2, default='')
    workexperienceexcusedabsences = models.CharField('work experience: excused absences (item 53b)', max_length=2, default='')
    workexperienceholidays = models.CharField('work experience: holidays (item 53c)', max_length=2, default='')
    onthejobtraining = models.CharField('on the job training (item 54)', max_length=2, default='')
    jobsearchhours = models.CharField('job search & job readiness: hours of participation (item 55a)', max_length=2, default='')
    jobsearchexcusedabsences = models.CharField('job search & job readiness: excused absences (item 55b)', max_length=2, default='')
    jobsearchholidays = models.CharField('job search & job readiness: holidays (item 55c)', max_length=2, default='')
    communitysvchours = models.CharField('community svs prog: hours of participation (item 56a)', max_length=2, default='')
    communitysvcexcusedabsences = models.CharField('community svs prog: excused absences (item 56b)', max_length=2, default='')
    communitysvcholidays = models.CharField('community svs prog: holidays (item 56c)', max_length=2, default='')
    vocationaltraininghours = models.CharField('vocational education training: hours of participation (item 57a)', max_length=2, default='')
    vocationaltrainingexcusedabsences = models.CharField('vocational education training: excused absences (item 57b)', max_length=2, default='')
    vocationaltrainingholidays = models.CharField('vocational education training: holidays (item 57c)', max_length=2, default='')
    jobskillshours = models.CharField('job skills training employment related: hours of participation (item 58a)', max_length=2, default='')
    jobskillsexcusedabsences = models.CharField('job skills training employment related: excused absences (item 58b)', max_length=2, default='')
    jobskillsholidays = models.CharField('job skills training employment related: holidays (item 58c)', max_length=2, default='')
    eduwithnodiplomahours = models.CharField('education related to employment with no high school diploma: hours of participation (item 59a)', max_length=2, default='')
    eduwithnodiplomaexcusedabsences = models.CharField('education related to employment with no high school diploma: excused absences (item 59b)', max_length=2, default='')
    eduwithnodiplomaholidays = models.CharField('education related to employment with no high school diploma: holidays (item 59c)', max_length=2, default='')
    satisfactoryschoolhours = models.CharField('satisfactory school attendance: hours of participation (item 60a)', max_length=2, default='')
    satisfactoryschoolexcusedabsences = models.CharField('satisfactory school attendance: excused absences (item 60b)', max_length=2, default='')
    satisfactoryschoolholidays = models.CharField('satisfactory school attendance: holidays (item 60c)', max_length=2, default='')
    providingchildcarehours = models.CharField('providing child care: hours of participation (item 61a)', max_length=2, default='')
    providingchildcareexcusedabsences = models.CharField('providing child care: excused absences (item 61b)', max_length=2, default='')
    providingchildcareholidays = models.CharField('providing child care: holidays (item 61c)', max_length=2, default='')
    otherwork = models.CharField('other work activities (item 62)', max_length=2, default='')
    corehoursforoverallrate = models.CharField('number of deemed core hours for overall rate (item 63)', max_length=2, default='')
    corehoursfortwoparentrate = models.CharField('number of deemed core hours for the two-parent rate (item 64)', max_length=2, default='')
    earnedincome = models.CharField('amount of earned income (item 65)', default='', max_length=4)
    unearnedincomeincometaxcredit = models.CharField('amount of unearned income: earned income tax credit (item 66a)', max_length=4, default='')
    unearnedincomesocialsecurity = models.CharField('amount of unearned income: social security (item 66b)', max_length=4, default='')
    unearnedincomessi = models.CharField('amount of unearned income: SSI (item 66c)', max_length=4, default='')
    unearnedincomeworkerscomp = models.CharField('amount of unearned income: workers compensation (item 66d)', max_length=4, default='')
    unearnedincomeother = models.CharField('amount of unearned income: other unearned income (item 66e)', max_length=4, default='')


# T3:  https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section1_10_2008.pdf
class Child(models.Model):
    # metadata
    imported_at = models.DateTimeField('time record was imported (metadata)')
    imported_by = models.CharField('who record was imported by (metadata)', max_length=64)
    valid = models.BooleanField('has record passed validation checks', default=True)
    invalidreason = models.CharField('Reason(s) why record did not pass validation. (metadata)', max_length=1024, default='')

    # header data
    calendar_quarter = models.IntegerField('calendar quarter (header)')
    state_code = models.CharField('state fips code (header)', max_length=3)
    tribe_code = models.CharField('tribe code (header)', max_length=3)

    # record data
    recordtype = models.CharField('record type (T3)', max_length=2)
    reportingmonth = models.CharField('reporting month (item 4)', max_length=6)
    casenumber = models.CharField('case number (item 6)', max_length=11)

    familyafilliation_1 = models.IntegerField('family affiliation1: Child 1,3,5,7,9 (item 67)', default=0)
    dateofbirth_1 = models.DateField('date of birth (item 68)')
    socialsecuritynumber_1 = models.CharField('social security number (item 69)', max_length=9, default='')
    racehispanic_1 = models.CharField('race/ethnicity: hispanic or latino (item 70a)', max_length=1, default='')
    racenativeamerican_1 = models.CharField('race/ethnicity: american indian or alaska native (item 70b)', max_length=1, default='')
    raceasian_1 = models.CharField('race/ethnicity: asian (item 70c)', max_length=1, default='')
    raceblack_1 = models.CharField('race/ethnicity: black or african american islander (item 70d)', max_length=1, default='')
    racepacific_1 = models.CharField('race/ethnicity: native hawaiian or other pacific islander (item 70e)', max_length=1, default='')
    racewhite_1 = models.CharField('race/ethnicity: white (item 70f)', max_length=1, default='')
    gender_1 = models.IntegerField('gender (item 71)', default=0)
    nonssabenefits_1 = models.CharField('receives disability benefits: receives benefits based on federal disability status under non-ssa programs (item 72a)', max_length=1, default='')
    titlexvissibenefits_1 = models.CharField('receives disability benefits: received ssi under title xvi-ssi (item 72b)', max_length=1, default='')
    relationshiptohh_1 = models.IntegerField('relationship to head of household (item 73)', default=0)
    parentminorchild_1 = models.CharField('parent with minor child in the family (item 74)', max_length=1, default='')
    educationlevel_1 = models.CharField('education level (item 75)', max_length=12, default='')
    citizenship_1 = models.CharField('citizenship/alienage (item 76)', max_length=1, default='')
    unearnedincomessi_1 = models.CharField('amount of unearned income: SSI (item 77a)', max_length=4, default='')
    unearnedincomeother_1 = models.CharField('amount of unearned income: other unearned income (item 77b)', max_length=4, default='')

    familyafilliation_2 = models.IntegerField('family affiliation 2: Child 2,4,6,8,10 (item 67)', default=0)
    dateofbirth_2 = models.DateField('date of birth (item 68)', default=datetime.date.today)
    socialsecuritynumber_2 = models.CharField('social security number (item 69)', max_length=9, default='')
    racehispanic_2 = models.CharField('race/ethnicity: hispanic or latino (item 70a)', max_length=1, default='')
    racenativeamerican_2 = models.CharField('race/ethnicity: american indian or alaska native (item 70b)', max_length=1, default='')
    raceasian_2 = models.CharField('race/ethnicity: asian (item 70c)', max_length=1, default='')
    raceblack_2 = models.CharField('race/ethnicity: black or african american islander (item 70d)', max_length=1, default='')
    racepacific_2 = models.CharField('race/ethnicity: native hawaiian or other pacific islander (item 70e)', max_length=1, default='')
    racewhite_2 = models.CharField('race/ethnicity: white (item 70f)', max_length=1, default='')
    gender_2 = models.IntegerField('gender (item 71)', default=0)
    nonssabenefits_2 = models.CharField('receives disability benefits: receives benefits based on federal disability status under non-ssa programs (item 72a)', max_length=1, default='')
    titlexvissibenefits_2 = models.CharField('receives disability benefits: received ssi under title xvi-ssi (item 72b)', max_length=1, default='')
    relationshiptohh_2 = models.IntegerField('relationship to head of household (item 73)', default=0)
    parentminorchild_2 = models.CharField('parent with minor child in the family (item 74)', max_length=1, default='')
    educationlevel_2 = models.CharField('education level (item 75)', max_length=12, default='')
    citizenship_2 = models.CharField('citizenship/alienage (item 76)', max_length=1, default='')
    unearnedincomessi_2 = models.CharField('amount of unearned income: SSI (item 77a)', max_length=4, default='')
    unearnedincomeother_2 = models.CharField('amount of unearned income: other unearned income (item 77b)', max_length=4, default='')

    jobsearchhours = models.CharField('job search & job readiness: hours of participation (item 55a)', max_length=2, default='')
    jobsearchexcusedabsences = models.CharField('job search & job readiness: excused absences (item 55b)', max_length=2, default='')
    jobsearchholidays = models.CharField('job search & job readiness: holidays (item 55c)', max_length=2, default='')
    communitysvchours = models.CharField('community svs prog: hours of participation (item 56a)', max_length=2, default='')
    communitysvcexcusedabsences = models.CharField('community svs prog: excused absences (item 56b)', max_length=2, default='')
    communitysvcholidays = models.CharField('community svs prog: holidays (item 56c)', max_length=2, default='')
    vocationaltraininghours = models.CharField('vocational education training: hours of participation (item 57a)', max_length=2, default='')
    vocationaltrainingexcusedabsences = models.CharField('vocational education training: excused absences (item 57b)', max_length=2, default='')
    vocationaltrainingholidays = models.CharField('vocational education training: holidays (item 57c)', max_length=2, default='')
    jobskillshours = models.CharField('job skills training employment related: hours of participation (item 58a)', max_length=2, default='')
    jobskillsexcusedabsences = models.CharField('job skills training employment related: excused absences (item 58b)', max_length=2, default='')
    jobskillsholidays = models.CharField('job skills training employment related: holidays (item 58c)', max_length=2, default='')
    eduwithnodiplomahours = models.CharField('education related to employment with no high school diploma: hours of participation (item 59a)', max_length=2, default='')
    eduwithnodiplomaexcusedabsences = models.CharField('education related to employment with no high school diploma: excused absences (item 59b)', max_length=2, default='')
    eduwithnodiplomaholidays = models.CharField('education related to employment with no high school diploma: holidays (item 59c)', max_length=2, default='')
    satisfactoryschoolhours = models.CharField('satisfactory school attendance: hours of participation (item 60a)', max_length=2, default='')
    satisfactoryschoolexcusedabsences = models.CharField('satisfactory school attendance: excused absences (item 60b)', max_length=2, default='')
    satisfactoryschoolholidays = models.CharField('satisfactory school attendance: holidays (item 60c)', max_length=2, default='')
    providingchildcarehours = models.CharField('providing child care: hours of participation (item 61a)', max_length=2, default='')
    providingchildcareexcusedabsences = models.CharField('providing child care: excused absences (item 61b)', max_length=2, default='')
    providingchildcareholidays = models.CharField('providing child care: holidays (item 61c)', max_length=2, default='')
    otherwork = models.CharField('other work activities (item 62)', max_length=2, default='')
    corehoursforoverallrate = models.CharField('number of deemed core hours for overall rate (item 63)', max_length=2, default='')
    corehoursfortwoparentrate = models.CharField('number of deemed core hours for the two-parent rate (item 64)', max_length=2, default='')
    earnedincome = models.CharField('amount of earned income (item 65)', max_length=4, default='')
    unearnedincomeincometaxcredit = models.CharField('amount of unearned income: earned income tax credit (item 66a)', max_length=4, default='')
    unearnedincomesocialsecurity = models.CharField('amount of unearned income: social security (item 66b)', max_length=4, default='')
    unearnedincomessi = models.CharField('amount of unearned income: SSI (item 66c)', max_length=4, default='')
    unearnedincomeworkerscomp = models.CharField('amount of unearned income: workers compensation (item 66d)', max_length=4, default='')
    unearnedincomeother = models.CharField('amount of unearned income: other unearned income (item 66e)', max_length=4, default='')


# T4: https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section2.pdf
class ClosedCase(models.Model):
    # metadata
    imported_at = models.DateTimeField('time record was imported (metadata)')
    imported_by = models.CharField('who record was imported by (metadata)', max_length=64)

    # header data
    calendar_quarter = models.IntegerField('calendar quarter (header)')
    state_code = models.CharField('state fips code (header)', max_length=3)
    tribe_code = models.CharField('tribe code (header)', max_length=3)

    # record data
    recordtype = models.CharField('record type (T4)', max_length=2)
    reportingmonth = models.CharField('reporting month (item 4)', max_length=6)
    casenumber = models.CharField('case number (item 6)', max_length=11)
    countyfipscode = models.IntegerField('county fips code (item 2)')
    stratum = models.IntegerField('stratum (item 5)')
    zipcode = models.CharField('zipcode (item 7)', max_length=5)
    disposition = models.IntegerField('disposition (item 8)')
    closurereason = models.IntegerField('reason for closure (item 9)')
    receivessubsidizedhousing = models.CharField('receives subsidized housing (item 10)', max_length=1)
    receivesmedicalassistance = models.CharField('receives medical assistance (item 11)', max_length=1)
    receivesfoodstamps = models.CharField('receives food stamps (item 12)', max_length=1)
    receivessubsidizedchildcare = models.CharField('receives subsidized child care (item 13)', max_length=1)


# T5: https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section2.pdf
class ClosedPerson(models.Model):
    # metadata
    imported_at = models.DateTimeField('time record was imported (metadata)')
    imported_by = models.CharField('who record was imported by (metadata)', max_length=64)
    valid = models.BooleanField('has record passed validation checks', default=True)
    invalidreason = models.CharField('Reason(s) why record did not pass validation. (metadata)', max_length=1024, default='')

    # header data
    calendar_quarter = models.IntegerField('calendar quarter (header)')
    state_code = models.CharField('state fips code (header)', max_length=3)
    tribe_code = models.CharField('tribe code (header)', max_length=3)

    # record data
    recordtype = models.CharField('record type (T5)', max_length=2)
    reportingmonth = models.CharField('reporting month (item 4)', max_length=6)
    casenumber = models.CharField('case number (item 6)', max_length=11)
    familyafilliation = models.IntegerField('family affiliation (item 14)')
    dateofbirth = models.DateField('date of birth (item 15)')
    socialsecuritynumber = models.CharField('social security number (item 16)', max_length=9)
    racehispanic = models.CharField('race/ethnicity: hispanic or latino (item 17a)', max_length=1)
    racenativeamerican = models.CharField('race/ethnicity: american indian or alaska native (item 17b)', max_length=1)
    raceasian = models.CharField('race/ethnicity: asian (item 17c)', max_length=1)
    raceblack = models.CharField('race/ethnicity: black or african american (item 17d)', max_length=1)
    racepacific = models.CharField('race/ethnicity: native hawaiian or other pacific islander (item 17e)', max_length=1)
    racewhite = models.CharField('race/ethnicity: white (item 17f)', max_length=1)
    gender = models.IntegerField('gender (item 18)')
    oasdibenefits = models.CharField('receives disability benefits: received federal disability insurance benefits under the oasdi program (item 19a)', max_length=1)
    nonssabenefits = models.CharField('receives disability benefits: receives benefits based on federal disability status under non-ssa programs (item 19b)', max_length=1)
    titlexivapdtbenefits = models.CharField('receives disability benefits: received aid to the permanently and totally disabled under title xiv-apdt (item 19c)', max_length=1)
    titlexviaabdbenefits = models.CharField('receives disability benefits: received aid to the aged, blind, and disabled under title xvi-aabd (item 19d)', max_length=1)
    titlexvissibenefits = models.CharField('receives disability benefits: received ssi under title xvi-ssi (item 19e)', max_length=1)
    maritalstatus = models.CharField('marital status (item 20)', max_length=1)
    relationshiptohh = models.IntegerField('relationship to head of household (item 21)')
    parentminorchild = models.CharField('parent with minor child in the family (item 22)', max_length=1)
    pregnantneeds = models.CharField('needs of a pregnant woman (item 23)', max_length=11)
    educationlevel = models.CharField('education level (item 24)', max_length=12)
    citizenship = models.CharField('citizenship/alienage (item 25)', max_length=1)
    countablemonths = models.IntegerField('number of countable months toward federal time limit (item 26)')
    countablemonthsremaining = models.IntegerField('number of countable months remaining under state/tribe limit (item 27)')
    employmentstatus = models.CharField('employment status (item 28)', max_length=1)
    earnedincome = models.IntegerField('amount of earned income (item 29)')
    unearnedincome = models.IntegerField('amount of unearned income (item 30)')


# T6: https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section3.pdf
class AggregatedData(models.Model):
    # metadata
    imported_at = models.DateTimeField('time record was imported (metadata)')
    imported_by = models.CharField('who record was imported by (metadata)', max_length=64)
    valid = models.BooleanField('has record passed validation checks', default=True)
    invalidreason = models.CharField('Reason(s) why record did not pass validation. (metadata)', max_length=1024, default='')

    # header data
    calendar_quarter = models.IntegerField('calendar quarter (header)')
    state_code = models.CharField('state fips code (header)', max_length=3)
    tribe_code = models.CharField('tribe code (header)', max_length=3)

    # record data
    recordtype = models.CharField('record type (T6)', max_length=2)
    calendaryear = models.IntegerField('calendar year (item 3)')
    calendarquarter = models.IntegerField('calendar quarter (item 3)')
    firstmonthapps = models.IntegerField('total number of applicants: first month (item 4)')
    secondmonthapps = models.IntegerField('total number of applicants: second month (item 4)')
    thirdmonthapps = models.IntegerField('total number of applicants: third month (item 4)')
    firstmonthapprovals = models.IntegerField('total number of approved applications: first month (item 5)')
    secondmonthapprovals = models.IntegerField('total number of approved applications: second month (item 5)')
    thirdmonthapprovals = models.IntegerField('total number of approved applications: third month (item 5)')
    firstmonthdenied = models.IntegerField('total number of denied applications: first month (item 6)')
    secondmonthdenied = models.IntegerField('total number of denied applications: second month (item 6)')
    thirdmonthdenied = models.IntegerField('total number of denied applications: third month (item 6)')
    firstmonthassist = models.IntegerField('total amount of assistance: first month (item 7)', default=0)
    secondmonthassist = models.IntegerField('total amount of assistance: second month (item 7)', default=0)
    thirdmonthassist = models.IntegerField('total amount of assistance: third month (item 7)', default=0)
    # XXX many more fields need to be added here


# T7: https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section4.pdf
class FamiliesByStratumData(models.Model):
    # metadata
    imported_at = models.DateTimeField('time record was imported (metadata)')
    imported_by = models.CharField('who record was imported by (metadata)', max_length=64)
    valid = models.BooleanField('has record passed validation checks', default=True)
    invalidreason = models.CharField('Reason(s) why record did not pass validation. (metadata)', max_length=1024, default='')

    # header data
    calendar_quarter = models.IntegerField('calendar quarter (header)')
    state_code = models.CharField('state fips code (header)', max_length=3)
    tribe_code = models.CharField('tribe code (header)', max_length=3)

    # record data
    recordtype = models.CharField('record type (T7)', max_length=2)
    calendaryear = models.IntegerField('calendar year (item 3)')
    calendarquarter = models.IntegerField('calendar quarter (item 3)')
    # XXX many more fields need to be added here
