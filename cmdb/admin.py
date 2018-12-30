from django.contrib import admin
from .models import Host, Cluster, Model, Business, Datacenter, Cabinet

admin.site.register(Host)
admin.site.register(Cluster)
admin.site.register(Model)
admin.site.register(Business)
admin.site.register(Datacenter)
admin.site.register(Cabinet)
