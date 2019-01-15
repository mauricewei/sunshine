#! /usr/bin/env python3

import datetime
import xlwt
import xlrd

from xlrd import xldate_as_tuple
from io import BytesIO
from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from .models import Host, Business, Datacenter, Cabinet, Cluster
from .form import HostForm
from .paginator import paginate

class HostListView(ListView):
    """ 主机列表视图 """
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
    export = None
    host_id_all = None
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
        self.export = request.GET.get('export')
        self.host_id_all = request.GET.getlist("id")
        # 从视图获取每页显示的主机个数默认为10
        # paginate_by是父类原有的变量，赋值后每页主机个数自动生效
        self.paginate_by = request.GET.get('paginate_by', '10')
        if self.export:
            response = create_host_excel(self.export, self.host_id_all) 
        else:
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
        pagination_data = paginate(paginator, page, is_paginated)
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

class HostDetailView(DetailView):
    """ 主机详情视图 """
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
    """ 添加主机视图 """
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
    """ 主机编辑视图 """
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
    """ 删除视图 """
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

    return HttpResponse('删除成功')

def create_host_excel(export, host_id_all):
    """ 
    该函数用来创建主机信息文件,并返回response对象
    """
    # 样式初始化
    style = xlwt.XFStyle()
    # 设置字体
    font = xlwt.Font()
    font.height = 20 * 12
    style.font = font
    # 设置对齐方式
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
    style.alignment = alignment
    # 设置时间格式
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'yyyy-mm-dd hh:mm'
    date_format.alignment = alignment
    date_format.font = font
    # 创建工作薄
    wb = xlwt.Workbook(encoding='utf-8')
    # 创建sheet
    ws = wb.add_sheet("主机信息")
    # 设置单元格长宽
    ws.col(0).width=100*30
    ws.col(1).width=250*30
    ws.col(2).width=150*30
    ws.col(3).width=150*30
    ws.col(4).width=150*30
    ws.col(5).width=250*30
    ws.col(6).width=200*30
    ws.col(7).width=400*30
    ws.col(8).width=100*30
    ws.col(9).width=100*30
    ws.col(10).width=100*30
    ws.col(11).width=100*30
    ws.col(12).width=100*30
    ws.col(13).width=100*30
    ws.col(14).width=100*30
    ws.col(15).width=150*30
    ws.col(16).width=400*30
    ws.col(17).width=150*30
    ws.col(18).width=100*30
    ws.col(19).width=100*30
    ws.col(20).width=300*30
    ws.col(21).width=100*30
    ws.col(22).width=100*30
    ws.col(23).width=100*30
    ws.col(24).width=200*30
    ws.col(25).width=200*30
    ws.col(26).width=100*30
    ws.col(27).width=100*30
    ws.col(28).width=400*30
    # 写入表头数据
    ws.write(0, 0, "主机类型", style)
    ws.write(0, 1, "主机名或fqdn名", style)
    ws.write(0, 2, "IPMI地址", style)
    ws.write(0, 3, "管理IP地址", style)
    ws.write(0, 4, "外网IP地址", style)
    ws.write(0, 5, "其它IP", style)
    ws.write(0, 6, "管理网MAC地址", style)
    ws.write(0, 7, "CPU型号", style)
    ws.write(0, 8, "CPU个数", style)
    ws.write(0, 9, "CPU逻辑核心数", style)
    ws.write(0, 10, "内存大小(MB)", style)
    ws.write(0, 11, "磁盘大小(GB)", style)
    ws.write(0, 12, "操作系统类型", style)
    ws.write(0, 13, "操作系统名称", style)
    ws.write(0, 14, "操作系统位数", style)
    ws.write(0, 15, "所属业务", style)
    ws.write(0, 16, "所属集群", style)
    ws.write(0, 17, "所属数据中心", style)
    ws.write(0, 18, "所属机柜", style)
    ws.write(0, 19, "主机状态", style)
    ws.write(0, 20, "SN号", style)
    ws.write(0, 21, "厂商", style)
    ws.write(0, 22, "质保年限", style)
    ws.write(0, 23, "SLA级别", style)
    ws.write(0, 24, "上架时间", style)
    ws.write(0, 25, "上次修改时间", style)
    ws.write(0, 26, "主要维护人", style)
    ws.write(0, 27, "备份维护人", style)
    ws.write(0, 28, "备注", style)
    # 生成主机列表或QuerySet
    if export == "true":
        if host_id_all:
            host_find = []
            for host_id in host_id_all:
                host_item = Host.objects.get(pk=host_id)
                if host_item:
                    host_find.append(host_item)
    elif export == "all":
        host_find = Host.objects.all()
    # 写入主机信息数据
    excel_row = 1
    for host in host_find:
        host_type_this = ''
        host_status_this = ''
        os_type_this = ''
        business_this = ''
        datacenter_this = ''
        cabinet_this = ''
        cluster_list = []
        # 生成出主机类型别名
        for htype in Host.HOST_TYPE_CHOICES:
            if htype[0] == host.host_type:
                host_type_this = htype[1]
        # 生成出主机状态别名
        for hstatus in Host.HOST_STATUS_CHOICES:
            if hstatus[0] == host.host_status:
                host_status_this = hstatus[1]
        # 生成出操作系统类型别名
        for otype in Host.OS_TYPE_CHOICES:
            if otype[0] == host.os_type:
                os_type_this = otype[1]
        # 生成业务名称
        if host.business:
            business_this = host.business.name
        # 生成数据中心名称
        if host.datacenter:
            datacenter_this = host.datacenter.name
        # 生成机柜名称
        if host.cabinet:
            cabinet_this = host.cabinet.name
        # 生成集群名称的字符串，以逗号间隔
        for cluster in host.cluster.all():
            cluster_list.append(cluster)
        cluster_this = ",".join(str(c) for c in cluster_list) 

        ws.write(excel_row, 0, host_type_this, style)
        ws.write(excel_row, 1, host.host_name, style)
        ws.write(excel_row, 2, host.ipmi_ip, style)
        ws.write(excel_row, 3, host.host_innerip, style)
        ws.write(excel_row, 4, host.host_outerip, style)
        ws.write(excel_row, 5, host.other_ip, style)
        ws.write(excel_row, 6, host.mac_addr, style)
        ws.write(excel_row, 7, host.cpu_module, style)
        ws.write(excel_row, 8, host.cpu_num, style)
        ws.write(excel_row, 9, host.cpu_core_count, style)
        ws.write(excel_row, 10, host.mem_mb, style)
        ws.write(excel_row, 11, host.disk_gb, style)
        ws.write(excel_row, 12, os_type_this, style)
        ws.write(excel_row, 13, host.os_name, style)
        ws.write(excel_row, 14, host.os_bit, style)
        ws.write(excel_row, 15, business_this, style)
        ws.write(excel_row, 16, cluster_this, style)
        ws.write(excel_row, 17, datacenter_this, style)
        ws.write(excel_row, 18, cabinet_this, style)
        ws.write(excel_row, 19, host_status_this, style)
        ws.write(excel_row, 20, host.sn, style)
        ws.write(excel_row, 21, host.manufacturer, style)
        ws.write(excel_row, 22, host.service_term, style)
        ws.write(excel_row, 23, host.sla, style)
        ws.write(excel_row, 24, host.created_time, date_format)
        ws.write(excel_row, 25, host.modified_time, date_format)
        ws.write(excel_row, 26, host.manager, style)
        ws.write(excel_row, 27, host.bak_manager, style)
        ws.write(excel_row, 28, host.comment, style)
        excel_row += 1

    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    file_name = 'sunshine_cmdb_' + now + '.xls'
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    response = HttpResponse(bio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename='+file_name
    response.write(bio.getvalue())
    return response

def host_import(request):
    """ 
    该函数用来处理导入的主机信息文件
    """
    status = 0
    if request.method == "POST":
        f = request.FILES.get('host_import')
        wb = xlrd.open_workbook(filename=None, file_contents=f.read())
        table = wb.sheets()[0]
        nrows = table.nrows  #行数
        ncole = table.ncols  #列数
        # 简单判断表头是否符合格式要求
        title_data = table.row_values(0)
        if title_data[0] == "主机类型" and title_data[15] == "所属业务" and \
        title_data[28] == "备注":
            pass    
        else:
            print("Excel title Error!")
            return render(request, 'cmdb/host_import.html', {'status': 2})
        
        # 尝试将Excel每一行信息写入数据库
        try:
            for line in range(1, nrows):
                row_data = table.row_values(line)  #一行的数据
                try:
                    host = Host.objects.get(host_innerip=row_data[3])
                except Exception as msg:
                    host = Host()
                    host.host_innerip = row_data[3]
                # 存储主机类型信息
                host_type_this = ''
                for x, v in Host.HOST_TYPE_CHOICES:
                    if v == row_data[0]:
                        host_type_this = x
                host.host_type = host_type_this
                # 存储主机状态信息
                host_status_this = ''
                for x, v in Host.HOST_STATUS_CHOICES:
                    if v == row_data[19]:
                        host_status_this = x
                host.host_status = host_status_this
                # 存储操作系统类型信息
                os_type_this = ''
                for x, v in Host.OS_TYPE_CHOICES:
                    if v == row_data[12]:
                        os_type_this = x
                host.os_type = os_type_this
                # 存储所属业务信息
                if row_data[15]:
                    try:
                        bus = Business.objects.get(name=row_data[15])
                        host.business_id = bus.id
                    except Exception as e:
                        print(e)
                        print("Business import Error")
                # 存储所属数据中心信息
                if row_data[17]:
                    try:
                        dc = Datacenter.objects.get(name=row_data[17])
                        host.datacenter_id = dc.id
                    except Exception as e:
                        print(e)
                        print("Datacenter import Error")
                # 存储所属机柜信息
                if row_data[18]:
                    try:
                        cab = Cabinet.objects.get(name=row_data[18])
                        host.cabinet_id = cab.id
                    except Exception as e:
                        print(e)
                        print("Business import Error")
                host.host_name = row_data[1]
                host.ipmi_ip = str(row_data[2])
                host.host_outerip = str(row_data[4])
                host.other_ip = str(row_data[5])
                host.mac_addr = row_data[6]
                host.cpu_module = row_data[7]
                host.cpu_num = row_data[8]
                host.cpu_core_count = row_data[9]
                host.mem_mb = row_data[10]
                host.disk_gb = row_data[11]
                host.os_name = row_data[13]
                host.os_bit = row_data[14]
                host.sn = row_data[20]
                host.manufacturer = row_data[21]
                host.service_term = row_data[22]
                host.sla = row_data[23]
                # 将Excel时间戳转换为标准时间格式
                c_time = datetime.datetime(*xldate_as_tuple(row_data[24],0))
                host.created_time = c_time.strftime("%Y-%m-%d %H:%M:%S")
                # 将Excel时间戳转换为标准时间格式
                m_time = datetime.datetime(*xldate_as_tuple(row_data[25],0))
                host.modified_time = m_time.strftime("%Y-%m-%d %H:%M:%S")
                host.manager = row_data[26]
                host.bak_manager = row_data[27]
                host.comment = row_data[28]
                host.save()
                # 存储所属集群信息,Host与Cluster为多对多字段，必须save()之后再添加
                if row_data[16]:
                    for clu_name in row_data[16].split(','):
                        try:
                            clu = Cluster.objects.get(name=clu_name)
                            host.cluster.add(clu)
                        except Exception as e:
                            print(e)
                            print("Cluster import Error")
            status = 1
        except Exception as e:
            print(e)
            print("Host import Failed")
            status = 2
    return render(request, 'cmdb/host_import.html', {'status': status})
