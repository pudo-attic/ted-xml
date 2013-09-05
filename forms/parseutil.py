from lxml import etree
from glob import iglob
from pprint import pprint
import tarfile

from common import EXPORTS_PATH

def ted_documents():
    for compl in iglob(EXPORTS_PATH + '/*.tgz'):
        tf = tarfile.open(compl, 'r:gz')
        for member in tf.getmembers():
            if not member.name.endswith('.xml'):
                continue
            fh = tf.extractfile(member)
            #print member, len(fh.read())
            #doc = etree.parse(fh)
            yield member.name, fh.read()
            fh.close()


class Extractor(object):

    def __init__(self, el):
        self.el = el
        self.paths = {}
        self._ignore = set()
        self.generate(el)

    def element_name(self, el):
        if el == self.el:
            return '.'
        return self.element_name(el.getparent()) + '/' + el.tag

    def generate(self, el):
        children = el.getchildren()
        if len(children):
            for child in children:
                self.generate(child)
        else:
            name = self.element_name(el)
            if not name in self.paths:
                self.paths[name] = el

    def ignore(self, path):
        if path.endswith('*'):
            path = path[:len(path)-1]
            for p in self.paths.keys():
                if p.startswith(path):
                    self._ignore.add(p)
        else:
            self._ignore.add(path)

    def text(self, path, ignore=True):
        if path is None:
            return
        el = self.el.find(path)
        if el is None:
            return None
        if ignore:
            self.ignore(self.element_name(el))
        return el.text
    
    def html(self, path, ignore=True):
        if path is None:
            return
        el = self.el.find(path)
        if el is None:
            return None
        if ignore:
            self.ignore(self.element_name(el))
        return etree.tostring(el)

    def attr(self, path, attr, ignore=True):
        if path is None:
            return
        el = self.el.find(path)
        if el is None:
            return None
        if ignore:
            self.ignore(self.element_name(el))
        return el.get(attr)

    def audit(self):
        #print "UNPARSED:"
        for k, v in sorted(self.paths.items()):
            if k in self._ignore:
                continue
            if v.text or len(v.attrib.keys()):
                pprint({
                    'path': k,
                    'text': v.text,
                    'attr': v.attrib
                })


