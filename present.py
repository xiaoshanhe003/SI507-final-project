#################################
##### Name: Xiaoshan He
##### Uniqname: xshe
#################################

import sqlite3
import plotly.graph_objects as go
import base64
import re

DBNAME = "pantries.sqlite"
STATUS = {"back":0, "exit":1}
error_invalid_input = "[ERROR] Invalid input, please try agian!"

def convert_b64(string:str):
    '''convert a base encoded string into utf-8
    Parameters
    --
    string: String
    a string, base64 encoded, format: "b'.....'"

    Return
    --
    result: String
    a string, utf-8 encoded  
    '''
    temp = string[1:]
    temp = temp.strip("'")
    temp = bytes(temp, 'utf-8')
    result = base64.b64decode(temp).decode()
    return result

def get_cities_by_state(state:str):
    '''enter state name, return a list of cities
    Parameters
    --
    state: String
    name of a state

    Return
    --
    result: List
    a list of cities, each has such structure:
    ( [city_id:int], [name:str], [count_pantries:int] )
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    limit = 10
    query_state = f'''
        SELECT id FROM State
        WHERE name=="{state}"
    '''
    state_id = cur.execute(query_state).fetchone()[0]
    state_id = int(state_id)
    query = f'''
        SELECT Pantry.city_id, City.name, COUNT(Pantry.id)
        FROM Pantry
        INNER JOIN City ON Pantry.city_id=City.id
        WHERE City.state_id={state_id}
        GROUP BY Pantry.city_id
        ORDER BY RANDOM()
        LIMIT {limit}
    '''
    result = cur.execute(query).fetchall()
    conn.close()
    return result

def get_pantries_by_city(city_id:int):
    '''enter city_id, return a list of pantries in that city
    Parameters
    --
    city: String
    name of a city

    Return
    --
    result: List
    a list of food pantries records, each has such structure:
    ( [id:int], [name:str], [post:str])
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    limit = 10
    query = f'''
        SELECT id, name, post
        FROM Pantry
        WHERE city_id={city_id}
        ORDER BY RANDOM()
        LIMIT {limit}
    '''
    tuples = cur.execute(query).fetchall()
    conn.close()
    result = []
    for record in tuples:
        item = []
        item.append( record[0] )
        item.append( convert_b64(record[1]) )
        item.append( record[2] )
        result.append(item)
    return result

def get_pantries_by_post(post:str):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    limit = 10
    query = f'''
        SELECT id, name, post
        FROM Pantry
        WHERE post={post}
        ORDER BY RANDOM()
        LIMIT {limit}
    '''
    tuples = cur.execute(query).fetchall()
    conn.close()
    result = []
    for record in tuples:
        item = []
        item.append( record[0] )
        item.append( convert_b64(record[1]) )
        item.append( record[2] )
        result.append(item)
    return result

def get_pantry_by_id(id:int):
    '''enter id, return a dictionary of information
    Parameters
    --
    id: Int
    the id of the pantry

    Return
    --
    result: Dict
    a dictionary of information
    { "id":, "name":, "description", "post", "city", "state", "phone","url"}
    '''
    result = {}
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    query = f'''
        SELECT Pantry.name, Pantry.description, Pantry.post, City.name, State.name, Pantry.phone, Pantry.url
        FROM Pantry
        INNER JOIN City ON Pantry.city_id=City.id
        INNER JOIN State ON City.state_id=State.id
        WHERE Pantry.id={id}
    '''
    record = cur.execute(query).fetchone()
    conn.close()
    if len(record) == 0:
        return False
    result["name"] = convert_b64(record[0])
    result["description"] = convert_b64(record[1])
    result["post"] = record[2]
    result["city"] = record[3]
    result["state"] = record[4]
    result["phone"] = record[5]
    result["url"] = record[6]
    return result

def display_cities(cities:list):
    '''print a list of cities
    Parameters
    --
    cities:list
    a list of cities, with such format:
    ( [city_id:int], [name:str], [count_pantries:int] )

    Return
    --
    None
    '''
    for i,item in enumerate(cities):
        print(f'''[{i+1}] {item[1].title()}, with {item[2]} food pantr{"ies" if item[2]>1 else "y"}''')

def display_pantries(pantries:list):
    '''print a list of pantries
    Parameters
    --
    pantries:list
    a list of pantries, with such format:
    ( [id:int], [name:str], [post:str])

    Return
    --
    None
    '''
    for i,item in enumerate(pantries):
        print(f'''[{i+1}] {item[1].title()}, {item[2]}''')

def display_pantry_detail(pantry:dict):
    '''print a list of cities
    Parameters
    --
    pantry:Dict
    a dictionary of pantry information, with such format:
    { "id":, "name":, "description", "post", "city", "state", "phone","url"}

    Return
    --
    None
    '''
    print("Name:", pantry["name"].title())
    print("--")
    print("Description:",pantry["description"])
    print()
    url = "| URL: " + pantry["url"] + " |"
    width = len(url)-2
    phone = "| Phone: " + pantry["phone"]
    addr = f'''| Address: {pantry["city"].title()}, {pantry["state"].title()} {pantry["post"]}'''
    phone = phone + " "*(width - len(phone)) + " |"
    addr = addr + " "*(width - len(addr)) + " |"
    print(" "+"-"*(int((width-19)/2))+"C--O--N--T--A--C--T"+"-"*(int((width-19)/2)))
    print(addr)
    print(phone)
    print(url)
    print( "", "-"*width)

