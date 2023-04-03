from django.contrib import admin
from ..models import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7
from .tanf import TANF_T1Admin, TANF_T2Admin, TANF_T3Admin, TANF_T4Admin, TANF_T5Admin, TANF_T6Admin, TANF_T7Admin

admin.site.register(TANF_T1, TANF_T1Admin)
admin.site.register(TANF_T2, TANF_T2Admin)
admin.site.register(TANF_T3, TANF_T3Admin)
admin.site.register(TANF_T4, TANF_T4Admin)
admin.site.register(TANF_T5, TANF_T5Admin)
admin.site.register(TANF_T6, TANF_T6Admin)
admin.site.register(TANF_T7, TANF_T7Admin)
