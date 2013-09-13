import os
import dataset

EXPORTS_PATH = os.environ.get('TED_EXPORTS_PATH', 'ted_exports')

TED_USER = os.environ.get('TED_USER')
TED_PASSWORD = os.environ.get('TED_PASSWORD')

DATABASE = os.environ.get('TED_DATABASE_URL', 'sqlite:///ted.db')
engine = dataset.connect(DATABASE)

documents_table = engine['documents']
contracts_table = engine['contracts']
references_table = engine['references']
cpvs_table = engine['cpvs']


