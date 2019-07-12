import phoenixdb
import phoenixdb.cursor
from datetime import datetime, timedelta
import hashlib, sys

from config import FHIR247_DB

def generateNewToken(apikey, apisecret):
    connDB = phoenixConn()
    cursor = connDB.cursor()

    cmd = "SELECT user_id, TO_CHAR(expiry_token, 'yyyy-MM-dd HH:mm:ss'), token FROM FHIR247.UI_USERS WHERE apikey = ? AND apisecret= ? "
    cursor.execute(cmd, (apikey, apisecret),)
    dataUser = cursor.fetchall()

    result = {}
    if len(dataUser) > 0:
        #check expiry token existing
        for data in dataUser:
            userID = data[0]
            expiry = data[1]
            token = data[2]

        if token != None:
            if expiry > datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                print("Token masih aktif")
                newToken = token
                expiryToken = expiry
            else:
                # set token 1 hours
                print("Token expired 1")
                newToken = generateUniqeID('T0K247')
                expiryTokenOneHours = datetime.now() + timedelta(hours=1)
                expiryToken = expiryTokenOneHours.strftime('%Y-%m-%d %H:%M:%S')

                # upsert
                cmd = "UPSERT INTO FHIR247.UI_USERS(user_id, token, expiry_token) SELECT user_id, '" + newToken + "', TO_DATE('" + expiryToken + "', 'yyyy-MM-dd HH:mm:ss') FROM FHIR247.UI_USERS WHERE user_id = '" + userID + "'"
                cursor.execute(cmd)
        else:
            #set token 1 hours
            print("Token expired 2")
            newToken = generateUniqeID('T0K247')
            expiryTokenOneHours = datetime.now() + timedelta(hours=1)
            expiryToken = expiryTokenOneHours.strftime('%Y-%m-%d %H:%M:%S')

            #upsert
            cmd = "UPSERT INTO FHIR247.UI_USERS(user_id, token, expiry_token) SELECT user_id, '"+ newToken +"', TO_DATE('"+ expiryToken +"', 'yyyy-MM-dd HH:mm:ss') FROM FHIR247.UI_USERS WHERE user_id = '"+ userID + "'"
            cursor.execute(cmd)

        result = {"status": 200, "token": newToken, "expiry": expiryToken}
    else:
        result = {"status": 200, "message": "Apikey and apisecret is not exist."}

    connDB.close()

    return result

def tokenValidate(token):
    result = {}
    resultSecret = getApikeyApiSecretSuperAdmin(token)

    if resultSecret:
        result = {"status": 200, "message": "This is token SuperAdmin!"}
    else:
        #check from db
        connDB = phoenixConn()
        cursor = connDB.cursor()

        cmd = "SELECT user_id, TO_CHAR(expiry_token, 'yyyy-MM-dd HH:mm:ss'), token FROM FHIR247.UI_USERS WHERE token = '"+ token +"' "
        cursor.execute(cmd)
        dataUser = cursor.fetchall()

        if len(dataUser) > 0:
            for data in dataUser:
                # userID = data[0]
                expiry = data[1]
                # token = data[2]

            if expiry > datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                result = {"status": 200, "message": "Token is valid!"}
            else:
                result = {"status": 403, "message": "Token is expired!"}
        else:
            result = {"status": 404, "message": "Token is not found!"}

        connDB.close()

    return result

def usernameValidate(username):
    result = {}
    #check from db
    connDB = phoenixConn()
    cursor = connDB.cursor()

    cmd = "SELECT user_id FROM FHIR247.UI_USERS WHERE username = '"+ username +"' "
    cursor.execute(cmd)
    dataUser = cursor.fetchall()

    if len(dataUser) > 0:
        result = {"status": 403, "message": "Username already exist!"}
    else:
        result = {"status": 200, "message": "Username ready to use."}

    connDB.close()

    return result

def emailValidate(email):
    result = {}
    #check from db
    connDB = phoenixConn()
    cursor = connDB.cursor()

    cmd = "SELECT user_id FROM FHIR247.UI_USERS WHERE email = '"+ email +"' "
    cursor.execute(cmd)
    dataUser = cursor.fetchall()

    if len(dataUser) > 0:
        result = {"status": 403, "message": "Email already exist!"}
    else:
        result = {"status": 200, "message": "Email ready to use."}

    connDB.close()

    return result

def getCountDataOfTable(table):
    connDB = phoenixConn()
    cursor = connDB.cursor()

    cmd = "SELECT COUNT(1) total FROM " + table
    cursor.execute(cmd)
    total = cursor.fetchone()

    connDB.close()

    return total[0]

