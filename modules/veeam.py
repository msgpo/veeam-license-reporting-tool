#!/usr/bin/env python
import base64
import xmltodict
import urllib2
import ssl

class VeeamConnector(object):
    def __init__(self, enterprise_server):
        self.veeam_hostname = enterprise_server['hostname']
        self.veeam_username = enterprise_server['username']
        self.veeam_password = enterprise_server['password']
        self.veeam_url = 'https://' + self.veeam_hostname + ':9398/api/'

        self.urllib_timeout = 30 # seconds
        self.veeam_task_timeout = 20 # seconds

        self.ssl_context_enabled = False

        try:
            self.ssl_context = ssl._create_unverified_context()
            self.ssl_context_enabled = True
        except AttributeError:
            pass

        (self.veeam_session_id, self.session_id_decoded) = self._RequestVeeamSessionId()

    def _RequestVeeamSessionId(self):
        url = self.veeam_url + 'sessionMngr/?v=v1_3'
        login_base64 = base64.b64encode('%s:%s' % (self.veeam_username, self.veeam_password))
        header = {
            'Authorization': 'Basic %s' % (login_base64),
            'X-Requested-With' : 'urllib2'
        }
        request = urllib2.Request(url = url, data = '', headers = header) # data must be something to be a post
        request.get_method = lambda: 'POST'
        if self.ssl_context_enabled:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)
        else:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout)
        session_id = response.info().getheader('X-RestSvcSessionId')
        session_id_decoded = base64.b64decode(session_id)
        return session_id, session_id_decoded

    def _RequestVeeamSessionDelete(self):
        url = self.veeam_url + 'logonSessions/' + self.session_id_decoded
        header = {
            'X-RestSvcSessionId': self.veeam_session_id,
            'X-Requested-With' : 'urllib2'
        }
        request = urllib2.Request(url = url, data = '', headers = header)
        request.get_method = lambda: 'DELETE'
        if self.ssl_context_enabled:
            urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)
        else:
            urllib2.urlopen(request, timeout = self.urllib_timeout)
        return

    def _RequestVeeamData(self, url, data, method, add_full_url = True):
        if method == 'post':
            method = 'POST'
            header = {
            'X-RestSvcSessionId': self.veeam_session_id,
            'Content-Type': 'text/xml',
            'X-Requested-With' : 'urllib2'
        }
        elif method == 'delete':
            method = 'DELETE'
            data = ''
            header = {
            'X-RestSvcSessionId': self.veeam_session_id,
            'X-Requested-With' : 'urllib2'
        }
        else:
            method = 'GET'
            data = ''
            header = {
            'X-RestSvcSessionId': self.veeam_session_id,
            'Content-Type': 'text/xml',
            'X-Requested-With' : 'urllib2'
        }

        if add_full_url:
            url = self.veeam_url + url

        request = urllib2.Request(url = url, data = data, headers = header)
        request.get_method = lambda: method
        if self.ssl_context_enabled:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)
        else:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout)
        if method == 'DELETE':
            ret = response.read()
        else:
            ret = self._ParseXmlToDict(response.read())
        code = response.getcode()
        headers = response.info()
        return headers, code, ret

    def _GetVeeamVmsSummaryOverview(self):
        (headers, code, ret) = self._RequestVeeamData(url = 'reports/summary/vms_overview', data = '', method = 'get')
        data_return = []
        for summary in ret:
            if summary == 'VmsOverviewReportFrame':
                summary = {
                    'ProtectedVms': int(self._CheckIfKeyExistsInDict(ret[summary], 'ProtectedVms')),
                    'BackedUpVms': int(self._CheckIfKeyExistsInDict(ret[summary], 'BackedUpVms')),
                    'ReplicatedVms': int(self._CheckIfKeyExistsInDict(ret[summary], 'ReplicatedVms')),
                    'RestorePoints': int(self._CheckIfKeyExistsInDict(ret[summary], 'RestorePoints')),
                    'FullBackupPointsSize': int(self._CheckIfKeyExistsInDict(ret[summary], 'FullBackupPointsSize')),
                    'IncrementalBackupPointsSize': int(self._CheckIfKeyExistsInDict(ret[summary], 'IncrementalBackupPointsSize')),
                    'ReplicaRestorePointsSize': int(self._CheckIfKeyExistsInDict(ret[summary], 'ReplicaRestorePointsSize')),
                    'SourceVmsSize': int(self._CheckIfKeyExistsInDict(ret[summary], 'SourceVmsSize')),
                    'SuccessBackupPercents': int(self._CheckIfKeyExistsInDict(ret[summary], 'SuccessBackupPercents')),
                    'ProtectedVmsReportLink': self._CheckIfKeyExistsInDict(ret[summary], 'ProtectedVmsReportLink')
                }
                data_return.append(summary)

        return data_return

    def _GetVeeamProcessedVmsSummary(self):
        (headers, code, ret) = self._RequestVeeamData(url = 'reports/summary/processed_vms', data = '', method = 'get')
        data_return = []
        print ret
        o = self._CheckIfKeyExistsInDict(ret, 'ProcessedVmsReportFrame')
        if o:
            t = self._CheckIfKeyExistsInDict(o, 'Day')
            print t
            print 'robin'

        for processed_vms_report in ret:
            test = self._CheckIfKeyExistsInDict(ret, 'ProcessedVmsReportFrame')
            print test
            #if len(processed_vms_report['ProcessedVmsReportFrame']) > 0:
            #    for test in processed_vms_report['ProcessedVmsReportFrame']:
            #        print test

            #if summary == 'ProcessedVmsReportFrame':
                #summary = {
                #    'ProtectedVms': int(self._CheckIfKeyExistsInDict(ret[summary], 'ProtectedVms')),
                #    'BackedUpVms': int(self._CheckIfKeyExistsInDict(ret[summary], 'BackedUpVms')),
                #    'ReplicatedVms': int(self._CheckIfKeyExistsInDict(ret[summary], 'ReplicatedVms')),
                #    'RestorePoints': int(self._CheckIfKeyExistsInDict(ret[summary], 'RestorePoints')),
                #    'FullBackupPointsSize': int(self._CheckIfKeyExistsInDict(ret[summary], 'FullBackupPointsSize')),
                #    'IncrementalBackupPointsSize': int(self._CheckIfKeyExistsInDict(ret[summary], 'IncrementalBackupPointsSize')),
                #    'ReplicaRestorePointsSize': int(self._CheckIfKeyExistsInDict(ret[summary], 'ReplicaRestorePointsSize')),
                #    'SourceVmsSize': int(self._CheckIfKeyExistsInDict(ret[summary], 'SourceVmsSize')),
                #    'SuccessBackupPercents': int(self._CheckIfKeyExistsInDict(ret[summary], 'SuccessBackupPercents')),
                #    'ProtectedVmsReportLink': self._CheckIfKeyExistsInDict(ret[summary], 'ProtectedVmsReportLink')
                #}
                #data_return.append(summary)

                #print summary['ProcessedVmsReportFrame']['Day']

            #print summary

        return data_return

    def _CalculateProtectedVms(self):
        summary = self._GetVeeamVmsSummaryOverview()

        # return false if list is empty
        if not summary:
            return False
        else:
            protected_vms = 0
            for sum in summary:
                protected_vms += sum['ProtectedVms']

            return protected_vms


    def _CheckIfKeyExistsInDict(self, data, key):
        if not data:
            return False
        if key in data:
            return data[key]
        else:
            return False

    def _ParseXmlToDict(self, xml):
        contents = xmltodict.parse(xml, attr_prefix = '', dict_constructor = dict)
        return contents
