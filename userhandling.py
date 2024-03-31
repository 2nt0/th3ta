def isValidEmail(email): # returns True if email is valid (x@x.x)
    if "@" in email: # check for @
        email = email.split("@")
    else:
        return False
    
    if len(email) == 2 and email[0]: # check that there is only 1 @ sign and it isn't at the start
        email = email[1] # discard all before @
    else:
        return False
    
    if "." in email: # check domain contains a .
        email = email.split(".")
    else:
        return False

    if email[0] and email[-1]: # check that . isn't at start or end of domain
        return True
    else:
        return False

def saltHash(username, password):
    from hashlib import sha3_512
    return sha3_512(("#"+username.upper()+"!"+password).encode()).hexdigest()

def makeSession(username):
    from uuid import uuid4
    from datetime import datetime, timedelta
    from hashlib import sha3_512

    session_id = str(uuid4())
    expiry = datetime.timestamp(datetime.now() + timedelta(minutes=30)) # TODO decide on expiry timedelta
    
    with open("sessions.csv","a") as sessions:
        sessions.write([sha3_512(session_id.encode()), username.lower(), str(expiry)+"\n"].join(","))
    
    return session_id

def readSession(session_id, username): # returns expiry date as a unix timestamp (float, seconds) or 0.0 if invalid session
    from hashlib import sha3_512
    from datetime import datetime, timedelta

    expiry = 0.0

    with open("sessions.csv","r") as sessions:
        for row in sessions.readlines():
            if row.split(",")[0] == sha3_512(session_id.encode()) and row.split(",")[1] == username.lower(): # check session is valid - if not expired, expiredSessionHandlerThread will delete autonomously
                expiry = datetime.timestamp(datetime.now() + timedelta(minutes=30))

    if expiry:
        with open("sessions.csv","a") as sessions:
            sessions.write([sha3_512(session_id.encode()), username.lower(), str(expiry)+"\n"].join(",")) # refresh session with new expiry - TODO actually replace session line in file
    
    return expiry

def expiredSessionHandlerThread():
    from time import sleep
    from datetime import datetime, timedelta

    sessions_towrite = []

    while True:
        with open("sessions.csv","r") as sessions:
            session_list = sessions.readlines()
        
        for row in session_list:
            if row.split(",")[2] > datetime.timestamp(datetime.now()):
                sessions_towrite.append(row)
        
        with open("sessions.csv","w") as sessions:
            sessions.writelines(sessions_towrite)

def userSignUp(form): # returns a list of rejection reasons (or empty list if none), and signs up a user if not rejected
    rejection = [] # set up list of rejection reasons

    if not(form["username"]):
        rejection.append("You must enter a username")
    else:
        with open("users.csv","r") as users:
            csvreader = [row.split(",") for row in users.readlines()] # format as csv
            for row in csvreader:
                if row[0].lower() == form["username"].lower():
                    rejection.append("Username is already in use")
    
    if not(form["email"]):
        rejection.append("You must enter an email address")
    elif not(isValidEmail(form["email"])):
        rejection.append("Email is not valid")
    else:
        with open("users.csv","r") as users:
            csvreader = [row.split(",") for row in users.readlines()] # format as csv
            for row in csvreader:
                if row[1] == form["email"]:
                    rejection.append("Email is already in use")
    
    if not(form["password"]): # TODO secure passwords?
        rejection.append("You must enter a password")

    if form["password"] != form["password-conf"]: # check [password confirm] field against [password] field
        rejection.append("Passwords do not match")
    
    if not(rejection):
        with open("users.csv","a") as users:
            users.write([form["username"], form["email"], saltHash(form["username"], form["password"])+"\n"].join(","))
    
    return rejection

def userLogin(form):
    rejection = []

    with open("users.csv", "r") as users:
        csvreader = [row.split(",") for row in users.readlines()]
        for row in csvreader: # check username and password match:
            if not(row[0].lower() == form["username"].lower() and row[2] == saltHash(form["username"], form["password"])):
                rejection.append("Username and/or password do not match")
    
    return rejection