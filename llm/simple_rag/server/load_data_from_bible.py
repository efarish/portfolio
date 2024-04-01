import os
from dotenv import load_dotenv
import json
import xmltodict
from typing import Tuple

def create_json_from_xml(_file:str) -> dict:
    with open( _file, encoding='utf8' ) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
    json_data = json.dumps(data_dict)
    with open(_file + ".json", "w") as json_file:
        json_file.write(json_data)
    with open(_file + ".json", "r") as f:
        json_doc = json.load(f)    
    return json_doc

def create_book_list(_json:dict) -> list:
    start_book = 'Matthew'
    one_chpt_books = ['Philemon','2 John', '3 John', 'Jude']
    start = False
    books_lst = []

    for book in _json['XMLBIBLE']['BIBLEBOOK']:
        if book['@bname'].strip() == start_book: start = True
        if not start: continue
        bk ={}
        bk['@bname'] = book['@bname']
        bk['CHPTS'] = []
        for idx, chapter in enumerate(book['CHAPTER'], start=1):
            chpt = {}
            chpt['CHPT'] = str(idx)
            chpt['VERS_LST'] = []
            chpt['CHPT_TXT'] = ""
            if book['@bname'] in one_chpt_books:
                for verse in book['CHAPTER']['VERS']:
                    chpt['VERS_LST'].append( verse['#text'].strip() )
            else:
                for verse in chapter['VERS']:
                    chpt['VERS_LST'].append( verse['#text'].strip() )
            chpt['CHPT_TXT'] += " ".join(chpt['VERS_LST'])
            bk['CHPTS'].append(chpt)
        books_lst.append(bk)
    return books_lst

def create_doc_meta_lists(_bks:list) -> Tuple[list, list]:

    texts = []
    metas = []

    for bk in _bks:
        for idx, chpt in enumerate(bk['CHPTS']):
            texts.append( chpt['CHPT_TXT'] )
            meta = {}
            meta['book'] = bk['@bname']
            meta['chapter'] = idx+1
            metas.append(meta)

    return texts, metas    

def get_doc_meta_list() -> Tuple[list, list]:
    load_dotenv()
    json = create_json_from_xml(os.environ['CORPUS_SRC']) 
    bk_list = create_book_list(json)
    docs, metas = create_doc_meta_lists(bk_list)
    return docs, metas



def main():
    docs, metas = get_doc_meta_list()
    print(f'# docs: {len(docs)}')
    print(f'# metas: {len(metas)}')
    print(f'1st meta contents: {metas[0]}')

if __name__ == '__main__':
    main()
   