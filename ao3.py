import requests
import time
import datetime
from datetime import datetime as dtime
from bs4 import BeautifulSoup
import string
import math
import pandas as pd
from urllib.parse import urlencode
import ast

def redate(date_string):
    # convert dates from AO3 formate to YYYYMMDD integer string, via datetime
    d=dtime.strptime(date_string, '%d %b %Y')
    outdate = int(d.strftime('%Y%m%d'))
    return outdate

def query_AO3_work(work):

    # prime all the entry valies with nulls
    wurl=''
    node=0
    title='' 
    creator=[]
    curl=[]
    gift = []
    fandom=[] 
    rating=''
    category=[] 
    warning=[]
    complete=''
    date=0
    relationship_tags=[]
    characters_tags=[]
    freeform_tags=[]
    all_tags=[]
    summary=''
    language=''
    words=0
    chapters=[1,'?']
    collection=0
    comments=0
    kudos=0
    hits=0
    bookmarks=0
    series=[]
    series_part=[]
    series_url=[]
    
    # title level meta
    a = work.find_all('h4')
    v = BeautifulSoup(str(a),'html.parser')
    refs = v.select('a')
    for ref in refs:
        ref = BeautifulSoup(str(ref),'html.parser')
        url = ref.a.get('href')
        if url.startswith('/works/'):
            url = str(v.a.get('href'))
            wurl = 'https://archiveofourown.org' + url
            n = url.split('/')
            node =  int(n[-1])
            title = str(v.a.string)
        else:
            if url.endswith('/gifts'):
                gift.append(ref.a.string)
            else:
                curl.append("https://archiveofourown.org" + ref.a.get('href'))
                creator.append(ref.a.string)
    # fandom tags
    a = work.find_all('h5')
    v = BeautifulSoup(str(a),'html.parser')
    if v.h5['class']==["fandoms","heading"]:
        refs = v.select('a[class]')
        fandom = []
        for f in refs:
            w = BeautifulSoup(str(f),'html.parser')
            if w.a['class']==["tag"]:
                fandom.append(w.a.string)
    # date
    a = work.find_all('div')
    v = BeautifulSoup(str(a[0]),'html.parser')
    date = redate(v.find('p').string)
    # classifications 
    a = work.find_all('ul')
    b = a[0].find_all('li')
    for tag in b:
        v = BeautifulSoup(str(tag),'html.parser')
        if v.span['class']:
            cl = v.span['class']
            if cl[0].startswith('rating'):
                rating = tag.span['title']
            if cl[0].startswith('warning'):
                warning = tag.span['title'].split(',')
            if cl[0].startswith('category'):
                category = tag.span['title'].split(',')
            if cl[0].startswith('complete'):
                complete = tag.span['title']
    # work tags
    b = a[1].find_all('li')
    for tag in b:
        v = BeautifulSoup(str(tag),'html.parser')
        if v.li['class']==['relationships']:
            relationship_tags.append(tag.string)  
        if v.li['class']==['characters']:
            characters_tags.append(tag.string)
        if v.li['class']==['freeforms']:
            freeform_tags.append(tag.string)            
    all_tags = relationship_tags + characters_tags + freeform_tags
    # series details
    for ain in a[2:]:
        b = ain.find_all('li')
        for tag in b:
            t = tag.find('strong')
            series_part.append(int(t.string))
            t = tag.find('a')
            series.append(t.string)
            v = BeautifulSoup(str(tag),'html.parser')
            series_url.append('https://archiveofourown.org' + v.a.get('href'))
    # work stats
    a = work.find_all('dd')
    for tag in a:
        v = BeautifulSoup(str(tag),'html.parser')
        if v.dd['class']==['language']:
            language = str(tag.string)
        if v.dd['class']==['words']:
            w = tag.string.split(',')
            words = int(''.join(w))  
        if v.dd['class']==['chapters']:
            w = v.get_text()
            w = w.split('/')
            if w[1].isdigit():
                w[1]=int(w[1])
            w[0] = int(w[0])
            chapters = w
        if v.dd['class']==['collections']:
            collection = int(tag.string)
        if v.dd['class']==['kudos']:
            kudos = int(tag.string)  
        if v.dd['class']==['comments']:
            comments = int(tag.string)
        if v.dd['class']==['hits']:
            hits = int(tag.string)
        if v.dd['class']==['bookmarks']:
            bookmarks= int(tag.string)
    # summary        
    a = work.find_all('blockquote')
    if a:
        for w in a[0].find_all('p'):
            k = str(w).replace('<br/>','\n')
            v = BeautifulSoup(k,'html.parser')
            summary+= v.get_text() + '\n'
            
    # dictionary of work information
    entry = {
        'url': wurl, 
        'Node': node, 
        'Title': title, 
        'Creator': creator,
        'Gift':gift,
        'cURL':curl,
        'Fandom': fandom, 
        'Rating': rating, 
        'Category': category, 
        'Warning': warning, 
        'Complete': complete, 
        'Date': date, 
        'Relationship_tags': relationship_tags,
        'Character_tags': characters_tags,
        'Freeform_tags': freeform_tags,
        'Tags': all_tags, 
        'Summary': summary,
        'Language': language,
        'Words': words,
        'Chapters': chapters,
        'Collection': collection,
        'Comments': comments,
        'Kudos': kudos,
        'Hits': hits,
        'Bookmarks': bookmarks,
        'Series': series,
        'Series_part': series_part,
        'sURL': series_url}
    #print entry
    
    return entry    

