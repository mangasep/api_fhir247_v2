from flask import request
import requests, json, calendar, time, urllib, base64
from datetime import datetime

# from config import FHIR247_DB
from Secret247 import phoenixConn, generateUniqeID, tokenValidate, encryptPassword, generateNewToken, \
    getCountDataOfTable, getUserIDbyToken, usernameValidate, emailValidate, getUserbyID, checkPrivilegeMenu, \
    getGroupbyID, groupNameValidate, getMenubyID, getMenuByName, getPrivilegeByID, getUserByEmailOrUsername, \
    getMenubyGroup, getMenuPrivileges


#generate Token
def generateToken():
    apikey = request.headers['apikey']
    apisecret = request.headers['apisecret']

    result = generateNewToken(apikey, apisecret)

    return result

def login():
    errCode = 0
    # parsing request
    data = request.data
    dataUser = json.loads(data)

    # username
    if 'username' in dataUser and dataUser['username'] != '':
        username = dataUser['username']
    else:
        username = ""

    # email
    if 'email' in dataUser and dataUser['email'] != '':
        email = dataUser['email']
    else:
        email = ""


    #checking username or email
    if not username and not email:
        errCode = 14006
        message = "Username or Email is empty."

    # password
    if 'password' in dataUser and dataUser['password'] != '':
        password = encryptPassword(dataUser['password'])
    else:
        errCode = 14007
        message = "Password is required."

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        #login processing
        try:

            now = datetime.now()
            LoginDate = now.strftime('%Y-%m-%d %H:%M:%S')

            #select user by username or email
            user = getUserByEmailOrUsername(username, email)

            if user['status'] == 200:
                #check is_active, is_login, is_block
                if not user["data"]["isActive"]:
                    result = {"status": 140012, "message": "User is not active"}
                elif user["data"]["isBlock"]:
                    result = {"status": 140013, "message": "User is blocked by system"}
                elif user["data"]['isLogin']:
                    result = {"status": 140014, "message": "This account is currently active login"}
                elif user["data"]['password'] != password:
                    result = {"status": 140015, "message": "Wrong Password"}
                else:
                    #update status login user


                    # set update by and update date
                    fieldsNameUsers = "is_login, first_login"
                    valuesNameUsers = " TRUE, TO_DATE('" + LoginDate + "', 'yyyy-MM-dd HH:mm:ss') "

                    # upsert user
                    cmd = "UPSERT INTO FHIR247.UI_USERS(user_id, " + fieldsNameUsers + ") SELECT user_id, " + valuesNameUsers + " FROM FHIR247.UI_USERS WHERE user_id = '" + user["data"]['id'] + "'"
                    cursor.execute(cmd)

                    if user["data"]["groupId"] and user["data"]["groupId"] != '':
                        group = getGroupbyID(user["data"]["groupId"])
                        group = group["data"]

                        menu = getMenubyGroup(user["data"]["groupId"])
                        menu = menu["data"]
                    else:
                        group = ""
                        menu = ""


                    result = {"data": [{"user": user["data"]}, {"group": group}, {"menu": menu}]}

            else:
                result = {"status": user['status'], "message": user['message']}

        except OSError as err:
            errCode = 13002
            message = err

            result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def logout():
    errCode = 0
    # parsing request
    data = request.data
    dataUser = json.loads(data)

    # username
    if 'username' in dataUser and dataUser['username'] != '':
        username = dataUser['username']
    else:
        username = ""

    # email
    if 'email' in dataUser and dataUser['email'] != '':
        email = dataUser['email']
    else:
        email = ""


    #checking username or email
    if not username and not email:
        errCode = 14006
        message = "Username or Email is empty."

    # password
    if 'password' in dataUser and dataUser['password'] != '':
        password = encryptPassword(dataUser['password'])
    else:
        errCode = 14007
        message = "Password is required."

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        #login processing
        try:

            now = datetime.now()
            LoginDate = now.strftime('%Y-%m-%d %H:%M:%S')

            #select user by username or email
            user = getUserByEmailOrUsername(username, email)

            if user['status'] == 200:
                #check is_active, is_login, is_block
                if not user["data"]["isActive"]:
                    result = {"status": 140012, "message": "User is not active"}
                elif user["data"]["isBlock"]:
                    result = {"status": 140013, "message": "User is blocked by system"}
                elif not user["data"]['isLogin']:
                    result = {"status": 140014, "message": "This account is currently not active login"}
                elif user["data"]['password'] != password:
                    result = {"status": 140015, "message": "Wrong Password"}
                else:
                    # set update by and update date
                    fieldsNameUsers = "is_login, last_activity"
                    valuesNameUsers = " FALSE, TO_DATE('" + LoginDate + "', 'yyyy-MM-dd HH:mm:ss') "

                    # upsert user
                    cmd = "UPSERT INTO FHIR247.UI_USERS(user_id, " + fieldsNameUsers + ") SELECT user_id, " + valuesNameUsers + " FROM FHIR247.UI_USERS WHERE user_id = '" + user["data"]['id'] + "'"
                    cursor.execute(cmd)

                    result = {"status": 200, "message": "User have been log off from application."}

            else:
                result = {"status": user['status'], "message": user['message']}

        except OSError as err:
            errCode = 13002
            message = err

            result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result






