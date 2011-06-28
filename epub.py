#!/usr/bin/python
import zipfile
from lxml import etree
import sys
from BeautifulSoup import BeautifulSoup
from django.utils.encoding import smart_str, smart_unicode
from textwrap import wrap, fill, dedent
import curses
import math

def main(screen):
    book = sys.argv[1]
    for chapter in get_epub_files(book):
        if "htm" not in chapter:
            continue
        contents = read_chapter(book, chapter)
        contents = ''.join(BeautifulSoup(contents).findAll("body",text=True))
        contents  = wrap(smart_str(contents), int(math.floor(curses.COLS * .8)))
        y = 0
        for line in contents:
            if(y < curses.LINES - 2):
                screen.addstr(y, 0, line + "\n")
                y = y+1
                screen.refresh()
            else:
                #Wait for user input
                c = screen.getch()
                if c == ord('c'): break;
                elif c == ord('q'): exit()  # Exit the while()
                screen.clear()
                y = 0
        #If the chapter didn't end cleanly at the end of the page, hold until the reader is ready to move on
        if(y != 0):
            screen.hline(y, 0, '-', int(math.floor(curses.COLS * .8)))
            c = screen.getch()
        #Clean the screen for each new chapter
        screen.clear()

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
    if(len(sys.argv) < 2):
        exit()
    curses.wrapper(main)

