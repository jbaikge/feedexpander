#!/usr/bin/env python3
# internal imports
import getopt
import hashlib
import io
import os
import sys
import tempfile
import time
# third party imports
import feedparser
import newspaper
from lxml import etree

cache_dir = os.path.join(tempfile.gettempdir(), 'feed_cache')

def usage():
    print('%s [--cache-dir=%s]' % (sys.argv[0], cache_dir))
    sys.exit(1)

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hd:', ['cache-dir='])
except getopt.GetoptError:
    usage()

for opt, arg in opts:
    if opt == '-h':
        usage()
    elif opt in ('-d', '--cache-dir'):
        cache_dir = arg

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

    # Load up contents from cache or the innernet
    try:
        cached_html = open(filename, 'r').read()
        body_node = etree.HTML(cached_html)
    except OSError:
        article = newspaper.Article(entry.link)
        article.download()
        article.parse()
        body_node = article.clean_top_node
        body_xml = etree.tostring(body_node, pretty_print=True)
        cache = open(filename, 'wb')
        cache.write(body_xml)
        cache.close()

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
    content.append(body_node)

xml_output = etree.tostring(
    root,
    encoding=doc.encoding,
    pretty_print=True,
    xml_declaration=True)

sys.stdout.buffer.write(xml_output)