#user management
def getUsers():
    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    #checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    isActive = request.args.get('isActive')
    username = request.args.get('username')
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    fullname = request.args.get('fullname')
    email = request.args.get('email')
    isBlock = request.args.get('isBlock')
    isLogin = request.args.get('isLogin')
    isDeleted = request.args.get('isDeleted')
    lastLogin = request.args.get('lastLogin')
    lastActivity = request.args.get('lastActivity')

    groupName = request.args.get('groupName')

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasView']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        condition = ""
        offset_limit = ""
        join_with_groups = ""

        if isActive:
            condition += " IS_ACTIVE = " + isActive + " AND "

        if username:
            condition += " USERNAME LIKE '%" + username + "%'" + " AND "

        if firstname:
            condition += " FIRSTNAME LIKE '%" + firstname + "%'" + " AND "

        if lastname:
            condition += " LASTNAME LIKE '%" + lastname + "%'" + " AND "

        if fullname:
            condition += " FULLNAME LIKE '%" + fullname + "%'" + " AND "

        if email:
            condition += " EMAIL LIKE '%" + email + "%'" + " AND "

        if isBlock:
            condition += " IS_BLOCK = " + isBlock + " AND "

        if isLogin:
            condition += " IS_LOGIN = " + isLogin + " AND "

        if isDeleted:
            condition += " IS_DELETED = " + isDeleted + " AND "

        if lastLogin:
            condition += " LAST_LOGIN LIKE '" + lastLogin + "%'" + " AND "

        if lastActivity:
            condition += " LAST_ACTIVITY LIKE '" + lastActivity + "%'" + " AND "

        if offset and limit:
            offset_limit = "LIMIT "+ limit +" OFFSET "+ offset
        else:
            offset = 0
            limit = 0

        if groupName:
            join_with_groups = "a, FHIR247.UI_GROUPS b "
            condition += "b.name = '" + groupName + "'" + " AND "
            condition += "b.group_id = a.group_id " + " AND "

        if condition != '':
            condition = " WHERE " + condition[:-5]

        cmd = "SELECT user_id, username, firstname, lastname, fullname, email," \
              " TO_CHAR(last_login, 'yyyy-MM-dd HH:mm:ss'), TO_CHAR(last_activity, 'yyyy-MM-dd HH:mm:ss'), is_login, is_block, " \
              " TO_CHAR(first_login, 'yyyy-MM-dd HH:mm:ss'), TO_CHAR(last_pass_change, 'yyyy-MM-dd HH:mm:ss'), is_active, " \
              " TO_CHAR(created_date, 'yyyy-MM-dd HH:mm:ss'), created_by, TO_CHAR(updated_date, 'yyyy-MM-dd HH:mm:ss'), updated_by, is_deleted, " \
              " apikey, apisecret, token " \
              " FROM FHIR247.UI_USERS " + join_with_groups + condition +" ORDER BY user_id " + offset_limit

        conn = phoenixConn()
        cursor = conn.cursor()

        cursor.execute(cmd)
        listUser = cursor.fetchall()
        total = getCountDataOfTable('FHIR247.UI_USERS ' + join_with_groups + condition)

        conn.close()

        User = []
        for data in listUser:
            UserJSON = {}
            UserJSON["id"] = data[0]
            UserJSON["username"] = data[1]
            UserJSON["firstname"] = data[2]
            UserJSON["lastname"] = data[3]
            UserJSON["fullname"] = data[4]
            UserJSON["email"] = data[5]
            UserJSON["lastLogin"] = data[6]
            UserJSON["lastActivity"] = data[7]
            UserJSON["isLogin"] = data[8]
            UserJSON["isBlock"] = data[9]
            UserJSON["firstLogin"] = data[10]
            UserJSON["lastPassChange"] = data[11]
            UserJSON["isActive"] = data[12]
            UserJSON["createdDate"] = data[13]
            UserJSON["createdBy"] = data[14]
            UserJSON["updatedDate"] = data[15]
            UserJSON["updatedBy"] = data[16]
            UserJSON["isDeleted"] = data[17]
            UserJSON["apiKey"] = data[18]
            UserJSON["apiSecret"] = data[19]
            UserJSON["token"] = data[20]

            User.append(UserJSON)

        result = {"status": 200, "offset": offset, "limit": limit, "total": total, "data": User}
    else:
        result = {"status": errCode, "message": message}

    return result

def getUser(id):
    # validate access token
    userID = id
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasView']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"


    if errCode == 0:
        result = getUserbyID(userID)
    else:
        result = {"status": errCode, "message": message}

    return result

