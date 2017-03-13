#!/usr/bin/env python3

import feedparser
import hashlib
import io
import newspaper
import os
import sys
import tempfile
import time

from lxml import etree

cache_dir = os.path.join(tempfile.gettempdir(), 'feed_cache')

xml_input = sys.stdin.read()

doc = feedparser.parse(xml_input)
xpath_ns = {'ns': doc.namespaces['']}

root = etree.fromstring(xml_input.encode(doc.encoding))


link_hash = hashlib.sha1(doc.feed.link.encode(doc.encoding)).hexdigest()
cache_dir = os.path.join(cache_dir, link_hash)
os.makedirs(cache_dir, mode=0o755, exist_ok=True)

for entry in doc.entries:
    filename_hash = hashlib.sha1(entry.link.encode(doc.encoding)).hexdigest()
    filename = os.path.join(cache_dir, filename_hash)

    article = newspaper.Article(entry.link)
    # Load up contents from cache or the innernet
    try:
        cached_html = open(filename, 'r').read()
        article.download(html=cached_html)
    except OSError:
        article.download()
        cache = open(filename, 'w')
        cache.write(article.html)
        cache.close()
        time.sleep(5)
    # Carry on body extraction
    article.parse()

    # Find entry to add full content to
    entry_xpath = '/ns:feed/ns:entry[ns:id="%s"]' % (entry.id)
    nodes = root.xpath(entry_xpath, namespaces=xpath_ns)
    if len(nodes) < 1:
        print('Error finding entry with id "%s"' % (entry.id))
        sys.exit(1)
    if len(nodes) > 1:
        print('Too many nodes with the same id "%s"' % (entry.id))
        sys.exit(1)
    entry_node = nodes[0]

    # Create new content node
    content = etree.SubElement(entry_node, 'content', type='text/html')
    content.append(article.clean_top_node)

xml_output = etree.tostring(
    root,
    encoding=doc.encoding,
    pretty_print=True,
    xml_declaration=True)

sys.stdout.buffer.write(xml_output)