def work_eval_print(work):
    a = work.find_all('h4')
    v = BeautifulSoup(str(a),'html.parser')
#     if v.h4['class']==["heading"]:
#         url = str(v.a.get('href'))
#         print("url: https://archiveofourown.org" + url)
#         n = url.split('/')
#         print('Node: ' +  n[-1])
#         print('Title: ' + v.a.string)

    refs = v.select('a')
    authors = []
    aurls = []
    gifts = []
    
    for ref in refs:
        ref = BeautifulSoup(str(ref),'html.parser')
        url = ref.a.get('href')
        if url.startswith('/works/'):
            print("URL: https://archiveofourown.org" + url)
            n = url.split('/')
            print('Node: ' +  n[-1])
            print('Title: ' + ref.a.string )
        else:
            if url.endswith('/gifts'):
                gifts.append(ref.a.string)
            else:
                authors.append(ref.a.string)
                aurls.append("https://archiveofourown.org" + v.a.get('href'))

#     for a in refs:
#         v = BeautifulSoup(str(a),'html.parser')
#         if v.a['rel']==["author"]:
#             aurls.append("https://archiveofourown.org" + v.a.get('href'))
#             authors.append(v.a.string)
    print('Creator: ' + str(authors))
    print('aURL: ' + str(aurls))
    print('Gifts: ' + str(gifts))
    
    a = work.find_all('h5')
    v = BeautifulSoup(str(a),'html.parser')
    if v.h5['class']==["fandoms","heading"]:
        refs = v.select('a[class]')
        fs = []
        for f in refs:
            w = BeautifulSoup(str(f),'html.parser')
            if w.a['class']==["tag"]:
                fs.append(w.a.string)
        print('Fandom: ' + str(fs))

    a = work.find_all('div')
    v = BeautifulSoup(str(a[0]),'html.parser')
    date = redate(v.find('p').string)
    print('Date: ' + str(date))
    
    a = work.find_all('ul')
    b = a[0].find_all('li')
    # print(b)
    for tag in b:
        v = BeautifulSoup(str(tag),'html.parser')
        if v.span['class']:
            cl = v.span['class']
            if cl[0].startswith('rating'):
                print('Rating: ' + tag.span['title'])
            if cl[0].startswith('warning'):
                print('Warning: ' + str(tag.span['title'].split(',')))
            if cl[0].startswith('category'):
                print('Category: ' + str(tag.span['title'].split(',')))
            if cl[0].startswith('complete'):
                print('Complete: ' + tag.span['title'])

    b = a[1].find_all('li')
    print('tags:' + str(len(b)))
    Warnings = []
    Ships = []
    Characters = []
    Freeforms = []
    for tag in b:
        v = BeautifulSoup(str(tag),'html.parser')
        if v.li['class']==['warnings']:
            Warnings.append(tag.string)
        if v.li['class']==['relationships']:
            Ships.append(tag.string)  
        if v.li['class']==['characters']:
            Characters.append(tag.string)
        if v.li['class']==['freeforms']:
            Freeforms.append(tag.string)            
    Alltags = Ships + Characters + Freeforms

    print('Warning: ' + str(Warnings))
    print('Relationships: ' + str(Ships))
    print('Characters: '+ str(Characters))
    print('Freeform: ' + str(Freeforms))            
    print('Tags: ' + str(Alltags))

    for ain in a[2:]:
        b = ain.find_all('li')
        print(len(b))
        for tag in b:
            t = tag.find('strong')
            print('Series_Part: ' + t.string)
            t = tag.find('a')
            print('Series: ' + t.string)
            v = BeautifulSoup(str(tag),'html.parser')
            print("sURL: https://archiveofourown.org" + v.a.get('href'))

    a = work.find_all('dd')
    for tag in a:
        v = BeautifulSoup(str(tag),'html.parser')
        if v.dd['class']==['language']:
            print('Language: ' + tag.string)
        if v.dd['class']==['words']:
            w = tag.string.split(',')
            print('Words: ' + ''.join(w))  
        if v.dd['class']==['chapters']:
            w = v.get_text()
            w = w.split('/')
            print('Chapters: '+ w[0] + ' of ' + w[-1])
        if v.dd['class']==['collections']:
            print('Collections: ' + tag.string)
        if v.dd['class']==['kudos']:
            print('Kudos: ' + tag.string)  
        if v.dd['class']==['comments']:
            print('Comments: '+ tag.string)
        if v.dd['class']==['hits']:
            print('Hits: '+ tag.string)
        if v.dd['class']==['bookmarks']:
            print('Bookmarks: '+ tag.string)
            
    Summary = ''
    a = work.find_all('blockquote')
    for w in a[0].find_all('p'):
        k = str(w).replace('<br/>','\n')
        v = BeautifulSoup(k,'html.parser')
        Summary+= v.get_text() + '\n'

    print('Summary: ' + Summary)
    
    return