def build_state_list(states:list):
    temp = []
    width = 12
    for index,item in enumerate(states):
        if index%4==0 and index != 0:
            temp.append("\n")
        temp.append(f'''[{index+1}] {item.capitalize()}{" "*(width - len(item))}''')
    return "".join(temp)

def draw_bar_plot(state:str):
    '''process data and show a bar plot of 
    top 10 cities pantry count in the specific state
    Parameters
    ---
    None

    Return
    ---
    None
    '''
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    query = f'''
        SELECT City.name, COUNT(Pantry.id)
        FROM Pantry
        INNER JOIN City ON Pantry.city_id=City.id
        INNER JOIN State ON City.state_id=State.id
        WHERE State.name="{state}"
        GROUP BY Pantry.city_id
        ORDER BY COUNT(Pantry.id) DESC
        LIMIT 10
    '''
    data = cur.execute(query).fetchall()
    conn.close()
    xvals = []
    yvals = []
    for row in data:
        xvals.append( row[0].title() )
        yvals.append( row[1] )
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title=f"10 cities with the most food pantries in {state.title()}")
    fig = go.Figure(data=bar_data, layout=basic_layout)

    fig.update_xaxes(title_text = "City")
    fig.update_yaxes(title_text = "Count of Food Pantries")
    
    fig.show()

def interface_cities(state:str):
    '''interactive interface of a list of cities
    Parameter
    --
    state: String
    state name

    Return
    --
    status: int
    status when exiting this interface
    '''
    city_list =  get_cities_by_state(state)
    while(True):
        print()
        print(f"=====CITIES==IN=={state.upper()}=====")
        display_cities(city_list)
        user_input = input('''Select a city by index, "show plot", "back" to previous interface or "exit"\n: ''').lower()
        if user_input in STATUS:
            return STATUS[user_input]
        elif user_input == "show plot":
            draw_bar_plot(state)
            continue
        else:
            try:
                index = int(user_input) - 1
                id = city_list[index][0]
                pantries = get_pantries_by_city(id)
                status = interface_pantries(pantries)
                if status == STATUS["exit"]:
                    return status
            except:
                print(error_invalid_input)

def interface_pantries(pantry_list:list):
    '''interactive interface of a list of pantries
    Parameter
    --
    pantry_list: List
    a list of pantries

    Return
    --
    status: int
    status when exiting this interface
    '''
    while(True):
        print()
        print("========PANTRY==LIST========")
        display_pantries(pantry_list)
        print("----------------------------")
        user_input = input('''Select a pantry by index, "back" to previous interface or "exit"\n: ''').lower()
        if user_input in STATUS:
            return STATUS[user_input]
        else:
            try:
                index = int(user_input) - 1
                id = pantry_list[index][0]
                status = interface_pantry(id)
                if status == STATUS["exit"]:
                    return status
            except:
                print(error_invalid_input)

def interface_pantry(id:int):
    '''interactive interface of a list of pantries
    Parameter
    --
    id: int
    pantry id

    Return
    --
    status: int
    status when exiting this interface
    '''
    pantry = get_pantry_by_id(id)
    print("========PANTRY==DETAIL========")
    display_pantry_detail(pantry)
    
    while(True):
        print()
        user_input = input(''' "Back" to previous interface or "exit"\n: ''')
        if user_input in STATUS:
            return STATUS[user_input]
        else:
            print()
            print(error_invalid_input)

def interactive_prompt():
    states = ["michigan","alaska","florida","california","delaware","georgia","ohio","texas"]
    str_states = build_state_list(states)
    print("=========")
    print("Welcome to Interactive Food Pantry List ^_^")
    print("=========")
    while(True):
        status = ""
        print()
        print("=======STATE==LIST=======")
        print("Please select from the following states:")
        print(str_states)
        print("OR enter a postal code(6 digits)")
        user_input = input("Enter here(state name or index or postal code): ").lower()
        if user_input == "exit":
            break
        try:#int, index selection or postal code
            index = int(user_input) - 1 
            if index < 10000:
                state = states[index]
                status = interface_cities(state)
            else:
                pantry_list = get_pantries_by_post(user_input)
                status = interface_pantries(pantry_list)
        except:# str, state or invalid
            if user_input in states:
                status = interface_cities(user_input)
            else:
                print(error_invalid_input)
        if status == STATUS["exit"]:
            break
    
    print("=========")
    print("Bye!")
    print("=========")

if __name__ == "__main__":
    # result = get_pantries_by_city(2788)
    # result = get_pantries_by_post('48105')
    # result = get_pantry_by_id(1096)
    # print(result)
    # cities = get_cities_by_state("alaska")
    # display_cities(cities)
    interactive_prompt()
    # display_pantries(pantries)
    # pantry = get_pantry_by_id(1096)
    # display_pantry_detail(pantry)
