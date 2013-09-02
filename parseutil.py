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

