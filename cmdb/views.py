from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Host, Business, Datacenter, Cluster

class HostListView(ListView):
    model = Host
    template_name = 'cmdb/index.html'
    context_object_name = 'host_list'

    datacenter_all = Datacenter.objects.all()
    business_all = Business.objects.all()
    host_status_all = Host.HOST_STATUS_CHOICES
    host_type_all = Host.HOST_TYPE_CHOICES
    host_find = Host.objects.all()

    datacenter = None
    business = None
    host_status = None
    host_type = None
    keyword = None
   
    # 重写get函数，获取request的一些参数
    def get(self, request, *args, **kwargs):
        self.datacenter = request.GET.get('datacenter')
        self.business = request.GET.get('business')
        self.host_status = request.GET.get('status')
        self.host_type = request.GET.get('type')
        self.keyword = request.GET.get('keyword')
        response = super().get(request, *args, **kwargs)
        return response

    # 重写get_query_set函数，根据条件查询数据库
    def get_queryset(self):
        if self.datacenter:
            self.host_find = self.host_find.filter(datacenter__name__icontains=self.datacenter)
        if self.business:
            self.host_find = self.host_find.filter(business__name__icontains=self.business)
        if self.host_status:
            self.host_find = self.host_find.filter(host_status__icontains=self.host_status)
        if self.host_type:
            self.host_find = self.host_find.filter(host_type__icontains=self.host_type)
        if self.keyword:
            self.host_find = self.host_find.filter(
                    Q(fqdn_name__icontains=self.keyword) |
                    Q(ipmi_ip__icontains=self.keyword) |
                    Q(host_outerip__icontains=self.keyword) |
                    Q(host_innerip__icontains=self.keyword) |
                    Q(manufacturer__icontains=self.keyword) |
                    Q(sn__icontains=self.keyword) |
                    Q(os_type__icontains=self.keyword) |
                    Q(os_name__icontains=self.keyword) |
                    Q(other_ip__icontains=self.keyword) |
                    Q(mac_addr__icontains=self.keyword) |
                    Q(cabinet__name__icontains=self.keyword)
                    )
        return self.host_find

    # 重写get_context_data函数，添加向模版传输的内容
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
                {
                'datacenter_all': self.datacenter_all,
                'business_all': self.business_all,
                'host_status_all': self.host_status_all,
                'host_type_all': self.host_type_all,
                'datacenter_name': self.datacenter,
                'business_name': self.business,
                'host_status': self.host_status,
                'host_type': self.host_type,
                }
                )
        return context

class HostDetailView(DetailView):
    model = Host
    template_name = 'cmdb/host_detail.html'

    # 重写函数，传递指定参数
    def get_context_data(self, **kwargs):
        host = super().get_object()
        context = super().get_context_data(**kwargs)
        cluster = host.cluster.all()
        host_type_this = ''
        host_status_this = ''
        os_type_this = ''

        for htype in Host.HOST_TYPE_CHOICES:
            if htype[0] == host.host_type:
                host_type_this = htype[1]

        for status in Host.HOST_STATUS_CHOICES:
            if status[0] == host.host_status:
                host_status_this = status[1]

        for otype in Host.OS_TYPE_CHOICES:
            if otype[0] == host.os_type:
                os_type_this = otype[1]

        context.update(
                {
                'host_type_this': host_type_this,
                'host_status_this': host_status_this,
                'os_type_this': os_type_this,
                'cluster': cluster,
                }
                )
        return context
