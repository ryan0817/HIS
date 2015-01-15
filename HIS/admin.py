from django.contrib import admin
from HIS.models import SickRecord, Issue, Source

admin.site.register(SickRecord)
admin.site.register(Issue)
admin.site.register(Source)
