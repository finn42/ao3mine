import requests
import time
import datetime
from datetime import datetime as dtime
from bs4 import BeautifulSoup
import string
import math
import numpy as np
import pandas as pd
from urllib.parse import urlencode
import ast
import sqlite3

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
            if tag.string is not None:
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
            if tag.string is not None:
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
                    if r[i].startswith('[') and r[i].endswith(']'):
                        if len(r[i].split(','))>1:
                            row.append(ast.literal_eval(r[i]))
                        else: 
                            if r[i].endswith('"]'):
                                row.append(ast.literal_eval(r[i]))
                            else:
                                row.append(r[i])
                    else:
                        row.append(r[i])
            else:
                row.append(r[i])
        ent = dict(zip(cols,row))
        df_full=df_full.append(ent,ignore_index=True)
    return df_full

def ao3_sql_2_db(sqlName):
    conn = sqlite3.connect(sqlName)  
    c = conn.cursor()
    c.execute("SELECT * FROM WORKS")
    cols = [tuple[0] for tuple in c.description]
    req ="SELECT * FROM WORKS"
    res = pd.read_sql(req, conn)
    tic = time.time()
    df_DB = pd.DataFrame(index = res.index)
    list_feilds = [ 'Creator', 'Gift', 'cURL', 'Fandom', 'Category', 'Warning', 'Relationship_tags', 'Character_tags', 'Freeform_tags', 'Tags', 'Chapters', 'Series', 'Series_part', 'sURL']
    for feild in cols:
        req ="SELECT " + feild + " FROM WORKS"
        res = pd.read_sql(req, conn)
        if feild in list_feilds:
            res2 = pd.DataFrame(index=res.index,columns=[feild])
            for index, row in res.iterrows():
                res2.loc[index,feild] = ast.literal_eval(row[feild][4:])
            res = res2.copy()
        if feild.startswith('Date'):
            res2 = pd.DataFrame(index=res.index,columns=[feild])
            for index, row in res.iterrows():
                res2.loc[index,feild] = to_datetime(row[feild])
            res = res2.copy()
        df_DB[feild] = res
    
    return df_DB

# http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def daysSince(date,dateRef):
    dRef = str(dateRef)
    yrRef = int(dRef[0:4])
    mnRef = int(dRef[4:6])
    dyRef = int(dRef[6:8])
                
    d = str(date)
    yr = int(d[0:4])
    mn = int(d[4:6])
    dy = int(d[6:8])
    d = datetime.datetime(yr,mn,dy) - datetime.datetime(yrRef,mnRef,dyRef)
    
    return d.days

def to_datetime(date):
    d = str(date)
    yr = int(d[0:4])
    mn = int(d[4:6])
    dy = int(d[6:8])  
    d = datetime.datetime(yr,mn,dy)

    return d

def timeStats_numeric(df_DB,dateSeries,feildName):
    # dateSeries is a date range ex: months = pd.Series(pd.date_range("2010-01-01", "2021-01-01", freq="M")
    # df_DB is a pandas dataframe of fanworks metadata that includes the feild 'Date' per work, meaning the date the work was last updated in the source database.
    # feildName is the feild to be evaluated in the intervals set out by the dateSeries
    #    at present, this feild must be numeric (float or int)
    
    # the output dataframe
    df_stats = pd.DataFrame(index = dateSeries[:-1])
    work_counts = []
    
    # if type is Numeric:
    feild_totals = []
    feild_median = []

    # evaluate between dates of the dateSeries
    for m_i in range(len(dateSeries)-1):
        mask = (df_DB['Date']> dateSeries[m_i]) & (df_DB['Date']<= dateSeries[m_i+1])
        interval_works = df_DB.loc[mask]
    
        work_counts.append(len(interval_works))
        # if type is Numeric: 
        feild_totals.append(interval_works[feildName].sum())
        feild_median.append(interval_works[feildName].median())

    df_stats['Work_Counts'] = work_counts
    df_stats['Median_' + feildName] = feild_median
    df_stats['Total_' + feildName] = feild_totals
    
    return df_stats

def timeStats_list(df_DB,dateSeries,feildName):
    # dateSeries is a date range ex: months = pd.Series(pd.date_range("2010-01-01", "2021-01-01", freq="M")
    # df_DB is a pandas dataframe of fanworks metadata that includes the feild 'Date' per work, meaning the date the work was last updated in the source database.
    # feildName is the feild to be evaluated in the intervals set out by the dateSeries
    #    at present, this feild must be numeric (float or int)
    df_stats = pd.DataFrame(index = dateSeries[:-1])

    # if type is list of strings, like tags, creators, etc:
    work_counts = []
    feild_uniqueN = [] # number of unique strings across all work lists in interval
    feild_unique = [] # actual lists of unique entries
    feild_meanN = [] # median number of strings per work list
    feild_newN = [] # number of new unique strings in this interval, assuming the date intervals are chronological
    feild_new = [] # actual lists of unique new entries this interval
    list_all = []
    # evaluate between dates of the dateSeries
    for m_i in range(len(dateSeries)-1):
        mask = (df_DB['Date']> dateSeries[m_i]) & (df_DB['Date']<= dateSeries[m_i+1])
        interval_works = df_DB.loc[mask]    
        work_counts.append(len(interval_works))

        full_list = flatten(list(interval_works[feildName].values))
        flatList = np.unique(full_list)
        feild_uniqueN.append(len(flatList))# number of unique strings across all work lists in interval
        feild_unique.append(flatList)# actual lists of unique entries
        if len(interval_works)>0:
            feild_meanN.append(len(full_list)/len(interval_works)) # median number of strings per work list
        else:
            feild_meanN.append(0)
        new_strings = np.setdiff1d(flatList,list_all)
        feild_newN.append(len(new_strings))# number of new unique strings in this interval, assuming the date intervals are chronological
        feild_new.append(new_strings) # actual lists of unique new entries this interval
        list_all = np.union1d(flatList,list_all)
        
    df_stats['Work_Counts'] = work_counts
    df_stats['Unique_Count_' + feildName] = feild_uniqueN
    df_stats['Unique_' + feildName] = feild_unique 
    df_stats['Mean_Count_' + feildName] = feild_meanN
    df_stats['New_Count_' + feildName] = feild_newN
    df_stats['New_' + feildName] = feild_new
    
    return df_stats
  