#!/usr/bin/python
# coding=utf-8
# Findeco is dually licensed under GPLv3 or later and MPLv2.
#
# Copyright (c) 2012 Klaus Greff <klaus.greff@gmx.net>
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

from django.test import TestCase

from microblogging.factory import parse_microblogging
from microblogging.factory import validate_microblogging_schema

from node_storage.factory import create_user, create_nodes_for_path
from node_storage.path_helpers import get_root_node


class MicrobloggingSchemaTest(TestCase):

    def setUp(self):
        self.hugo = create_user('hugo')
        self.herbert = create_user('herbert')
        self.foo1 = create_nodes_for_path('foo.1')

        self.schema_skeleton = {
            'author': 0,
            'location': 0,
            'time': 0,
            'type': "userpost",
            'template_text': "some text",
            'mentions': [],
            'references': [],
            'answer_to': -1
        }

        self.wrong_schema = {
            'author': self.hugo,
            'location': 'foo.1',
            'time': '12:30',
            'type': 5,
            'template_text': None,
            'mentions': {},
            'references': {},
            'answer_to': 'my_mom'
        }

    def test_validate_microblogging_schema_skeleton(self):
        self.assertTrue(validate_microblogging_schema(self.schema_skeleton))

    def test_validate_microblogging_schema_with_mentions(self):
        self.schema_skeleton['mentions'] = [self.hugo.id, self.herbert.id]
        self.assertTrue(validate_microblogging_schema(self.schema_skeleton))

    def test_validate_microblogging_schema_with_references(self):
        self.schema_skeleton['references'] = ['', 'foo.1']
        self.assertTrue(validate_microblogging_schema(self.schema_skeleton))

    def test_validate_microblogging_schema_fails_for_missing_entries(self):
        entries = self.schema_skeleton.keys()
        for e in entries:
            schema = dict(self.schema_skeleton)
            del schema[e]
            with self.assertRaisesRegexp(AssertionError, e):
                validate_microblogging_schema(schema)

    def test_validate_microblogging_schema_fails_for_wrong_datatypes(self):
        for n, e in self.wrong_schema.items():
            schema = dict(self.schema_skeleton)
            schema[n] = e
            with self.assertRaisesRegexp(AssertionError, n):
                validate_microblogging_schema(schema)

    def test_validate_microblogging_schema_fails_for_wrong_type(self):
        schema = dict(self.schema_skeleton)
        schema['type'] = 'uncle bob'
        with self.assertRaisesRegexp(AssertionError, 'type'):
            validate_microblogging_schema(schema)

    def test_validate_microblogging_schema_fails_for_duplicate_mentions(self):
        self.schema_skeleton['mentions'] = [self.hugo.id, self.hugo.id]
        with self.assertRaisesRegexp(AssertionError, "unique"):
            self.assertTrue(validate_microblogging_schema(self.schema_skeleton))

    def test_validate_microblogging_schema_fails_for_unsorted_mentions(self):
        self.schema_skeleton['mentions'] = [self.herbert.id, self.hugo.id]
        with self.assertRaisesRegexp(AssertionError, "sorted"):
            self.assertTrue(validate_microblogging_schema(self.schema_skeleton))

    def test_validate_microblogging_schema_fails_for_duplicate_references(self):
        self.schema_skeleton['references'] = ['foo.1', 'foo.1']
        with self.assertRaisesRegexp(AssertionError, "unique"):
            self.assertTrue(validate_microblogging_schema(self.schema_skeleton))

    def test_validate_microblogging_schema_fails_for_unsorted_references(self):
        self.schema_skeleton['references'] = ['foo.1', '']
        with self.assertRaisesRegexp(AssertionError, "sorted"):
            self.assertTrue(validate_microblogging_schema(self.schema_skeleton))


class MicrobloggingParserTest(TestCase):
    def setUp(self):
        self.hugo = create_user('hugo')
        self.herbert = create_user('herbert')
        self.root = get_root_node()
        # self.foo1 = create_nodes_for_path('foo.1')
        self.foo2 = create_nodes_for_path('foo.2')

    def assert_schema_equal(self, actual, expected):
        for n, e in expected.items():
            self.assertEqual(e, actual[n], "Mismatch for '%s': %s != %s" %
                                           (n, e, actual[n]))

    def test_parseMicroblogging(self):
        mbs = parse_microblogging("text", self.hugo, "")
        expected = {
            'author': self.hugo.id,
            'location': self.root.id,
            'type': "userpost",
            'template_text': "text",
            'mentions': [],
            'references': [],
            'answer_to': -1
        }
        self.assert_schema_equal(mbs, expected)

    def test_parseMicroblogging_correct_location(self):
        mbs = parse_microblogging("text", self.hugo, "foo.2")
        self.assertEqual(mbs['location'], self.foo2.id)

    def test_parseMicroblogging_single_node_reference(self):
        mbs = parse_microblogging("the proposal /foo.1 is cool", self.hugo, "")
        expected = {
            'template_text': "the proposal {n0} is cool",
            'references': ['foo.1'],
        }
        self.assert_schema_equal(mbs, expected)

    def test_parseMicroblogging_multiple_node_references(self):
        mbs = parse_microblogging("/foo.1 was improved to /foo.2 and is now "
                                  "better than /foo.1 because /foo.1 sucks",
                                  self.hugo, "")
        expected = {
            'template_text': "{n0} was improved to {n1} and is now better than "
                             "{n0} because {n0} sucks",
            'references': ['foo.1', 'foo.2'],
        }
        self.assert_schema_equal(mbs, expected)

    def test_parseMicroblogging_single_mention(self):
        mbs = parse_microblogging("hey @herbert cool name", self.hugo, "")
        expected = {
            'author': self.hugo.id,
            'template_text': "hey {u0} cool name",
            'mentions': [self.herbert.id],
        }
        self.assert_schema_equal(mbs, expected)

    def test_parseMicroblogging_multiple_mention(self):
        mbs = parse_microblogging("@herbert is like @hugo but more @herbert",
                                  self.hugo, "")
        expected = {
            'author': self.hugo.id,
            'template_text': "{u1} is like {u0} but more {u1}",
            'mentions': [self.hugo.id, self.herbert.id],
        }
        self.assert_schema_equal(mbs, expected)

    def test_parseMicroblogging_invalid_mention(self):
        mbs = parse_microblogging("does anyone know @ninja",
                                  self.hugo, "")
        expected = {
            'author': self.hugo.id,
            'template_text': "does anyone know @ninja",
            'mentions': [],
        }
        self.assert_schema_equal(mbs, expected)