def addUser():
    errCode = 0

    #validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin']:
        errCode = 0
        message = "SuperAdmin"
    elif not privilegeMenu['hasInsert']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataUser = json.loads(data)

    #username
    if 'username' in dataUser and dataUser['username'] != '':
        username = dataUser['username']

        # validate username must uniqe value
        checkUsername = usernameValidate(username)
        if checkUsername['status'] > 200:
            errCode = checkUsername['status']
            message = checkUsername['message']
    else:
        errCode = 14002
        message = "Username is required."

    #firstname
    if 'firstname' in dataUser and dataUser['firstname'] != '':
        firstname = dataUser['firstname']
    else:
        errCode = 14003
        message = "Firstname is required."

    #lastname
    if 'lastname' in dataUser and dataUser['lastname'] != '':
        lastname = dataUser['lastname']
    else:
        errCode = 14004
        message = "Lastname is required."

    #fullname
    if 'fullname' in dataUser and dataUser['fullname'] != '':
        fullname = dataUser['fullname']
    else:
        errCode = 14005
        message = "Fullname is required."

    #email
    if 'email' in dataUser and dataUser['email'] != '':
        email = dataUser['email']

        # validate email must uniqe value
        checkEmail = emailValidate(email)
        if checkEmail['status'] > 200:
            errCode = checkEmail['status']
            message = checkEmail['message']
    else:
        errCode = 14006
        message = "Email is required."

    #password
    if 'password' in dataUser and dataUser['password'] != '':
        password = encryptPassword(dataUser['password'])
    else:
        errCode = 14007
        message = "Password is required."

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        #insert processing
        try:
            isActive = True
            now = datetime.now()
            createDate = now.strftime('%Y-%m-%d %H:%M:%S')

            #get userID
            userByToken = getUserIDbyToken(accessToken)
            if userByToken['super_admin'] and userByToken['status'] == 200:
                createBy = 'SuperAdmin'
            else:
                createBy = userByToken['userId']

            apikey = generateUniqeID('AP1247')
            apisecret = generateUniqeID('53C247')

            # insert user
            cmd = "UPSERT INTO FHIR247.UI_USERS " \
                  "(USER_ID, USERNAME, FIRSTNAME, LASTNAME, FULLNAME, EMAIL, PASSWORD, IS_ACTIVE, CREATED_DATE, CREATED_BY, APIKEY, APISECRET) " \
                  " VALUES" \
                  "('"+ generateUniqeID('U53247') + "','" + username + "','" + firstname + "','" + lastname + "','" + fullname + "','" + email + "','" + password + "'," + str(isActive) + ", TO_DATE('" + createDate + "', 'yyyy-MM-dd HH:mm:ss'),'" + createBy + "','" + apikey + "','" + apisecret + "')"
            cursor.execute(cmd)

            errCode = 200
            message = "User have been insert."
        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def updateUser(id):
    errCode = 0
    userID = id

    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    #check user
    checkUserID = getUserbyID(userID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkUserID['status'] > 200:
        errCode = 14002
        message = checkUserID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasUpdate']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataUser = json.loads(data)

    fieldsNameUsers = ""
    valuesNameUsers = ""

    # username
    if 'username' in dataUser and dataUser['username'] != '':
        username = dataUser['username']
        fieldsNameUsers += "username,"
        valuesNameUsers += "'"+ username + "',"

        # validate username must uniqe value
        checkUsername = usernameValidate(username)
        if checkUsername['status'] > 200:
            errCode = checkUsername['status']
            message = checkUsername['message']

    # firstname
    if 'firstname' in dataUser and dataUser['firstname'] != '':
        firstname = dataUser['firstname']
        fieldsNameUsers += "firstname,"
        valuesNameUsers += "'" + firstname + "',"

    # lastname
    if 'lastname' in dataUser and dataUser['lastname'] != '':
        lastname = dataUser['lastname']
        fieldsNameUsers += "lastname,"
        valuesNameUsers += "'" + lastname + "',"

    # fullname
    if 'fullname' in dataUser and dataUser['fullname'] != '':
        fullname = dataUser['fullname']
        fieldsNameUsers += "fullname,"
        valuesNameUsers += "'" + fullname + "',"

    # email
    if 'email' in dataUser and dataUser['email'] != '':
        email = dataUser['email']
        fieldsNameUsers += "email,"
        valuesNameUsers += "'" + email + "',"

        # validate email must uniqe value
        checkEmail = emailValidate(email)
        if checkEmail['status'] > 200:
            errCode = checkEmail['status']
            message = checkEmail['message']

    # password
    if 'password' in dataUser and dataUser['password'] != '':
        password = encryptPassword(dataUser['password'])
        fieldsNameUsers += "password,"
        valuesNameUsers += "'" + password + "',"

    # isLogin
    if 'isLogin' in dataUser and dataUser['isLogin'] != '':
        isLogin = dataUser['isLogin']
        fieldsNameUsers += "is_login,"
        valuesNameUsers += str(isLogin) + ","

    # isBlock
    if 'isBlock' in dataUser and dataUser['isBlock'] != '':
        isBlock = dataUser['isBlock']
        fieldsNameUsers += "is_block,"
        valuesNameUsers += str(isBlock) + ","

    #isActive
    if 'isActive' in dataUser and dataUser['isActive'] != '':
        isActive = dataUser['isActive']
        fieldsNameUsers += "is_active,"
        valuesNameUsers += str(isActive) + ","

    #isDeleted
    if 'isDeleted' in dataUser and dataUser['isDeleted'] != '':
        isDeleted = dataUser['isDeleted']
        fieldsNameUsers += "is_deleted,"
        valuesNameUsers += str(isDeleted) + ","

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:
            now = datetime.now()
            updatedDate = now.strftime('%Y-%m-%d %H:%M:%S')

            # get userID
            userByToken = getUserIDbyToken(accessToken)
            if userByToken['super_admin'] and userByToken['status'] == 200:
                updateBy = 'SuperAdmin'
            else:
                updateBy = userByToken['userId']

            #set update by and update date
            fieldsNameUsers += "updated_by, updated_date"
            valuesNameUsers += "'" + updateBy + "', TO_DATE('"+ updatedDate +"', 'yyyy-MM-dd HH:mm:ss')"


            #upsert user
            cmd = "UPSERT INTO FHIR247.UI_USERS(user_id, "+ fieldsNameUsers +") SELECT user_id, "+ valuesNameUsers +"  FROM FHIR247.UI_USERS WHERE user_id = '" + userID + "'"
            cursor.execute(cmd)

            result = getUserbyID(userID)

            if result['status'] == 200:
                result = {"status": result['status'] , "message": "User have been updated.", "data": result['data']}
            else:
                result = {"status": result['status'], "message": result['message']}

        except OSError as err:
            errCode = 13002
            message = err

            result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def deleteUser(id):
    errCode = 0
    userID = id

    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    #check user
    checkUserID = getUserbyID(userID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkUserID['status'] > 200:
        errCode = 14002
        message = checkUserID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasDelete']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # deleted processing
        try:
            now = datetime.now()
            updatedDate = now.strftime('%Y-%m-%d %H:%M:%S')

            # get userID
            userByToken = getUserIDbyToken(accessToken)
            if userByToken['super_admin'] and userByToken['status'] == 200:
                updateBy = 'SuperAdmin'
            else:
                updateBy = userByToken['userId']

            # set update by and update date
            fieldsNameUsers = "updated_by, updated_date, is_deleted, is_active"
            valuesNameUsers = "'" + updateBy + "', TO_DATE('" + updatedDate + "', 'yyyy-MM-dd HH:mm:ss'), TRUE, FALSE "

            # upsert user
            cmd = "UPSERT INTO FHIR247.UI_USERS(user_id, " + fieldsNameUsers + ") SELECT user_id, " + valuesNameUsers + "  FROM FHIR247.UI_USERS WHERE user_id = '" + userID + "'"
            cursor.execute(cmd)

            errCode = 200
            message = "User have been deleted."

        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

#group management
def getGroups():
    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    groupName = request.args.get('groupName')

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasView']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        condition = ""
        offset_limit = ""

        if groupName:
            condition += "name = '" + groupName + "'"

        if condition != '':
            condition = " WHERE " + condition

        if offset and limit:
            offset_limit = "LIMIT "+ limit +" OFFSET "+ offset
        else:
            offset = 0
            limit = 0

        cmd = "SELECT group_id, name, description FROM FHIR247.UI_GROUPS " + condition + " ORDER BY group_id " + offset_limit

        conn = phoenixConn()
        cursor = conn.cursor()

        cursor.execute(cmd)
        listGroup = cursor.fetchall()

        total = getCountDataOfTable('FHIR247.UI_GROUPS ' + condition)
        conn.close()

        Group = []
        for data in listGroup:
            GroupJSON = {}
            GroupJSON["id"] = data[0]
            GroupJSON["name"] = data[1]
            GroupJSON["description"] = data[2]

            Group.append(GroupJSON)

        result = {"status": 200, "offset": offset, "limit": limit, "total": total, "data": Group}
    else:
        result = {"status": errCode, "message": message}

    return result

def addGroup():
    errCode = 0

    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin']:
        errCode = 0
        message = "SuperAdmin"
    elif not privilegeMenu['hasInsert']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataGroup = json.loads(data)

    # name
    if 'name' in dataGroup and dataGroup['name'] != '':
        name = dataGroup['name']

        # validate username must uniqe value
        checkGroupName = groupNameValidate(name)
        if checkGroupName['status'] > 200:
            errCode = checkGroupName['status']
            message = checkGroupName['message']
    else:
        errCode = 14002
        message = "Group name is required."

    # description
    if 'description' in dataGroup and dataGroup['description'] != '':
        description = dataGroup['description']
    else:
        errCode = 14003
        message = "Group description is required."


    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:
            # insert group
            cmd = "UPSERT INTO FHIR247.UI_GROUPS (GROUP_ID, NAME, DESCRIPTION) " \
                  " VALUES ('" + generateUniqeID('9RP247') + "','" + name + "','" + description+ "')"
            cursor.execute(cmd)

            errCode = 200
            message = "Group have been insert."
        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def getGroup(id):
    # validate access token
    groupID = id
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasView']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        result = getGroupbyID(groupID)
    else:
        result = {"status": errCode, "message": message}

    return result

def updateGroup(id):
    errCode = 0
    groupID = id

    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    # check group
    checkGroupID = getGroupbyID(groupID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkGroupID['status'] > 200:
        errCode = 14002
        message = checkGroupID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasUpdate']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataGroup = json.loads(data)

    fieldsNameGroups = ""
    valuesNameGroups = ""

    # name
    if 'name' in dataGroup and dataGroup['name'] != '':
        name = dataGroup['name']
        fieldsNameGroups += "name,"
        valuesNameGroups += "'" + name + "',"

        # validate username must uniqe value
        checkGroupname = groupNameValidate(name)
        if checkGroupname['status'] > 200:
            errCode = checkGroupname['status']
            message = checkGroupname['message']

    # description
    if 'description' in dataGroup and dataGroup['description'] != '':
        description = dataGroup['description']
        fieldsNameGroups += "description,"
        valuesNameGroups += "'" + description + "',"


    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:

            # upsert group
            cmd = "UPSERT INTO FHIR247.UI_GROUPS(group_id, " + fieldsNameGroups[:-1] + ") SELECT group_id, " + valuesNameGroups[:-1] + " FROM FHIR247.UI_GROUPS WHERE group_id = '" + groupID + "'"
            cursor.execute(cmd)

            result = getGroupbyID(groupID)

            if result['status'] == 200:
                result = {"status": result['status'], "message": "Group have been updated.", "data": result['data']}
            else:
                result = {"status": result['status'], "message": result['message']}

        except OSError as err:
            errCode = 13002
            message = err

            result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def deleteGroup(id):
    errCode = 0
    groupID = id

    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    # check group
    checkGroupID = getGroupbyID(groupID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkGroupID['status'] > 200:
        errCode = 14002
        message = checkGroupID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasDelete']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # deleted processing
        try:
            #delete group
            cmd = "DELETE FROM FHIR247.UI_GROUPS WHERE group_id = '"+ groupID +"' "
            cursor.execute(cmd)

            # upsert user
            cmd = "UPSERT INTO FHIR247.UI_USERS(user_id, group_id) SELECT user_id, null  FROM FHIR247.UI_USERS WHERE group_id = '" + groupID + "'"
            cursor.execute(cmd)

            errCode = 200
            message = "Group have been deleted."

        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def getMembers(id):
    # validate access token
    groupID = id
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    status = request.args.get('status')

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    # check group
    checkGroupID = getGroupbyID(groupID)

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkGroupID['status'] > 200:
        errCode = 14002
        message = checkGroupID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasUpdate']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        offset_limit = ""

        if offset and limit:
            offset_limit = "LIMIT "+ limit +" OFFSET "+ offset
        else:
            offset = 0
            limit = 0

        if status == 'available-user' and status != '':
            cmd =  "SELECT user_id, firstname, lastname, fullname FROM FHIR247.UI_USERS WHERE group_id IS NULL AND is_active = TRUE "

            total = getCountDataOfTable("FHIR247.UI_USERS WHERE group_id IS NULL AND is_active = TRUE ")
        else:
            cmd = "SELECT user_id, firstname, lastname, fullname FROM FHIR247.UI_USERS u, FHIR247.UI_GROUPS g " \
              "WHERE u.group_id = g.group_id AND g.group_id = '"+ groupID +"' ORDER BY g.group_id " + offset_limit

            total = getCountDataOfTable("FHIR247.UI_USERS WHERE group_id = '" + groupID + "' ")

        conn = phoenixConn()
        cursor = conn.cursor()

        cursor.execute(cmd)
        listGroup = cursor.fetchall()
        conn.close()

        Group = []
        for data in listGroup:
            GroupJSON = {}
            GroupJSON["id"] = data[0]
            GroupJSON["firstname"] = data[1]
            GroupJSON["lastname"] = data[2]
            GroupJSON["fullname"] = data[3]

            Group.append(GroupJSON)

        result = {"status": 200, "offset": offset, "limit": limit, "total": total, "data": Group}

    else:
        result = {"status": errCode, "message": message}

    return result

def updateMember(id):
    errCode = 0
    groupID = id

    #type member
    memberType = request.args.get('type')

    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    # check group
    checkGroupID = getGroupbyID(groupID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkGroupID['status'] > 200:
        errCode = 14002
        message = checkGroupID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasUpdate']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataGroup = json.loads(data)

    fieldsNameGroups = ""
    valuesNameGroups = ""

    # name
    if 'userId' in dataGroup and dataGroup['userId'] != '':
        userID = dataGroup['userId']
        fieldsNameGroups += "group_id"

        if memberType.lower() == 'create':
            valuesNameGroups += "'" + groupID + "'"
            message = "Member have been add in this group."
        else:
            valuesNameGroups += "null"
            message = "Member have been remove in this group."

        # validate username must uniqe value
        checkUserID = getUserbyID(userID)
        if checkUserID['status'] > 200:
            errCode = checkUserID['status']
            message = checkUserID['message']

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:
            # upsert user
            cmd = "UPSERT INTO FHIR247.UI_USERS(user_id, " + fieldsNameGroups + ") SELECT user_id, " + valuesNameGroups + \
                  " FROM FHIR247.UI_USERS WHERE user_id = '" + userID + "'"
            cursor.execute(cmd)

            errCode = 200

        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

#menu management
def getMenus():
    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    menuName = request.args.get('name')
    menuLabel = request.args.get('label')
    menuActived = request.args.get('isActive')

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasView']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        condition = ""
        offset_limit = ""

        if menuName:
            condition += "menu_name = '" + menuName + "',"

        if menuLabel:
            condition += "menu_label = '" + menuLabel + "',"

        if menuActived:
            condition += "menu_active = " + str(menuActived) + ","


        if condition != '':
            condition = " WHERE " + condition[:-1]

        if offset and limit:
            offset_limit = "LIMIT " + limit + " OFFSET " + offset
        else:
            offset = 0
            limit = 0

        cmd = "SELECT menu_id, menu_parent, menu_label, menu_name, menu_description, menu_active, menu_url, menu_config, menu_icon, menu_sort " \
              "FROM FHIR247.UI_MENU " + condition + " ORDER BY menu_id " + offset_limit

        conn = phoenixConn()
        cursor = conn.cursor()

        cursor.execute(cmd)
        listMenu = cursor.fetchall()

        total = getCountDataOfTable('FHIR247.UI_MENU ' + condition)
        conn.close()

        Menu = []
        SubMenu = []

        for data in listMenu:
            if data[1] == None:
                MenuJSON = {}
                MenuJSON["id"] = data[0]
                MenuJSON["parent"] = data[1]
                MenuJSON["label"] = data[2]
                MenuJSON["name"] = data[3]
                MenuJSON["description"] = data[4]
                MenuJSON["active"] = data[5]
                MenuJSON["url"] = data[6]
                MenuJSON["config"] = data[7]
                MenuJSON["icon"] = data[8]
                MenuJSON["sort"] = data[9]
                MenuJSON["submenu"] = []

                Menu.append(MenuJSON)
            else:
                MenuJSON = {}
                MenuJSON["id"] = data[0]
                MenuJSON["parent"] = data[1]
                MenuJSON["label"] = data[2]
                MenuJSON["name"] = data[3]
                MenuJSON["description"] = data[4]
                MenuJSON["active"] = data[5]
                MenuJSON["url"] = data[6]
                MenuJSON["config"] = data[7]
                MenuJSON["icon"] = data[8]
                MenuJSON["sort"] = data[9]
                MenuJSON["submenu"] = []

                SubMenu.append(MenuJSON)


        for i, parent in enumerate(Menu):
            for j, parent2 in enumerate(SubMenu):
                if parent["id"] == parent2["parent"]:
                    Menu[i]["submenu"].append(SubMenu[j])


        result = {"status": 200, "offset": offset, "limit": limit, "total": total, "data": Menu}
    else:
        result = {"status": errCode, "message": message}

    return result

def addMenu():
    errCode = 0

    # validate access token
    menuID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin']:
        errCode = 0
        message = "SuperAdmin"
    elif not privilegeMenu['hasInsert']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataMenu = json.loads(data)

    # parent
    if 'parent' in dataMenu and dataMenu['parent'] != '':
        parent = dataMenu['parent']

        # validate menuID/Parent
        checkMenuID = getMenubyID(parent)
        if checkMenuID['status'] > 200:
            errCode = checkMenuID['status']
            message = checkMenuID['message']
    else:
        parent = ""

    # label
    if 'label' in dataMenu and dataMenu['label'] != '':
        label = dataMenu['label']
    else:
        errCode = 14003
        message = "Menu label is required."

    # name
    if 'name' in dataMenu and dataMenu['name'] != '':
        name = dataMenu['name']
        name = name.lower()
        name = name.replace(" ", "_")

        checkMenuName = getMenuByName(name)
        if checkMenuName['status'] > 200:
            errCode = checkMenuName['status']
            message = checkMenuName['message']
    else:
        errCode = 14004
        message = "Menu name is required."

    # description
    if 'description' in dataMenu and dataMenu['description'] != '':
        description = dataMenu['description']
    else:
        errCode = 14005
        message = "Description is required."

    # active
    if 'active' in dataMenu and dataMenu['active'] != '':
        active = dataMenu['active']
    else:
        active = True

    # url
    if 'url' in dataMenu and dataMenu['url'] != '':
        url = dataMenu['url']
    else:
        url = '#'

    # config
    if 'config' in dataMenu and dataMenu['config'] != '':
        config = dataMenu['config']
    else:
        config = ""

    if 'icon' in dataMenu and dataMenu['icon'] != '':
        icon = dataMenu['icon']
    else:
        errCode = 14007
        message = "Icon is required."

    if 'sort' in dataMenu and dataMenu['sort'] != '':
        sort = dataMenu['sort']
    else:
        sort = 1


    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:
            # insert menu
            cmd = "UPSERT INTO FHIR247.UI_MENU " \
                  "(MENU_ID, MENU_PARENT, MENU_LABEL, MENU_NAME, MENU_DESCRIPTION, MENU_ACTIVE, MENU_URL, MENU_CONFIG, MENU_ICON, MENU_SORT) " \
                  " VALUES" \
                  "('" + generateUniqeID(
                'M3N247') + "','" + parent + "','" + label + "','" + name + "','" + description+ "', " + str(active) + ",'" + url + "','" + config + "', '" + icon + "', " + str(sort) + ")"
            cursor.execute(cmd)

            errCode = 200
            message = "Menu have been insert."
        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def getMenu(id):
    # validate access token
    menuID = id
    menuAccessID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuAccessID)

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasView']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        result = getMenubyID(menuID)
    else:
        result = {"status": errCode, "message": message}

    return result

def updateMenu(id):
    errCode = 0
    menuID = id

    # validate access token
    menuAccessID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuAccessID)

    # check menu
    checkMenuID = getMenubyID(menuID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkMenuID['status'] > 200:
        errCode = 14002
        message = checkMenuID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasUpdate']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataMenu = json.loads(data)

    fieldsNameMenu = ""
    valuesNameMenu = ""

    # parent
    if 'parent' in dataMenu and dataMenu['parent'] != '':
        parent = dataMenu['parent']
        fieldsNameMenu += "menu_parent,"
        valuesNameMenu += "'" + parent + "',"

        # validate menuID/Parent
        checkMenuID = getMenubyID(parent)
        if checkMenuID['status'] > 200:
            errCode = checkMenuID['status']
            message = checkMenuID['message']

    # label
    if 'label' in dataMenu and dataMenu['label'] != '':
        label = dataMenu['label']
        fieldsNameMenu += "menu_label,"
        valuesNameMenu += "'" + label + "',"

    # name
    if 'name' in dataMenu and dataMenu['name'] != '':
        name = dataMenu['name']
        name = name.lower()
        name = name.replace(" ", "_")

        fieldsNameMenu += "menu_name,"
        valuesNameMenu += "'" + name + "',"

        checkMenuName = getMenuByName(name)
        if checkMenuName['status'] > 200:
            errCode = checkMenuName['status']
            message = checkMenuName['message']

    # description
    if 'description' in dataMenu and dataMenu['description'] != '':
        description = dataMenu['description']

        fieldsNameMenu += "menu_description,"
        valuesNameMenu += "'" + description + "',"

    # active
    if 'active' in dataMenu and dataMenu['active'] != '':
        active = dataMenu['active']
        fieldsNameMenu += "menu_active,"
        valuesNameMenu +=  str(active) + ","

    # url
    if 'url' in dataMenu and dataMenu['url'] != '':
        url = dataMenu['url']

        fieldsNameMenu += "menu_url,"
        valuesNameMenu += "'" + url + "',"

    # config
    if 'config' in dataMenu and dataMenu['config'] != '':
        config = dataMenu['config']

        fieldsNameMenu += "menu_config,"
        valuesNameMenu += "'" + config + "',"

    if 'icon' in dataMenu and dataMenu['icon'] != '':
        icon = dataMenu['icon']

        fieldsNameMenu += "menu_icon,"
        valuesNameMenu += "'" + icon + "',"

    if 'sort' in dataMenu and dataMenu['sort'] != '':
        sort = dataMenu['sort']

        fieldsNameMenu += "menu_sort,"
        valuesNameMenu +=  str(sort) + ","

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:

            # upsert menu
            cmd = "UPSERT INTO FHIR247.UI_MENU(menu_id, " + fieldsNameMenu[:-1] + ") SELECT menu_id, " + valuesNameMenu[:-1] + \
                  " FROM FHIR247.UI_MENU WHERE menu_id = '" + menuID + "'"
            cursor.execute(cmd)

            result = getMenubyID(menuID)

            if result['status'] == 200:
                result = {"status": result['status'], "message": "Menu have been updated.", "data": result['data']}
            else:
                result = {"status": result['status'], "message": result['message']}

        except OSError as err:
            errCode = 13002
            message = err

            result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def deleteMenu(id):
    errCode = 0
    menuID = id

    # validate access token
    menuAccessID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuAccessID)

    # check group
    checkMenuID = getMenubyID(menuID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkMenuID['status'] > 200:
        errCode = 14002
        message = checkMenuID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasDelete']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # deleted processing
        try:
            # delete menu
            cmd = "DELETE FROM FHIR247.UI_MENU WHERE menu_id = '" + menuID + "' OR menu_parent = '" + menuID+ "' "
            cursor.execute(cmd)

            # delete privilege menu
            cmd = "DELETE FROM FHIR247.UI_PRIVILEGES WHERE menu_id = '" + menuID + "' "
            cursor.execute(cmd)

            errCode = 200
            message = "Menu have been deleted."

        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

#privileges management
def getPrivileges(id):
    # validate access token
    groupID = id
    menuAccessID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuAccessID)

    # check group
    checkGroupID = getGroupbyID(groupID)

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif checkGroupID['status'] > 200:
        errCode = 14004
        message = checkGroupID['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasView']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        result = getMenuPrivileges(groupID)
    else:
        result = {"status": errCode, "message": message}

    return result

def addPrivilege(id):
    errCode = 0
    groupID = id

    # validate access token
    menuAccessID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuAccessID)

    # check group
    checkGroupID = getGroupbyID(groupID)


    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif checkGroupID['status'] > 200:
        errCode = 14002
        message = checkGroupID['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasInsert']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataPrivilege = json.loads(data)

    # menu_id
    if 'menuId' in dataPrivilege and dataPrivilege['menuId'] != '':
        menuID = dataPrivilege['menuId']

        # validate menu
        checkMenuID = getMenubyID(menuID)
        if checkMenuID['status'] > 200:
            errCode = checkMenuID['status']
            message = checkMenuID['message']

    # has insert
    if 'hasInsert' in dataPrivilege and dataPrivilege['hasInsert'] != '':
        hasInsert = str(dataPrivilege['hasInsert'])
    else:
        errCode = 14004
        message = "Has insert is required"

    # has update
    if 'hasUpdate' in dataPrivilege and dataPrivilege['hasUpdate'] != '':
        hasUpdate = str(dataPrivilege['hasUpdate'])
    else:
        errCode = 14005
        message = "Has update is required"

    # has delete
    if 'hasDelete' in dataPrivilege and dataPrivilege['hasDelete'] != '':
        hasDelete = str(dataPrivilege['hasDelete'])
    else:
        errCode = 14006
        message = "Has Delete is required"

    # has view
    if 'hasView' in dataPrivilege and dataPrivilege['hasView'] != '':
        hasView = str(dataPrivilege['hasView'])
    else:
        errCode = 14006
        message = "Has View is required"

    # has approval
    if 'hasApproval' in dataPrivilege and dataPrivilege['hasApproval'] != '':
        hasApproval = str(dataPrivilege['hasApproval'])
    else:
        errCode = 14006
        message = "Has Approval is required"


    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:
            # upsert privilege
            cmd = "UPSERT INTO FHIR247.UI_PRIVILEGES(privilege_id, has_insert, has_update, has_delete, has_view, has_approval, group_id, menu_id) " \
                  "VALUES('"+ generateUniqeID('PR1247') +"', "+ hasInsert +","+ hasUpdate +","+ hasDelete +","+ hasView +","+ hasApproval +", '"+ groupID +"', '"+ menuID +"')"
            cursor.execute(cmd)

            errCode = 200
            message = "Menu privilege have been add in this group."

        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def getPrivilege(id, privilege_id):
    # validate access token
    groupID = id
    privilegeID = privilege_id
    menuAccessID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuAccessID)

    #check group
    checkGroupID = getGroupbyID(groupID)

    #check privilege
    checkPrivilegeID = getPrivilegeByID(privilegeID)

    errCode = 0

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif checkGroupID['status'] > 200:
        errCode = 14004
        message = checkGroupID['message']
    elif checkPrivilegeID['status'] > 200:
        errCode = 14005
        message = checkPrivilegeID['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasView']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    if errCode == 0:
        result = getPrivilegeByID(privilegeID)
    else:
        result = {"status": errCode, "message": message}

    return result

def updatePrivilege(id, privilege_id):
    errCode = 0
    groupID = id
    privilegeID = privilege_id

    # validate access token
    menuAccessID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuAccessID)

    # check group
    checkGroupID = getGroupbyID(groupID)

    # check privilege
    checkPrivilegeID = getPrivilegeByID(privilegeID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif checkGroupID['status'] > 200:
        errCode = 14004
        message = checkGroupID['message']
    elif checkPrivilegeID['status'] > 200:
        errCode = 14005
        message = checkPrivilegeID['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasUpdate']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"

    # parsing request
    data = request.data
    dataPrivilege = json.loads(data)

    fieldsNamePrivilege = ""
    valuesNamePrivilege = ""

    # menu_id
    if 'menuId' in dataPrivilege and dataPrivilege['menuId'] != '':
        menuID = dataPrivilege['menuId']
        fieldsNamePrivilege += "menu_id,"
        valuesNamePrivilege += "'" + menuID + "',"

        # validate menu
        checkMenuID = getMenubyID(menuID)
        if checkMenuID['status'] > 200:
            errCode = checkMenuID['status']
            message = checkMenuID['message']

    # has insert
    if 'hasInsert' in dataPrivilege and dataPrivilege['hasInsert'] != '':
        hasInsert = str(dataPrivilege['hasInsert'])

        fieldsNamePrivilege += "has_insert,"
        valuesNamePrivilege +=  str(hasInsert) + ","

    # has update
    if 'hasUpdate' in dataPrivilege and dataPrivilege['hasUpdate'] != '':
        hasUpdate = str(dataPrivilege['hasUpdate'])

        fieldsNamePrivilege += "has_update,"
        valuesNamePrivilege += str(hasUpdate) + ","

    # has delete
    if 'hasDelete' in dataPrivilege and dataPrivilege['hasDelete'] != '':
        hasDelete = str(dataPrivilege['hasDelete'])

        fieldsNamePrivilege += "has_delete,"
        valuesNamePrivilege += str(hasDelete) + ","

    # has view
    if 'hasView' in dataPrivilege and dataPrivilege['hasView'] != '':
        hasView = str(dataPrivilege['hasView'])

        fieldsNamePrivilege += "has_view,"
        valuesNamePrivilege += str(hasView) + ","

    # has approval
    if 'hasApproval' in dataPrivilege and dataPrivilege['hasApproval'] != '':
        hasApproval = str(dataPrivilege['hasApproval'])

        fieldsNamePrivilege += "has_approval,"
        valuesNamePrivilege += str(hasApproval) + ","

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:
            # upsert privilege
            cmd = "UPSERT INTO FHIR247.UI_PRIVILEGES(privilege_id, " + fieldsNamePrivilege[:-1] + ") SELECT privilege_id, " + valuesNamePrivilege[:-1] + \
                  " FROM FHIR247.UI_PRIVILEGES WHERE privilege_id = '" + privilegeID + "'"
            cursor.execute(cmd)

            result = getPrivilegeByID(privilegeID)

            if result['status'] == 200:
                result = {"status": result['status'], "message": "Menu privilege have been update in this group.", "data": result['data']}
            else:
                result = {"status": result['status'], "message": result['message']}

        except OSError as err:
            errCode = 13002
            message = err

            result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def deletePrivilege(id, privilege_id):
    errCode = 0
    groupID = id
    privilegeID = privilege_id

    # validate access token
    menuAccessID = request.headers['menuId']
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check privilege menu
    privilegeMenu = checkPrivilegeMenu(accessToken, menuAccessID)

    # check group
    checkGroupID = getGroupbyID(groupID)

    # check privilege
    checkPrivilegeID = getPrivilegeByID(privilegeID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    elif privilegeMenu['status'] > 200:
        errCode = 14002
        message = privilegeMenu['message']
    elif checkGroupID['status'] > 200:
        errCode = 14004
        message = checkGroupID['message']
    elif checkPrivilegeID['status'] > 200:
        errCode = 14005
        message = checkPrivilegeID['message']
    elif privilegeMenu['super_admin'] or privilegeMenu['hasDelete']:
        errCode = 0
        message = "Access is permitted"
    else:
        errCode = 14003
        message = "Permission denied to access this menu!"


    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        # insert processing
        try:
            # delete privilege
            cmd = "DELETE FROM FHIR247.UI_PRIVILEGES WHERE privilege_id = '" + privilegeID + "'"
            cursor.execute(cmd)

            errCode = 200
            message = "Menu privilege have been update in this group."

        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result





