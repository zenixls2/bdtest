Flask Example For Writing an Event Registration System
======================================================

1. Prepare

Please have your `python` and `pip` in your system `PATH`.  
We encourage users to use `venv` so that installation won't pollute your environment.  
Assume that you already cloned the project and in its root directory:  
Windows:
```bat
pip install -r requirements.txt
set FLASK_APP=emgr
set FLASK_ENV=developement
```
Unix:
```bash
pip install -r requirements.txt
export FLASK_APP=emgr
export FLASK_ENV=developement
```

2. Init database:

by default the database file will be generated under instance folder
```bash
flask init-db
```

3. To run the app:

The default url is `http://localhost:5000/`.
```bash
flask run
```

4. Cleanup database

```bash
flask clean-db
```

5. Swagger doc

Open `http://localhost:5000/doc/` in browser

6. APIs

GET `/` `/js/<path>`  
  - serve files in static folders. `/` points to `index.html`
  
GET `/add_event?name=xdd&location=tw&start_time=2020/12/18-12:30:00&end_time=2020/12/31-12:30:00`  
  - explain: create a new event
  - response: `{status: "Error", msg: "error msg"}`
  - response: `{status: "Ok", id: "Event id (primary key)"}`
  
GET `/add_user?email=abc@1234`  
  - explain: register an email for a new user
  - response: `{status: "Error", msg: "error msg"}`
  - response: `{status: "Ok", user_id: "User id (primary key)"}`
  
GET `/get_event?id=1`  
  - explain: get event together with all sign up emails
  - response: `{status: "Error", msg: "error msg"}`
  - response: `{status: "Ok", event: {name, location, start_time, end_time}, users: [emails]}`
  
GET `/sign_event?id=1&user_id=1[&send_mail=1]`  
  - explain: sign up for an event
  - response: `{status: "Ok"}`
  - response: `{status: "Error", msg: "error msg"}`
  
GET `/unsign_event?id=1&email=abc@123`  
  - explain: unsign a email from an event
  - response: `{status: "Ok"}`
  - response: `{status: "Error", msg: "error msg"}`
  
GET `/get_user?email=abc@123` `/get_user?user_id=1`  
  - explain: get user info by email, with all signed event ids.
  - response: `{status: "Ok", user: {user_id, email}, event: [event id]}`
  - response: `{status: "Error", msg: "error msg"}`
  
GET `/listall`  
  - explain: get all event structs
  - response: `[{id, name, location, start_time, end_time}]`


<H3>TODO ITEMS</H3>
Currently only using swagger ui for manual testing. Need a fancy UI for user registration and operations. Documentation for API returning objects in swagger UI is also not completed yet.
