from lxml import etree
from glob import iglob
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


def text_get(el, path):
    subel = el.find(path)
    if subel is None:
        return None
    return subel.text


def attr_get(el, path, attr):
    subel = el.find(path)
    if subel is None:
        return None
    return subel.get(attr)


def generate_paths(el):
    print el.tag

def warn_paths(paths):
    pass

