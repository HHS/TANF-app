from django.contrib import admin
from .. import models
from . import tanf

admin.site.register(models.tanf.TANF_T1, tanf.TANF_T1Admin)
admin.site.register(models.tanf.TANF_T2, tanf.TANF_T2Admin)
admin.site.register(models.tanf.TANF_T3, tanf.TANF_T3Admin)
admin.site.register(models.tanf.TANF_T4, tanf.TANF_T4Admin)
admin.site.register(models.tanf.TANF_T5, tanf.TANF_T5Admin)
admin.site.register(models.tanf.TANF_T6, tanf.TANF_T6Admin)
admin.site.register(models.tanf.TANF_T7, tanf.TANF_T7Admin)
