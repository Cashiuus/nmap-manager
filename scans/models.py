import os
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _

from .choices import STATE_CHOICES


def set_files_path(instance, filename):
    """ This'll be appended to your MEDIA_ROOT as the save directory. """
    # one option is also to create date-based sub-dirs:
    # upload = models.FileField(upload_to='uploads/%Y/%m/%d/')
    # results in files saved to: MEDIA_ROOT/2021/01/09/
    # used in this function, it'd be:
    return 'scan_files/%Y/{0}'.format(filename)


class Scan(models.Model):
    #id = models.AutoField(primary_key=True)
    name = models.CharField(_('name'), max_length=50, unique_for_date='date_created')
    arguments = models.TextField()
    scan_start = models.DateTimeField(_('Scan Start'))
    scan_end = models.DateTimeField(_('Scan End'))
    duration = models.DurationField()
    nmap_version = models.CharField(max_length=20)
    xml_version = models.CharField(max_length=20)
    count_live_hosts = models.IntegerField(_('Live Hosts'))
    scan_file = models.FileField(_('scan file'), upload_to=set_files_path,
                                 help_text='Nmap XML file')
    scan_md5 = models.CharField(_('MD5'), max_length=32, 
                                help_text='MD5 hash of the XML file used for this scan record')
    notes = models.TextField(blank=True, default='')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_duration(self):
        return self.scan_end - self.scan_start

    def save(self, *args, **kwargs):
        self.duration = self.scan_end - self.scan_start
        super(Scan, self).save(*args, **kwargs)

    class Meta:
        ordering = ('id',)
        verbose_name = _('scan')
        verbose_name_plural = _('scans')
    
    def __str__(self):
        return self.name


class HostManager(models.Manager):
    """ Custom objects manager for the Host class to return only live hosts by default. """
    # Get a count of live hosts: Host.objects.livehosts().count()
    def livehosts(self, **kwargs):
        return self.filter(state=Host.LIVE)


class Host(models.Model):
    hostname = models.CharField(max_length=100, blank=True, default='')
    hostname_type = models.CharField(_('Host Type'), max_length=50, blank=True, default='')
    ip_address = models.GenericIPAddressField(_('IP Address'), protocol='IPv4')
    mac_address = models.CharField(_('MAC Address'), max_length=30, blank=True, default='')
    scan_id = models.ForeignKey('Scan', on_delete=models.PROTECT, verbose_name='Scan ID')
    assessment_status_1 = models.CharField(_('Test Status'), max_length=50, default='New')
    os_name = models.CharField(max_length=100, blank=True, default='')
    os_family = models.CharField(max_length=100, blank=True, default='')
    os_vendor = models.CharField(max_length=100, blank=True, default='')
    os_gen = models.CharField(max_length=100, blank=True, default='')
    os_type = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=2, 
                             choices=STATE_CHOICES,
                             help_text='Host is live or down')
    state_reason = models.CharField(_('state reason'), max_length=100, blank=True, default='')
    # TODO: Come up with categories we care about, e.g. workstation, server, printer, OT...
    category = models.CharField(max_length=100, blank=True, default='')
    criticality = models.SmallIntegerField(_('Asset Criticality'), default=50,
                                           help_text='Asset importance/criticality score 1-100')
    date_discovered = models.DateTimeField(auto_now=True, help_text='Date first seen/scanned')
    date_last_seen = models.DateTimeField(auto_now=True, help_text='Date last seen/scanned')
    count_scanned = models.SmallIntegerField(help_text='Number of times this host has been scanned')

    def high_value_target(self):
        return self.asset_criticality >= 75

    # Adding a customized default objects manager for this class. Access it like this:
    #   Host.objects.count()
    #   Host.objects.livehosts().count()
    # If enabled, you must always set the original default first in the sequence to avoid weird query errors
    # So, if you uncomment, ensure you uncomment both lines below, not just one or the other
    #objects = models.Manager()
    #objects = HostManager()

    class Meta:
        ordering = ('ip_address',)
        verbose_name = _('host')
        verbose_name_plural = _('hosts')
    
    def __str__(self):
        return self.ip_address


