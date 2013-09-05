from pprint import pprint
from parseutil import Extractor

def extract_address(ext, prefix, query):
    data = {
        prefix + '_official_name': ext.text(query+'OFFICIALNAME'),
        prefix + '_address': ext.text(query+'ADDRESS'),
        prefix + '_town': ext.text(query+'TOWN'),
        prefix + '_postal_code': ext.text(query+'POSTAL_CODE'),
        prefix + '_country': ext.attr(query+'COUNTRY', 'VALUE'),
        prefix + '_attention': ext.text(query+'ATTENTION'),
        prefix + '_phone': ext.text(query+'PHONE'),
        prefix + '_email': ext.text(query+'EMAIL') or ext.text(query+'E_MAIL'),
        prefix + '_fax': ext.text(query+'FAX'),
        prefix + '_url': ext.text(query+'URL_GENERAL') or ext.text(query+'URL'),
        prefix + '_url_buyer': ext.text(query+'URL_BUYER'),
        prefix + '_url_info': ext.text(query+'URL_INFORMATION'),
        prefix + '_url_participate': ext.text(query+'URL_PARTICIPATE')
    }
    for k, v in data.items():
        if v is None:
            del data[k]
    return data


def extract_values(ext, prefix, query):
    data = {
        prefix + '_currency': ext.attr(query, 'CURRENCY'),
        prefix + '_cost': ext.attr(query + '/VALUE_COST', 'FMTVAL'),
        prefix + '_low': ext.attr(query + '//LOW_VALUE', 'FMTVAL'),
        prefix + '_high': ext.attr(query + '//HIGH_VALUE', 'FMTVAL'),
        prefix + '_vat_rate': ext.attr(query + '//VAT_PRCT', 'FMTVAL')
    }

    if ext.el.find(query + '/INCLUDING_VAT') is not None:
        data[prefix + '_vat_included'] = True
    if ext.el.find(query + '/EXCLUDING_VAT') is not None:
        data[prefix + '_vat_included'] = False

    for k, v in data.items():
        if v is None:
            del data[k]
    return data


def parse_award(root):
    ext = Extractor(root)
    contract = {
        'contract_number': ext.text('./CONTRACT_NUMBER'),
        'lot_number': ext.text('./LOT_NUMBER'),
        'contract_title': ext.text('./CONTRACT_TITLE/P') or ext.text('./CONTRACT_TITLE'),
        'contract_award_day': ext.text('.//CONTRACT_AWARD_DATE/DAY'),
        'contract_award_month': ext.text('.//CONTRACT_AWARD_DATE/MONTH'),
        'contract_award_year': ext.text('.//CONTRACT_AWARD_DATE/YEAR'),
        'offers_received_num': ext.text('.//OFFERS_RECEIVED_NUMBER'),
        'offers_received_meaning': ext.text('.//OFFERS_RECEIVED_NUMBER_MEANING')
    }

    contract.update(extract_values(ext, 'contract_value', './/COSTS_RANGE_AND_CURRENCY_WITH_VAT_RATE'))
    contract.update(extract_values(ext, 'initial_value', './/INITIAL_ESTIMATED_TOTAL_VALUE_CONTRACT'))
    contract.update(extract_address(ext, 'operator', './ECONOMIC_OPERATOR_NAME_ADDRESS//'))
    return contract
    #from lxml import etree
    #print etree.tostring(root, pretty_print=True)
    #pprint(contract)
    #ext.audit()


