#!/usr/bin/python
import zipfile
from lxml import etree
import sys
from BeautifulSoup import BeautifulSoup
from django.utils.encoding import smart_str, smart_unicode
from textwrap import wrap, fill, dedent


def main(argv):
    if(len(argv) > 1):
        for filename in get_epub_files(sys.argv[1]):
            if "htm" not in filename:
                continue
            contents = read_chapter(sys.argv[1], filename)
            htmlless = ''.join(BeautifulSoup(contents).findAll("body",text=True))
            htmlless.replace("&nbsp;", " ")
            print "*"*80
            print filename
            print "*"*80
            print dedent(fill(smart_str(htmlless), 80))
            print "*"*80

def read_chapter(fname, filename):
    zip = zipfile.ZipFile(fname)

    # find the contents metafile
    txt = zip.read("OEBPS/" + filename)
    return txt

def get_epub_files(fname):
    ns = {
        'n':'urn:oasis:names:tc:opendocument:xmlns:container',
        'pkg':'http://www.idpf.org/2007/opf',
        'dc':'http://purl.org/dc/elements/1.1/'
    }

    # prepare to read from the .epub file
    zip = zipfile.ZipFile(fname)

    # find the contents metafile
    txt = zip.read('META-INF/container.xml')
    tree = etree.fromstring(txt)
    cfname = tree.xpath('n:rootfiles/n:rootfile/@full-path',namespaces=ns)[0]

    # grab the metadata block from the contents metafile
    cf = zip.read(cfname)
    tree = etree.fromstring(cf)
    p = tree.xpath('/pkg:package/pkg:manifest',namespaces=ns)[0]

    # repackage the data
    res = p.xpath('pkg:item/@href', namespaces=ns)

    return res


def get_epub_info(fname):
    ns = {
        'n':'urn:oasis:names:tc:opendocument:xmlns:container',
        'pkg':'http://www.idpf.org/2007/opf',
        'dc':'http://purl.org/dc/elements/1.1/'
    }

    # prepare to read from the .epub file
    zip = zipfile.ZipFile(fname)

    # find the contents metafile
    txt = zip.read('META-INF/container.xml')
    tree = etree.fromstring(txt)
    cfname = tree.xpath('n:rootfiles/n:rootfile/@full-path',namespaces=ns)[0]

    # grab the metadata block from the contents metafile
    cf = zip.read(cfname)
    tree = etree.fromstring(cf)
    p = tree.xpath('/pkg:package/pkg:metadata',namespaces=ns)[0]

    # repackage the data
    res = {}
    for s in ['title','language','creator','date','identifier']:
        res[s] = p.xpath('dc:%s/text()'%(s),namespaces=ns)[0]

    return res

if __name__ == "__main__":
    main(sys.argv)

