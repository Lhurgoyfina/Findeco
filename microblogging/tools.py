#!/usr/bin/python
# coding=utf-8
from __future__ import division, print_function, unicode_literals
from time import mktime
from findeco.search_tools import get_search_query
from .models import Post


def convert_to_response_list(post_list):
    response_list = []
    for post in post_list:
        authors = [post.author.username]
        if post.is_answer_to:
            authors.append(post.is_reference_to.author.username)
        response_list.append(
            {'microblogText': post.text_cache,
             'authorGroup': authors,
             'location': post.location_id,
             'locationPath': post.location.get_a_path(),
             'microblogTime': int(mktime(post.time.timetuple())),
             'microblogID': post.pk})
    return response_list


def search_for_microblogging(search_string):
    microblogging_query = get_search_query(search_string, ['text_cache', ])
    found_posts = Post.objects.filter(microblogging_query).order_by("-id")
    return convert_to_response_list(found_posts)


def change_microblogging_authorship(old_user, new_user):
    # change author of post to new user
    for post in old_user.microblogging_posts.all():
        post.author = new_user
        post.render()
        post.save()

    # change mention of post to new user
    for post in Post.objects.filter(mentions=old_user):
        old_order = [u.id for u in post.mentions.order_by('id')]
        post.mentions.remove(old_user)
        post.mentions.add(new_user)
        post.save()
        new_order = [u.id for u in post.mentions.order_by('id')]

        permutation = []
        for user_id in old_order:
            if user_id == old_user.id:
                permutation.append(new_order.index(new_user.id))
            else:
                permutation.append(new_order.index(user_id))

        print(old_order)
        print(new_order)
        print(permutation)
        for i in range(len(permutation)):
            post.text_template = post.text_template.replace('{u%d}' % i,
                                                            '{P%d}' % i)

        for i, p in enumerate(permutation):
            post.text_template = post.text_template.replace('{P%d}' % i,
                                                            '{u%d}' % p)
        post.render()


def delete_posts_referring_to(node):
    Post.objects.filter(node_references=node).delete()
    Post.objects.filter(location=node).delete()