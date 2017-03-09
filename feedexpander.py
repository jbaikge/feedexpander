#!/usr/bin/env python3

import feedparser
import fileinput
import newspaper
import sys

from lxml import etree

feed_in = ''
for line in fileinput.input():
    feed_in += line

doc = feedparser.parse(feed_in)

feed = etree.Element('feed', xmlns='http://www.w3.org/2005/Atom')
etree.SubElement(feed, 'id').text = doc.feed.id
etree.SubElement(feed, 'title').text = doc.feed.title
etree.SubElement(feed, 'subtitle').text = doc.feed.subtitle
etree.SubElement(feed, 'updated').text = doc.feed.updated

author = etree.SubElement(feed, 'author')
for k in doc.feed.author_detail:
    etree.SubElement(author, k).text = doc.feed.author_detail[k]

for e in doc.entries:
    article = newspaper.Article(e.link)
    # article.download()
    # article.parse()
    entry = etree.SubElement(feed, 'entry')
    etree.SubElement(entry, 'id').text = e.id
    etree.SubElement(entry, 'link').text = e.link
    etree.SubElement(entry, 'updated').text = e.updated
    etree.SubElement(entry, 'summary').text = e.summary

    author = etree.SubElement(entry, 'author')
    for k in e.author_detail:
        etree.SubElement(author, k).text = e.author_detail[k]
    # etree.SubElement(entry, 'content').text = article.text

xml = etree.tostring(
    feed,
    encoding=doc.encoding,
    pretty_print=True,
    xml_declaration=True)

sys.stdout.buffer.write(xml)
