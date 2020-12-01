#################################
##### Name: Xiaoshan He
##### Uniqname: xshe
#################################

import sqlite3
from bs4 import BeautifulSoup
import requests
import json
import re
import base64

CACHE_FILENAME = "cache.json"
CACHE_DICT = {}
DBNAME = "pantries.sqlite"

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def init_states():
    ''' Drop table "State" if exists, and create one

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    
    drop_states = '''
        DROP TABLE IF EXISTS "State";
    '''
    create_states = '''
        CREATE TABLE IF NOT EXISTS "State" (
            "id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "name"  TEXT NOT NULL UNIQUE,
            "url"   TEXT NOT NULL UNIQUE
        );
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(drop_states)
    cur.execute(create_states)
    conn.commit()
    conn.close()

def init_cities():
    ''' Drop table "City" if exists, and create one

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    drop_cities = '''
        DROP TABLE IF EXISTS "City";
    '''
   
    create_cities = '''
        CREATE TABLE IF NOT EXISTS "City" (
            "id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "name"  TEXT NOT NULL,
            "state_id" INTERGER NOT NULL,
            "url"   TEXT NOT NULL,
            FOREIGN KEY ("state_id")  REFERENCES "State" ("id")
        );
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(drop_cities)
    cur.execute(create_cities)
    conn.commit()
    conn.close()

def init_pantries():
    ''' Drop table "Pantry" if exists, and create one

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    drop_pantries = '''
        DROP TABLE IF EXISTS "Pantry";
    '''
   
    create_pantries = '''
        CREATE TABLE IF NOT EXISTS "Pantry" (
            "id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "name"  TEXT NOT NULL,
            "description" TEXT,
            "post" TEXT,
            "city_id" INTERGER NOT NULL,
            "url"   TEXT,
            "phone" TEXT,
            FOREIGN KEY ("city_id")  REFERENCES "City" ("id")
        );
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    cur.execute(drop_pantries)
    cur.execute(create_pantries)
    conn.commit()
    conn.close()

def build_states():
    ''' Add data to table "States" with contents from "https://www.foodpantries.org/"

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    init_states(conn)

    url = "https://www.foodpantries.org/"

    CACHE_DICT = open_cache()
    if url in CACHE_DICT:
        print("Using cache")
        page = CACHE_DICT[url]
    else:
        print("Fetching")
        page = requests.get(url).content.decode()
        CACHE_DICT[url] = page
        save_cache(CACHE_DICT)
        
    soup = BeautifulSoup(page,'html.parser')
    results = soup.find('tbody').findAll('tr')
    for row in results:
        cells = row.findAll('td')
        for cell in cells:
            a = cell.find("a")
            if a:
                name = a.text.lower()
                url = a.attrs['href']
                query = f'''
                    INSERT INTO State (name,url) VALUES("{name}","{url}");
                '''
                cur.execute(query)
        
    conn.commit()
    conn.close()

def build_cities():
    ''' Add data to table "City" with content from State.url

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    init_cities()
    query_states = '''
        SELECT id,url FROM State
    '''
    states = cur.execute(query_states).fetchall()
    
    CACHE_DICT = open_cache()
    for record in states:
        url = record[1]
        state_id = record[0]
        if url in CACHE_DICT:
            print("Using cache")
            page = CACHE_DICT[url]
        else:
            print("Fetching")
            page = requests.get(url).content.decode()
            CACHE_DICT[url] = page
            save_cache(CACHE_DICT) 
        
        soup = BeautifulSoup(page,'html.parser')
        table = soup.find('tbody').findAll('tr')
        for row in table:
            cells = row.findAll('td')
            for cell in cells:
                a = cell.find("a")
                if a:
                    url = a.attrs['href']
                    name = a.text.lower()
                    query = f'''
                        INSERT INTO City (name,url,state_id) VALUES("{name}","{url}","{state_id}");
                    '''
                    cur.execute(query)
    conn.commit()
    conn.close()

def build_pantries():
    ''' Add data to table "Pantry" with content from City.url

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    init_pantries()
    query_cities = '''
        SELECT City.id,City.url,State.name FROM City
        INNER JOIN State ON City.state_id=State.id
        WHERE State.name IN("michigan","alaska","florida")
    '''
    cities = cur.execute(query_cities).fetchall()
    for record in cities:
        city_url = record[1]
        city_id = record[0]
        if city_url in CACHE_DICT:
            print("Using cache")
            page = CACHE_DICT[city_url]
        else:
            print("Fetching")
            page = requests.get(city_url).content.decode("utf8","ignore")
            CACHE_DICT[city_url] = page
        
        soup = BeautifulSoup(page,'html.parser')
        lists = soup.findAll('ul',{'class':'blog-list'})
        for pantry_list in lists:
            titles = pantry_list.findAll('h2')
            paras = pantry_list.findAll('p') #all paragraphs
            for index,item in enumerate(titles):
                a = item.find("a")
                if a:
                    name = a.text.lower()
                    if len(name)==0:
                        continue
                    name = base64.b64encode(bytes(name, 'utf-8'))
                    
                    try:
                        url = a.attrs["href"]
                    except:
                        url = ""
                    try:
                        des = paras[ 2*index + 1 ].text.strip()
                        des = base64.b64encode(bytes(des, 'utf-8'))
                    except:
                        des = ""
                    try:
                        rows = paras[ 2*index ].text.split('\n')
                        try:
                            post = re.search(r'[0-9]{5}',rows[2].strip())
                            post = post.group() if post!=None else ""
                        except:
                            post = ""
                        try:
                            phone = rows[3].strip()
                        except:
                            phone = ""
                    except:
                        post = ""
                        phone = ""
                        
                    query = f'''
                        INSERT INTO Pantry (name,description,post,city_id,url,phone) 
                        VALUES("{name}","{des}","{post}","{city_id}","{url}","{phone}");
                    '''
                    try:
                        cur.execute(query)
                        conn.commit()
                    except:
                        print("-------")
                        print(query)
                        print("-------")
                        return False
    
    save_cache(CACHE_DICT) 
    conn.close()

if __name__ == "__main__":
    # print(build_cities_states(conn))
    # states = build_states(conn)
    # build_cities(conn)
    # url = "https://www.foodpantries.org/ci/ak-wasilla"
    # print(pantry(url))
    build_pantries()
    