def getUserIDbyToken(token):
    resultSecret = getApikeyApiSecretSuperAdmin(token)

    if resultSecret:
        result = {"status": 200, "message": "This is token SuperAdmin!", "super_admin": True}
    else:
        #check from db
        connDB = phoenixConn()
        cursor = connDB.cursor()

        cmd = "SELECT user_id FROM FHIR247.UI_USERS WHERE token = '"+ token +"' "
        cursor.execute(cmd)
        dataUser = cursor.fetchone()

        if len(dataUser) > 0:
            userID = dataUser[0]
            result = {"status": 200, "userId": userID, "super_admin": False}

        else:
            result = {"status": 404, "message": "Token is not found!"}

        connDB.close()

    return result

def getUserbyID(id):
    cmd = "SELECT user_id, username, firstname, lastname, fullname, email," \
          " TO_CHAR(last_login, 'yyyy-MM-dd HH:mm:ss'), TO_CHAR(last_activity, 'yyyy-MM-dd HH:mm:ss'), is_login, is_block, " \
          " TO_CHAR(first_login, 'yyyy-MM-dd HH:mm:ss'), TO_CHAR(last_pass_change, 'yyyy-MM-dd HH:mm:ss'), is_active, " \
          " TO_CHAR(created_date, 'yyyy-MM-dd HH:mm:ss'), created_by, TO_CHAR(updated_date, 'yyyy-MM-dd HH:mm:ss'), updated_by, is_deleted, " \
          " apikey, apisecret, token " \
          " FROM FHIR247.UI_USERS WHERE user_id = '" + id + "' ORDER BY user_id "

    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listUser = cursor.fetchall()

    conn.close()

    if len(listUser) > 0:
        UserJSON = {}
        for data in listUser:
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

        result = {"status": 200, "data": UserJSON}
    else:
        result = {"status": 404, "message": "User ID is not found."}

    return result

def getUserByEmailOrUsername(username, email):
    cmd = "SELECT user_id, username, firstname, lastname, fullname, email," \
          " TO_CHAR(last_login, 'yyyy-MM-dd HH:mm:ss'), TO_CHAR(last_activity, 'yyyy-MM-dd HH:mm:ss'), is_login, is_block, " \
          " TO_CHAR(first_login, 'yyyy-MM-dd HH:mm:ss'), TO_CHAR(last_pass_change, 'yyyy-MM-dd HH:mm:ss'), is_active, " \
          " TO_CHAR(created_date, 'yyyy-MM-dd HH:mm:ss'), created_by, TO_CHAR(updated_date, 'yyyy-MM-dd HH:mm:ss'), updated_by, is_deleted, " \
          " apikey, apisecret, token, group_id, password " \
          " FROM FHIR247.UI_USERS WHERE username = '" + username + "' OR email = '"+ email +"' ORDER BY user_id "

    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listUser = cursor.fetchall()

    conn.close()

    if len(listUser) > 0:
        UserJSON = {}
        for data in listUser:
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
            UserJSON["groupId"] = data[21]
            UserJSON["password"] = data[22]

        result = {"status": 200, "data": UserJSON}
    else:
        result = {"status": 404, "message": "User is not found."}

    return result

def checkPrivilegeMenu(token, menu):
    resultSecret = getApikeyApiSecretSuperAdmin(token)

    if resultSecret:
        result = {"status": 200, "message": "This is token SuperAdmin!", "super_admin": True}
    else:
        #check from db
        connDB = phoenixConn()
        cursor = connDB.cursor()

        cmd = "SELECT privilege_id, has_insert, has_update, has_delete, has_view FROM FHIR247.UI_PRIVILEGES p, " \
              "FHIR247.UI_GROUPS g, FHIR247.UI_MENU m, FHIR247.UI_USERS u " \
              "WHERE p.group_id = g.group_id AND p.menu_id = m.menu_id AND g.group_id = u.group_id AND " \
              "u.token = '"+ token +"' AND m.menu_id = '"+ menu +"' "

        cursor.execute(cmd)
        dataPrivileges = cursor.fetchall()

        if len(dataPrivileges) > 0:
            for privilege in dataPrivileges:
                privilegeId = privilege[0]
                hasInsert = privilege[1]
                hasUpdate = privilege[2]
                hasDelete = privilege[3]
                hasView = privilege[4]

            result = {"status": 200, "privilegeId": privilegeId, "hasInsert": hasInsert, "hasUpdate": hasUpdate, "hasDelete": hasDelete, "hasView": hasView, "super_admin": False}

        else:
            result = {"status": 404, "message": "Permission denied, user privileges not found!"}

        connDB.close()

    return result