def parse_form(root, data):
    ext = Extractor(root)
    form = {
        'file_reference': ext.text('.//ADMINISTRATIVE_INFORMATION_CONTRACT_AWARD/FILE_REFERENCE_NUMBER/P'),
        'relates_to_eu_project': ext.text('.//RELATES_TO_EU_PROJECT_YES/P'),
        'notice_dispatch_day': ext.text('.//NOTICE_DISPATCH_DATE/DAY'),
        'notice_dispatch_month': ext.text('.//NOTICE_DISPATCH_DATE/MONTH'),
        'notice_dispatch_year': ext.text('.//NOTICE_DISPATCH_DATE/YEAR'),
        'appeal_procedure': ext.text('.//PROCEDURES_FOR_APPEAL//LODGING_OF_APPEALS_PRECISION/P'),
        'location': ext.text('.//DESCRIPTION_AWARD_NOTICE_INFORMATION/LOCATION_NUTS/LOCATION/P') or ext.text('.//DESCRIPTION_AWARD_NOTICE_INFORMATION/LOCATION_NUTS/LOCATION'),
        'location_nuts': ext.attr('.//DESCRIPTION_AWARD_NOTICE_INFORMATION/LOCATION_NUTS/NUTS', 'CODE'),
        'type_contract': ext.attr('.//DESCRIPTION_AWARD_NOTICE_INFORMATION//TYPE_CONTRACT', 'VALUE'),
        'gpa_covered': ext.attr('.//DESCRIPTION_AWARD_NOTICE_INFORMATION/CONTRACT_COVERED_GPA', 'VALUE'),
        'electronic_auction': ext.attr('.//F03_IS_ELECTRONIC_AUCTION_USABLE', 'VALUE'),
        'cpv_code': ext.attr('.//DESCRIPTION_AWARD_NOTICE_INFORMATION/CPV/CPV_MAIN/CPV_CODE', 'CODE'),
        #'cpv_additional_code': ext.attr('.//DESCRIPTION_AWARD_NOTICE_INFORMATION/CPV/CPV_ADDITIONAL/CPV_CODE', 'CODE'),
        'authority_type': ext.text('.//TYPE_AND_ACTIVITIES_AND_PURCHASING_ON_BEHALF//TYPE_OF_CONTRACTING_AUTHORITY', 'VALUE'),
        'authority_type_other': ext.text('.//TYPE_AND_ACTIVITIES_AND_PURCHASING_ON_BEHALF//TYPE_AND_ACTIVITIES/TYPE_OF_CONTRACTING_AUTHORITY_OTHER', 'VALUE'),
        'activity_type': ext.text('.//TYPE_AND_ACTIVITIES_AND_PURCHASING_ON_BEHALF//TYPE_OF_ACTIVITY'),
        'activity_type_other': ext.text('.//TYPE_AND_ACTIVITIES_AND_PURCHASING_ON_BEHALF//TYPE_OF_ACTIVITY_OTHER'),
        'concessionaire_email': ext.text('.//CA_CE_CONCESSIONAIRE_PROFILE/E_MAILS/E_MAIL'),
        'concessionaire_nationalid': ext.text('.//CA_CE_CONCESSIONAIRE_PROFILE/ORGANISATION/NATIONALID'),
        'concessionaire_contact': ext.text('.//CA_CE_CONCESSIONAIRE_PROFILE/CONTACT_POINT'),
        'contract_award_title': ext.text('.//DESCRIPTION_AWARD_NOTICE_INFORMATION/TITLE_CONTRACT/P'),
        'contract_description': ext.html('.//DESCRIPTION_AWARD_NOTICE_INFORMATION/SHORT_CONTRACT_DESCRIPTION/P'),
        'additional_information': ext.html('.//COMPLEMENTARY_INFORMATION_CONTRACT_AWARD/ADDITIONAL_INFORMATION/P'),
        'contract_type_supply': ext.attr('.//TYPE_CONTRACT_LOCATION_W_PUB/TYPE_SUPPLIES_CONTRACT', 'VALUE')
    }

    form.update(extract_address(ext, 'authority', './/CONTRACTING_AUTHORITY_INFORMATION_CONTRACT_AWARD/NAME_ADDRESSES_CONTACT_CONTRACT_AWARD//'))
    form.update(extract_address(ext, 'appeal_body', './/PROCEDURES_FOR_APPEAL/APPEAL_PROCEDURE_BODY_RESPONSIBLE//'))
    form.update(extract_address(ext, 'on_behalf', './/TYPE_AND_ACTIVITIES_AND_PURCHASING_ON_BEHALF/PURCHASING_ON_BEHALF//'))
    #form.update(extract_address(ext, 'lodging_info', './/PROCEDURES_FOR_APPEAL/LODGING_INFORMATION_FOR_SERVICE//'))
    ext.ignore('./FD_CONTRACT_AWARD/COMPLEMENTARY_INFORMATION_CONTRACT_AWARD/PROCEDURES_FOR_APPEAL/MEDIATION_PROCEDURE_BODY_RESPONSIBLE/*')
    ext.ignore('./FD_CONTRACT_AWARD/COMPLEMENTARY_INFORMATION_CONTRACT_AWARD/PROCEDURES_FOR_APPEAL/LODGING_INFORMATION_FOR_SERVICE/*')

    # Make awards criteria their own table.
    ext.ignore('./FD_CONTRACT_AWARD/PROCEDURE_DEFINITION_CONTRACT_AWARD_NOTICE/AWARD_CRITERIA_CONTRACT_AWARD_NOTICE_INFORMATION/AWARD_CRITERIA_DETAIL_F03/*')
    ext.ignore('./FD_CONTRACT_AWARD/AWARD_OF_CONTRACT/*')
    ext.ignore('./FD_CONTRACT_AWARD/PROCEDURE_DEFINITION_CONTRACT_AWARD_NOTICE/ADMINISTRATIVE_INFORMATION_CONTRACT_AWARD/PREVIOUS_PUBLICATION_INFORMATION_NOTICE_F3/*')

    ext.text('.//TYPE_CONTRACT_LOCATION_W_PUB/SERVICE_CATEGORY_PUB')
    ext.text('.//CPV/CPV_ADDITIONAL/CPV_CODE')
    
    form.update(extract_values(ext, 'total_value', './/TOTAL_FINAL_VALUE/COSTS_RANGE_AND_CURRENCY_WITH_VAT_RATE'))

    #from lxml import etree
    #el = root.find('./FD_CONTRACT_AWARD/OBJECT_CONTRACT_INFORMATION_CONTRACT_AWARD_NOTICE/TOTAL_FINAL_VALUE')
    #if el:
    #    print etree.tostring(el, pretty_print=True)
    #    #pprint(form)
    ext.audit()

    for award in root.findall('.//AWARD_OF_CONTRACT'):
        contract = parse_award(award)
        contract.update(form)
        contract['doc_no'] = data['doc_no']
        #pprint(contract)
