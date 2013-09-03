import os
from lxml import etree
from pprint import pprint
from parseutil import ted_documents, text_get, attr_get, generate_paths
from collections import defaultdict

FORM_TYPES = defaultdict(int)


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
        self._ignore.add(path)

    def text(self, path, ignore=True):
        el = self.el.find(path)
        if el is None:
            return None
        if ignore:
            self.ignore(self.element_name(el))
        return el.text

    def attr(self, path, attr, ignore=True):
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
            pprint({
                'path': k,
                'text': v.text,
                'attr': v.attrib
            })


def select_form(form, lang):
    lang = lang.split()[0]
    children = form.getchildren()
    if len(children) == 1:
        return children.pop()
    orig = None
    for child in children:
        if child.get('LG') == 'EN':
            return child
        if child.get('LG') == lang:
            orig = child
    return orig


def parse(filename, file_content):
    #fh = open(filename, 'rb')
    xmldata = file_content.replace('xmlns="', 'xmlns_="')
    #fh.close()
    #print xmldata.decode('utf-8').encode('ascii', 'replace')
    root = etree.fromstring(xmldata)
    form = root.find('.//FORM_SECTION')
    form.getparent().remove(form)
    ext = Extractor(root)
    #audit(filename, doc)
    cpvs = [{'code': e.get('CODE'), 'text': e.text} for e in root.findall('.//NOTICE_DATA/ORIGINAL_CPV')]
    ext.ignore('./CODED_DATA_SECTION/NOTICE_DATA/ORIGINAL_CPV')
    
    refs = [e.text for e in root.findall('.//NOTICE_DATA/REF_NOTICE/NO_DOC_OJS')]
    ext.ignore('./CODED_DATA_SECTION/NOTICE_DATA/REF_NOTICE/NO_DOC_OJS')

    data = {
        'technical_reception_id': ext.text('./TECHNICAL_SECTION/RECEPTION_ID'),
        'technical_comments': ext.text('./TECHNICAL_SECTION/COMMENTS'),
        'technical_deletion_date': ext.text('./TECHNICAL_SECTION/DELETION_DATE'),
        'technical_form_lang': ext.text('./TECHNICAL_SECTION/FORM_LG_LIST'),
        'reception_id': ext.text('./TECHNICAL_SECTION/RECEPTION_ID'),
        'oj_collection': ext.text('.//REF_OJS/COLL_OJ'),
        'oj_number': ext.text('.//REF_OJS/NO_OJ'),
        'oj_date': ext.text('.//REF_OJS/DATE_PUB'),
        'doc_no': ext.text('.//NOTICE_DATA/NO_DOC_OJS'),
        'doc_url': ext.text('.//NOTICE_DATA//URI_DOC[@LG="EN"]') or ext.text('.//NOTICE_DATA//URI_DOC'),
        'info_url': ext.text('.//NOTICE_DATA/IA_URL_GENERAL'),
        'etendering_url': ext.text('.//NOTICE_DATA/IA_URL_ETENDERING'),
        'orig_language': ext.text('.//NOTICE_DATA/LG_ORIG'),
        'orig_nuts': ext.text('.//NOTICE_DATA/ORIGINAL_NUTS'),
        'orig_nuts_code': ext.attr('.//NOTICE_DATA/ORIGINAL_NUTS', 'CODE'),
        'iso_country': ext.attr('.//NOTICE_DATA/ISO_COUNTRY', 'VALUE'),
        'original_cpv': cpvs,
        'references': refs,
        'dispatch_date': ext.text('.//CODIF_DATA/DS_DATE_DISPATCH'),
        'request_document_date': ext.text('.//CODIF_DATA/DD_DATE_REQUEST_DOCUMENT'),
        'submission_date': ext.text('.//CODIF_DATA/DT_DATE_FOR_SUBMISSION'),
        'heading': ext.text('.//CODIF_DATA/HEADING'),
        'directive': ext.attr('.//CODIF_DATA/DIRECTIVE', 'VALUE'),
        'authority_type_code': ext.attr('.//CODIF_DATA/AA_AUTHORITY_TYPE', 'CODE'),
        'authority_type': ext.text('.//CODIF_DATA/AA_AUTHORITY_TYPE'),
        'document_type_code': ext.attr('.//CODIF_DATA/TD_DOCUMENT_TYPE', 'CODE'),
        'document_type': ext.text('.//CODIF_DATA/TD_DOCUMENT_TYPE'),
        'contract_nature_code': ext.attr('.//CODIF_DATA/NC_CONTRACT_NATURE', 'CODE'),
        'contract_nature': ext.text('.//CODIF_DATA/NC_CONTRACT_NATURE'),
        'procedure_code': ext.attr('.//CODIF_DATA/PR_PROC', 'CODE'),
        'procedure': ext.text('.//CODIF_DATA/PR_PROC'),
        'regulation_code': ext.attr('.//CODIF_DATA/RP_REGULATION', 'CODE'),
        'regulation': ext.text('.//CODIF_DATA/RP_REGULATION'),
        'bid_type_code': ext.attr('.//CODIF_DATA/TY_TYPE_BID', 'CODE'),
        'bid_type': ext.text('.//CODIF_DATA/TY_TYPE_BID'),
        'award_criteria_code': ext.attr('.//CODIF_DATA/AC_AWARD_CRIT', 'CODE'),
        'award_criteria': ext.text('.//CODIF_DATA/AC_AWARD_CRIT'),
        'main_activities_code': ext.attr('.//CODIF_DATA/MA_MAIN_ACTIVITIES', 'CODE'),
        'main_activities': ext.text('.//CODIF_DATA/MA_MAIN_ACTIVITIES'),
        'title_text': ext.text('.//ML_TITLES/ML_TI_DOC[@LG="EN"]/TI_TEXT'),
        'title_town': ext.text('.//ML_TITLES/ML_TI_DOC[@LG="EN"]/TI_TOWN'),
        'title_country': ext.text('.//ML_TITLES/ML_TI_DOC[@LG="EN"]/TI_CY'),
        'authority_name': ext.text('./TRANSLATION_SECTION/ML_AA_NAMES/AA_NAME')
    }

    ext.ignore('./LINKS_SECTION/FORMS_LABELS_LINK')
    ext.ignore('./LINKS_SECTION/OFFICIAL_FORMS_LINK')
    ext.ignore('./LINKS_SECTION/ORIGINAL_NUTS_LINK')
    ext.ignore('./LINKS_SECTION/ORIGINAL_CPV_LINK')
    ext.ignore('./LINKS_SECTION/XML_SCHEMA_DEFINITION_LINK')
    
    # TODO: Figure out if we need any of this, even with the forms.
    ext.ignore('./CODED_DATA_SECTION/NOTICE_DATA/VALUES_LIST/VALUES/SINGLE_VALUE/VALUE')
    ext.ignore('./CODED_DATA_SECTION/NOTICE_DATA/VALUES_LIST')
    ext.ignore('./CODED_DATA_SECTION/NOTICE_DATA/VALUES_LIST/VALUES/RANGE_VALUE/VALUE')
    #ext.ignore('')
    
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/TOWN')
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/POSTAL_CODE')
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/PHONE')
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/ORGANISATION/OFFICIALNAME')
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/FAX')
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/COUNTRY')
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/CONTACT_POINT')
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/ATTENTION')
    ext.ignore('./TRANSLATION_SECTION/TRANSLITERATIONS/TRANSLITERATED_ADDR/ADDRESS')
    #ext.ignore('')
    #ext.ignore('')
    #ext.ignore('')
    #ext.ignore('')
    #ext.ignore('')
    
    ext.audit()
    
    form_ = select_form(form, data['orig_language'])
    #ext.ignore('')
    #el = root.find('./CODED_DATA_SECTION/NOTICE_DATA/VALUES_LIST')
    #if el is not None:
    #    print etree.tostring(el, pretty_print=True)
    #missing: values

    #print doc.find('.//REF_OJS/COLL_OJ')
    #pprint(data)


def parse_all(path):
    for (dirpath, dirname, filenames) in os.walk(path):
        for filename in filenames:
            parse(os.path.join(dirpath, filename))

    pprint(dict(FORM_TYPES))

if __name__ == '__main__':
    import sys
    for file_name, file_content in ted_documents():
        parse(file_name, file_content)
        #break
    #parse_all(sys.argv[1])