def getGroupbyID(id):
    cmd = "SELECT group_id, name, description FROM FHIR247.UI_GROUPS WHERE group_id = '" + id + "' ORDER BY group_id "

    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listGroup = cursor.fetchall()

    conn.close()

    if len(listGroup) > 0:
        GroupJSON = {}
        for data in listGroup:
            GroupJSON["id"] = data[0]
            GroupJSON["name"] = data[1]
            GroupJSON["description"] = data[2]

        result = {"status": 200, "data": GroupJSON}
    else:
        result = {"status": 404, "message": "Group ID is not found."}

    return result

def groupNameValidate(name):
    result = {}
    # check from db
    connDB = phoenixConn()
    cursor = connDB.cursor()

    cmd = "SELECT group_id FROM FHIR247.UI_GROUPS WHERE name = '" + name + "' "
    cursor.execute(cmd)
    dataUser = cursor.fetchall()

    if len(dataUser) > 0:
        result = {"status": 403, "message": "Group name already exist!"}
    else:
        result = {"status": 200, "message": "Group name ready to use."}

    connDB.close()

    return result

def getMenubyID(id):
    cmd = "SELECT menu_id, menu_parent, menu_label, menu_name, menu_description, menu_active, menu_url, menu_config, menu_icon, menu_sort " \
              "FROM FHIR247.UI_MENU WHERE menu_id = '" + id + "'"

    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listMenu = cursor.fetchall()

    conn.close()

    if len(listMenu) > 0:
        MenuJSON = {}
        for data in listMenu:
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

        result = {"status": 200, "data": MenuJSON}
    else:
        result = {"status": 404, "message": "Menu ID is not found."}

    return result

def getMenuByName(name):
    cmd = "SELECT menu_id, menu_parent, menu_label, menu_name, menu_description, menu_active, menu_url, menu_config, menu_icon, menu_sort " \
          "FROM FHIR247.UI_MENU WHERE menu_name = '" + name + "'"

    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listMenu = cursor.fetchall()

    conn.close()

    if len(listMenu) > 0:
        result = {"status": 403, "message": "Menu name already exist."}
    else:
        result = {"status": 200, "message": "Menu name is ready to use."}

    return result

def getMenubyGroup(id):
    cmd = "SELECT m.menu_id as menu_id, menu_parent, menu_label, menu_name, menu_description, menu_active, menu_url, menu_config, menu_icon, menu_sort " \
          "FROM FHIR247.UI_MENU m, FHIR247.UI_GROUPS g, FHIR247.UI_PRIVILEGES p " \
          "WHERE m.menu_id = p.menu_id AND p.group_id = g.group_id AND g.group_id = '"+ id +"' ORDER BY m.menu_id"

    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listMenu = cursor.fetchall()

    conn.close()

    Menu = []
    SubMenu = []


    if len(listMenu) > 0:
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

        result = {"status": 200, "data": Menu}
    else:
        result = {"status": 400, "message": "Menu for this user is not found.", "data":""}

    return result

def getPrivilegeByID(id):
    cmd = "SELECT privilege_id, has_insert, has_update, has_delete, has_view, has_approval " \
          "FROM FHIR247.UI_PRIVILEGES WHERE privilege_id = '" + id + "'"

    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listPrivilege = cursor.fetchall()

    conn.close()

    if len(listPrivilege) > 0:
        PrivilegeJSON = {}
        for data in listPrivilege:
            PrivilegeJSON["id"] = data[0]
            PrivilegeJSON["hasInsert"] = data[1]
            PrivilegeJSON["hasUpdate"] = data[2]
            PrivilegeJSON["hasDelete"] = data[3]
            PrivilegeJSON["hasView"] = data[4]
            PrivilegeJSON["hasApproval"] = data[5]

        result = {"status": 200, "data": PrivilegeJSON}
    else:
        result = {"status": 404, "message": "Privilege ID is not found."}

    return result

