from flask import request
import json

from Secret247 import phoenixConn, tokenValidate

def getAdministrativeGenders():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        cmd = "select * from FHIR247.REF_ADMINISTRATIVE_GENDER"
        conn = phoenixConn()
        cursor = conn.cursor()
        cursor.execute(cmd)
        listUser = cursor.fetchall()

        User = []
        for data in listUser:
            UserJSON = {}
            UserJSON['code'] = data[0]
            UserJSON['display'] = data[1]
            UserJSON['definition'] = data[2]

            User.append(UserJSON)
        conn.close ()
        result = User
    return result

def addAdministrativeGender():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    # request
    data = request.data
    dataUser = json.loads(data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        code = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."

    if errCode == 0:
        conn = phoenixConn()
        cursor = conn.cursor()

        #insert
        try:
            cmd = "UPSERT INTO FHIR247.REF_ADMINISTRATIVE_GENDER " \
                  "(CODE, DISPLAY, DEFINITION) " \
                  " VALUES" \
                  "('" + code + "','" + display + "','" + definition + "')"
            cursor.execute(cmd)
            conn.close ()
            errCode = 200
            message = "User added successfully"
        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def getAdministrativeGender(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_ADMINISTRATIVE_GENDER WHERE CODE = '" + code + "'"
            cursor.execute(select)
            dataCode = cursor.fetchone()
            errCode = 14002

            if dataCode:
                cmd = "select * from FHIR247.REF_ADMINISTRATIVE_GENDER WHERE code = '"+ code +"' "
                cursor.execute(cmd)
                listUser = cursor.fetchall ()

                User = []
                for data in listUser:
                    UserJSON = { }
                    UserJSON['code'] = data[0]
                    UserJSON['display'] = data[1]
                    UserJSON['definition'] = data[2]

                    User.append (UserJSON)
                conn.close()
                result = User
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def updateAdministrativeGender(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    # request
    data = request.data
    dataUser = json.loads(data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        codee = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."
        result = { "status": errCode, "message": message }

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."
        result = { "status": errCode, "message": message }

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_ADMINISTRATIVE_GENDER WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "UPSERT INTO FHIR247.REF_ADMINISTRATIVE_GENDER " \
                      "(CODE, DISPLAY, DEFINITION) " \
                      "VALUES" \
                      "('" + codee + "','" + display + "','" + definition + "')"
                cursor.execute(cmd)
                conn.close ()
                errCode = 200
                message = "User update successfully"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = {"status": errCode, "message": message}
        except OSError as err:
            errCode = 13002
            message = err
            result = {"status": errCode, "message": message }
    return result

def deleteAdministrativeGender(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_ADMINISTRATIVE_GENDER WHERE CODE = '" + code + "'"
            cursor.execute(select)
            dataCode = cursor.fetchone()
            errCode = 14002

            if dataCode:
                cmd = "DELETE from FHIR247.REF_ADMINISTRATIVE_GENDER WHERE CODE = '" + code + "'"
                cursor.execute(cmd)
                conn.close ()
                errCode = 200
                message = "Successfully deleted"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = {"status": errCode, "message": message}
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def getMaritalStatuses():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        cmd = "select * from FHIR247.REF_MARITAL_STATUS"
        conn = phoenixConn()
        cursor = conn.cursor()
        cursor.execute(cmd)
        listUser = cursor.fetchall ()

        User = []
        for data in listUser:
            UserJSON = { }
            UserJSON['code'] = data[0]
            UserJSON['system'] = data[1]
            UserJSON['display'] = data[2]
            UserJSON['definition'] = data[3]

            User.append (UserJSON)
        conn.close ()
        result = User
    return result

def addMaritalStatus():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    # request
    data = request.data
    dataUser = json.loads(data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        code = dataUser['code']
    else:
        errCode = 14003
        message = "code is required."

    # system
    if 'system' in dataUser and dataUser['system'] != '':
        system = dataUser['system']
    else:
        errCode = 14003
        message = "system is required."

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."

    if errCode == 0:
        conn = phoenixConn()
        cursor = conn.cursor()

        # insert
        try:
            cmd = "UPSERT INTO FHIR247.REF_MARITAL_STATUS " \
                  "(CODE, SYSTEM, DISPLAY, DEFINITION) " \
                  " VALUES" \
                  "('" + code + "','" + system + "','" + display + "','" + definition + "')"
            cursor.execute(cmd)
            conn.close ()
            errCode = 200
            message = "User added successfully"
        except OSError as err:
            errCode = 13002
            message = err

        result = { "status": errCode, "message": message }
    else:
        result = { "status": errCode, "message": message }
    return result

def getMaritalStatus(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_MARITAL_STATUS WHERE CODE = '" + code + "'"
            cursor.execute(select)
            dataCode = cursor.fetchone()
            errCode = 14002

            if dataCode:
                cmd = "select * from FHIR247.REF_MARITAL_STATUS WHERE code = '" + code + "' "
                cursor.execute(cmd)
                listUser = cursor.fetchall ()

                User = []
                for data in listUser:
                    UserJSON = { }
                    UserJSON['code'] = data[0]
                    UserJSON['system'] = data[1]
                    UserJSON['display'] = data[2]
                    UserJSON['definition'] = data[3]

                    User.append (UserJSON)
                conn.close ()
                result = User

            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def updateMaritalStatus(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    # request
    data = request.data
    dataUser = json.loads (data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        codee = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."
        result = { "status": errCode, "message": message }

    # system
    if 'system' in dataUser and dataUser['system'] != '':
        system = dataUser['system']
    else:
        errCode = 14003
        message = "system is required."
        result = { "status": errCode, "message": message }

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."
        result = { "status": errCode, "message": message }

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_MARITAL_STATUS WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "UPSERT INTO FHIR247.REF_MARITAL_STATUS " \
                      "(CODE, SYSTEM, DISPLAY, DEFINITION) " \
                      " VALUES" \
                      "('" + codee + "','" + system + "','" + display + "','" + definition + "')"
                cursor.execute(cmd)
                conn.close ()
                errCode = 200
                message = "User updated successfully"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = {"status": errCode, "message": message}
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def deleteMaritalStatus(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_MARITAL_STATUS WHERE CODE = '" + code + "'"
            cursor.execute(select)
            dataCode = cursor.fetchone()
            errCode = 14002

            if dataCode:
                cmd = "DELETE from FHIR247.REF_MARITAL_STATUS WHERE code = '" + code + "' "
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "Successfully deleted"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def getPatientContactRelationships():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        cmd = "select * from FHIR247.REF_PATIENT_CONTACTRELATIONSHIP"
        conn = phoenixConn()
        cursor = conn.cursor()
        cursor.execute(cmd)
        listUser = cursor.fetchall ()

        User = []
        for data in listUser:
            UserJSON = { }
            UserJSON['code'] = data[0]
            UserJSON['display'] = data[1]
            UserJSON['definition'] = data[2]

            User.append (UserJSON)
        conn.close ()
        result = User
    return result

def addPatientContactRelationship():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    # request
    data = request.data
    dataUser = json.loads (data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        code = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."

    if errCode == 0:
        conn = phoenixConn()
        cursor = conn.cursor()

        # insert
        try:
            cmd = "UPSERT INTO FHIR247.REF_PATIENT_CONTACTRELATIONSHIP" \
                  "(CODE, DISPLAY, DEFINITION) " \
                  " VALUES" \
                  "('" + code + "','" + display + "','" + definition + "')"
            cursor.execute (cmd)
            conn.close ()
            errCode = 200
            message = "User added successfully"
        except OSError as err:
            errCode = 13002
            message = err

        result = { "status": errCode, "message": message }
    else:
        result = { "status": errCode, "message": message }
    return result

def getPatientContactRelationship(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn()
        cursor = conn.cursor()
        try:
            select = "SELECT CODE FROM FHIR247.REF_PATIENT_CONTACTRELATIONSHIP WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "select * from FHIR247.REF_PATIENT_CONTACTRELATIONSHIP WHERE code = '" + code + "' "
                cursor.execute(cmd)
                listUser = cursor.fetchall ()

                User = []
                for data in listUser:
                    UserJSON = { }
                    UserJSON['code'] = data[0]
                    UserJSON['display'] = data[1]
                    UserJSON['definition'] = data[2]

                    User.append (UserJSON)
                conn.close ()
                result = User
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def updatePatientContactRelationship(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    # request
    data = request.data
    dataUser = json.loads (data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        codee = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."
        result = { "status": errCode, "message": message }

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."
        result = { "status": errCode, "message": message }

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_PATIENT_CONTACTRELATIONSHIP WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "UPSERT INTO FHIR247.REF_PATIENT_CONTACTRELATIONSHIP " \
                      "(CODE, DISPLAY, DEFINITION) " \
                      " VALUES" \
                      "('" + codee + "','" + display + "','" + definition + "')"
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "User updated successfully"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = {"status": errCode, "message": message}
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def deletePatientContactRelationship(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_PATIENT_CONTACTRELATIONSHIP WHERE CODE = '" + code + "'"
            cursor.execute(select)
            dataCode = cursor.fetchone()
            errCode = 14002

            if dataCode:
                cmd = "DELETE from FHIR247.REF_PATIENT_CONTACTRELATIONSHIP WHERE code = '" + code + "' "
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "Successfully deleted"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def getLanguages():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        cmd = "select * from FHIR247.REF_LANGUAGES"
        conn = phoenixConn ()
        cursor = conn.cursor ()
        cursor.execute (cmd)
        listUser = cursor.fetchall ()

        User = []
        for data in listUser:
            UserJSON = { }
            UserJSON['code'] = data[0]
            UserJSON['display'] = data[1]

            User.append (UserJSON)
        conn.close ()
        result = User
    return result

def addLanguage():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    # request
    data = request.data
    dataUser = json.loads(data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        code = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()

        # insert
        try:
            cmd = "UPSERT INTO FHIR247.REF_LANGUAGES" \
                  "(CODE, DISPLAY) " \
                  " VALUES" \
                  "('" + code + "','" + display + "')"
            cursor.execute(cmd)
            conn.close ()
            errCode = 200
            message = "User added successfully"
        except OSError as err:
            errCode = 13002
            message = err

        result = { "status": errCode, "message": message }
    else:
        result = { "status": errCode, "message": message }
    return result

def getLanguage(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_LANGUAGES WHERE CODE = '" + code + "'"
            cursor.execute(select)
            dataCode = cursor.fetchone()
            errCode = 14002

            if dataCode:
                cmd = "select * from FHIR247.REF_LANGUAGES WHERE code = '" + code + "' "
                cursor.execute (cmd)
                listUser = cursor.fetchall ()

                User = []
                for data in listUser:
                    UserJSON = { }
                    UserJSON['code'] = data[0]
                    UserJSON['display'] = data[1]

                    User.append (UserJSON)
                conn.close ()
                result = User
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def updateLanguage(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    # request
    data = request.data
    dataUser = json.loads (data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        codee = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."
        result = { "status": errCode, "message": message }

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."
        result = { "status": errCode, "message": message }

    if errCode == 0:
        connDB = phoenixConn ()
        cursor = connDB.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_LANGUAGES WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "UPSERT INTO FHIR247.REF_LANGUAGES " \
                      "(CODE, DISPLAY) " \
                      " VALUES" \
                      "('" + codee + "','" + display + "')"
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "User updated successfully"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def deleteLanguage(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_LANGUAGES WHERE CODE = '" + code + "'"
            cursor.execute(select)
            dataCode = cursor.fetchone()
            errCode = 14002

            if dataCode:
                cmd = "DELETE from FHIR247.REF_LANGUAGES WHERE code = '" + code + "' "
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "Successfully deleted"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = {"status": errCode, "message": message}
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def getLinkTypes():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        cmd = "select * from FHIR247.REF_LINK_TYPE"
        conn = phoenixConn ()
        cursor = conn.cursor ()
        cursor.execute (cmd)
        listUser = cursor.fetchall ()

        User = []
        for data in listUser:
            UserJSON = { }
            UserJSON['code'] = data[0]
            UserJSON['display'] = data[1]
            UserJSON['definition'] = data[2]

            User.append (UserJSON)
        conn.close ()
        result = User
    return result

def addLinkType():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    # request
    data = request.data
    dataUser = json.loads (data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        code = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()

        # insert
        try:
            cmd = "UPSERT INTO FHIR247.REF_LINK_TYPE " \
                  "(CODE, DISPLAY, DEFINITION) " \
                  " VALUES" \
                  "('" + code + "','" + display + "','" + definition + "')"
            cursor.execute (cmd)
            conn.close ()
            errCode = 200
            message = "User added successfully"
        except OSError as err:
            errCode = 13002
            message = err

        result = { "status": errCode, "message": message }
    else:
        result = { "status": errCode, "message": message }
    return result

def getLinkType(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_LINK_TYPE WHERE CODE = '" + code + "'"
            cursor.execute(select)
            dataCode = cursor.fetchone()
            errCode = 14002

            if dataCode:
                cmd = "select * from FHIR247.REF_LINK_TYPE WHERE code = '" + code + "' "
                cursor.execute (cmd)
                listUser = cursor.fetchall ()

                User = []
                for data in listUser:
                    UserJSON = { }
                    UserJSON['code'] = data[0]
                    UserJSON['display'] = data[1]
                    UserJSON['definition'] = data[2]

                    User.append (UserJSON)
                conn.close ()
                result = User
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def updateLinkType(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    # request
    data = request.data
    dataUser = json.loads (data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        codee = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."
        result = { "status": errCode, "message": message }

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."
        result = { "status": errCode, "message": message }

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_LINK_TYPE WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "UPSERT INTO FHIR247.REF_LINK_TYPE " \
                      "(CODE, DISPLAY, DEFINITION) " \
                      "VALUES" \
                      "('" + codee + "','" + display + "','" + definition + "')"
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "User update successfully"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def deleteLinkType(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_LINK_TYPE WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "DELETE from FHIR247.REF_LINK_TYPE WHERE code = '" + code + "' "
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "Successfully deleted"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = {"status": errCode, "message": message}
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def getIdentityAssuranceLevels():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        cmd = "select * from FHIR247.REF_IDENTITY_ASSURANCE_LEVEL"
        conn = phoenixConn ()
        cursor = conn.cursor ()
        cursor.execute (cmd)
        listUser = cursor.fetchall ()

        User = []
        for data in listUser:
            UserJSON = { }
            UserJSON['code'] = data[0]
            UserJSON['display'] = data[1]
            UserJSON['definition'] = data[2]

            User.append (UserJSON)
        conn.close ()
        result = User
    return result

def addIdentityAssuranceLevel():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    # request
    data = request.data
    dataUser = json.loads (data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        code = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()

        # insert
        try:
            cmd = "UPSERT INTO FHIR247.REF_IDENTITY_ASSURANCE_LEVEL " \
                  "(CODE, DISPLAY, DEFINITION) " \
                  " VALUES" \
                  "('" + code + "','" + display + "','" + definition + "')"
            cursor.execute (cmd)
            conn.close ()
            errCode = 200
            message = "User added successfully"
        except OSError as err:
            errCode = 13002
            message = err

        result = { "status": errCode, "message": message }
    else:
        result = { "status": errCode, "message": message }
    return result

def getIdentityAssuranceLevel(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_IDENTITY_ASSURANCE_LEVEL WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "select * from FHIR247.REF_IDENTITY_ASSURANCE_LEVEL WHERE code = '" + code + "' "
                cursor.execute (cmd)
                listUser = cursor.fetchall ()

                User = []
                for data in listUser:
                    UserJSON = { }
                    UserJSON['code'] = data[0]
                    UserJSON['display'] = data[1]
                    UserJSON['definition'] = data[2]

                    User.append (UserJSON)
                conn.close ()
                result = User
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def updateIdentityAssuranceLevel(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    # request
    data = request.data
    dataUser = json.loads (data)

    # code
    if 'code' in dataUser and dataUser['code'] != '':
        codee = dataUser['code']
    else:
        errCode = 14003
        message = "Code is required."
        result = { "status": errCode, "message": message }

    # display
    if 'display' in dataUser and dataUser['display'] != '':
        display = dataUser['display']
    else:
        errCode = 14003
        message = "display is required."
        result = { "status": errCode, "message": message }

    # definition
    if 'definition' in dataUser and dataUser['definition'] != '':
        definition = dataUser['definition']
    else:
        errCode = 14003
        message = "definition is required."
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_IDENTITY_ASSURANCE_LEVEL WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "UPSERT INTO FHIR247.REF_IDENTITY_ASSURANCE_LEVEL " \
                      "(CODE, DISPLAY, DEFINITION) " \
                      "VALUES" \
                      "('" + codee + "','" + display + "','" + definition + "')"
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "User update successfully"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result

def deleteIdentityAssuranceLevel(code):
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
        result = { "status": errCode, "message": message }

    if errCode == 0:
        conn = phoenixConn ()
        cursor = conn.cursor ()
        try:
            select = "SELECT CODE FROM FHIR247.REF_IDENTITY_ASSURANCE_LEVEL WHERE CODE = '" + code + "'"
            cursor.execute (select)
            dataCode = cursor.fetchone ()
            errCode = 14002

            if dataCode:
                cmd = "DELETE from FHIR247.REF_IDENTITY_ASSURANCE_LEVEL WHERE CODE = '" + code + "'"
                cursor.execute (cmd)
                conn.close ()
                errCode = 200
                message = "Successfully deleted"
                result = { "status": errCode, "message": message }
            else:
                message = "Data doesn't exist"
                result = { "status": errCode, "message": message }
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    return result