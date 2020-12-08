# SI507 Final Project: Interactive Food Pantry List

This is a program about food pantries, which users can interact with via command lines.

## Getting Started

Run present.py in the terminal.

### Pages

1. State List Page
```
=======STATE==LIST=======
Please select from the following states:
[1] Michigan    [2] Alaska      [3] Florida     [4] California  
[5] Delaware    [6] Georgia     [7] Ohio        [8] Texas
OR enter a postal code(6 digits)
Enter here(state name or index or postal code):
``` 

2. City List Page
```
=====CITIES==IN==MICHIGAN=====
[1] Michigan Center, with 3 food pantries
[2] Au Gres, with 2 food pantries
...
[10] Pontiac, with 26 food pantries
Select a city by index, "show plot", "back" to previous interface or "exit"
:
```

3. Pantry List Page
```
========PANTRY==LIST========
[1] Monroe Outreach Ministries, 48161
[2] Hourse Of Restoration - Hot Meals, 48161
[3] Mcop'S The Lord'S Harvest Pantry, 48161
[4] The Salvation Army Family Manor Of Monroe, 48161
----------------------------
Select a pantry by index, "back" to previous interface or "exit"
: 
```

4. Pantry Detail Page
```
========PANTRY==DETAIL========
Name: Monroe Outreach Ministries
--
Description: Hours:The 3rd Saturday of the month11:00am to 12:00pmFor more information, please call.

 -----------------------C--O--N--T--A--C--T-----------------------
| Address: Monroe, Michigan 48161                                 |
| Phone: (734) 241-6955                                           |
| URL: https://www.foodpantries.org/li/monroe-outreach-ministries |
 -----------------------------------------------------------------

 "Back" to previous interface or "exit"
: 
```

### Features

1. Select a state by entering state name or an valid index on the "state list page"  --> Get a list of cities in that state
2. Select a city by entering an index on the "city list page" --> Get a list of pantries in that city
3. Enter a postal code on the "state list page" --> Get a list of pantries with that postal code
4. Select a pantry by entering an index on the "pantry list page" --> Get detailed information of that food pantry
5. Enter "show plot" on the "city list page" --> Get a bar plot of cities with the most food pantries in that state, opened in your browser
6. Go back to previous "page" by entering "back"
7. Exit the program by entering "exit"

## Files

* present.py

Contains programs needed for interactive prompts.
**Dependence: sqlite3, plotly**

* create_db.py

Contains programs needed for building a database for food pantries (pantries.sqlite)
**Dependence: sqlite3, BeautifulSoup, requests**

* pantries.sqlite

Database file