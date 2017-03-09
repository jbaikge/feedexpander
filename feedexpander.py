#!/usr/bin/env python3

import feedparser
import fileinput
import newspaper
import sys

from lxml import etree

feed_in = ''
for line in fileinput.input():
    feed_in += line

feed = feedparser.parse(feed_in)

root = etree.Element('feed', version='1.0', xmlns='http://www.w3.org/2005/Atom')
# etree.SubElement(rss, 'title').text = feed.title

for e in feed.entries:
    article = newspaper.Article(e.link)
    article.download()
    article.parse()
    entry = etree.SubElement(root, 'entry')
    etree.SubElement(entry, 'link').text = e.link
    etree.SubElement(entry, 'author').text = e.author
    etree.SubElement(entry, 'description').text = article.text
    break

xml = etree.tostring(
    root,
    encoding='UTF-8',
    pretty_print=True,
    xml_declaration=True)

sys.stdout.buffer.write(xml)
