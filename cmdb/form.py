from django import forms
from django.forms.widgets import *

from .models import Host

class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        exclude = ("id",)
        widgets = {
            'host_type': Select(attrs={'class': 'form-control', 'style': 'width:530px;'}),
            'host_name': TextInput(
                    attrs={
                        'class': 'form-control',
                        'style': 'width:530px;',
                        'placeholder': '必填项 优先fqdn'
                        }
                    ),
            'ipmi_ip': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'host_innerip': TextInput(
                    attrs={
                        'class': 'form-control',
                        'style': 'width:530px;',
                        'placeholder': '必填项'
                        }
                    ),
            'host_outerip': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'other_ip': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'mac_addr': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'cpu_module': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'cpu_num': NumberInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'cpu_core_count': NumberInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'mem_mb': NumberInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'disk_gb': NumberInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'os_type': Select(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'os_name': TextInput(
                    attrs={
                        'class': 'form-control', 
                        'style':'width:530px;',
                        'placeholder': '例如Centos7.2'
                        }
                    ),
            'os_bit': NumberInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'business': Select(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'cluster': SelectMultiple(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'datacenter': Select(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'cabinet': Select(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'host_status': Select(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'sn': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'manufacturer': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'service_term': NumberInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'sla': Select(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'created_time': DateTimeInput(
                    attrs={
                        'class': 'form-control',
                        'style':'width:530px;',
                        'placeholder': '格式要求: 2006-10-25 14:30'
                        }
                    ),
            'modified_time': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'manager': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'bak_manager': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
            'comment': TextInput(attrs={'class': 'form-control', 'style':'width:530px;'}),
        }
