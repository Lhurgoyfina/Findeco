#!/usr/bin/python
# coding=utf-8
# Findeco is dually licensed under GPLv3 or later and MPLv2.
#
################################################################################
# Copyright (c) 2012 Johannes Merkert <jonny@pinae.net>
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
################################################################################
#
################################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
################################################################################
from __future__ import division, print_function, unicode_literals

from django.db.models import Q
from django.contrib.auth.models import User

from findeco.view_helpers import assert_node_for_path, assert_active_user
from findeco.view_helpers import assert_authentication, assert_post_parameters
from findeco.view_helpers import ViewErrorHandling
from microblogging import convert_response_list
from microblogging.view_helpers import convert_long_urls, microblogging_response
from .models import Post
from findeco.view_helpers import json_response
from node_storage.path_helpers import get_node_for_path


@ViewErrorHandling
def load_microblogging_all(request):
    return microblogging_response(Q(), request.GET)


@ViewErrorHandling
def load_microblogging_for_node(request, path):
    node = get_node_for_path(path)
    query = Q(location=node) | Q(node_references=node)
    return microblogging_response(query, request.GET)


@ViewErrorHandling
def load_microblogging_timeline(request, name):
    pass


@ViewErrorHandling
def load_microblogging_mentions(request, name):
    pass


@ViewErrorHandling
def load_microblogging_from_user(request, name):
    pass


@ViewErrorHandling
def load_microblogging_for_followed_nodes(request, name):
    pass


@ViewErrorHandling
def load_microblogging_for_authored_nodes(request, name):
    pass


@ViewErrorHandling
def store_microblogging(request, path):
    pass



@ViewErrorHandling
def load_microblogging(request, path, select_id, microblogging_load_type):
    # TODO refactor and optimize this method
    node = assert_node_for_path(path)
    if not select_id: # Get latest posts
        posts = list(reversed(node.microblogging_references.order_by('-time').
                              prefetch_related('author', 'is_reference_to')[:20]))
    else:
        if microblogging_load_type == "newer":
            posts = list(node.microblogging_references.filter(id__gt=select_id).
                         order_by('time').prefetch_related('author', 'is_reference_to')[:20])
        else:  # older
            posts = list(reversed(node.microblogging_references.filter(id__lt=select_id).
                                  order_by('-time').prefetch_related('author', 'is_reference_to')[:20]))
    return json_response({
        'loadMicrobloggingResponse': convert_response_list(reversed(posts))})


@ViewErrorHandling
def load_timeline(request, name, select_id, microblogging_load_type):
    """
Use this function to get the timeline for the given user.

Referenced posts will show up in the timeline as the originals do.
Hiding of the original posts for a tidy
timeline should be done in the frontend due to performance reasons.
"""
    named_user = assert_active_user(name)

    if named_user == request.user:
        followed = Q(author__in=named_user.profile.followees.all())
    else:
        followed = Q(author=named_user)
    own = Q(author=named_user)
    if not select_id:  # Get latest posts
        feed = Post.objects.filter(followed | own). \
                   order_by('-time').distinct().prefetch_related('author', 'is_reference_to')[:20]
        return json_response({
            'loadMicrobloggingResponse': convert_response_list(feed)})
    else:
        if microblogging_load_type == "newer":
            startpoint = Q(id__gt=select_id)
        else:  # older
            startpoint = Q(id__lt=select_id)
        feed = Post.objects.filter(followed | own)
        feed = feed.filter(startpoint).order_by('time').distinct()
        feed = feed.prefetch_related('author', 'is_reference_to')[:20]
        return json_response({
            'loadMicrobloggingResponse': convert_response_list(reversed(feed))})


@ViewErrorHandling
def load_mentions(request, name, select_id, microblogging_load_type):
    """
Use this function to get the timeline of mentions of the given user.

Referenced posts will show up in the timeline as the originals do.
Hiding of the original posts for a tidy
timeline should be done in the frontend due to performance reasons.
"""
    named_user = assert_active_user(name)

    if not select_id:  # Get latest posts
        feed = named_user.mentioning_entries.order_by('-time').distinct()
        feed = feed.prefetch_related('author', 'is_reference_to')[:20]
        return json_response({
            'loadMicrobloggingResponse': convert_response_list(feed)})
    else:
        if microblogging_load_type == "newer":
            startpoint = Q(id__gt=select_id)
        else:  # older
            startpoint = Q(id__lt=select_id)
        feed = named_user.mentioning_entries
        feed = feed.filter(startpoint).order_by('time').distinct()
        feed = feed.prefetch_related('author', 'is_reference_to')[:20]
        return json_response({
            'loadMicrobloggingResponse': convert_response_list(reversed(feed))})