def db2sqlTypes(df_work):
    # convert columns of database into values suitable for sql_types
    #    floats to int (specifically appropriate for this project)
    #    lists to string
    df_sql = pd.DataFrame(index = df_work.index)
    cols = df_work.columns
    for c in cols:
        A = df_work[c]
        B = []
        for a in A:
            if type(a) is list:
                B.append('list'+str(a))
            if type(a) is float:
                B.append(int(a))
            if type(a) is str:
                B.append(a)
        df_sql[c] = pd.Series(B,df_work.index)
    return df_sql

def sql2dbListTypes(data,cols):
    # convert back sqlite db of works to pandas dataFramewith more complex objects
    # namely, convert table entry strings that start with '[' into lists. 
    # Inputs: data is the output of the .fetchall(), a list of ordered entries 
    #         cols are the column titles to build back into a pandas database
    df_full = pd.DataFrame(columns = cols)
    for r in data: # entries row by row, yeah it's slow
        row = []
        for i in range(len(r)):
            if type(r[i]) is str:
                if r[i].startswith('list['):
                    row.append(ast.literal_eval(r[i][4:]))
                else:
                    row.append(r[i])
            else:
                row.append(r[i])
        ent = dict(zip(cols,row)) 
        df_full=df_full.append(ent,ignore_index=True)
    return df_full