#!/usr/bin/python
# coding=utf-8
# Findeco is dually licensed under GPLv3 or later and MPLv2.
#
# Copyright (c) 2012 Klaus Greff <klaus.greff@gmx.net>,
# Johannes Merkert <jonny@pinae.net>
# This file is part of Findeco.
#
# Findeco is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# Findeco is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Findeco. If not, see <http://www.gnu.org/licenses/>.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import division, print_function, unicode_literals
from django.core.urlresolvers import reverse
from django.test import TestCase
from node_storage import get_root_node, Node
from node_storage.factory import create_user, create_slot

class StoreTextTest(TestCase):
    def setUp(self):
        self.root = get_root_node()
        self.hugo = create_user("Hugo", password="1234")
        self.slot = create_slot("Slot")
        self.root.append_child(self.slot)

    def test_store_textNode(self):
        self.assertTrue(self.client.login(username="Hugo", password="1234"))
        response = self.client.post(reverse('store_text', kwargs=dict(path="Slot.1")),dict(wikiText="= Bla =\nBlubb."))
        self.assertEqual(response.status_code,200)
        self.assertEqual(Node.objects.filter(parents=self.slot).count(),1)
        self.assertEqual(Node.objects.filter(parents=self.slot).all()[0].title,"Bla")
        self.assertEqual(Node.objects.filter(parents=self.slot).all()[0].text.text,"Blubb.")