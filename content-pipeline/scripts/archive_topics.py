#!/usr/bin/env python3
"""Read-only topic leads from the public WordPress.com archive."""
import argparse
import html
import json
import re
import urllib.parse
import urllib.request

API = 'https://public-api.wordpress.com/rest/v1.1/sites/218070053/posts/'


def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', value or ''))).strip()


def topics(limit=25):
    found, offset = None, 0
    while found is None or offset < found:
        query = urllib.parse.urlencode({'number': 100, 'offset': offset, 'fields': 'ID,date,slug,URL,title,excerpt'})
        request = urllib.request.Request(API + '?' + query, headers={'User-Agent': 'docnunez-topic-research/1.0'})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
        found = data['found']
        posts = data['posts']
        for post in posts:
            yield {'title': clean(post.get('title')), 'slug': post.get('slug'),
                   'date': post.get('date', '')[:10], 'source_url': post.get('URL'),
                   'excerpt': clean(post.get('excerpt'))}
            limit -= 1
            if not limit:
                return
        if not posts:
            return
        offset += len(posts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=25)
    args = parser.parse_args()
    if not 1 <= args.limit <= 1000:
        parser.error('--limit must be between 1 and 1000')
    print(json.dumps(list(topics(args.limit)), indent=2, ensure_ascii=False))
