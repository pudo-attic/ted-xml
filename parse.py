import os
from lxml import etree
from pprint import pprint

from parseutil import ted_documents

"""
<CODIF_DATA>
 ///   <DS_DATE_DISPATCH>20130619</DS_DATE_DISPATCH>
 ///   <AA_AUTHORITY_TYPE CODE="R">Regional or local Agency/Office</AA_AUTHORITY_TYPE>
 ///   <TD_DOCUMENT_TYPE CODE="7">Contract award</TD_DOCUMENT_TYPE>
 ///   <NC_CONTRACT_NATURE CODE="4">Service contract</NC_CONTRACT_NATURE>
 ///   <PR_PROC CODE="1">Open procedure </PR_PROC>
 ///   <RP_REGULATION CODE="Z">Not specified</RP_REGULATION>
 ///   <TY_TYPE_BID CODE="9">Not applicable</TY_TYPE_BID>
 ///   <AC_AWARD_CRIT CODE="2">The most economic tender</AC_AWARD_CRIT>
    <MA_MAIN_ACTIVITIES CODE="A">Housing and community amenities</MA_MAIN_ACTIVITIES>
 ///   <HEADING>01303</HEADING>
    <DIRECTIVE VALUE="2004/18/EC"/>
</CODIF_DATA>
"""


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

from collections import defaultdict
FORM_TYPES = defaultdict(int)

def audit(filename, doc):

    # codif.
    KNOWN = ['DIRECTIVE', 'HEADING', 'AA_AUTHORITY_TYPE', 'TD_DOCUMENT_TYPE',
             'PR_PROC', 'NC_CONTRACT_NATURE', 'RP_REGULATION', 'TY_TYPE_BID',
             'AC_AWARD_CRIT', 'MA_MAIN_ACTIVITIES']
    for el in doc.find('.//CODIF_DATA').getchildren():
        if el.tag not in KNOWN:
            el.tag

    forms = doc.find('.//FORM_SECTION').getchildren()
    print filename, set([f.tag for f in forms]), len(forms), len(set([f.tag for f in forms]))
    for f in forms:
        FORM_TYPES[f.tag] += 1
    #print doc.find('.//FORM_SECTION').getchildren()


def parse(filename, file_content):
    #fh = open(filename, 'rb')
    xmldata = file_content.replace('xmlns="', 'xmlns_="')
    #fh.close()
    doc = etree.fromstring(xmldata)
    audit(filename, doc)
    cpvs = [{'code': e.get('CODE'), 'text': e.text} for e in doc.findall('.//NOTICE_DATA/ORIGINAL_CPV')]
    data = {
        'oj_collection': doc.find('.//REF_OJS/COLL_OJ').text,
        'oj_number': doc.find('.//REF_OJS/NO_OJ').text,
        'oj_date': doc.find('.//REF_OJS/DATE_PUB').text,
        'doc_no': doc.find('.//NOTICE_DATA/NO_DOC_OJS').text,
        'doc_url': text_get(doc, './/NOTICE_DATA//URI_DOC[@LG="EN"]') or text_get(doc, './/NOTICE_DATA//URI_DOC'),
        'orig_language': doc.find('.//NOTICE_DATA/LG_ORIG').text,
        'iso_country': doc.find('.//NOTICE_DATA/ISO_COUNTRY').get('VALUE'),
        'original_cpv': cpvs,

        'dispatch_date': text_get(doc, './/CODIF_DATA/DS_DATE_DISPATCH'),
        'request_document_date': text_get(doc, './/CODIF_DATA/DD_DATE_REQUEST_DOCUMENT'),
        'submission_date': text_get(doc, './/CODIF_DATA/DT_DATE_FOR_SUBMISSION'),
        'heading': text_get(doc, './/CODIF_DATA/HEADING'),
        'directive': attr_get(doc, './/CODIF_DATA/DIRECTIVE', 'VALUE'),
        'authority_type_code': attr_get(doc, './/CODIF_DATA/AA_AUTHORITY_TYPE', 'CODE'),
        'authority_type': text_get(doc, './/CODIF_DATA/AA_AUTHORITY_TYPE'),
        'document_type_code': attr_get(doc, './/CODIF_DATA/TD_DOCUMENT_TYPE', 'CODE'),
        'document_type': text_get(doc, './/CODIF_DATA/TD_DOCUMENT_TYPE'),
        'contract_nature_code': attr_get(doc, './/CODIF_DATA/NC_CONTRACT_NATURE', 'CODE'),
        'contract_nature': text_get(doc, './/CODIF_DATA/NC_CONTRACT_NATURE'),
        'procedure_code': attr_get(doc, './/CODIF_DATA/PR_PROC', 'CODE'),
        'procedure': text_get(doc, './/CODIF_DATA/PR_PROC'),
        'regulation_code': attr_get(doc, './/CODIF_DATA/RP_REGULATION', 'CODE'),
        'regulation': text_get(doc, './/CODIF_DATA/RP_REGULATION'),
        'bid_type_code': attr_get(doc, './/CODIF_DATA/TY_TYPE_BID', 'CODE'),
        'bid_type': text_get(doc, './/CODIF_DATA/TY_TYPE_BID'),
        'award_criteria_code': attr_get(doc, './/CODIF_DATA/AC_AWARD_CRIT', 'CODE'),
        'award_criteria': text_get(doc, './/CODIF_DATA/AC_AWARD_CRIT'),
        'main_activities_code': attr_get(doc, './/CODIF_DATA/MA_MAIN_ACTIVITIES', 'CODE'),
        'main_activities': text_get(doc, './/CODIF_DATA/MA_MAIN_ACTIVITIES'),

        'title': text_get(doc, './/ML_TITLES/ML_TI_DOC[@LG="EN"]/TI_TEXT'),
        'town': text_get(doc, './/ML_TITLES/ML_TI_DOC[@LG="EN"]/TI_TOWN'),
        'country': text_get(doc, './/ML_TITLES/ML_TI_DOC[@LG="EN"]/TI_CY')
    }
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
    #parse_all(sys.argv[1])
