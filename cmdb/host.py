from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from .models import Host, Business, Datacenter, Cluster
from .form import HostForm

class HostListView(ListView):
    model = Host
    template_name = 'cmdb/index.html'

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
    paginate_by = None
   
    def get(self, request, *args, **kwargs):
        """
        重写get函数，获取我们需要的request参数
        """

        self.datacenter = request.GET.get('datacenter')
        self.business = request.GET.get('business')
        self.host_status = request.GET.get('status')
        self.host_type = request.GET.get('type')
        self.keyword = request.GET.get('keyword')
		# 从视图获取每页显示的主机个数默认为10
		# paginate_by是父类原有的变量，赋值后每页主机个数自动生效
        self.paginate_by = request.GET.get('paginate_by', '10')
        response = super().get(request, *args, **kwargs)
        return response

    def get_queryset(self):
        """ 
        重写get_query_set函数，根据条件查询数据库
        用于实现页面上筛选和搜索功能
        """
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
                    Q(host_name__icontains=self.keyword) |
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

    def get_context_data(self, **kwargs):
        """
        重写get_context_data函数，添加向模版传输的内容
        """

        context = super().get_context_data(**kwargs)
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)
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
                'paginate_by': self.paginate_by,
                }
                )
        context.update(pagination_data)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        """
        该函数用来生成分页程序的变量数据
        这些变量将通过get_context_data函数传输到模版
        """
        if not is_paginated:
            return {}
        # 当前页左边连续的页码号，初始值为空
        left = []
        # 当前页右边连续的页码号，初始值为空
        right = []
        # 表示第 1 页页码后是否需要显示省略号
        left_has_more = False
        # 表示最后一页页码前是否需要显示省略号
        right_has_more = False
        # 表示是否需要显示第 1 页的页码号
        first = False
        # 表示是否需要显示最后一页的页码号
        last = False
        
        page_number = page.number
        total_pages = paginator.num_pages
        page_range = paginator.page_range

        if page_number == 1:
            # 获取当前页码后的3个页码
            right = page_range[page_number:page_number + 3]
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            # 获取当前页码前连续3个页码
            left = page_range[(page_number - 4) if (page_number - 4) > 0 else 0:page_number -1]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        else:
            left = page_range[(page_number - 4) if (page_number - 4) > 0 else 0:page_number -1]
            right = page_range[page_number:page_number + 3]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }
        return data

class HostDetailView(DetailView):
    model = Host
    template_name = 'cmdb/host_detail.html'

    def get_context_data(self, **kwargs):
        """
        重写函数，传递指定参数给模版
        """
        host = super().get_object()
        context = super().get_context_data(**kwargs)
        cluster_this = host.cluster.all()
        host_type_this = ''
        host_status_this = ''
        os_type_this = ''

        # 用于生成主机详情页的主机类型字段的值
        for htype in Host.HOST_TYPE_CHOICES:
            if htype[0] == host.host_type:
                host_type_this = htype[1]

        # 用于生成主机详情页的主机状态字段的值
        for status in Host.HOST_STATUS_CHOICES:
            if status[0] == host.host_status:
                host_status_this = status[1]

        # 用于生成主机详情页的系统类型字段的值
        for otype in Host.OS_TYPE_CHOICES:
            if otype[0] == host.os_type:
                os_type_this = otype[1]

        context.update(
                {
                'host_type_this': host_type_this,
                'host_status_this': host_status_this,
                'os_type_this': os_type_this,
                'cluster_this': cluster_this,
                }
                )
        return context

class HostAddView(CreateView):
    model = Host
    template_name_suffix = '_add'
    form_class = HostForm

    def form_invalid(self, form):
        """
        重写函数，表单数据不合法时，将指定参数传递给模版
        """
        return self.render_to_response(
                self.get_context_data(
                    form=form,
                    tips='添加失败！',
                    display_control=' '
                    )
                )

    def form_valid(self, form):
        """
        重写函数，表单数据合法时，保存表单数据，并将指定参数传递给给模版
        """
        self.object = form.save()
        return self.render_to_response(
                self.get_context_data(
                    form=form,
                    tips='添加成功！',
                    display_control=' '
                    )
                )

class HostEditView(UpdateView):
    model = Host
    template_name_suffix = '_edit'
    form_class = HostForm

    def get_success_url(self):
        """ 
        重写函数，将表单数据填写成功后返回的url指定为/cmdb/host/edit/x
        """
        path = self.request.path
        return path

    def form_valid(self, form):
        """
        重写函数，使其返值为对host_edit.html模版的渲染，并将status的参数传递给给模版
        """
        self.object = form.save()
        return self.render_to_response(
                self.get_context_data(
                    status='1'
                    )
                )

def host_del(request):
    # 当request请求为get时，删除指定的某条数据 
    host_id = request.GET.get('id', '')
    if host_id:
        Host.objects.filter(id=host_id).delete()
    # 当request请求为post时，删除指定的某些数据
    if request.method == 'POST':
        host_batch = request.GET.get('arg', '')
        host_id_all = str(request.POST.get('host_id_all', ''))

        if host_batch:
            for host_id in host_id_all.split(','):
                host_item = Host.objects.filter(id=host_id).delete()

    return HttpResponse(u'删除成功')
