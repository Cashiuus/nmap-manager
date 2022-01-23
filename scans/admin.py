from django.contrib import admin

from .models import Host, Scan, Service, ScanPolicy


class ScanAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['name', 'scan_end', 'count_live_hosts', 'duration']

class HostAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['hostname', 'ip_address', 'scan_id', 'assessment_status_1',
                    'os_name', 'state', 'category', 'criticality',
    ]
    list_editable = ['category', 'criticality',]

class ServiceAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['port_number', 'service_name', 'product_name', 
                    'host_id', 'scan_id', 'assessment_status_1',
                    'state', 'category', 'attack_value',
    ]
    list_editable = ['category', 'attack_value']

class ScanPolicyAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['name', 'scan_type', 'arguments']
    list_editable = ['scan_type', 'arguments']


admin.site.register(Host, HostAdmin)
admin.site.register(Scan, ScanAdmin)
admin.site.register(ScanPolicy, ScanPolicyAdmin)
admin.site.register(Service, ServiceAdmin)