def getMenuPrivileges(id):
    cmd = "SELECT m.menu_id as menu_id, menu_parent, menu_label, menu_name, menu_active, privilege_id, has_insert, has_update, has_delete, has_approval " \
          "FROM FHIR247.UI_MENU m, FHIR247.UI_GROUPS g, FHIR247.UI_PRIVILEGES p " \
          "WHERE m.menu_id = p.menu_id AND p.group_id = g.group_id AND g.group_id = '"+ id +"' ORDER BY m.menu_id"

    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listMenu = cursor.fetchall()

    conn.close()

    Menu = []
    SubMenu = []


    if len(listMenu) > 0:
        for data in listMenu:
            if data[1] == None:
                MenuJSON = {"menu":{},"privileges":{}}
                MenuJSON["menu"]["id"] = data[0]
                MenuJSON["menu"]["parent"] = data[1]
                MenuJSON["menu"]["label"] = data[2]
                MenuJSON["menu"]["name"] = data[3]
                MenuJSON["menu"]["active"] = data[4]
                MenuJSON["privileges"]["id"] = data[5]
                MenuJSON["privileges"]["hasInsert"] = data[6]
                MenuJSON["privileges"]["hasUpdate"] = data[7]
                MenuJSON["privileges"]["hasDelete"] = data[8]
                MenuJSON["privileges"]["hasApproval"] = data[9]
                MenuJSON["submenu"] = []

                Menu.append(MenuJSON)
            else:
                MenuJSON = {"menu": {}, "privileges": {}}
                MenuJSON["menu"]["id"] = data[0]
                MenuJSON["menu"]["parent"] = data[1]
                MenuJSON["menu"]["label"] = data[2]
                MenuJSON["menu"]["name"] = data[3]
                MenuJSON["menu"]["active"] = data[4]
                MenuJSON["privileges"]["id"] = data[5]
                MenuJSON["privileges"]["hasInsert"] = data[6]
                MenuJSON["privileges"]["hasUpdate"] = data[7]
                MenuJSON["privileges"]["hasDelete"] = data[8]
                MenuJSON["privileges"]["hasApproval"] = data[9]
                MenuJSON["submenu"] = []

                SubMenu.append(MenuJSON)


        for i, parent in enumerate(Menu):
            for j, parent2 in enumerate(SubMenu):
                if parent["menu"]["id"] == parent2["menu"]["parent"]:
                    Menu[i]["submenu"].append(SubMenu[j])

        result = {"status": 200, "data": Menu}
    else:
        result = {"status": 400, "message": "Menu for this user is not found.", "data":""}

    return result

def getPatientbyID(id):
    cmd = "SELECT PATIENT_ID FROM FHIR247.PATIENT WHERE PATIENT_ID = '" + id + "' ORDER BY PATIENT_ID "
    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listPatient = cursor.fetchall()

    conn.close()

    if len(listPatient) > 0:
        result = {"status": 200}
    else:
        result = {"status": 404, "message": "Patient ID is not found."}

    return result

def getPersonbyID(id):
    cmd = "SELECT PERSON_ID FROM FHIR247.PERSON WHERE PERSON_ID = '" + id + "' ORDER BY PERSON_ID "
    conn = phoenixConn()
    cursor = conn.cursor()

    cursor.execute(cmd)
    listPerson = cursor.fetchall()

    conn.close()

    if len(listPerson) > 0:
        result = {"status": 200}
    else:
        result = {"status": 404, "message": "Person ID is not found."}

    return result

##phoenix db config
def phoenixConn():
    database_url = FHIR247_DB
    conn = phoenixdb.connect(database_url, autocommit=True)

    return conn

def phoenixClose(connection):
    return connection.close()

##generate ID
def generateUniqeID(secretkey):
    currentTime = datetime.now()
    key = str(currentTime.microsecond) + secretkey
    UniqeID = hashlib.sha1(key.encode())
    return UniqeID.hexdigest()

def encryptPassword(passwd):
    encryptedPass = hashlib.sha1(passwd.encode())
    return encryptedPass.hexdigest()

def RemoveDuplicateArray(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list

#secret
def getApikeyApiSecretSuperAdmin(token):
    # check from db
    connDB = phoenixConn()
    cursor = connDB.cursor()

    cmd = "SELECT user_id, apikey, apisecret FROM FHIR247.UI_USERS WHERE token = '" + token + "' "
    cursor.execute(cmd)
    dataUser = cursor.fetchall()
    connDB.close()
    if len(dataUser) > 0:
        for data in dataUser:
            # userID = data[0]
            apiKey = data[1]
            apiSecret = data[2]

        if apiKey == '64cb156db93458ac469e8a3562b7892fa0d08597' and apiSecret == 'e5101c5b7dac13db925b99a53d174bbdc648b0eb':
        	return True
        else:
        	return False
    else:
        return False

