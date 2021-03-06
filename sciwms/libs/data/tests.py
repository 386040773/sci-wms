"""
COPYRIGHT 2010 RPS ASA

This file is part of SCI-WMS.

    SCI-WMS is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SCI-WMS is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with SCI-WMS.  If not, see <http://www.gnu.org/licenses/>.

This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
from time import sleep

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
import django.contrib.auth.hashers as hashpass

from sciwms.apps.wms.models import Dataset, Group, Server
import sciwms.libs.data.grid_init_script as grid_cache

resource_path = os.path.join(settings.PROJECT_ROOT, 'apps', 'wms', 'resources')
cache_path = os.path.join(settings.PROJECT_ROOT, 'apps', 'wms', "testcache")
if not os.path.exists(cache_path):
    os.makedirs(cache_path)


def remove_cache():
    try:
        os.unlink(os.path.join(cache_path, "test.nc"))
        os.unlink(os.path.join(cache_path, "test_nodes.idx"))
        os.unlink(os.path.join(cache_path, "test_nodes.dat"))
    except:
        pass
    try:
        os.unlink(os.path.join(cache_path, "test_cells.idx"))
        os.unlink(os.path.join(cache_path, "test_cells.dat"))
        os.unlink(os.path.join(cache_path, "test.domain"))
    except:
        pass


def wait_on_cache():
    #self.client.get('/update')
    grid_cache.check_topology_age()
    c = 0
    while (not os.path.exists(os.path.join(cache_path, "test.nc"))) and (c < 10):
        sleep(3)
        print "Waiting on NC file..."
        c += 1
        pass


def wait_on_domain():
    c = 0
    while (not os.path.exists(os.path.join(cache_path, "test.domain"))) and (c < 10):
        sleep(3)
        print "Waiting on Domain file..."
        c += 1
        pass


def add_server():
    s = Server.objects.create()
    s.save()


def add_group():
    g = Group.objects.create(name = 'MyTestGroup',)
    g.save()


def post_add(self, filename):
    params = {  "uri"       : filename,
                "id"        : "test",
                "title"     : "test",
                "abstract"  : "my test dataset",
                "update"    : "True",
                "groups"    : ""
             }
    response = self.client.post("/add_dataset", params)
    self.assertEqual(response.status_code, 200)


def add_dataset(filename):
    add_group()
    d = Dataset.objects.create(uri                   = os.path.join(resource_path, filename),
                               name                  = "test",
                               title                 = "Test dataset",
                               abstract              = "Test data set for sci-wms tests.",
                               display_all_timesteps = False,
                               keep_up_to_date       = False,)
    d.save()


def add_user():
    u = User(username="testuser",
             first_name="test",
             last_name="user",
             email="test@yser.comn",
             password=hashpass.make_password("test"),
             is_active=True,
             is_superuser=True,
            )
    u.save()


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_index(self):
        add_server()
        response = self.client.get('/index.html')
        self.assertEqual(response.status_code, 200)


class TestUgrid(TestCase):
    """
    http://wms.glos.us:8080/wms/SLRFVM_Latest_Forecast/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=facets_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326
    """
    def test_add_server(self):
        add_server()

    def test_add_group(self):
        add_group()

    #def test_post_add(self):
    #    post_add(self, "201220109.nc")

    def test_add_dataset(self):
        add_dataset("201220109.nc")

    def test_web_remove(self):
        #auth_headers = { 'HTTP_AUTHORIZATION':
        #                 'Basic ' + base64.b64encode('testuser:test')}
        add_server()
        add_group()
        add_dataset("201220109.nc")
        add_user()
        response = self.client.get('/wms/remove_dataset/?id=test&username=testuser&password=test')
        self.assertEqual(response.status_code, 200)

    def test_facets(self):
        remove_cache()
        add_dataset("201220109.nc")
        wait_on_cache()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=facets_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_pcolor(self):
        remove_cache()
        add_dataset("201220109.nc")
        wait_on_cache()
        wait_on_domain()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=pcolor_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_contours(self):
        remove_cache()
        add_dataset("201220109.nc")
        wait_on_cache()
        wait_on_domain()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=contours_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_filledcontours(self):
        remove_cache()
        add_dataset("201220109.nc")
        wait_on_cache()
        wait_on_domain()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=filledcontours_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_vectors(self):
        remove_cache()
        add_dataset("201220109.nc")
        wait_on_cache()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=vectors_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_getLegend(self):
        pass

    def test_getCaps(self):
        add_dataset("201220109.nc")
        add_server()
        wait_on_cache()
        response = self.client.get('/wms/datasets/test/?REQUEST=GetCapabilities')
        self.assertEqual(response.status_code, 200)


class TestCgrid(TestCase):

    def test_add_server(self):
        add_server()

    def test_add_group(self):
        add_group()

    def test_add_dataset(self):
        add_dataset("nasa_scb20111015.nc")

    #def test_post_add(self):
    #    post_add(self, "nasa_scb20111015.nc")

    def test_web_remove(self):
        #import base64
        #auth_headers = { 'HTTP_AUTHORIZATION':
        #                 'Basic ' + base64.b64encode('testuser:test')}
        add_server()
        add_group()
        add_user()
        add_dataset("nasa_scb20111015.nc")
        response = self.client.get('/wms/remove_dataset/?id=test&username=testuser&password=test')
        self.assertEqual(response.status_code, 200)

    def test_pcolor(self):
        remove_cache()
        add_dataset("nasa_scb20111015.nc")
        wait_on_cache()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=pcolor_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_contours(self):
        remove_cache()
        add_dataset("nasa_scb20111015.nc")
        wait_on_cache()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=contours_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_filledcontours(self):
        remove_cache()
        add_dataset("nasa_scb20111015.nc")
        wait_on_cache()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=filledcontours_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_vectors(self):
        remove_cache()
        add_dataset("nasa_scb20111015.nc")
        wait_on_cache()
        response = self.client.get('/wms/datasets/test/?LAYERS=u%2Cv&TRANSPARENT=TRUE&STYLES=vectors_average_jet_None_None_cell_False&TIME=&ELEVATION=0&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8543030.3273202,5492519.0747705,-8401010.3287862,5542356.0172055&WIDTH=929&HEIGHT=326')
        self.assertEqual(response.status_code, 200)
        remove_cache()

    def test_getLegend(self):
        pass

    def test_getCaps(self):
        add_dataset("nasa_scb20111015.nc")
        add_server()
        wait_on_cache()
        response = self.client.get('/wms/datasets/test/?REQUEST=GetCapabilities')
        self.assertEqual(response.status_code, 200)

#class TestDap(TestCase):
    #def test_post_add(self):
    #    post_add(self, "http://tds.glos.us:8080/thredds/dodsC/glos/glcfs/michigan/fcfmrc-2d/Lake_Michigan_-_2D_best.ncd")
