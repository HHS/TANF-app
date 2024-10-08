# Generated by Django 3.2.15 on 2022-12-08 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='t1',
            old_name='fips_code',
            new_name='FIPS_CODE',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='amt_sub_cc',
            new_name='AMT_SUB_CC',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='cc_nbr_of_months',
            new_name='CC_NBR_MONTHS',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='cash_amount',
            new_name='CASH_AMOUNT',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='nbr_months',
            new_name='NBR_MONTHS',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='nbr_of_family_members',
            new_name='NBR_FAMILY_MEMBERS',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='amt_food_stamp_assistance',
            new_name='AMT_FOOD_STAMP_ASSISTANCE',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='receives_sub_cc',
            new_name='RECEIVES_SUB_CC',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='record',
            new_name='RecordType',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='family_sanct_adult',
            new_name='FAMILY_SANC_ADULT',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='family_cap',
            new_name='FAMILY_CAP',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='failure_to_comply',
            new_name='FAILURE_TO_COMPLY',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='reductions_on_receipts',
            new_name='REDUCTIONS_ON_RECEIPTS',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='non_cooperation_cse',
            new_name='NON_COOPERATION_CSE',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='other_sanction',
            new_name='OTHER_SANCTION',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='recoupment_prior_ovrpmt',
            new_name='RECOUPMENT_PRIOR_OVRPMT',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='sanct_teen_parent',
            new_name='SANC_TEEN_PARENT',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='work_req_sanction',
            new_name='WORK_REQ_SANCTION',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='sanc_reduction_amount',
            new_name='SANC_REDUCTION_AMT',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='rpt_month_year',
            new_name='RPT_MONTH_YEAR',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='cc_amount',
            new_name='CC_AMOUNT',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='family_exempt_time_limits',
            new_name='FAMILY_EXEMPT_TIME_LIMITS',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='family_new_child',
            new_name='FAMILY_NEW_CHILD',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='other_total_reductions',
            new_name='OTHER_TOTAL_REDUCTIONS',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='transp_amount',
            new_name='TRANSP_AMOUNT',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='waiver_evalu_control_grps',
            new_name='WAIVER_EVAL_CONTROL_GRPS',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='other_nbr_of_months',
            new_name='OTHER_NBR_MONTHS',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='transp_nbr_months',
            new_name='TRANSP_NBR_MONTHS',
        ),
        migrations.RemoveField(
            model_name='t1',
            name='blank',
        ),
        migrations.RemoveField(
            model_name='t3',
            name='blank',
        ),
        migrations.RemoveField(
            model_name='t4',
            name='blank',
        ),
    ]
