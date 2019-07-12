19 june
def getPatients():
    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    #
    # condition = ""
    offset_limit = ""

    if offset and limit:
        offset_limit = 'LIMIT ' + limit + ' OFFSET ' + offset
    else:
        offset = 0
        limit = 0

    ##metode2 (JOIN di Phoenix)

    cmd = 'SELECT a.IDENTIFIER_ID, a."USE", a.TYPE, a.SYSTEM, a."VALUE", ' \
          'e.ATTACHMENT_ID, e.CONTENT_TYPE, e.LANGUAGE, e.DATA, e.URL, e.SIZE, e.HASH, e.TITLE, ' \
          'f.CONTACT_ID, f.RELATIONSHIP, f.GENDER, f.ORGANIZATION, g.COMMUNICATION_ID, g.LANGUAGE, g.PREFERRED, ' \
          'h.LINK_ID, h.OTHER, h.TYPE, i.PATIENT_ID, i.RESOURCE_TYPE, i.LAST_UPDATED, i."ACTIVE", ' \
          'i.GENDER, i.BIRTHDATE, i.DECEASED_BOOLEAN, i.DECEASED_DATETIME, ' \
          'i.MARITAL_STATUS, i.MULTIPLE_BIRTH_BOOLEAN, i.MULTIPLE_BIRTH_INTEGER ' \
          'FROM FHIR247.IDENTIFIER a, ' \
          'FHIR247.ATTACHMENT e, FHIR247.CONTACT f, FHIR247.COMMUNICATION g, FHIR247.LINK h, FHIR247.PATIENT i ' \
          'WHERE i.PATIENT_ID = a.RESOURCE_ID AND i.PATIENT_ID = e.RESOURCE_ID AND i.PATIENT_ID = f.RESOURCE_ID ' \
          'AND i.PATIENT_ID = g.RESOURCE_ID AND i.PATIENT_ID = h.RESOURCE_ID ' \
          'ORDER BY a.RESOURCE_ID '

    conn = phoenixConn()
    cursor = conn.cursor()

    Patient = []

    cursor.execute(cmd)
    data = result = cursor.fetchall()

    # set default value of resources
    PatientID = ""
    index = 0

    for dt in data:
        if PatientID == dt[23]:
            exist = True
        else:
            PatientID = dt[23]
            exist = False

        if exist:
            # insert identifier
            identifier = {"id": dt[0], "use": dt[1], "type": {"text": dt[2], "coding": []}, "system": dt[3],
                          "value": dt[4]}
            Patient[index - 1]["identifier"].append(identifier)
            Patient[index - 1]["identifier"] = RemoveDuplicateArray(Patient[index - 1]["identifier"])

            # # insert human_name
            # humanName = {"id": dt[5], "use": dt[6], "text": dt[7], "family": dt[8], "given": dt[9].split('|'),
            #              "prefix": dt[10].split('|'), "suffix": dt[11].split('|')}
            # Patient[index - 1]["name"].append(humanName)
            # Patient[index - 1]["name"] = RemoveDuplicateArray(Patient[index - 1]["name"])
            #
            # # insert telecom/contactpoint
            # contactPoint = {"id": dt[13], "system": dt[14], "value": dt[15], "use": dt[16], "rank": dt[17]}
            # Patient[index - 1]["telecom"].append(contactPoint)
            # Patient[index - 1]["telecom"] = RemoveDuplicateArray(Patient[index - 1]["telecom"])
            #
            # # insert address
            # address = {"id": dt[18], "use": dt[19], "type": dt[20], "text": dt[21], "line": dt[22].split('|'),
            #            "city": dt[23], "district": dt[24], "state": dt[25], "postalCode": dt[26], "country": dt[27]}
            # Patient[index - 1]["address"].append(address)
            # Patient[index - 1]["address"] = RemoveDuplicateArray(Patient[index - 1]["address"])

            # insert photo/attachment
            photo = {"id": dt[5], "contentType": dt[6], "language": dt[7], "data": dt[8], "url": dt[9],
                     "size": dt[10], "hash": dt[11], "title": dt[12]}
            Patient[index - 1]["photo"].append(photo)
            Patient[index - 1]["photo"] = RemoveDuplicateArray(Patient[index - 1]["photo"])

            # insert contact
            contact = {"id": dt[13], "relationship": {"text": dt[14], "coding": []}, "gender": dt[15],
                       "organization": dt[16]}
            Patient[index - 1]["contact"].append(contact)
            Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

            # insert communication
            communication = {"id": dt[17], "language": {"text": dt[18], "coding": []}, "preferred": dt[19]}
            Patient[index - 1]["communication"].append(communication)
            Patient[index - 1]["communication"] = RemoveDuplicateArray(Patient[index - 1]["communication"])

            # insert link
            link = {"id": dt[20], "other": {}, "type": dt[22]} #warn
            Patient[index - 1]["link"].append(link)
            Patient[index - 1]["link"] = RemoveDuplicateArray(Patient[index - 1]["link"])

            # insert patient
            patient = {"resourceType": dt[24], "meta": {"lastUpdate": dt[25], "versionId": 0}, "active": dt[26],
                       "gender": dt[27], "birthDate": dt[28], "deceasedBoolean": dt[29], "deceasedDateTime": dt[30],
                       "maritalStatus": {"text": dt[31], "coding": []}, "multipleBirthBoolean": dt[32],
                       "multipleBirthInteger": dt[33]}
            Patient.append(patient)
            Patient = RemoveDuplicateArray(Patient)

        else:
            jsonPatient = {
                "resourceType": dt[24],
                "id": dt[23],
                "meta": {"lastUpdated": dt[25], "versionId": ""},
                "text": {"status": "", "div": ""},
                "identifier": [],
                "active": dt[26],
                "name": [],
                "telecom": [],
                "gender": dt[27],
                "birthDate": (dt[28]).strftime("%Y-%m-%d, %H:%M:%S"),
                "deceasedBoolean": dt[29],
                "deceasedDateTime": dt[30],
                "address": [],
                "maritalStatus": {"text": dt[31], "coding": []},
                "multipleBirthBoolean": dt[32],
                "multipleBirthInteger": dt[33],
                "photo": [],
                "contact": [],
                "communication": [],
                "generalPractitioner": [{}],
                "managingOrganization": {},
                "link": []
            }

            # parsing identifier
            identifier = {"id": dt[0], "use": dt[1], "type": {"text": dt[2], "coding": []}, "system": dt[3],
                          "value": dt[4]}
            jsonPatient["identifier"].append(identifier)

            # parsing human_name
            cmd = "select HUMAN_NAME_ID, \"USE\", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX from fhir247.human_name where resource_id = '" + PatientID + "' " \
                   "order by RESOURCE_ID ASC LIMIT 1"
            cursor.execute(cmd, (PatientID,))
            dataHumanName = cursor.fetchall()

            for hum in dataHumanName:
                humanName = {"id": hum[0], "use": hum[1], "text": hum[2], "family": hum[3], "given": hum[4].split('|'),
                             "prefix": hum[5].split('|'), "suffix": hum[6].split('|')}
                jsonPatient["name"].append(humanName)

            # parsing contact_point
            cmd = "select CONTACT_POINT_ID, SYSTEM, \"VALUE\", 'USE', RANK FROM fhir247.contact_point where resource_id = '" + PatientID + "' " \
                  "order by RESOURCE_ID ASC LIMIT 1"
            cursor.execute(cmd, (PatientID,))
            dataTelecom = cursor.fetchall()

            for tel in dataTelecom:
                telecom = {"id": tel[0], "system": tel[1], "value": tel[2], "use": tel[3], "rank": tel[4]}
                jsonPatient["telecom"].append(telecom)

            # parsing address
            cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
                  "FROM fhir247.address where resource_id = '" + PatientID + "' order by RESOURCE_ID ASC LIMIT 1"
            cursor.execute(cmd, (PatientID,))
            dataAddress = cursor.fetchall()

            for add in dataAddress:
                address = {"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
                           "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8], "country": add[9]}
                jsonPatient["address"].append(address)

            # parsing photo/attachment
            photo = {"id": dt[5], "contentType": dt[6], "language": dt[7], "data": dt[8], "url": dt[9],
                     "size": dt[10], "hash": dt[11], "title": dt[12]}
            jsonPatient["photo"].append(photo)

            # parsing contact
            contactID = dt[13]
            contact = {"id": dt[13], "relationship": {"text": dt[14], "coding": []}, "gender": dt[15],
                       "organization": dt[16]}
            jsonPatient["contact"].append(contact)

            # parsing contact human name
            cmd = "select HUMAN_NAME_ID, \"USE\", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX from fhir247.human_name where resource_id = '" + contactID + "' " \
                  "order by RESOURCE_ID ASC"
            cursor.execute(cmd, (PatientID,))
            dataHumanName = cursor.fetchall()

            for hum in dataHumanName:
                humanName = {
                    "name": {"id": hum[0], "use": hum[1], "text": hum[2], "family": hum[3], "given": hum[4].split('|'),
                             "prefix": hum[5].split('|'), "suffix": hum[6].split('|')}}
                jsonPatient["contact"].append(humanName)

            # parsing contact telecom
            cmd = "select CONTACT_POINT_ID, SYSTEM, \"VALUE\", 'USE', RANK FROM fhir247.contact_point where resource_id = '" + contactID + "' " \
                  "order by RESOURCE_ID ASC"
            cursor.execute(cmd, (PatientID,))
            dataTelecom = cursor.fetchall()

            for tel in dataTelecom:
                telecom = {"telecom": {"id": tel[0], "system": tel[1], "value": tel[2], "use": tel[3], "rank": tel[4]}}
                jsonPatient["contact"].append(telecom)

            # parsing contact address
            cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
                  "FROM fhir247.address where resource_id = '" + contactID + "' order by RESOURCE_ID ASC"
            cursor.execute(cmd, (PatientID,))
            dataAddress = cursor.fetchall()

            for add in dataAddress:
                address = {
                    "address": {"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
                                "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8],
                                "country": add[9]}}
                jsonPatient["contact"].append(address)

            # parsing communication
            communication = {"id": dt[17], "language": {"text": dt[18], "coding": []}, "preferred": dt[19]}
            jsonPatient["communication"].append(communication)

            # parsing link
            link = {"id": dt[20], "other": {}, "type": dt[22]} #warn
            jsonPatient["link"].append(link)

            Patient.append(jsonPatient)
            index += 1

    conn.close()
    return Patient

21 june / fix getPatients() query in looping

def getPatients():
    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    #
    # condition = ""
    offset_limit = ""

    if offset and limit:
        offset_limit = 'LIMIT ' + limit + ' OFFSET ' + offset
    else:
        offset = 0
        limit = 0

    ##metode2 (JOIN di Phoenix)



    cmd = "SELECT a.IDENTIFIER_ID, a.\"USE\", a.TYPE, a.SYSTEM, a.\"VALUE\", " \
          "e.ATTACHMENT_ID, e.CONTENT_TYPE, e.LANGUAGE, e.DATA, e.URL, e.SIZE, e.HASH, e.TITLE, " \
          "f.CONTACT_ID, f.RELATIONSHIP, f.GENDER, f.ORGANIZATION, g.COMMUNICATION_ID, g.LANGUAGE, g.PREFERRED, " \
          "h.LINK_ID, h.OTHER, h.TYPE, i.PATIENT_ID, i.RESOURCE_TYPE, TO_CHAR(i.LAST_UPDATED, \'yyyy-MM-dd HH:mm:ss\'), i.\"ACTIVE\", " \
          "i.GENDER, TO_CHAR(i.BIRTHDATE, \'yyyy-MM-dd\'), i.DECEASED_BOOLEAN, TO_CHAR(i.DECEASED_DATETIME, \'yyyy-MM-dd HH:mm:ss\'), " \
          "i.MARITAL_STATUS, i.MULTIPLE_BIRTH_BOOLEAN, i.MULTIPLE_BIRTH_INTEGER, i.MANAGING_ORGANIZATION, j.GENERAL_PRACTITONER_ID, " \
          "j.REFERENCE " \
          "FROM FHIR247.IDENTIFIER a, " \
          "FHIR247.ATTACHMENT e, FHIR247.CONTACT f, FHIR247.COMMUNICATION g, FHIR247.LINK h, FHIR247.PATIENT i, FHIR247.GENERAL_PRACTITONER j " \
          "WHERE i.PATIENT_ID = a.RESOURCE_ID AND i.PATIENT_ID = e.RESOURCE_ID AND i.PATIENT_ID = f.RESOURCE_ID " \
          "AND i.PATIENT_ID = g.RESOURCE_ID AND i.PATIENT_ID = h.RESOURCE_ID AND i.PATIENT_ID = j.RESOURCE_ID " \
          "ORDER BY i.PATIENT_ID "

    # identifier 0 - 4, attachment 5 - 12, contact 13-16, communication 17 - 19, link 20 - 22, patient 23 - 34, general_prac 35 - 36

    conn = phoenixConn()
    cursor = conn.cursor()

    Patient = []

    cursor.execute(cmd)
    data = result = cursor.fetchall()

    # set default value of resources
    PatientID = ""
    index = 0

    for dt in data:
        if PatientID == dt[23]:
            exist = True
        else:
            PatientID = dt[23]
            exist = False

        # if exist:
        #     # insert identifier
        #     identifier = {"id": dt[0], "use": dt[1], "type": {"text": dt[2], "coding": []}, "system": dt[3],
        #                   "value": dt[4]}
        #     Patient[index - 1]["identifier"].append(identifier)
        #     Patient[index - 1]["identifier"] = RemoveDuplicateArray(Patient[index - 1]["identifier"])
        #
        #     # # insert human_name
        #     # humanName = {"id": dt[5], "use": dt[6], "text": dt[7], "family": dt[8], "given": dt[9].split('|'),
        #     #              "prefix": dt[10].split('|'), "suffix": dt[11].split('|')}
        #     # Patient[index - 1]["name"].append(humanName)
        #     # Patient[index - 1]["name"] = RemoveDuplicateArray(Patient[index - 1]["name"])
        #     #
        #     # # insert telecom/contactpoint
        #     # contactPoint = {"id": dt[13], "system": dt[14], "value": dt[15], "use": dt[16], "rank": dt[17]}
        #     # Patient[index - 1]["telecom"].append(contactPoint)
        #     # Patient[index - 1]["telecom"] = RemoveDuplicateArray(Patient[index - 1]["telecom"])
        #     #
        #     # # insert address
        #     # address = {"id": dt[18], "use": dt[19], "type": dt[20], "text": dt[21], "line": dt[22].split('|'),
        #     #            "city": dt[23], "district": dt[24], "state": dt[25], "postalCode": dt[26], "country": dt[27]}
        #     # Patient[index - 1]["address"].append(address)
        #     # Patient[index - 1]["address"] = RemoveDuplicateArray(Patient[index - 1]["address"])
        #
        #     # insert photo/attachment
        #     photo = {"id": dt[5], "contentType": dt[6], "language": dt[7], "data": dt[8], "url": dt[9],
        #              "size": dt[10], "hash": dt[11], "title": dt[12]}
        #     Patient[index - 1]["photo"].append(photo)
        #     Patient[index - 1]["photo"] = RemoveDuplicateArray(Patient[index - 1]["photo"])
        #
        #     # insert contact
        #     contact = {"id": dt[13], "relationship": {"text": dt[14], "coding": []}, "gender": dt[15],
        #                "organization": dt[16]}
        #     Patient[index - 1]["contact"].append(contact)
        #     Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])
        #
        #
        #
        #     # insert communication
        #     communication = {"id": dt[17], "language": {"text": dt[18], "coding": []}, "preferred": dt[19]}
        #     Patient[index - 1]["communication"].append(communication)
        #     Patient[index - 1]["communication"] = RemoveDuplicateArray(Patient[index - 1]["communication"])
        #
        #     # insert link
        #     link = {"id": dt[20], "other": {"reference": dt[21]}, "type": dt[22]} #warn
        #     Patient[index - 1]["link"].append(link)
        #     Patient[index - 1]["link"] = RemoveDuplicateArray(Patient[index - 1]["link"])
        #
        #     # insert general practitoner
        #     generalPractitioner =  {"id": dt[35], "reference": dt[36]}  # warn
        #     Patient[index - 1]["generalPractitioner"].append(generalPractitioner)
        #     Patient[index - 1]["generalPractitioner"] = RemoveDuplicateArray(Patient[index - 1]["generalPractitioner"])
        #
        #     # insert patient
        #     patient = {"resourceType": dt[24], "meta": {"lastUpdate": dt[25], "versionId": 0}, "active": dt[26],
        #                "gender": dt[27], "birthDate": dt[28], "deceasedBoolean": dt[29], "deceasedDateTime": dt[30],
        #                "maritalStatus": {"text": dt[31], "coding": []}, "multipleBirthBoolean": dt[32],
        #                "multipleBirthInteger": dt[33], "managingOrganization" : {"reference": dt[34]}}
        #     Patient.append(patient)
        #     Patient = RemoveDuplicateArray(Patient)
        #
        # else:
            jsonPatient = {
                "resourceType": dt[24],
                "id": dt[23],
                "meta": {"lastUpdated": dt[25], "versionId": ""},
                "text": {"status": "", "div": ""},
                "identifier": [],
                "active": dt[26],
                "name": [],
                "telecom": [],
                "gender": dt[27],
                "birthDate": dt[28],
                "deceasedBoolean": dt[29],
                "deceasedDateTime": dt[30],
                "address": [],
                "maritalStatus": {"text": dt[31], "coding": []},
                "multipleBirthBoolean": dt[32],
                "multipleBirthInteger": dt[33],
                "photo": [],
                "contact": [],
                "communication": [],
                "generalPractitioner": [],
                "managingOrganization": {"reference": dt[34]},
                "link": []
            }

            # parsing identifier
            identifier = {"id": dt[0], "use": dt[1], "type": {"text": dt[2], "coding": []}, "system": dt[3],
                          "value": dt[4]}
            jsonPatient["identifier"].append(identifier)


            # parsing human_name
            cmd = "select HUMAN_NAME_ID, \"USE\", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX from fhir247.human_name where resource_id = '" + PatientID + "' " \
                   "order by RESOURCE_ID ASC LIMIT 1"
            cursor.execute(cmd, (PatientID,))
            dataHumanName = cursor.fetchall()

            for hum in dataHumanName:
                humanName = {"id": hum[0], "use": hum[1], "text": hum[2], "family": hum[3], "given": hum[4].split('|'),
                             "prefix": hum[5].split('|'), "suffix": hum[6].split('|')}
                jsonPatient["name"].append(humanName)

            # new_data = []
            # not_found = True
            # for hum in dataHumanName:
            #     for resource_id in new_data:
            #         not_found = True
            #         if hum[6] == resource_id[6]:
            #             not_found = False
            #             for contact in resource_id['contact']:
            #                 contact['contact'].append({'name': resource[0], 'text': resource[1]})
            #             break
            #     if not_found:
            #         jsonPatient["contact"].append({'name': resource[0], 'text': [1]})

            # parsing contact_point
            cmd = "select CONTACT_POINT_ID, SYSTEM, \"VALUE\", 'USE', RANK FROM fhir247.contact_point where resource_id = '" + PatientID + "' " \
                  "order by RESOURCE_ID ASC LIMIT 1"
            cursor.execute(cmd, (PatientID,))
            dataTelecom = cursor.fetchall()

            for tel in dataTelecom:
                telecom = {"id": tel[0], "system": tel[1], "value": tel[2], "use": tel[3], "rank": tel[4]}
                jsonPatient["telecom"].append(telecom)

            # parsing address
            cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
                  "FROM fhir247.address where resource_id = '" + PatientID + "' order by RESOURCE_ID ASC LIMIT 1"
            cursor.execute(cmd, (PatientID,))
            dataAddress = cursor.fetchall()

            for add in dataAddress:
                address = {"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
                           "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8], "country": add[9]}
                jsonPatient["address"].append(address)

            # parsing photo/attachment
            photo = {"id": dt[5], "contentType": dt[6], "language": dt[7], "data": dt[8], "url": dt[9],
                     "size": dt[10], "hash": dt[11], "title": dt[12]}
            jsonPatient["photo"].append(photo)

            # parsing contact
            contactID = dt[13]
            contact = {"id": dt[13], "relationship": {"text": dt[14], "coding": []}, "gender": dt[15],
                       "organization": dt[16]}
            jsonPatient["contact"].append(contact)

            # parsing contact human name
            cmd = "select HUMAN_NAME_ID, \"USE\", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX from fhir247.human_name where resource_id = '" + contactID + "' " \
                  "order by RESOURCE_ID ASC"
            cursor.execute(cmd, (PatientID,))
            dataHumanName = cursor.fetchall()

            for hum in dataHumanName:
                humanName = {
                    "name": {"id": hum[0], "use": hum[1], "text": hum[2], "family": hum[3], "given": hum[4].split('|'),
                             "prefix": hum[5].split('|'), "suffix": hum[6].split('|')}}
                jsonPatient["contact"].append(humanName)

            # parsing contact telecom
            cmd = "select CONTACT_POINT_ID, SYSTEM, \"VALUE\", 'USE', RANK FROM fhir247.contact_point where resource_id = '" + contactID + "' " \
                  "order by RESOURCE_ID ASC"
            cursor.execute(cmd, (PatientID,))
            dataTelecom = cursor.fetchall()

            for tel in dataTelecom:
                telecom = {"telecom": {"id": tel[0], "system": tel[1], "value": tel[2], "use": tel[3], "rank": tel[4]}}
                jsonPatient["contact"].append(telecom)

            # parsing contact address
            cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
                  "FROM fhir247.address where resource_id = '" + contactID + "' order by RESOURCE_ID ASC"
            cursor.execute(cmd, (PatientID,))
            dataAddress = cursor.fetchall()

            for add in dataAddress:
                address = {
                    "address": {"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
                                "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8],
                                "country": add[9]}}
                jsonPatient["contact"].append(address)

            # parsing communication
            communication = {"id": dt[17], "language": {"text": dt[18], "coding": []}, "preferred": dt[19]}
            jsonPatient["communication"].append(communication)

            # parsing link
            link = {"id": dt[20], "other": {"reference": dt[21]}, "type": dt[22]} #warn
            jsonPatient["link"].append(link)

            # parsing general practitoner
            generalPractitioner = {"id": dt[35], "reference": dt[36]}  # warn
            jsonPatient["generalPractitioner"].append(generalPractitioner)


            Patient.append(jsonPatient)
            index += 1

    conn.close()
    return Patient

24 june / fix getPatient(id) query in looping
def getPatient(id):
    conn = phoenixConn()
    cursor = conn.cursor()
    resourceID = id
    #metode 1
    ##begin
    cursor.execute("select PATIENT_ID, RESOURCE_TYPE, TO_CHAR(LAST_UPDATED, 'yyyy-MM-dd HH:mm:ss'), 'ACTIVE', GENDER, "
                   "TO_CHAR(BIRTHDATE, 'yyyy-MM-dd HH:mm:ss'), DECEASED_BOOLEAN, TO_CHAR(DECEASED_DATETIME, 'yyyy-MM-dd HH:mm:ss'), "
                   "MARITAL_STATUS, MULTIPLE_BIRTH_BOOLEAN, MULTIPLE_BIRTH_INTEGER, MANAGING_ORGANIZATION "
                   "FROM fhir247.patient where patient_id = '"+ resourceID +"' ")
    result = cursor.fetchall()

    Patient = []

    for resource in result:
        resourceID = resource[0]
        jsonPatient = {
                        "resourceType": resource[1],
                        "id": resourceID,
                        "meta": {"lastUpdated": resource[2], "versionId": ""},
                        "text":{"status": "", "div": ""},
                        "identifier": [],
                        "active": resource[3],
                        "name": [],
                        "telecom": [],
                        "gender": resource[4],
                        "birthDate": resource[5],
                        "deceasedBoolean": resource[6],
                        "deceasedDateTime": resource[7],
                        "address": [],
                        "maritalStatus": {"text": resource[8], "coding": []},
                        "multipleBirthBoolean": resource[9],
                        "multipleBirthInteger": resource[10],
                        "photo": [],
                        "contact": [],
                        "communication": [],
                        "generalPractitioner": [],
                        "managingOrganization": {"reference": resource[11]},
                        "link": []
                    }

        # def getIdentifier(resourceID):
        cmd = "select IDENTIFIER_ID, \"USE\", TYPE, SYSTEM, \"VALUE\" from fhir247.identifier where resource_id = '"+ resourceID + "'"
        cursor.execute(cmd, (resourceID,))
        dataIdentifier = cursor.fetchall()

        for ide in dataIdentifier:
            identifier = {"id": ide[0], "use": ide[1], "type": {"text": ide[2], "coding": []}, "system": ide[3], "value": ide[4]}
            jsonPatient["identifier"].append(identifier)

        # def getHumanName(resourceID):
        cmd = "select HUMAN_NAME_ID, \"USE\", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX from fhir247.human_name where resource_id = '"+ resourceID +"' " \
              "order by RESOURCE_ID ASC LIMIT 1"
        cursor.execute(cmd, (resourceID,))
        dataHumanName = cursor.fetchall()

        for hum in dataHumanName:
            humanName = {"id": hum[0], "use": hum[1], "text": hum[2], "family": hum[3], "given": hum[4].split('|'),
                         "prefix": hum[5].split('|'), "suffix": hum[6].split('|')}
            jsonPatient["name"].append(humanName)


        # def getContactPoint(resourceID):
        cmd = "select CONTACT_POINT_ID, SYSTEM, \"VALUE\", 'USE', RANK FROM fhir247.contact_point where resource_id = '"+ resourceID +"' " \
              "order by RESOURCE_ID ASC LIMIT 1"
        cursor.execute(cmd, (resourceID,))
        dataTelecom = cursor.fetchall()

        for tel in dataTelecom:
            telecom = {"id": tel[0], "system": tel[1], "value": tel[2], "use": tel[3], "rank": tel[4]}
            jsonPatient["telecom"].append(telecom)

        # def getAddress(resourceID):
        cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
              "FROM fhir247.address where resource_id = '"+ resourceID +"' order by RESOURCE_ID ASC LIMIT 1"
        cursor.execute(cmd, (resourceID,))
        dataAddress = cursor.fetchall()

        for add in dataAddress:
            address = {"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
                       "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8], "country": add[9]}
            jsonPatient["address"].append(address)

        # def getPhoto(resourceID):
        # e.ATTACHMENT_ID, e.CONTENT_TYPE, e.LANGUAGE, e.DATA, e.URL, e.SIZE, e.HASH, e.TITLE, e.RESOURCE_ID,
        cmd = "select ATTACHMENT_ID, CONTENT_TYPE, LANGUAGE, DATA, URL, SIZE, HASH, TITLE " \
              "FROM fhir247.attachment where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataPhoto = cursor.fetchall()

        for att in dataPhoto:
            photo = {"id": att[0], "contentType": att[1], "language": att[2], "data": att[3], "url": att[4],
                     "size": att[5], "hash": att[6], "title": att[7]}
            jsonPatient["photo"].append(photo)

        # def getContact(resourceID):
        cmd = "select CONTACT_ID, RELATIONSHIP, GENDER, ORGANIZATION " \
              "FROM fhir247.contact where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataContact = cursor.fetchall()

        for con in dataContact:
            contactID = con[0]
            contact = {"id": con[0], "relationship": {"text": con[1], "coding": []}, "gender": con[2],"organization": con[3]}
            jsonPatient["contact"].append(contact)

        # def getHumanNameContact(resourceID):
        cmd = "select HUMAN_NAME_ID, \"USE\", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX from fhir247.human_name where resource_id = '"+ contactID +"' " \
              "order by RESOURCE_ID ASC"
        cursor.execute(cmd, (resourceID,))
        dataHumanName = cursor.fetchall()

        for hum in dataHumanName:
            humanName = {"name":{"id": hum[0], "use": hum[1], "text": hum[2], "family": hum[3], "given": hum[4].split('|'),
                         "prefix": hum[5].split('|'), "suffix": hum[6].split('|')}}
            jsonPatient["contact"].append(humanName)

        # def getContactPointContact(resourceID):
        cmd = "select CONTACT_POINT_ID, SYSTEM, \"VALUE\", 'USE', RANK FROM fhir247.contact_point where resource_id = '"+ contactID +"' " \
              "order by RESOURCE_ID ASC"
        cursor.execute(cmd, (resourceID,))
        dataTelecom = cursor.fetchall()

        for tel in dataTelecom:
            telecom = {"telecom":{"id": tel[0], "system": tel[1], "value": tel[2], "use": tel[3], "rank": tel[4]}}
            jsonPatient["contact"].append(telecom)

        # def getAddressContact(resourceID):
        cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
              "FROM fhir247.address where resource_id = '"+ contactID +"' order by RESOURCE_ID ASC"
        cursor.execute(cmd, (resourceID,))
        dataAddress = cursor.fetchall()

        for add in dataAddress:
            address = {"address":{"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
                       "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8], "country": add[9]}}
            jsonPatient["contact"].append(address)

        # def getCommunication(resourceID):
        cmd = "select COMMUNICATION_ID, LANGUAGE, PREFERRED FROM fhir247.communication where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataCommunication = cursor.fetchall()

        for comm in dataCommunication:
            communication = {"id": comm[0], "language": {"text": comm[1], "coding": []}, "preferred": comm[2]}
            jsonPatient["communication"].append(communication)

        # def getGeneralPractitoner(resourceID):
        cmd = "select GENERAL_PRACTITONER_ID, REFERENCE FROM fhir247.general_practitoner where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataGeneralPractitoner = cursor.fetchall()

        for genprac in dataGeneralPractitoner:
            generalPractitoner = {"id": genprac[0], "reference": genprac[1]}
            jsonPatient["generalPractitioner"].append(generalPractitoner)

        # def getLink(resourceID):
        cmd = "select LINK_ID, OTHER, TYPE FROM fhir247.link where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataLink = cursor.fetchall()

        for lnk in dataLink:
            link = {"id": lnk[0], "other": {"reference": lnk[1]}, "type": lnk[2]}
            jsonPatient["link"].append(link)

        # def getCon(resourceID);
        # cmd = "select PATIENT_ID, RESOURCE_TYPE, LAST_UPDATED, ACTIVE, GENDER, DECEASED_BOOLEAN, DECEASED_DATETIME," \
        #       "MARITAL_STATUS, MULTIPLE_BIRTH_BOOLEAN, MULTIPLE_BIRTH_INTEGER, MANAGING_ORGANIZATION " \
        #       "FROM fhir247.patient where patient_id = '"+ resourceID +"' "
        # cursor.execute(cmd, (resourceID,))
        # dataPatient = cursor.fetchall()
        #
        # for ptn in dataPatient:
        #     patient = {"resourceType": ptn[46], "meta": {"lastUpdate": ptn[47], "versionId": 0}, "active": ptn[48],
        #                "gender": ptn[49], "birthDate": ptn[50], "deceasedBoolean": ptn[51], "deceasedDateTime": ptn[52],
        #                "maritalStatus": {"text": ptn[53], "coding": []}, "multipleBirthBoolean": ptn[54], "multipleBirthInteger": ptn[55]}
        #     jsonPatient.append(patient)

        Patient.append(jsonPatient)

    #metode 1
    ##end

    return Patient


//query in not looping
def getPatients():
    try:
        conn = phoenixConn()
        cursor = conn.cursor()

        cmd = "SELECT b.HUMAN_NAME_ID , b.\"USE\", b.TEXT, b.FAMILY, b.GIVEN, b.PREFIX, b.SUFFIX, " \
              "c.CONTACT_POINT_ID, c.SYSTEM, c.\"VALUE\", c.\"USE\", c.RANK, " \
              "f.CONTACT_ID, f.RELATIONSHIP, f.GENDER, f.ORGANIZATION, " \
              "i.PATIENT_ID, i.RESOURCE_TYPE, TO_CHAR(i.LAST_UPDATED, \'yyyy-MM-dd HH:mm:ss\'), i.\"ACTIVE\", " \
              "i.GENDER, TO_CHAR(i.BIRTHDATE, \'yyyy-MM-dd\'), i.DECEASED_BOOLEAN, TO_CHAR(i.DECEASED_DATETIME, \'yyyy-MM-dd HH:mm:ss\'), " \
              "i.MARITAL_STATUS, i.MULTIPLE_BIRTH_BOOLEAN, i.MULTIPLE_BIRTH_INTEGER, i.MANAGING_ORGANIZATION " \
              "FROM FHIR247.HUMAN_NAME b, FHIR247.CONTACT_POINT c, " \
              "FHIR247.CONTACT f, FHIR247.PATIENT i " \
              "WHERE b.resource_id = i.patient_id AND c.resource_id = i.patient_id AND f.resource_id = i.patient_id " \
              "OR b.resource_id = f.contact_id AND c.resource_id = f.contact_id AND f.resource_id = i.patient_id " \
              "ORDER BY i.PATIENT_ID "
        cursor.execute(cmd)
        data = cursor.fetchall()

        # resp = jsonify(data)
        # resp.status_code = 200

        columns = [desc[0] for desc in cursor.description]
        result = []
        for row in data:
            row = dict(zip(columns, row))
            result.append(row)

        return result

    except Exception as e:
        print(e)
    finally:
        conn.close()

25 june
def getPatients():
    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    #
    # condition = ""
    offset_limit = ""

    if offset and limit:
        offset_limit = 'LIMIT ' + limit + ' OFFSET ' + offset
    else:
        offset = 0
        limit = 0

    ##metode2 (JOIN di Phoenix)

    # cmd = "SELECT a.IDENTIFIER_ID, a.\"USE\", a.TYPE, a.SYSTEM, a.\"VALUE\", " \
    #       "b.HUMAN_NAME_ID , b.\"USE\", b.TEXT, b.FAMILY, b.GIVEN, b.PREFIX, b.SUFFIX, b.RESOURCE_ID, " \
    #       "c.CONTACT_POINT_ID, c.SYSTEM, c.\"VALUE\", c.\"USE\", c.RANK, c.RESOURCE_ID, " \
    #       "d.ADDRESS_ID, d.\"USE\", d.\"TYPE\", d.TEXT, d.LINE, d.CITY, d.DISTRICT, d.STATE, d.COUNTRY, d.POSTAL_CODE, d.RESOURCE_ID, " \
    #       "e.ATTACHMENT_ID, e.CONTENT_TYPE, e.LANGUAGE, e.DATA, e.URL, e.SIZE, e.HASH, e.TITLE, " \
    #       "f.CONTACT_ID, f.RELATIONSHIP, f.GENDER, f.ORGANIZATION, f.RESOURCE_ID, " \
    #       "g.COMMUNICATION_ID, g.LANGUAGE, g.PREFERRED, h.LINK_ID, h.OTHER, h.TYPE, " \
    #       "i.PATIENT_ID, i.RESOURCE_TYPE, TO_CHAR(i.LAST_UPDATED, \'yyyy-MM-dd HH:mm:ss\'), i.\"ACTIVE\", " \
    #       "i.GENDER, TO_CHAR(i.BIRTHDATE, \'yyyy-MM-dd\'), i.DECEASED_BOOLEAN, TO_CHAR(i.DECEASED_DATETIME, \'yyyy-MM-dd HH:mm:ss\'), " \
    #       "i.MARITAL_STATUS, i.MULTIPLE_BIRTH_BOOLEAN, i.MULTIPLE_BIRTH_INTEGER, i.MANAGING_ORGANIZATION, " \
    #       "j.GENERAL_PRACTITONER_ID, j.REFERENCE " \
    #       "FROM FHIR247.IDENTIFIER a, FHIR247.HUMAN_NAME b, FHIR247.CONTACT_POINT c, FHIR247.ADDRESS d, " \
    #       "FHIR247.ATTACHMENT e, FHIR247.CONTACT f, FHIR247.COMMUNICATION g, FHIR247.LINK h, FHIR247.PATIENT i, FHIR247.GENERAL_PRACTITONER j " \
    #       "WHERE a.resource_id = i.patient_id AND e.resource_id = i.patient_id AND f.resource_id = i.patient_id AND " \
    #       "g.resource_id = i.patient_id AND (h.resource_id = i.patient_id OR h.resource_id IS NULL)AND j.resource_id = i.patient_id AND " \
    #       "((b.resource_id = i.patient_id AND c.resource_id = i.patient_id AND d.resource_id = i.patient_id) OR " \
    #       "(b.resource_id = f.contact_id AND c.resource_id = f.contact_id AND d.resource_id = f.contact_id)) " \
    #       "ORDER BY i.patient_id"

    cmd = "SELECT a.IDENTIFIER_ID, a.\"USE\", a.TYPE, a.SYSTEM, a.\"VALUE\", " \
          "b.HUMAN_NAME_ID , b.\"USE\", b.TEXT, b.FAMILY, b.GIVEN, b.PREFIX, b.SUFFIX, b.RESOURCE_ID, " \
          "c.CONTACT_POINT_ID, c.SYSTEM, c.\"VALUE\", c.\"USE\", c.RANK, c.RESOURCE_ID, " \
          "d.ADDRESS_ID, d.\"USE\", d.\"TYPE\", d.TEXT, d.LINE, d.CITY, d.DISTRICT, d.STATE, d.COUNTRY, d.POSTAL_CODE, d.RESOURCE_ID, " \
          "e.ATTACHMENT_ID, e.CONTENT_TYPE, e.LANGUAGE, e.DATA, e.URL, e.SIZE, e.HASH, e.TITLE, " \
          "f.CONTACT_ID, f.RELATIONSHIP, f.GENDER, f.ORGANIZATION, f.RESOURCE_ID, " \
          "g.COMMUNICATION_ID, g.LANGUAGE, g.PREFERRED, h.LINK_ID, h.OTHER, h.TYPE, " \
          "i.PATIENT_ID, i.RESOURCE_TYPE, TO_CHAR(i.LAST_UPDATED, \'yyyy-MM-dd HH:mm:ss\'), i.\"ACTIVE\", " \
          "i.GENDER, TO_CHAR(i.BIRTHDATE, \'yyyy-MM-dd\'), i.DECEASED_BOOLEAN, TO_CHAR(i.DECEASED_DATETIME, \'yyyy-MM-dd HH:mm:ss\'), " \
          "i.MARITAL_STATUS, i.MULTIPLE_BIRTH_BOOLEAN, i.MULTIPLE_BIRTH_INTEGER, i.MANAGING_ORGANIZATION, " \
          "j.GENERAL_PRACTITONER_ID, j.REFERENCE " \
          "FROM FHIR247.HUMAN_NAME b " \
          "LEFT JOIN FHIR247.IDENTIFIER a ON a.resource_id = b.resource_id " \
          "LEFT JOIN FHIR247.PATIENT i ON i.patient_id = b.resource_id " \
          "LEFT JOIN FHIR247.CONTACT_POINT c ON c.resource_id = b.resource_id " \
          "LEFT JOIN FHIR247.ADDRESS d ON d.resource_id = b.resource_id " \
          "LEFT JOIN FHIR247.ATTACHMENT e ON e.resource_id = b.resource_id " \
          "LEFT JOIN FHIR247.CONTACT f ON f.contact_id = b.resource_id " \
          "LEFT JOIN FHIR247.COMMUNICATION g ON g.resource_id = b.resource_id " \
          "LEFT JOIN FHIR247.LINK h ON h.resource_id = b.resource_id " \
          "LEFT JOIN FHIR247.GENERAL_PRACTITONER j ON j.resource_id = b.resource_id "

    # identifier 0-4, human_name 5 - 12, contact_id 13 -18, address 19-29, attachment 30-37, contact 38-42,
    # communication 43-45, link 46-48, patient 49-60, general_practitoner 61-62

    conn = phoenixConn()
    cursor = conn.cursor()

    Patient = []

    cursor.execute(cmd)
    data = result = cursor.fetchall()

    # set default value of resources
    PatientID = ""
    index = 0

    for dt in data:
        # patient 49-60
        if PatientID == dt[49]:
            exist = True
        else:
            PatientID = dt[49]
            exist = False

        if exist:
            # parsing identifier 0-4
            identifier = {"id": dt[0], "use": dt[1], "type": {"text": dt[2], "coding": []}, "system": dt[3],
                          "value": dt[4]}
            Patient[index - 1]["identifier"].append(identifier)
            Patient[index - 1]["identifier"] = RemoveDuplicateArray(Patient[index - 1]["identifier"])

            # parsing human_name 5-12
            if dt[12] == dt[49]:
                humanName = {"id": dt[5], "use": dt[6], "text": dt[7], "family": dt[8], "given": dt[9].split('|'),
                             "prefix": dt[10].split('|'), "suffix": dt[11].split('|')}
                Patient[index - 1]["name"].append(humanName)
                Patient[index - 1]["name"] = RemoveDuplicateArray(Patient[index - 1]["name"])
            else:
                humanNameContact = {"name": {"id": dt[5], "use": dt[6], "text": dt[7], "family": dt[8], "given": dt[9].split('|'),
                                    "prefix": dt[10].split('|'), "suffix": dt[11].split('|')}}
                Patient[index - 1]["contact"].append(humanNameContact)
                Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["name"])

            # parsing contact_point 13-18
            if dt[18] == dt[49]:
                telecom = {"id": dt[13], "system": dt[14], "value": dt[15], "use": dt[16], "rank": dt[17]}
                Patient[index - 1]["telecom"].append(telecom)
                Patient[index - 1]["telecom"] = RemoveDuplicateArray(Patient[index - 1]["telecom"])
            else:
                telecomContact = {"telecom": {"id": dt[13], "system": dt[14], "value": dt[15], "use": dt[16], "rank": dt[17]}}
                Patient[index - 1]["contact"].append(telecomContact)
                Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

            # parsing address 19-29
            if dt[29] == dt[49]:
                address = {"id": dt[19], "use": dt[20], "type": dt[21], "text": dt[22], "line": dt[23].split('|'),
                           "city": dt[24], "district": dt[25], "state": dt[26], "postalCode": dt[27], "country": dt[28]}
                Patient[index - 1]["address"].append(address)
                Patient[index - 1]["address"] = RemoveDuplicateArray(Patient[index - 1]["address"])
            else:
                addressContact = {"address":{"id": dt[19], "use": dt[20], "type": dt[21], "text": dt[22], "line": dt[23].split('|'),
                                "city": dt[24], "district": dt[25], "state": dt[26], "postalCode": dt[27], "country": dt[28]}}
                Patient[index - 1]["contact"].append(addressContact)
                Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

            # parsing photo/attachment 30-37
            photo = {"id": dt[30], "contentType": dt[31], "language": dt[32], "data": dt[33], "url": dt[34],
                     "size": dt[35], "hash": dt[36], "title": dt[37]}
            Patient[index - 1]["photo"].append(photo)
            Patient[index - 1]["photo"] = RemoveDuplicateArray(Patient[index - 1]["photo"])

            # parsing contact 38-42
            contact = {"id": dt[38], "relationship": {"text": dt[39], "coding": []}, "gender": dt[40],
                       "organization": dt[41]}
            Patient[index - 1]["contact"].append(contact)
            Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

            # parsing communication 43-45
            communication = {"id": dt[43], "language": {"text": dt[44], "coding": []}, "preferred": dt[45]}
            Patient[index - 1]["communication"].append(communication)
            Patient[index - 1]["communication"] = RemoveDuplicateArray(Patient[index - 1]["communication"])

            # parsing link 46-48
            link = {"id": dt[46], "other": {"reference": dt[47]}, "type": dt[48]}
            Patient[index - 1]["link"].append(link)
            Patient[index - 1]["link"] = RemoveDuplicateArray(Patient[index - 1]["link"])

            # parsing general practitoner 61-62
            generalPractitioner =  {"id": dt[61], "reference": dt[62]}
            Patient[index - 1]["generalPractitioner"].append(generalPractitioner)
            Patient[index - 1]["generalPractitioner"] = RemoveDuplicateArray(Patient[index - 1]["generalPractitioner"])

            # insert patient
            # patient = {"resourceType": dt[20], "meta": {"lastUpdate": dt[21], "versionId": 0}, "active": dt[22],
            #            "gender": dt[23], "birthDate": dt[24], "deceasedBoolean": dt[25], "deceasedDateTime": dt[26],
            #            "maritalStatus": {"text": dt[27], "coding": []}, "multipleBirthBoolean": dt[28],
            #            "multipleBirthInteger": dt[29], "managingOrganization" : {"reference": dt[30]}}
            # Patient.append(patient)
            # Patient[index - 1] = RemoveDuplicateArray(Patient[index - 1])

        else:
            # patient 49-60
            jsonPatient = {
                "resourceType": dt[50],
                "id": dt[49],
                "meta": {"lastUpdated": dt[51], "versionId": ""},
                "text": {"status": "", "div": ""},
                "identifier": [],
                "active": dt[52],
                "name": [],
                "telecom": [],
                "gender": dt[53],
                "birthDate": dt[54],
                "deceasedBoolean": dt[55],
                "deceasedDateTime": dt[56],
                "address": [],
                "maritalStatus": {"text": dt[57], "coding": []},
                "multipleBirthBoolean": dt[58],
                "multipleBirthInteger": dt[59],
                "photo": [],
                "contact": [],
                "communication": [],
                "generalPractitioner": [],
                "managingOrganization": {"reference": dt[60]},
                "link": []
            }

            # parsing identifier 0-4
            identifier = {"id": dt[0], "use": dt[1], "type": {"text": dt[2], "coding": []}, "system": dt[3],
                          "value": dt[4]}
            jsonPatient["identifier"].append(identifier)

            # parsing human_name 5-12
            if dt[12] == dt[49]:
                humanName = {"id": dt[5], "use": dt[6], "text": dt[7], "family": dt[8], "given": dt[9].split('|'),
                             "prefix": dt[10].split('|'), "suffix": dt[11].split('|')}
                jsonPatient["name"].append(humanName)
            else:
                humanNameContact = {"name": {"id": dt[5], "use": dt[6], "text": dt[7], "family": dt[8], "given": dt[9].split('|'),
                             "prefix": dt[10].split('|'), "suffix": dt[11].split('|')}}
                jsonPatient["contact"].append(humanNameContact)

            # parsing contact_id 13-18
            if dt[18] == dt[49]:
                telecom = {"id": dt[13], "system": dt[14], "value": dt[15], "use": dt[16], "rank": dt[17]}
                jsonPatient["telecom"].append(telecom)
            else:
                telecomContact = {"telecom": {"id": dt[13], "system": dt[14], "value": dt[15], "use": dt[16], "rank": dt[17]}}
                jsonPatient["contact"].append(telecomContact)

            # parsing address 19-29
            if dt[29] == dt[49]:
                address = {"id": dt[19], "use": dt[20], "type": dt[21], "text": dt[22], "line": dt[23].split('|'),
                           "city": dt[24], "district": dt[25], "state": dt[26], "postalCode": dt[27], "country": dt[28]}
                jsonPatient["address"].append(address)
            else:
                addressContact = {"address":{"id": dt[19], "use": dt[20], "type": dt[21], "text": dt[22], "line": dt[23].split('|'),
                           "city": dt[24], "district": dt[25], "state": dt[26], "postalCode": dt[27], "country": dt[28]}}
                jsonPatient["contact"].append(addressContact)

            # parsing photo/attachment 30-37
            photo = {"id": dt[30], "contentType": dt[31], "language": dt[32], "data": dt[33], "url": dt[34],
                     "size": dt[35], "hash": dt[36], "title": dt[37]}
            jsonPatient["photo"].append(photo)

            # parsing contact 38-42
            contact = {"id": dt[38], "relationship": {"text": dt[39], "coding": []}, "gender": dt[40],
                       "organization": dt[41]}
            jsonPatient["contact"].append(contact)

            # parsing communication 43-45
            communication = {"id": dt[43], "language": {"text": dt[44], "coding": []}, "preferred": dt[45]}
            jsonPatient["communication"].append(communication)

            # parsing link 46-48
            link = {"id": dt[46], "other": {"reference": dt[47]}, "type": dt[48]}
            jsonPatient["communication"].append(communication)

            # parsing general practitoner 61-62
            generalPractitioner =  {"id": dt[61], "reference": dt[62]}
            jsonPatient["generalPractitioner"].append(generalPractitioner)

            Patient.append(jsonPatient)
            index += 1

    conn.close()
    return Patient

26 june
//query getPatient(id) not query in looping
def getPatient(id):
    conn = phoenixConn()
    cursor = conn.cursor()
    resourceID = id
    #metode 1
    ##begin
    cursor.execute("select PATIENT_ID, RESOURCE_TYPE, TO_CHAR(LAST_UPDATED, 'yyyy-MM-dd HH:mm:ss'), 'ACTIVE', GENDER, "
                   "TO_CHAR(BIRTHDATE, 'yyyy-MM-dd HH:mm:ss'), DECEASED_BOOLEAN, TO_CHAR(DECEASED_DATETIME, 'yyyy-MM-dd HH:mm:ss'), "
                   "MARITAL_STATUS, MULTIPLE_BIRTH_BOOLEAN, MULTIPLE_BIRTH_INTEGER, MANAGING_ORGANIZATION "
                   "FROM fhir247.patient where patient_id = '"+ resourceID +"' ")
    result = cursor.fetchall()

    Patient = []

    for resource in result:
        resourceID = resource[0]
        jsonPatient = {
                        "resourceType": resource[1],
                        "id": resourceID,
                        "meta": {"lastUpdated": resource[2], "versionId": ""},
                        "text":{"status": "", "div": ""},
                        "identifier": [],
                        "active": resource[3],
                        "name": [],
                        "telecom": [],
                        "gender": resource[4],
                        "birthDate": resource[5],
                        "deceasedBoolean": resource[6],
                        "deceasedDateTime": resource[7],
                        "address": [],
                        "maritalStatus": {"text": resource[8], "coding": []},
                        "multipleBirthBoolean": resource[9],
                        "multipleBirthInteger": resource[10],
                        "photo": [],
                        "contact": [],
                        "communication": [],
                        "generalPractitioner": [],
                        "managingOrganization": {"reference": resource[11]},
                        "link": []
                    }

        # def getIdentifier(resourceID):
        cmd = "select IDENTIFIER_ID, \"USE\", TYPE, SYSTEM, \"VALUE\" from fhir247.identifier where resource_id = '"+ resourceID + "'"
        cursor.execute(cmd, (resourceID,))
        dataIdentifier = cursor.fetchall()

        for ide in dataIdentifier:
            identifier = {"id": ide[0], "use": ide[1], "type": {"text": ide[2], "coding": []}, "system": ide[3], "value": ide[4]}
            jsonPatient["identifier"].append(identifier)

        # def getHumanName(resourceID):
        cmd = "select HUMAN_NAME_ID, \"USE\", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX from fhir247.human_name where resource_id = '"+ resourceID +"' " \
              "order by RESOURCE_ID ASC LIMIT 1"
        cursor.execute(cmd, (resourceID,))
        dataHumanName = cursor.fetchall()

        for hum in dataHumanName:
            humanName = {"id": hum[0], "use": hum[1], "text": hum[2], "family": hum[3], "given": hum[4].split('|'),
                         "prefix": hum[5].split('|'), "suffix": hum[6].split('|')}
            jsonPatient["name"].append(humanName)


        # def getContactPoint(resourceID):
        cmd = "select CONTACT_POINT_ID, SYSTEM, \"VALUE\", 'USE', RANK FROM fhir247.contact_point where resource_id = '"+ resourceID +"' " \
              "order by RESOURCE_ID ASC LIMIT 1"
        cursor.execute(cmd, (resourceID,))
        dataTelecom = cursor.fetchall()

        for tel in dataTelecom:
            telecom = {"id": tel[0], "system": tel[1], "value": tel[2], "use": tel[3], "rank": tel[4]}
            jsonPatient["telecom"].append(telecom)

        # def getAddress(resourceID):
        cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
              "FROM fhir247.address where resource_id = '"+ resourceID +"' order by RESOURCE_ID ASC LIMIT 1"
        cursor.execute(cmd, (resourceID,))
        dataAddress = cursor.fetchall()

        for add in dataAddress:
            address = {"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
                       "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8], "country": add[9]}
            jsonPatient["address"].append(address)

        # def getPhoto(resourceID):
        # e.ATTACHMENT_ID, e.CONTENT_TYPE, e.LANGUAGE, e.DATA, e.URL, e.SIZE, e.HASH, e.TITLE, e.RESOURCE_ID,
        cmd = "select ATTACHMENT_ID, CONTENT_TYPE, LANGUAGE, DATA, URL, SIZE, HASH, TITLE " \
              "FROM fhir247.attachment where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataPhoto = cursor.fetchall()

        for att in dataPhoto:
            photo = {"id": att[0], "contentType": att[1], "language": att[2], "data": att[3], "url": att[4],
                     "size": att[5], "hash": att[6], "title": att[7]}
            jsonPatient["photo"].append(photo)

        # def getContact(resourceID):
        cmd = "select CONTACT_ID, RELATIONSHIP, GENDER, ORGANIZATION " \
              "FROM fhir247.contact where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataContact = cursor.fetchall()

        for con in dataContact:
            contactID = con[0]
            contact = {"id": con[0], "relationship": {"text": con[1], "coding": []}, "gender": con[2],"organization": con[3]}
            jsonPatient["contact"].append(contact)

        # def getHumanNameContact(resourceID):
        cmd = "select HUMAN_NAME_ID, \"USE\", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX from fhir247.human_name where resource_id = '"+ contactID +"' " \
              "order by RESOURCE_ID ASC"
        cursor.execute(cmd, (resourceID,))
        dataHumanName = cursor.fetchall()

        for hum in dataHumanName:
            humanName = {"name":{"id": hum[0], "use": hum[1], "text": hum[2], "family": hum[3], "given": hum[4].split('|'),
                         "prefix": hum[5].split('|'), "suffix": hum[6].split('|')}}
            jsonPatient["contact"].append(humanName)

        # def getContactPointContact(resourceID):
        cmd = "select CONTACT_POINT_ID, SYSTEM, \"VALUE\", 'USE', RANK FROM fhir247.contact_point where resource_id = '"+ contactID +"' " \
              "order by RESOURCE_ID ASC"
        cursor.execute(cmd, (resourceID,))
        dataTelecom = cursor.fetchall()

        for tel in dataTelecom:
            telecom = {"telecom":{"id": tel[0], "system": tel[1], "value": tel[2], "use": tel[3], "rank": tel[4]}}
            jsonPatient["contact"].append(telecom)

        # def getAddressContact(resourceID):
        cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
              "FROM fhir247.address where resource_id = '"+ contactID +"' order by RESOURCE_ID ASC"
        cursor.execute(cmd, (resourceID,))
        dataAddress = cursor.fetchall()

        for add in dataAddress:
            address = {"address":{"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
                       "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8], "country": add[9]}}
            jsonPatient["contact"].append(address)

        # def getCommunication(resourceID):
        cmd = "select COMMUNICATION_ID, LANGUAGE, PREFERRED FROM fhir247.communication where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataCommunication = cursor.fetchall()

        for comm in dataCommunication:
            communication = {"id": comm[0], "language": {"text": comm[1], "coding": []}, "preferred": comm[2]}
            jsonPatient["communication"].append(communication)

        # def getGeneralPractitoner(resourceID):
        cmd = "select GENERAL_PRACTITONER_ID, REFERENCE FROM fhir247.general_practitoner where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataGeneralPractitoner = cursor.fetchall()

        for genprac in dataGeneralPractitoner:
            generalPractitoner = {"id": genprac[0], "reference": genprac[1]}
            jsonPatient["generalPractitioner"].append(generalPractitoner)

        # def getLink(resourceID):
        cmd = "select LINK_ID, OTHER, TYPE FROM fhir247.link where resource_id = '"+ resourceID +"' "
        cursor.execute(cmd, (resourceID,))
        dataLink = cursor.fetchall()

        for lnk in dataLink:
            link = {"id": lnk[0], "other": {"reference": lnk[1]}, "type": lnk[2]}
            jsonPatient["link"].append(link)

        # def getCon(resourceID);
        # cmd = "select PATIENT_ID, RESOURCE_TYPE, LAST_UPDATED, ACTIVE, GENDER, DECEASED_BOOLEAN, DECEASED_DATETIME," \
        #       "MARITAL_STATUS, MULTIPLE_BIRTH_BOOLEAN, MULTIPLE_BIRTH_INTEGER, MANAGING_ORGANIZATION " \
        #       "FROM fhir247.patient where patient_id = '"+ resourceID +"' "
        # cursor.execute(cmd, (resourceID,))
        # dataPatient = cursor.fetchall()
        #
        # for ptn in dataPatient:
        #     patient = {"resourceType": ptn[46], "meta": {"lastUpdate": ptn[47], "versionId": 0}, "active": ptn[48],
        #                "gender": ptn[49], "birthDate": ptn[50], "deceasedBoolean": ptn[51], "deceasedDateTime": ptn[52],
        #                "maritalStatus": {"text": ptn[53], "coding": []}, "multipleBirthBoolean": ptn[54], "multipleBirthInteger": ptn[55]}
        #     jsonPatient.append(patient)

        Patient.append(jsonPatient)

    #metode 1
    ##end

    return Patient

# 24 june get not query in loop
def getPatients():
    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    #
    # condition = ""
    offset_limit = ""

    if offset and limit:
        offset_limit = 'LIMIT ' + limit + ' OFFSET ' + offset
    else:
        offset = 0
        limit = 0

    ##metode2 (JOIN di Phoenix)

    cmd = "SELECT b.HUMAN_NAME_ID , b.\"USE\", b.TEXT, b.FAMILY, b.GIVEN, b.PREFIX, b.SUFFIX, b.RESOURCE_ID, " \
          "c.CONTACT_POINT_ID, c.SYSTEM, c.\"VALUE\", c.\"USE\", c.RANK, c.RESOURCE_ID, " \
          "f.CONTACT_ID, f.RELATIONSHIP, f.GENDER, f.ORGANIZATION, f.RESOURCE_ID, " \
          "i.PATIENT_ID, i.RESOURCE_TYPE, TO_CHAR(i.LAST_UPDATED, \'yyyy-MM-dd HH:mm:ss\'), i.\"ACTIVE\", " \
          "i.GENDER, TO_CHAR(i.BIRTHDATE, \'yyyy-MM-dd\'), i.DECEASED_BOOLEAN, TO_CHAR(i.DECEASED_DATETIME, \'yyyy-MM-dd HH:mm:ss\'), " \
          "i.MARITAL_STATUS, i.MULTIPLE_BIRTH_BOOLEAN, i.MULTIPLE_BIRTH_INTEGER, i.MANAGING_ORGANIZATION " \
          "FROM FHIR247.HUMAN_NAME b, FHIR247.CONTACT_POINT c, " \
          "FHIR247.CONTACT f, FHIR247.PATIENT i " \
          "WHERE b.resource_id = i.patient_id AND c.resource_id = i.patient_id AND f.resource_id = i.patient_id " \
          "OR b.resource_id = f.contact_id AND c.resource_id = f.contact_id AND f.resource_id = i.patient_id " \
          "ORDER BY i.PATIENT_ID "
    # cmd = "SELECT b.HUMAN_NAME_ID as humanNameID, b.\"USE\" as use, b.TEXT as text, b.FAMILY as family, b.GIVEN as given, b.PREFIX as prefix, b.SUFFIX as suffix, b.RESOURCE_ID as nameResourceID, " \
    #       "c.CONTACT_POINT_ID as contactPointID, c.SYSTEM as system, c.\"VALUE\" as value, c.\"USE\" as use, c.RANK as rank, c.RESOURCE_ID as telecomResourceID, " \
    #       "f.CONTACT_ID as contactID, f.RELATIONSHIP as relationship, f.GENDER as gender, f.ORGANIZATION as organization, f.RESOURCE_ID as contactResourceID, " \
    #       "i.PATIENT_ID as patientID, i.RESOURCE_TYPE as resourceType, TO_CHAR(i.LAST_UPDATED, \'yyyy-MM-dd HH:mm:ss\') as lastUpdated, i.\"ACTIVE\" as active, " \
    #       "i.GENDER as gender, TO_CHAR(i.BIRTHDATE, \'yyyy-MM-dd\') as birthDate, i.DECEASED_BOOLEAN as deceasedBoolean, TO_CHAR(i.DECEASED_DATETIME, \'yyyy-MM-dd HH:mm:ss\') as deceasedDatetime, " \
    #       "i.MARITAL_STATUS as maritalStatus, i.MULTIPLE_BIRTH_BOOLEAN as multipleBirthBoolean, i.MULTIPLE_BIRTH_INTEGER as multipleBirthInteger, i.MANAGING_ORGANIZATION as managingOrganization" \
    #       "FROM FHIR247.HUMAN_NAME b, FHIR247.CONTACT_POINT c, " \
    #       "FHIR247.CONTACT f, FHIR247.PATIENT i " \
    #       "WHERE b.resource_id = i.patient_id AND c.resource_id = i.patient_id AND f.resource_id = i.patient_id " \
    #       "OR b.resource_id = f.contact_id AND c.resource_id = f.contact_id AND f.resource_id = i.patient_id " \
    #       "ORDER BY i.PATIENT_ID "


    # human_name 0-7, contact_point 8 - 13, contact 14-18, patient 19-30
    # identifier 0 - 4, attachment 5 - 12, contact 13-16, communication 17 - 19, link 20 - 22, patient 23 - 34, general_prac 35 - 36

    conn = phoenixConn()
    cursor = conn.cursor()

    Patient = []

    cursor.execute(cmd)
    data = result = cursor.fetchall()

    # resp = jsonify(data)
    # resp.status_code = 200
    # return resp

    # set default value of resources
    PatientID = ""
    index = 0

    for dt in data:
        if PatientID == dt[19]:
            exist = True
        else:
            PatientID = dt[19]
            exist = False

        if exist:
        # #     # insert identifier
        # #     # identifier = {"id": dt[0], "use": dt[1], "type": {"text": dt[2], "coding": []}, "system": dt[3],
        # #     #               "value": dt[4]}
        # #     # Patient[index - 1]["identifier"].append(identifier)
        # #     # Patient[index - 1]["identifier"] = RemoveDuplicateArray(Patient[index - 1]["identifier"])
        # #
        # #     # insert human_name
        # #     # humanName = {"id": dt[5], "use": dt[6], "text": dt[7], "family": dt[8], "given": dt[9].split('|'),
        # #     #              "prefix": dt[10].split('|'), "suffix": dt[11].split('|')}
        # #     # Patient[index - 1]["name"].append(humanName)
        # #     # Patient[index - 1]["name"] = RemoveDuplicateArray(Patient[index - 1]["name"])
        # #     #
        # #     # # insert telecom/contactpoint
        # #     # contactPoint = {"id": dt[13], "system": dt[14], "value": dt[15], "use": dt[16], "rank": dt[17]}
        # #     # Patient[index - 1]["telecom"].append(contactPoint)
        # #     # Patient[index - 1]["telecom"] = RemoveDuplicateArray(Patient[index - 1]["telecom"])
        # #
        # #     # for hum in data:
            if dt[7] == dt[19]:
                humanName = {"id": dt[0], "use": dt[1], "text": dt[2], "family": dt[3], "given": dt[4].split('|'),
                             "prefix": dt[5].split('|'), "suffix": dt[6].split('|')}
                jsonPatient["name"].append(humanName)
                Patient[index - 1]["name"].append(humanName)
                Patient[index - 1]["name"] = RemoveDuplicateArray(Patient[index - 1]["name"])
            else:
                humanNameContact = {"name": {"id": dt[0], "use": dt[1], "text": dt[2], "family": dt[3],
                                             "given": dt[4].split('|'),
                                             "prefix": dt[5].split('|'), "suffix": dt[6].split('|')}}
                jsonPatient["contact"].append(humanNameContact)
                Patient[index - 1]["contact"].append(humanNameContact)
                Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["name"])

            # parsing contact_point
            # for tel in data:
            if dt[13] == dt[19]:
                telecom = {"id": dt[8], "system": dt[9], "value": dt[10], "use": dt[11], "rank": dt[12]}
                jsonPatient["telecom"].append(telecom)
                Patient[index - 1]["telecom"].append(telecom)
                Patient[index - 1]["telecom"] = RemoveDuplicateArray(Patient[index - 1]["telecom"])
            else:
                telecomContact = {"telecom": {"id": dt[8], "system": dt[9], "value": dt[10], "use": dt[11], "rank": dt[12]}}
                jsonPatient["contact"].append(telecomContact)
                Patient[index - 1]["contact"].append(telecomContact)
                Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])
        #
        #     #
        #     # # insert address
        #     # address = {"id": dt[18], "use": dt[19], "type": dt[20], "text": dt[21], "line": dt[22].split('|'),
        #     #            "city": dt[23], "district": dt[24], "state": dt[25], "postalCode": dt[26], "country": dt[27]}
        #     # Patient[index - 1]["address"].append(address)
        #     # Patient[index - 1]["address"] = RemoveDuplicateArray(Patient[index - 1]["address"])
        #
        #     # # insert photo/attachment
        #     # photo = {"id": dt[5], "contentType": dt[6], "language": dt[7], "data": dt[8], "url": dt[9],
        #     #          "size": dt[10], "hash": dt[11], "title": dt[12]}
        #     # Patient[index - 1]["photo"].append(photo)
        #     # Patient[index - 1]["photo"] = RemoveDuplicateArray(Patient[index - 1]["photo"])
        #
            # insert contact
            contact = {"id": dt[14], "relationship": {"text": dt[15], "coding": []}, "gender": dt[16],
                       "organization": dt[17]}
            Patient[index - 1]["contact"].append(contact)
            Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])
        #
        #
        #     # # insert communication
        #     # communication = {"id": dt[17], "language": {"text": dt[18], "coding": []}, "preferred": dt[19]}
        #     # Patient[index - 1]["communication"].append(communication)
        #     # Patient[index - 1]["communication"] = RemoveDuplicateArray(Patient[index - 1]["communication"])
        #     #
        #     # # insert link
        #     # link = {"id": dt[20], "other": {"reference": dt[21]}, "type": dt[22]} #warn
        #     # Patient[index - 1]["link"].append(link)
        #     # Patient[index - 1]["link"] = RemoveDuplicateArray(Patient[index - 1]["link"])
        #     #
        #     # # insert general practitoner
        #     # generalPractitioner =  {"id": dt[35], "reference": dt[36]}  # warn
        #     # Patient[index - 1]["generalPractitioner"].append(generalPractitioner)
        #     # Patient[index - 1]["generalPractitioner"] = RemoveDuplicateArray(Patient[index - 1]["generalPractitioner"])
        #
            # insert patient
            # patient = {"resourceType": dt[20], "meta": {"lastUpdate": dt[21], "versionId": 0}, "active": dt[22],
            #            "gender": dt[23], "birthDate": dt[24], "deceasedBoolean": dt[25], "deceasedDateTime": dt[26],
            #            "maritalStatus": {"text": dt[27], "coding": []}, "multipleBirthBoolean": dt[28],
            #            "multipleBirthInteger": dt[29], "managingOrganization" : {"reference": dt[30]}}
            # Patient.append(patient)
            # Patient[index - 1] = RemoveDuplicateArray(Patient[index - 1])
        #
        else:

            jsonPatient = {
                "resourceType": dt[20],
                "id": dt[19],
                "meta": {"lastUpdated": dt[21], "versionId": ""},
                "text": {"status": "", "div": ""},
                "identifier": [],
                "active": dt[22],
                "name": [],
                "telecom": [],
                "gender": dt[23],
                "birthDate": dt[24],
                "deceasedBoolean": dt[25],
                "deceasedDateTime": dt[26],
                "address": [],
                "maritalStatus": {"text": dt[27], "coding": []},
                "multipleBirthBoolean": dt[28],
                "multipleBirthInteger": dt[29],
                "photo": [],
                "contact": [],
                "communication": [],
                "generalPractitioner": [],
                "managingOrganization": {"reference": dt[30]},
                "link": []
            }

            # parsing identifier
            # identifier = {"id": dt[0], "use": dt[1], "type": {"text": dt[2], "coding": []}, "system": dt[3],
            #               "value": dt[4]}
            # jsonPatient["identifier"].append(identifier)

            # human_name 0-7, contact_point 8 - 13, contact 14-18, patient 19-30

            # parsing human_name         for hum in dataPatient['name']:
            #for hum in data:
            # humanName = {"id": dt[0], "use": dt[1], "text": dt[2], "family": dt[3], "given": dt[4].split('|'),
            #              "prefix": dt[5].split('|'), "suffix": dt[6].split('|')}
            # jsonPatient["name"].append(humanName)

            if dt[7] == dt[19]:
                humanName = {"id": dt[0], "use": dt[1], "text": dt[2], "family": dt[3],"given": dt[4].split('|'),
                                 "prefix": dt[5].split('|'), "suffix": dt[6].split('|')}
                jsonPatient["name"].append(humanName)
            #elif dt[7] == dt[14]:
            else:
                humanNameContact = {"name":{"id": dt[0], "use": dt[1], "text": dt[2], "family": dt[3],
                                        "given": dt[4].split('|'),
                                        "prefix": dt[5].split('|'), "suffix": dt[6].split('|')}}
                jsonPatient["contact"].append(humanNameContact)

            # parsing contact_point
            # telecom = {"id": dt[8], "system": dt[9], "value": dt[10], "use": dt[11], "rank": dt[12]}
            # jsonPatient["telecom"].append(telecom)
            #for tel in data:
            if dt[13] == dt[19]:
                    telecom = {"id": dt[8], "system": dt[9], "value": dt[10], "use": dt[11], "rank": dt[12]}
                    jsonPatient["telecom"].append(telecom)
            #elif dt[7] == dt[14]:
            else:
                telecomContact = {"telecom":{"id": dt[8], "system": dt[9], "value": dt[10], "use": dt[11], "rank": dt[12]}}
                jsonPatient["contact"].append(telecomContact)

        # # parsing address
            # cmd = "select ADDRESS_ID, \"USE\", \"TYPE\", TEXT, LINE, CITY, DISTRICT, STATE, COUNTRY, POSTAL_CODE " \
            #       "FROM fhir247.address where resource_id = '" + PatientID + "' order by RESOURCE_ID ASC LIMIT 1"
            # cursor.execute(cmd, (PatientID,))
            # dataAddress = cursor.fetchall()
            #
            # for add in dataAddress:
            #     address = {"id": add[0], "use": add[1], "type": add[2], "text": add[3], "line": add[4].split('|'),
            #                "city": add[5], "district": add[6], "state": add[7], "postalCode": add[8], "country": add[9]}
            #     jsonPatient["address"].append(address)
            #
            # # parsing photo/attachment
            # photo = {"id": dt[5], "contentType": dt[6], "language": dt[7], "data": dt[8], "url": dt[9],
            #          "size": dt[10], "hash": dt[11], "title": dt[12]}
            # jsonPatient["photo"].append(photo)

            #parsing contact
            contact = {"id": dt[14], "relationship": {"text": dt[15], "coding": []}, "gender": dt[16],
                       "organization": dt[17]}
            jsonPatient["contact"].append(contact)

            # # parsing communication
            # communication = {"id": dt[17], "language": {"text": dt[18], "coding": []}, "preferred": dt[19]}
            # jsonPatient["communication"].append(communication)
            #
            # # parsing link
            # link = {"id": dt[20], "other": {"reference": dt[21]}, "type": dt[22]} #warn
            # jsonPatient["link"].append(link)
            #
            # # parsing general practitoner
            # generalPractitioner = {"id": dt[35], "reference": dt[36]}  # warn
            # jsonPatient["generalPractitioner"].append(generalPractitioner)


            Patient.append(jsonPatient)
            index += 1

    conn.close()
    return Patient

def getPatient(id):
    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    errCode = 0
    resourceID = id


    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    if errCode == 0:
        cmd = "SELECT a.patient_id, a.resource_type, TO_CHAR(a.last_updated, \'yyyy-MM-dd HH:mm:ss\'), a.\"ACTIVE\", a.gender," \
              "TO_CHAR(a.birthdate, \'yyyy-MM-dd\'), a.deceased_boolean, TO_CHAR(a.deceased_datetime, \'yyyy-MM-dd HH:mm:ss\'), " \
              "a.marital_status, a.multiple_birth_boolean, a.multiple_birth_integer, a.managing_organization, " \
              "b.human_name_id, b.\"USE\", b.text, b.family, b.given, b.prefix, b.suffix, b.resource_id, " \
              "c.identifier_id, c.\"USE\", c.type, c.system, c.\"VALUE\", c.resource_id, " \
              "d.address_id, d.\"USE\", d.\"TYPE\", d.text, d.line, d.city, d.district, d.state, d.country, d.postal_code, d.resource_id, " \
              "e.contact_point_id, e.system, e.\"VALUE\", e.\"USE\", e.rank, e.resource_id, " \
              "f.attachment_id, f.content_type, f.language, f.data, f.url, f.size, f.hash, f.title, f.resource_id, " \
              "g.communication_id, g.language, g.preferred, g.resource_id, " \
              "h.general_practitioner_id, h.reference, h.resource_id, " \
              "i.link_id, i.other, i.type, i.resource_id, " \
              "j.contact_id, j.relationship, j.gender, j.organization, j.resource_id, " \
              "k.address_id, k.\"USE\", k.\"TYPE\", k.text, k.line, k.city, k.district, k.state, k.country, k.postal_code, k.resource_id, " \
              "l.contact_point_id, l.system, l.\"VALUE\", l.\"USE\", l.rank, l.resource_id, " \
              "m.human_name_id, m.\"USE\", m.text, m.family, m.given, m.prefix, m.suffix, m.resource_id " \
              "FROM FHIR247.PATIENT a " \
              "LEFT JOIN FHIR247.HUMAN_NAME b ON a.patient_id = b.resource_id " \
              "LEFT JOIN FHIR247.IDENTIFIER c ON a.patient_id = c.resource_id " \
              "LEFT JOIN FHIR247.ADDRESS d ON a.patient_id = d.resource_id " \
              "LEFT JOIN FHIR247.CONTACT_POINT e ON a.patient_id = e.resource_id " \
              "LEFT JOIN FHIR247.ATTACHMENT f ON a.patient_id = f.resource_id " \
              "LEFT JOIN FHIR247.COMMUNICATION g ON a.patient_id = g.resource_id " \
              "LEFT JOIN FHIR247.GENERAL_PRACTITIONER h ON a.patient_id = h.resource_id " \
              "LEFT JOIN FHIR247.LINK i ON a.patient_id = i.resource_id " \
              "LEFT JOIN FHIR247.CONTACT j ON a.patient_id = j.resource_id " \
              "LEFT JOIN FHIR247.ADDRESS k ON j.contact_id = k.resource_id " \
              "LEFT JOIN FHIR247.CONTACT_POINT l ON j.contact_id = l.resource_id " \
              "LEFT JOIN FHIR247.HUMAN_NAME m ON j.contact_id = m.resource_id " \
              "WHERE a.patient_id = '"+ resourceID +"' " \
              "ORDER BY a.patient_id"

        # patient 0-11, human_name 12-19, identifier 20-25, address 26-36, contact_point 37-42, attachment 43-51,
        # communication 52-55, general_practitioner 56-58, link 59-62, contact 63-67,
        # address_contact 68-78, contact_point_contact 79-84, human_name_contact 85-92

        conn = phoenixConn()
        cursor = conn.cursor()

        Patient = []

        cursor.execute(cmd)
        data = result = cursor.fetchall()

        # set default value of resources
        PatientID = ""
        index = 0
        conn.close()

        for dt in data:
            # patient_id 0
            if PatientID == dt[0]:
                exist = True
            else:
                PatientID = dt[0]
                exist = False
            if exist:
                # parsing human_name 12-19
                humanName = {"id": dt[12], "use": dt[13], "text": dt[14], "family": dt[15], "given": dt[16].split('|'),
                             "prefix": dt[17].split('|'), "suffix": dt[18].split('|')}
                Patient[index - 1]["name"].append(humanName)
                Patient[index - 1]["name"] = RemoveDuplicateArray(Patient[index - 1]["name"])

                # parsing human_name_contact 85-92
                humanNameContact = {
                    "name": {"id": dt[85], "use": dt[86], "text": dt[87], "family": dt[88], "given": dt[89].split('|'),
                             "prefix": dt[90].split('|'), "suffix": dt[91].split('|')}}
                Patient[index - 1]["contact"].append(humanNameContact)
                # Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["name"])

                # parsing identifier 20-25
                identifier = {"id": dt[20], "use": dt[21], "type": {"text": dt[22], "coding": []}, "system": dt[23],
                              "value": dt[24]}
                Patient[index - 1]["identifier"].append(identifier)
                Patient[index - 1]["identifier"] = RemoveDuplicateArray(Patient[index - 1]["identifier"])

                # parsing address 26-36
                address = {"id": dt[26], "use": dt[27], "type": dt[28], "text": dt[29], "line": dt[30].split('|'),
                           "city": dt[31], "district": dt[32], "state": dt[33], "postalCode": dt[34], "country": dt[35]}
                Patient[index - 1]["address"].append(address)
                Patient[index - 1]["address"] = RemoveDuplicateArray(Patient[index - 1]["address"])

                # parsing address_contact 68-78
                addressContact = {
                    "address": {"id": dt[68], "use": dt[69], "type": dt[70], "text": dt[71], "line": dt[72].split('|'),
                                "city": dt[73], "district": dt[74], "state": dt[75], "postalCode": dt[76],
                                "country": dt[77]}}
                Patient[index - 1]["contact"].append(addressContact)
                # Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

                # parsing contact_point 37-42
                telecom = {"id": dt[37], "system": dt[38], "value": dt[39], "use": dt[40], "rank": dt[41]}
                Patient[index - 1]["telecom"].append(telecom)
                Patient[index - 1]["telecom"] = RemoveDuplicateArray(Patient[index - 1]["telecom"])

                # parsing contact_point_contact 79-84
                telecomContact = {
                    "telecom": {"id": dt[79], "system": dt[80], "value": dt[81], "use": dt[82], "rank": dt[83]}}
                Patient[index - 1]["contact"].append(telecomContact)
                # Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

                # parsing photo/attachment 43-51
                photo = {"id": dt[43], "contentType": dt[44], "language": dt[45], "data": dt[46], "url": dt[47],
                         "size": dt[48], "hash": dt[49], "title": dt[50]}
                Patient[index - 1]["photo"].append(photo)
                Patient[index - 1]["photo"] = RemoveDuplicateArray(Patient[index - 1]["photo"])

                # parsing communication 52-55
                communication = {"id": dt[52], "language": {"text": dt[53], "coding": []}, "preferred": dt[54]}
                Patient[index - 1]["communication"].append(communication)
                Patient[index - 1]["communication"] = RemoveDuplicateArray(Patient[index - 1]["communication"])

                # parsing general_practitioner 56-58
                generalPractitioner = {"id": dt[56], "reference": dt[57]}
                Patient[index - 1]["generalPractitioner"].append(generalPractitioner)
                Patient[index - 1]["generalPractitioner"] = RemoveDuplicateArray(Patient[index - 1]["generalPractitioner"])

                # parsing link 59-62
                link = {"id": dt[59], "other": {"reference": dt[60]}, "type": dt[61]}
                Patient[index - 1]["link"].append(link)
                Patient[index - 1]["link"] = RemoveDuplicateArray(Patient[index - 1]["link"])

                # parsing contact 63-67
                contact = {"id": dt[63], "relationship": {"text": dt[64], "coding": []}, "gender": dt[65],
                           "organization": dt[66]}
                Patient[index - 1]["contact"].append(contact)
                Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

                # insert patient
                # patient = {"resourceType": dt[20], "meta": {"lastUpdate": dt[21], "versionId": 0}, "active": dt[22],
                #            "gender": dt[23], "birthDate": dt[24], "deceasedBoolean": dt[25], "deceasedDateTime": dt[26],
                #            "maritalStatus": {"text": dt[27], "coding": []}, "multipleBirthBoolean": dt[28],
                #            "multipleBirthInteger": dt[29], "managingOrganization" : {"reference": dt[30]}}
                # Patient.append(patient)
                # Patient[index - 1] = RemoveDuplicateArray(Patient[index - 1])

            else:
                # patient 0-11
                jsonPatient = {
                    "resourceType": dt[1],
                    "id": dt[0],
                    "meta": {"lastUpdated": dt[2], "versionId": ""},
                    "text": {"status": "", "div": ""},
                    "identifier": [],
                    "active": dt[3],
                    "name": [],
                    "telecom": [],
                    "gender": dt[4],
                    "birthDate": dt[5],
                    "deceasedBoolean": dt[6],
                    "deceasedDateTime": dt[7],
                    "address": [],
                    "maritalStatus": {"text": dt[8], "coding": []},
                    "multipleBirthBoolean": dt[9],
                    "multipleBirthInteger": dt[10],
                    "photo": [],
                    "contact": [],
                    "communication": [],
                    "generalPractitioner": [],
                    "managingOrganization": {"reference": dt[11]},
                    "link": []
                }

                # parsing human_name 12-19
                humanName = {"id": dt[12], "use": dt[13], "text": dt[14], "family": dt[15], "given": dt[16].split('|'),
                             "prefix": dt[17].split('|'), "suffix": dt[18].split('|')}
                jsonPatient["name"].append(humanName)

                # parsing human_name_contact 85-92
                humanNameContact = {
                    "name": {"id": dt[85], "use": dt[86], "text": dt[87], "family": dt[88], "given": dt[89].split('|'),
                             "prefix": dt[90].split('|'), "suffix": dt[91].split('|')}}
                jsonPatient["contact"].append(humanNameContact)

                # parsing identifier 20-25
                identifier = {"id": dt[20], "use": dt[21], "type": {"text": dt[22], "coding": []}, "system": dt[23],
                              "value": dt[24]}
                jsonPatient["identifier"].append(identifier)

                # parsing address 26-36
                address = {"id": dt[26], "use": dt[27], "type": dt[28], "text": dt[29], "line": dt[30].split('|'),
                           "city": dt[31], "district": dt[32], "state": dt[33], "postalCode": dt[34], "country": dt[35]}
                jsonPatient["address"].append(address)

                # parsing address_contact 68-78
                addressContact = {"address": {"id": dt[68], "use": dt[69], "type": dt[70], "text": dt[71], "line": dt[72].split('|'),
                                "city": dt[73], "district": dt[74], "state": dt[75], "postalCode": dt[76],
                                "country": dt[77]}}
                jsonPatient["contact"].append(addressContact)

                # parsing contact_point 37-42
                telecom = {"id": dt[37], "system": dt[38], "value": dt[39], "use": dt[40], "rank": dt[41]}
                jsonPatient["telecom"].append(telecom)

                # parsing contact_point_contact 79-84
                telecomContact = {"telecom": {"id": dt[79], "system": dt[80], "value": dt[81], "use": dt[82], "rank": dt[83]}}
                jsonPatient["contact"].append(telecomContact)

                # parsing photo/attachment 43-51
                photo = {"id": dt[43], "contentType": dt[44], "language": dt[45], "data": dt[46], "url": dt[47],
                         "size": dt[48], "hash": dt[49], "title": dt[50]}
                jsonPatient["photo"].append(photo)

                # parsing communication 52-55
                communication = {"id": dt[52], "language": {"text": dt[53], "coding": []}, "preferred": dt[54]}
                jsonPatient["communication"].append(communication)

                # parsing general_practitioner 56-58
                generalPractitioner = {"id": dt[56], "reference": dt[57]}
                jsonPatient["generalPractitioner"].append(generalPractitioner)

                # parsing link 59-62
                link = {"id": dt[59], "other": {"reference": dt[60]}, "type": dt[61]}
                jsonPatient["link"].append(link)

                # parsing contact 63-67
                contact = {"id": dt[63], "relationship": {"text": dt[64], "coding": []}, "gender": dt[65],
                           "organization": dt[66]}
                jsonPatient["contact"].append(contact)

                Patient.append(jsonPatient)
                index += 1

        return Patient

    else:
        result = {"status": errCode, "message": message}

    return result