@ViewErrorHandling
def load_own(request, name, select_id, microblogging_load_type):
    """
    Use this function to get the own posts of the user.

    Referenced posts will show up in the timeline as the originals do.
    Hiding of the original posts for a tidy
    timeline should be done in the frontend due to performance reasons.
    """
    named_user = assert_active_user(name)

    own = Q(author=named_user)
    if not select_id:  # Get latest posts
        feed = Post.objects.filter(own). \
                   order_by('-time').distinct().prefetch_related('author', 'is_reference_to')[:20]
        return json_response({
            'loadMicrobloggingResponse': convert_response_list(feed)})
    else:
        if microblogging_load_type == "newer":
            startpoint = Q(id__gt=select_id)
        else: # older
            startpoint = Q(id__lt=select_id)
        feed = Post.objects.filter(own)
        feed = feed.filter(startpoint).order_by('time').distinct()
        feed = feed.prefetch_related('author', 'is_reference_to')[:20]
        return json_response({
            'loadMicrobloggingResponse': convert_response_list(reversed(feed))})


@ViewErrorHandling
def load_collection(request, select_id, microblogging_load_type, only_author=False, all_nodes=False):
    """
    Use this function to get a collection of blogposts regarding nodes
    which are followed by the user.
    """
    if not select_id:  # Get latest posts
        if all_nodes:
            feed = Post.objects.order_by('-time')
        else:
            feed = Post.objects.filter(node_references__votes__user=request.user).order_by('-time')
        if only_author:
            feed = feed.filter(node_references__text__authors=request.user)
        feed = feed.prefetch_related('author', 'is_reference_to')[:20]
        return json_response({'loadMicrobloggingResponse': convert_response_list(feed)})
    else:
        if microblogging_load_type == "newer":
            startpoint = Q(id__gt=select_id)
        else:  # older
            startpoint = Q(id__lt=select_id)
        if all_nodes:
            feed = Post.objects.filter(startpoint)
        else:
            feed = Post.objects.filter(node_references__votes__user=request.user).filter(startpoint)
        if only_author:
            feed = feed.filter(node_references__text__authors=request.user)
        feed = feed.order_by('time').prefetch_related('author', 'is_reference_to')[:20]
        return json_response({'loadMicrobloggingResponse': convert_response_list(reversed(feed))})


@ViewErrorHandling
def store_microblog_post(request, path):
    assert_authentication(request)
    assert_post_parameters(request, ['microblogText'])
    post_text = convert_long_urls(request)
#    create_post(post_text, request.user, path)
    return json_response({'storeMicrobloggingResponse': {}})


# Getter For Now only used for RSS

def get_mentions(username, count):
        users = User.objects.filter(username__iexact=username)
        named_user = users[0]
            
        feed_data = named_user.mentioning_entries.order_by('-time').distinct()
        feed_data = feed_data.prefetch_related('author', 'is_reference_to')[:count]
        return feed_data


def get_own(username, count):
        users = User.objects.filter(username__iexact=username)
        named_user = users[0]

        feed_data = Post.objects.filter(author=named_user).order_by('-time').distinct()
        feed_data = feed_data.prefetch_related('author', 'is_reference_to')[:count]
        return feed_data


def get_timeline(username, count):
        users = User.objects.filter(username__iexact=username)
        named_user = users[0]
        followed = Q(author__in=named_user.profile.followees.all())
        own = Q(author=named_user)
        feed_data = Post.objects.filter(followed | own).order_by('-time').distinct().prefetch_related('author', 'is_reference_to')[:20]
        return feed_data


def get_news():
        feed_data = Post.objects.order_by('-time')
        feed_data = feed_data.prefetch_related('author', 'is_reference_to')[:20]
        return feed_data


def get_newsAuthor(username, count):
        users = User.objects.filter(username__iexact=username)
        named_user = users[0]
        feed_data = Post.objects.filter(node_references__votes__user=named_user).order_by('-time')
        feed_data = feed_data.filter(node_references__text__authors=named_user)
        feed_data = feed_data.prefetch_related('author', 'is_reference_to')[:20]
        return feed_data


def get_newsFollow(username, count):
        users = User.objects.filter(username__iexact=username)
        named_user = users[0]
        feed_data = Post.objects.filter(node_references__votes__user=named_user).order_by('-time')
        feed_data = feed_data.prefetch_related('author', 'is_reference_to')[:20]
        return feed_data