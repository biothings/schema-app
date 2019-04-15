'''
    Registry Handler Tester
'''

from tornado.escape import json_encode
from tornado.web import create_signed_value

from biothings.tests import BiothingsTestCase, TornadoTestServerMixin
from biothings.tests.helper import equal
from discovery.tests import SCHEMAS, run


class DiscoveryAPITest(TornadoTestServerMixin, BiothingsTestCase):
    '''
        The tester will start its own tornado server
        existing 'discovery' will be overwitten
    '''
    __test__ = True

    api = '/api'

    @classmethod
    def setUpClass(cls):

        def cookie_header(username):
            cookie_name, cookie_value = 'user', {'login': username}
            secure_cookie = create_signed_value(
                cls.settings.COOKIE_SECRET,
                cookie_name,
                json_encode(cookie_value))
            return {'Cookie': '='.join((cookie_name, secure_cookie.decode()))}

        cls.auth_user = cookie_header('namespacestd')
        cls.evil_user = cookie_header('villain')

    def test_01(self):
        ''' HTTP GET /registry/__id__ '''
        res = self.request('registry/'+SCHEMAS[0].meta.id).json()
        equal('Retrived URL', res['_meta']['url'],
              'Source URL', SCHEMAS[0].to_dict()['_meta']['url'])

    def test_02(self):
        ''' HTTP POST /registry _ document creation '''
        doc = {'url': 'http://example.com/',
               'slug': 'com',
               'props': 'ebay'}
        self.request('registry', method='POST', json=doc, headers=self.auth_user, expect_status=201)
        self.query(q='ebay', expect_hits=False)
        self.query(q='com')

    def test_03(self):
        ''' HTTP POST /registry _ document modification '''
        doc = {'url': 'http://example.org/',
               'slug': 'org',
               'clses': ['costco', 'MTS']}
        self.request('registry', method='POST', json=doc, headers=self.auth_user, expect_status=201)
        self.query(q='MTS')

        self.query(q='orange', expect_hits=False)
        doc['slug'] = 'orange'
        self.request('registry', method='POST', json=doc, headers=self.auth_user)
        self.query(q='orange')

    def test_04(self):
        ''' HTTP DELETE /registry/__id__ '''
        res = self.query(q='d2h')
        _id = res['hits'][0]['_id']
        self.request('registry/'+_id, method='DELETE', headers=self.auth_user)
        self.query(q='d2h', expect_hits=False)

    def test_05(self):
        ''' HTTP PUT /registry/__id__ Update '''
        self.query(q='dev')
        self.query(q='devil', expect_hits=False)
        data = {'slug': 'devil'}
        res = self.request('registry/' + SCHEMAS[0].meta.id, method='PUT',
                           json=data, headers=self.auth_user).json()
        assert 'success' in res
        self.query(q='devil')
        self.query(q='dev', expect_hits=False)

    def test_06(self):
        ''' HTTP PUT /registry/__id__ Validation '''
        # Bad Request (No valid updatable field provided)
        self.request('registry/' + SCHEMAS[0].meta.id, method='PUT', json={'pwd': 'None'},
                     headers=self.auth_user, expect_status=400)
        # Forbidden (url is not an updatable field)
        self.request('registry/' + SCHEMAS[0].meta.id, method='PUT', json={'url': 'valid_url'},
                     headers=self.auth_user, expect_status=403)
        # Not Found (Document id does not exist)
        self.request('registry/666', method='PUT', json={'slug': 'new'},
                     headers=self.auth_user, expect_status=404)

    def test_07(self):
        ''' HTTP PUT /registry/__id__ Authentication '''
        # Unauthorized (Secured cookie is not provided)
        self.request('registry/' + SCHEMAS[0].meta.id, method='PUT', json={'slug': 'new'},
                     expect_status=401)
        # Forbidden (Document not owned by current user)
        self.request('registry/' + SCHEMAS[0].meta.id, method='PUT', json={'slug': 'new'},
                     headers=self.evil_user, expect_status=403)


if __name__ == '__main__':
    run('Registry Handler Test')
