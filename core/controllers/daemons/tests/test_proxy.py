'''
test_proxy.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import urllib2
import unittest

from nose.plugins.attrib import attr

from core.data.url.extended_urllib import ExtendedUrllib
from core.controllers.misc.temp_dir import create_temp_dir
from core.controllers.daemons.proxy import Proxy, w3afProxyHandler


@attr('moth')
class TestProxy(unittest.TestCase):

    IP = '127.0.0.1'

    def setUp(self):
        # Start the proxy server
        create_temp_dir()

        self._proxy = Proxy(self.IP, 0, ExtendedUrllib(), w3afProxyHandler)
        self._proxy.start()
        self._proxy.wait_for_start()
        
        port = self._proxy.get_port()
        
        # Build the proxy opener
        proxy_handler = urllib2.ProxyHandler({"http": "http://%s:%s"
                                              % (self.IP, port)})
        self.proxy_opener = urllib2.build_opener(proxy_handler,
                                                 urllib2.HTTPHandler)

    def test_do_req_through_proxy(self):
        resp_body = self.proxy_opener.open('http://moth').read()

        # Basic check
        self.assertTrue(len(resp_body) > 0)

        # Get response using the proxy
        proxy_resp = self.proxy_opener.open('http://moth')
        # Get it without any proxy
        direct_resp = urllib2.urlopen('http://moth')

        # Must be equal
        self.assertEqual(direct_resp.read(), proxy_resp.read())

        # Have to remove the Date header because in some cases they differ because
        # one request was sent in second X and the other in X+1, which makes the
        # test fail
        direct_resp_headers = dict(direct_resp.info())
        proxy_resp_headers = dict(proxy_resp.info())
        del direct_resp_headers['date']
        del proxy_resp_headers['date']
        self.assertEqual(direct_resp_headers, proxy_resp_headers)

    def test_do_SSL_req_through_proxy(self):
        resp_body = self.proxy_opener.open('https://moth').read()

        # Basic check
        self.assertTrue(len(resp_body) > 0)

        # Get response using the proxy
        proxy_resp = self.proxy_opener.open('https://moth')
        # Get it without any proxy
        direct_resp = urllib2.urlopen('https://moth')

        # Must be equal
        self.assertEqual(direct_resp.read(), proxy_resp.read())

        # Have to remove the Date header because in some cases they differ because
        # one request was sent in second X and the other in X+1, which makes the
        # test fail
        direct_resp_headers = dict(direct_resp.info())
        proxy_resp_headers = dict(proxy_resp.info())
        del direct_resp_headers['date']
        del proxy_resp_headers['date']
        self.assertEqual(direct_resp_headers, proxy_resp_headers)

    def test_proxy_req_ok(self):
        '''Test if self._proxy.stop() works as expected. Note that the check
        content is the same as the previous check, but it might be that this
        check fails because of some error in start() or stop() which is run
        during setUp and tearDown.'''
        # Get response using the proxy
        proxy_resp = self.proxy_opener.open('http://moth').read()
        # Get it the other way
        resp = urllib2.urlopen('http://moth').read()
        # They must be very similar
        self.assertEqual(resp, proxy_resp)
    
    def test_stop_no_requests(self):
        '''Test what happens if I stop the proxy without sending any requests
        through it'''
        # Note that the test is completed by self._proxy.stop() in tearDown
        pass

    def test_stop_stop(self):
        '''Test what happens if I stop the proxy twice.'''
        # Note that the test is completed by self._proxy.stop() in tearDown
        self._proxy.stop()
    
    def tearDown(self):
        # Shutdown the proxy server
        self._proxy.stop()
