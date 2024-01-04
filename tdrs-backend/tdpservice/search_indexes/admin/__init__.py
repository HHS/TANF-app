from django.contrib import admin
from .. import models
from . import tanf, tribal, ssp

admin.site.register(models.tanf.TANF_T1, tanf.TANF_T1Admin)
admin.site.register(models.tanf.TANF_T2, tanf.TANF_T2Admin)
admin.site.register(models.tanf.TANF_T3, tanf.TANF_T3Admin)
admin.site.register(models.tanf.TANF_T4, tanf.TANF_T4Admin)
admin.site.register(models.tanf.TANF_T5, tanf.TANF_T5Admin)
admin.site.register(models.tanf.TANF_T6, tanf.TANF_T6Admin)
admin.site.register(models.tanf.TANF_T7, tanf.TANF_T7Admin)

admin.site.register(models.tribal.Tribal_TANF_T1, tribal.Tribal_TANF_T1Admin)
admin.site.register(models.tribal.Tribal_TANF_T2, tribal.Tribal_TANF_T2Admin)
admin.site.register(models.tribal.Tribal_TANF_T3, tribal.Tribal_TANF_T3Admin)

admin.site.register(models.ssp.SSP_M1, ssp.SSP_M1Admin)
admin.site.register(models.ssp.SSP_M2, ssp.SSP_M2Admin)
admin.site.register(models.ssp.SSP_M3, ssp.SSP_M3Admin)
admin.site.register(models.ssp.SSP_M4, ssp.SSP_M4Admin)
admin.site.register(models.ssp.SSP_M5, ssp.SSP_M5Admin)
admin.site.register(models.ssp.SSP_M6, ssp.SSP_M6Admin)
admin.site.register(models.ssp.SSP_M7, ssp.SSP_M7Admin)