class Service(models.Model):
    """ A remote service that represents an open port with a listening service tied back to its host. """
    #id = models.PrimaryKey
    port_number = models.IntegerField(_('port'))
    port_proto = models.CharField(_('protocol'), max_length=10)
    service_name = models.CharField(_('service name'), max_length=255, blank=True, default='')
    product_name = models.CharField(_('product name'), max_length=255, blank=True, default='')
    product_version = models.CharField(_('product version'), max_length=50, blank=True, default='')
    product_extrainfo = models.TextField(blank=True, default='',
                                         help_text='Extra service info and/or raw scan output')
    host_id = models.ForeignKey('Host', on_delete=models.CASCADE, verbose_name='Host ID')
    scan_id = models.ForeignKey('Scan', on_delete=models.CASCADE, verbose_name='Scan ID')
    assessment_status_1 = models.CharField(_('Test Status'), max_length=50, default='New')
    state = models.CharField(_('state'), max_length=2, choices=STATE_CHOICES)
    state_reason = models.CharField(_('state reason'), max_length=100, blank=True, default='')
    # TODO: List out service/port categories we care about: remote access, file transfers, etc
    category = models.CharField(max_length=100, blank=True, default='')
    attack_value = models.SmallIntegerField(_('attack value'), default=0,
                                            help_text='Attack value score 1-100')
    notes = models.TextField(blank=True, default='')
    date_discovered = models.DateTimeField(auto_now=True, help_text='Date first seen/scanned')
    date_last_seen = models.DateTimeField(auto_now=True, help_text='Date last seen/scanned')
    count_scanned = models.SmallIntegerField(default=1, help_text='Number of times this host & port has been scanned')

    class Meta:
        ordering = ('port_number',)
        verbose_name = _('service')
        verbose_name_plural = _('services')
    
    def __str__(self):
        return self.port_number



class ScanPolicy(models.Model):
    name = models.CharField(_('name'), max_length=75, unique=True)
    scan_type = models.CharField(_('scan type'), max_length=50, default='Discovery')
    arguments = models.TextField(_('arguments'), help_text='nmap scan command arguments')
    output_filename = models.CharField(_('output filename'), max_length=150, default='nmap-scan-date.xml')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('scan_type', 'name')
        verbose_name = _('scan policy')
        verbose_name_plural = _('scan policies')
    
    def __str__(self):
        return self.name


# class ScanJob(models.Model):
#     name = models.CharField(max_length=75)
#     assigned_scan_id = models.ForeignKey('Scan', help_text='The original scan this job was created from to setup continuous scanning')
#     assigned_policy = models.ForeignKey('ScanPolicy', help_text='The scan policy to use, if different from the original scan settings')
#     execution_interval_numer = models.SmallIntegerField(help_text='Interval number for days/hours/etc.')
#     execution_interval_period = models.CharField(help_text='Choose day, week, month')
#     # NOTE: Build capability on website to upload a file list of target scope that is parsed to this field.
#     target_scope = models.TextField(_('target scope'))
#     date_last_execution = models.DateTimeField()
#     date_created = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(help_text='Is the job running, errored, enabled, or disabled')
#     notes = models.TextField()

#     class Meta:
#         ordering = ('id',)
#         verbose_name = _('scan')
#         verbose_name_plural = _('scans')
    
#     def __str__(self):
#         return self.name

# class Network(models.Model):
#     network_cidr = models.
#     date_created = models.DateTimeField()
#     date_updated = models.DateTimeField(auto_now=True)
#     sitecode = models.CharField(max_length=5)
#     count_scanned = models.SmallIntegerField(help_text='Number of times this host has been scanned')
#     notes = models.TextField()

#     class Meta:
#         ordering = ('network_cidr',)
#         verbose_name = _('network')
#         verbose_name_plural = _('networks')
    
#     def __str__(self):
#         return self.network_cidr
