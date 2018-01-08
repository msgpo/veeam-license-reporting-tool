#!/usr/bin/env python
import ssl
import urllib2
import json

class Baashunter(object):
    def __init__(self, baashunter_server):
        self.baashunter_hostname = baashunter_server['hostname']
        self.baashunter_username = baashunter_server['username']
        self.baashunter_password = baashunter_server['password']

        self.baashunter_url = 'https://' + self.baashunter_hostname + '/v1/'

        self.urllib_timeout = 30 # seconds

        self.ssl_context_enabled = False
        try:
            self.ssl_context = ssl._create_unverified_context()
            self.ssl_context_enabled = True
        except AttributeError:
            pass

        self.baashunter_token = self._RequestBaashunterAuthToken()


    def _RequestBaashunterAuthToken(self):
        url = self.baashunter_url + 'auth/login?username=%s&password=%s' % (self.baashunter_username, self.baashunter_password)
        header = {
            'X-Requested-With' : 'urllib2'
        }
        request = urllib2.Request(url = url, data = '', headers = header) # data must be something to be a post
        request.get_method = lambda: 'POST'
        if self.ssl_context_enabled:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)
        else:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout)
        auth_token = json.loads(response.read())['token']
        return auth_token

    def _RequestBaashunterSessionDelete(self):
        url = self.baashunter_url + 'auth/logout'
        header = {
            'Authorization': '%s' % (self.baashunter_token),
            'X-Requested-With' : 'urllib2'
        }

        request = urllib2.Request(url = url, data = 'd', headers = header) # data must be something to be a post
        request.get_method = lambda: 'POST'
        if self.ssl_context_enabled:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)
        else:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout)

    def _RequestBaashunterVmstat(self):
        header = {
            'Authorization': self.baashunter_token,
            'Content-Type': 'application/json',
            'X-Requested-With' : 'urllib2'
        }
        request = urllib2.Request(url = self.baashunter_url + 'statistics/vmstat', data = '', headers = header)
        request.get_method = lambda: 'GET'
        if self.ssl_context_enabled:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout, context = self.ssl_context)
        else:
            response = urllib2.urlopen(request, timeout = self.urllib_timeout)
        data = json.loads(response.read())
        code = response.getcode()
        headers = response.info()
        
        return data['vms']
