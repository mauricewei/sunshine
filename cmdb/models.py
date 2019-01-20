from django.db import models


class Business(models.Model):
    LIFECYCLE_CHOICES = (
        ('online', '已上线'),
        ('testing', '测试中'),
        ('terminal', '已终止'),
    )
    name = models.CharField('业务名称', max_length=60)
    lifecycle = models.CharField(
        '生命周期',
        max_length=60,
        choices=LIFECYCLE_CHOICES,
        blank=True,
    )
    manager = models.CharField('运维人员', max_length=60, blank=True)
    product_manager = models.CharField('产品经理', max_length=60, blank=True)
    tester = models.CharField('测试人员', max_length=60, blank=True)
    developer = models.CharField('开发人员', max_length=60, blank=True)
    operator = models.CharField('操作人员', max_length=60, blank=True)

    def __str__(self):
        return self.name


class Model(models.Model):
    STATUS = (
        ('open', '开启'),
        ('closed', '关闭'),
    )
    name = models.CharField('模块名称', max_length=60)
    desc = models.TextField('描述', blank=True)
    status = models.CharField(
        '服务状态',
        max_length=60,
        choices=STATUS,
        blank=True,
    )
    comment = models.TextField('备注', blank=True)
    business = models.ForeignKey(
        Business,
        verbose_name='所属业务',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Cluster(models.Model):
    name = models.CharField('集群名称', max_length=60)
    desc = models.TextField('描述', blank=True)
    manager = models.CharField('主要维护人', max_length=60, blank=True)
    bak_manager = models.CharField('备份维护人', max_length=60, blank=True)
    business = models.ForeignKey(
        Model,
        verbose_name='所属模块',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Datacenter(models.Model):
    identification = models.CharField("机房标识", max_length=255, unique=True)
    name = models.CharField("机房名称", max_length=255, unique=True)
    address = models.CharField("机房地址", max_length=100, blank=True)
    tel = models.CharField("机房电话", max_length=30, blank=True)
    manager = models.CharField("机房管理员", max_length=30, blank=True)
    mobile_phone = models.CharField("移动电话", max_length=30, blank=True)
    cabinet_info = models.CharField("机柜信息", max_length=30, blank=True)
    ip_range = models.CharField("IP范围", max_length=30, blank=True)
    bandwidth = models.CharField("接入带宽", max_length=30, blank=True)
    comment = models.TextField("备注", blank=True)

    def __str__(self):
        return self.name


class Cabinet(models.Model):
    name = models.CharField("机柜位置", max_length=60)
    desc = models.TextField("描述", blank=True)
    datacenter = models.ForeignKey(
        Datacenter,
        verbose_name="所在机房",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Host(models.Model):
    HOST_STATUS_CHOICES = (
        ('free', '空闲'),
        ('stoppage', '故障'),
        ('inuse', '使用中'),
    )
    OS_TYPE_CHOICES = (
        ('linux', 'Linux'),
        ('windows', 'Windows'),
    )
    SLA_CHOICES = (
        ('L1', '一级'),
        ('L2', '二级'),
        ('L3', '三级'),
    )
    HOST_TYPE_CHOICES = (
        ('phy', '物理机'),
        ('vir', '虚拟机'),
        ('container', '容器'),
        ('net', '网络设备'),
        ('safe', '安全设备'),
        ('other', '其他'),
    )

    host_type = models.CharField(
        "主机类型",
        max_length=60,
        choices=HOST_TYPE_CHOICES,
        blank=True,
    )
    host_name = models.CharField('主机名或fqdn名', max_length=100)
    ipmi_ip = models.GenericIPAddressField(
        'IPMI地址',
        max_length=20,
        null=True,
        blank=True,
    )
    host_innerip = models.GenericIPAddressField(
        '管理IP地址', max_length=20, unique=True)
    host_outerip = models.GenericIPAddressField(
        '外网IP地址',
        max_length=20,
        null=True,
        blank=True,
    )
    other_ip = models.CharField("其它IP", max_length=60, blank=True)
    mac_addr = models.CharField('管理网MAC地址', max_length=60, blank=True)
    cpu_module = models.CharField('CPU型号', max_length=100, blank=True)
    cpu_num = models.IntegerField('CPU个数', blank=True, null=True)
    cpu_core_count = models.IntegerField('CPU逻辑核心数', blank=True, null=True)
    mem_mb = models.IntegerField('内存大小(MB)', blank=True, null=True)
    disk_gb = models.IntegerField('磁盘大小(GB)', blank=True, null=True)
    os_type = models.CharField(
        '操作系统类型',
        max_length=60,
        choices=OS_TYPE_CHOICES,
        blank=True,
        default='linux',
    )
    os_name = models.CharField('操作系统名称', max_length=60, blank=True)
    os_bit = models.IntegerField('操作系统位数', blank=True, null=True)
    business = models.ForeignKey(
        Business,
        verbose_name='所属业务',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cluster = models.ManyToManyField(
        Cluster,
        verbose_name='所属集群',
        blank=True,
    )
    datacenter = models.ForeignKey(
        Datacenter,
        verbose_name='所属数据中心',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cabinet = models.ForeignKey(
        Cabinet,
        verbose_name='所属机柜',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    host_status = models.CharField(
        '主机状态',
        max_length=60,
        choices=HOST_STATUS_CHOICES,
        blank=True,
    )
    sn = models.CharField('SN号', max_length=60, blank=True)
    manufacturer = models.CharField('厂商', max_length=100, blank=True)
    service_term = models.IntegerField('质保年限', blank=True, null=True)
    sla = models.CharField(
        'SLA级别',
        max_length=60,
        choices=SLA_CHOICES,
        blank=True,
    )
    created_time = models.DateTimeField('上架时间', null=True, blank=True)
    modified_time = models.DateTimeField('上次修改时间', auto_now_add=True)
    manager = models.CharField('主要维护人', max_length=60, blank=True)
    bak_manager = models.CharField('备份维护人', max_length=60, blank=True)
    comment = models.TextField('备注', blank=True)

    def __str__(self):
        return self.host_name
