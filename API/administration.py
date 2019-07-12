from flask import request, jsonify

import requests, json, calendar, time, urllib, base64
from datetime import datetime
import threading

from Secret247 import phoenixConn, phoenixClose, generateUniqeID, RemoveDuplicateArray, tokenValidate, getPersonbyID, getPatientbyID


def getPatients():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    active = request.args.get('active')
    address = request.args.get('address')
    addressCity = request.args.get('address-city')
    addressCountry = request.args.get('address-country')
    addressPostalcode = request.args.get('address-postalcode')
    addressState = request.args.get('address-state')
    addressUse = request.args.get('address-use')
    birthDate = request.args.get('birthdate')
    deathDate = request.args.get('death-date')
    deceased = request.args.get('deceased')
    email = request.args.get('email')
    family = request.args.get('family')
    gender = request.args.get('gender')
    generalPractitioner = request.args.get('general-practitioner')
    given = request.args.get('given')
    identifier = request.args.get('identifier')
    language = request.args.get('language')
    link = request.args.get('link')
    name = request.args.get('name')
    organization = request.args.get('organization')
    phone = request.args.get('phone')
    telecom = request.args.get('telecom')

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    if errCode == 0:
        condition = ""
        offset_limit = ""

        if active:
           condition += " a.\"ACTIVE\" = " + active + " AND "
        if address:
            condition += " d.line LIKE '%" + address + "%' OR d.city LIKE UPPER('%" + address + "%') OR " \
                         "d.city LIKE UPPER('%" + address + "%') OR d.district LIKE UPPER('%" + address + "%') OR " \
                         "d.state LIKE UPPER('%" + address + "%') OR d.country LIKE UPPER('%" + address + "%') OR " \
                         "d.postal_code LIKE UPPER('%" + address + "%') OR d.text LIKE '%" + address + "%'" + " AND "
        if addressCity:
            condition += " d.city LIKE UPPER('%" + addressCity + "%')" + " AND "
        if addressCountry:
            condition += " d.country LIKE UPPER('%" + addressCountry + "%')" + " AND "
        if addressPostalcode:
            condition += " d.postal_code LIKE UPPER('%" + addressPostalcode + "%')" + " AND "
        if addressState:
            condition += " d.state LIKE UPPER('%" + addressState + "%')" + " AND "
        if addressUse:
            condition += " d.\"USE\" LIKE '%" + addressUse + "%'" + " AND "
        if birthDate:
            condition += " a.birthdate = TO_DATE('" + birthDate + "', 'yyyy-MM-dd')" + " AND "
        if deathDate:
            condition += " a.\"deceased_datetime\" = '" + deathDate + "', 'yyyy-" + " AND "
        if deceased:
            condition += " a.deceased_boolean = " + deceased + " AND "
        if email:
            condition += " e.system='email' AND e.\"VALUE\" LIKE '%" + email + "%'" + " AND "
        if family:
            condition += " b.family LIKE '%" + family + "%'" + " AND "
        if gender:
            condition += " a.gender LIKE '%" + gender + "%'" + " AND "
        if generalPractitioner:
            condition += " h.reference LIKE '%" + generalPractitioner + "%'" + " AND "
        if given:
            condition += " b.given LIKE '%" + given + "%'" + " AND "
        if identifier:
            condition += " c.\"VALUE\" LIKE '%" + identifier + "%'" + " AND "
        if language:
            condition += " g.language LIKE '%" + language + "%'" + " AND "
        if link:
            condition += " i.other LIKE '%" + link + "%'" + " AND "
        if name:
            condition += " b.text LIKE '%" + name + "%' OR b.family LIKE '%" + name + "%' OR " \
                         "b.given LIKE '%" + name + "%' OR b.prefix LIKE '%" + name + "%' OR " \
                         "b.suffix LIKE '%" + name + "%'" + " AND "
        if organization:
            condition += " a.managing_organization LIKE '%" + organization + "%'" + " AND "
        if phone:
            condition += " e.system='phone' AND e.\"VALUE\" LIKE '%" + phone + "%'" + " AND "
        if telecom:
            condition += " e.\"VALUE\" LIKE '%" + telecom + "%'" + " AND "

        if offset and limit:
            offset_limit = " LIMIT "+ limit +" OFFSET "+ offset
        else:
            offset = 0
            limit = 0

        if condition != '':
            condition = " WHERE " + condition[:-5]

        ##metode2 (JOIN di Phoenix)

        cmd = "SELECT a.patient_id, a.resource_type, TO_CHAR(a.last_updated, \'yyyy-MM-dd HH:mm:ss\'), a.\"ACTIVE\", a.gender," \
              "TO_CHAR(a.birthdate, \'yyyy-MM-dd\'), a.deceased_boolean, TO_CHAR(a.deceased_datetime, \'yyyy-MM-dd HH:mm:ss\'), " \
              "a.marital_status, a.multiple_birth_boolean, a.multiple_birth_integer, a.managing_organization, " \
              "b.human_name_id, b.\"USE\", b.text, b.family, b.given, b.prefix, b.suffix, b.resource_id, " \
              "c.identifier_id, c.\"USE\", c.type, c.system, c.\"VALUE\", c.resource_id, " \
              "d.address_id, d.\"USE\", d.\"TYPE\", d.text, d.line, d.city, d.district, d.state, d.postal_code, d.country, d.resource_id, " \
              "e.contact_point_id, e.system, e.\"VALUE\", e.\"USE\", e.rank, e.resource_id, " \
              "f.attachment_id, f.content_type, f.language, f.data, f.url, f.size, f.hash, f.title, f.resource_id, " \
              "g.communication_id, g.language, g.preferred, g.resource_id, " \
              "h.general_practitioner_id, h.reference, h.resource_id, " \
              "i.link_id, i.other, i.type, i.resource_id, " \
              "j.contact_id, j.relationship, j.gender, j.organization, j.resource_id, " \
              "k.address_id, k.\"USE\", k.\"TYPE\", k.text, k.line, k.city, k.district, k.state, k.postal_code, k.country, k.resource_id, " \
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
              "LEFT JOIN FHIR247.HUMAN_NAME m ON j.contact_id = m.resource_id " + condition + " ORDER BY a.patient_id " + offset_limit

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

                # parsing contact_point 37-42
                telecom = {"id": dt[37], "system": dt[38], "value": dt[39], "use": dt[40], "rank": dt[41]}
                Patient[index - 1]["telecom"].append(telecom)
                Patient[index - 1]["telecom"] = RemoveDuplicateArray(Patient[index - 1]["telecom"])

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
                           "organization": dt[66], "name":{"id": dt[85], "use": dt[86], "text": dt[87], "family": dt[88],
                           "given": dt[89].split('|'), "prefix": dt[90].split('|'), "suffix": dt[91].split('|')},
                           "address": {"address":{"id": dt[68], "use": dt[69], "type": dt[70], "text": dt[71],
                           "line": dt[72].split('|'), "city": dt[73], "district": dt[74], "state": dt[75], "postalCode": dt[76],
                           "country": dt[77]}}, "telecom":[{"id": dt[79], "system": dt[80], "value": dt[81],
                           "use": dt[82], "rank": dt[83]}]}
                Patient[index - 1]["contact"].append(contact)
                Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

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

                # parsing identifier 20-25
                identifier = {"id": dt[20], "use": dt[21], "type": {"text": dt[22], "coding": []}, "system": dt[23],
                              "value": dt[24]}
                jsonPatient["identifier"].append(identifier)

                # parsing address 26-36
                address = {"id": dt[26], "use": dt[27], "type": dt[28], "text": dt[29], "line": dt[30].split('|'),
                           "city": dt[31], "district": dt[32], "state": dt[33], "postalCode": dt[34], "country": dt[35]}
                jsonPatient["address"].append(address)

                # parsing contact_point 37-42
                telecom = {"id": dt[37], "system": dt[38], "value": dt[39], "use": dt[40], "rank": dt[41]}
                jsonPatient["telecom"].append(telecom)

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
                           "organization": dt[66], "name":{"id": dt[85], "use": dt[86], "text": dt[87], "family": dt[88],
                           "given": dt[89].split('|'), "prefix": dt[90].split('|'), "suffix": dt[91].split('|')},
                           "address": {"address":{"id": dt[68], "use": dt[69], "type": dt[70], "text": dt[71],
                           "line": dt[72].split('|'), "city": dt[73], "district": dt[74], "state": dt[75], "postalCode": dt[76],
                           "country": dt[77]}}, "telecom": [{"id": dt[79], "system": dt[80], "value": dt[81],
                           "use": dt[82], "rank": dt[83]}]}
                jsonPatient["contact"].append(contact)

                Patient.append(jsonPatient)
                index += 1

            result ={"status": 200, "offset": offset, "limit": limit, "data": Patient, "total": len(Patient)}
    else:
        result = {"status": errCode, "message": message}

    return result

def getPatient(id):
    resourceID = id
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check patient
    checkPatientID = getPatientbyID(resourceID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    if checkPatientID['status'] > 200:
        errCode = 14002
        message = checkPatientID['message']

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

                # parsing contact_point 37-42
                telecom = {"id": dt[37], "system": dt[38], "value": dt[39], "use": dt[40], "rank": dt[41]}
                Patient[index - 1]["telecom"].append(telecom)
                Patient[index - 1]["telecom"] = RemoveDuplicateArray(Patient[index - 1]["telecom"])

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
                contact = {"id": dt[63], "relationship": {"text": dt[64], "coding": []}, "gender": dt[65], "organization": dt[66],
                           "name": {"id": dt[85], "use": dt[86], "text": dt[87], "family": dt[88], "given": dt[89].split('|'),
                           "prefix": dt[90].split('|'), "suffix": dt[91].split('|')}, "address": {"id": dt[68], "use": dt[69],
                           "type": dt[70], "text": dt[71], "line": dt[72].split('|'), "city": dt[73], "district": dt[74],
                           "state": dt[75], "postalCode": dt[76], "country": dt[77]}, "telecom": [{"id": dt[79], "system": dt[80],
                           "value": dt[81], "use": dt[82], "rank": dt[83]}]}
                Patient[index - 1]["contact"].append(contact)
                Patient[index - 1]["contact"] = RemoveDuplicateArray(Patient[index - 1]["contact"])

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

                # parsing identifier 20-25
                identifier = {"id": dt[20], "use": dt[21], "type": {"text": dt[22], "coding": []}, "system": dt[23],
                              "value": dt[24]}
                jsonPatient["identifier"].append(identifier)

                # parsing address 26-36
                address = {"id": dt[26], "use": dt[27], "type": dt[28], "text": dt[29], "line": dt[30].split('|'),
                           "city": dt[31], "district": dt[32], "state": dt[33], "postalCode": dt[34], "country": dt[35]}
                jsonPatient["address"].append(address)

                # parsing contact_point 37-42
                telecom = {"id": dt[37], "system": dt[38], "value": dt[39], "use": dt[40], "rank": dt[41]}
                jsonPatient["telecom"].append(telecom)

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
                contact = {"id": dt[63], "relationship": {"text": dt[64], "coding": []}, "gender": dt[65], "organization": dt[66],
                           "name": {"id": dt[85], "use": dt[86], "text": dt[87], "family": dt[88], "given": dt[89].split('|'),
                           "prefix": dt[90].split('|'), "suffix": dt[91].split('|')}, "address": {"id": dt[68], "use": dt[69],
                           "type": dt[70], "text": dt[71], "line": dt[72].split('|'), "city": dt[73], "district": dt[74],
                           "state": dt[75], "postalCode": dt[76], "country": dt[77]}, "telecom": [{"id": dt[79], "system": dt[80],
                           "value": dt[81], "use": dt[82], "rank": dt[83]}]}
                jsonPatient["contact"].append(contact)

                Patient.append(jsonPatient)
                index += 1

        return Patient

    else:
        result = {"status": errCode, "message": message}

    return result

def addPatient():
    errCode = 0
    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    if errCode == 0:
        # parsing request
        data = request.data
        dataPatient = json.loads(data)

        patientID = generateUniqeID('P4T247')

        #identifier
        if 'identifier' in dataPatient and type(dataPatient['identifier']).__name__ == 'list' and len(dataPatient['identifier']) > 0:
            identifierValue = []
            for ide in dataPatient['identifier']:
                identifierID = generateUniqeID('1D3247')
                identifierValue.append('\'' + identifierID + '\',' + \
                                  '\'' + ide['use'] + '\',' + \
                                  '\'' + ide['type']['text'] + '\',' + \
                                  '\'' + ide['system'] + '\',' + \
                                  '\'' + ide['value'] + '\',' + \
                                  '\'' + patientID + '\'')
        else:
            errCode = 13001
            message = "Identifier request is required."

        #name
        if 'name' in dataPatient and type(dataPatient['name']).__name__ == 'list' and len(dataPatient['name']) > 0:
            humanNameValue = []
            for hum in dataPatient['name']:
                humanNameID = generateUniqeID('HU3247')
                humanNameValue.append('\'' + humanNameID + '\',' + \
                                  '\'' + hum['use'] + '\',' + \
                                  '\'' + ' '.join(hum['prefix']) + ' ' + hum['text'] + ', ' + ','.join(hum['suffix']) + '\',' + \
                                  '\'' + hum['family'] + '\',' + \
                                  '\'' + '|'.join(hum['given']) + '\',' + \
                                  '\'' + '|'.join(hum['prefix']) + '\',' + \
                                  '\'' + '|'.join(hum['suffix']) + '\',' + \
                                  '\'' + patientID + '\'')

        else:
            errCode = 13002
            message = "Name request is required."

        #telecom / contact point
        if 'telecom' in dataPatient and type(dataPatient['telecom']).__name__ == 'list' and len(dataPatient['telecom']) > 0:
            contactPointValue = []
            for tel in dataPatient['telecom']:
                telecomID = generateUniqeID('T3L247')
                contactPointValue.append('\'' + telecomID + '\',' + \
                                  '\'' + tel['system'] + '\',' + \
                                  '\'' + tel['value'] + '\',' + \
                                  '\'' + tel['use'] + '\',' + \
                                  '' + str(tel['rank']) + ',' + \
                                  '\'' + patientID + '\'')
        else:
            errCode = 13003
            message = "Telecom request is required."

        #address
        if 'address' in dataPatient and type(dataPatient['address']).__name__ == 'list' and len(dataPatient['address']) > 0:
            addressValue = []
            for addr in dataPatient['address']:
                addressID = generateUniqeID('4DD247')
                addressValue.append('\'' + addressID + '\',' + \
                                  '\'' + addr['use'] + '\',' + \
                                  '\'' + addr['type'] + '\',' + \
                                  '\'' + addr['text'] + '\',' + \
                                  '\'' + '|'.join(addr['line']) + '\',' + \
                                  '\'' + addr['city'].upper() + '\',' + \
                                  '\'' + addr['district'].upper() + '\',' + \
                                  '\'' + addr['state'].upper() + '\',' + \
                                  '\'' + addr['postalCode'] + '\',' + \
                                  '\'' + addr['country'].upper() + '\',' + \
                                  '\'' + patientID + '\'')
        else:
            errCode = 13004
            message = "Address request is required."

        #photo atau attachment
        if 'photo' in dataPatient and type(dataPatient['photo']).__name__ == 'list' and len(dataPatient['photo']) > 0:
            photoInsert = 1
            attachmentValue = []
            for att in dataPatient['photo']:
                attachmentID = generateUniqeID('4T7247')
                attachmentValue.append('\'' + attachmentID + '\',' + \
                                  '\'' + att['contentType'] + '\',' + \
                                  '\'' + att['language'] + '\',' + \
                                  '\'' + '' + '\',' + \
                                  '\'' + att['url'] + '\',' + \
                                  '\'' + att['size'] + '\',' + \
                                  '\'' + att['hash'] + '\',' + \
                                  '\'' + att['title'] + '\',' + \
                                  '\'' + patientID + '\'')
        else:
            photoInsert = 0

        # patient contact
        if 'contact' in dataPatient and type(dataPatient['contact']).__name__ == 'list' and len(dataPatient['contact']) > 0:
            contactValue = []
            humanNameContactValue = []
            contactPointContactValue = []
            addressContactValue = []

            for cont in dataPatient['contact']:
                contactID = generateUniqeID('C0N247')
                contactValue.append('\'' + contactID + '\',' + \
                                    '\'' + cont['relationship']['text'] + '\',' + \
                                    '\'' + cont['gender'] + '\',' + \
                                    '\'' + cont['organization'] + '\',' + \
                                    '\'' + patientID + '\'')

                #contact name
                humanNameID = generateUniqeID('HU3247')
                humanNameContactValue.append('\'' + humanNameID + '\',' + \
                                      '\'' + cont['name']['use'] + '\',' + \
                                      '\'' + ' '.join(cont['name']['prefix']) + ' ' + cont['name']['text'] + ', ' + ','.join(
                    cont['name']['suffix']) + '\',' + \
                                      '\'' + cont['name']['family'] + '\',' + \
                                      '\'' + '|'.join(cont['name']['given']) + '\',' + \
                                      '\'' + '|'.join(cont['name']['prefix']) + '\',' + \
                                      '\'' + '|'.join(cont['name']['suffix']) + '\',' + \
                                      '\'' + contactID + '\'')

                #contact telecom
                telecomID = generateUniqeID('T3L247')
                for tel in cont['telecom']:
                    contactPointContactValue.append('\'' + telecomID + '\',' + \
                                         '\'' + tel['system'] + '\',' + \
                                         '\'' + tel['value'] + '\',' + \
                                         '\'' + tel['use'] + '\',' + \
                                         '' + str(tel['rank']) + ',' + \
                                         '\'' + contactID + '\'')

                #contact address
                addressID = generateUniqeID('4DD247')
                addressContactValue.append('\'' + addressID + '\',' + \
                                    '\'' + cont['address']['use'] + '\',' + \
                                    '\'' + cont['address']['type'] + '\',' + \
                                    '\'' + cont['address']['text'] + '\',' + \
                                    '\'' + '|'.join(cont['address']['line']) + '\',' + \
                                    '\'' + cont['address']['city'].upper() + '\',' + \
                                    '\'' + cont['address']['district'].upper() + '\',' + \
                                    '\'' + cont['address']['state'].upper() + '\',' + \
                                    '\'' + cont['address']['postalCode'] + '\',' + \
                                    '\'' + cont['address']['country'].upper() + '\',' + \
                                    '\'' + contactID + '\'')
        else:
            errCode = 13005
            message = "Contact request is required."

        # patient communication
        if 'communication' in dataPatient and type(dataPatient['communication']).__name__ == 'list' and len(dataPatient['communication']) > 0:
            communicationValue = []

            for comm in dataPatient['communication']:
                communicationID = generateUniqeID('C0M247')
                communicationValue.append('\'' + communicationID + '\',' + \
                                    '\'' + comm['language']['text'] + '\',' + \
                                    '' +  str(comm['preferred'])  + ',' + \
                                    '\'' + patientID + '\'')
        else:
            errCode = 13006
            message = "Communication request is required."

        # patient link
        if 'link' in dataPatient and type(dataPatient['link']).__name__ == 'list' and len(dataPatient['link']) > 0:
            linkInsert = 1
            linkValue = []

            for lk in dataPatient['link']:
                linkID = generateUniqeID('l1nk247')
                linkValue.append('\'' + linkID + '\',' + \
                                 '\'' + lk['other']['reference'] + '\',' + \
                                 '\'' + lk['type'] + '\',' + \
                                 '\'' + patientID + '\'')
        else:
            linkInsert = 0

        # patient general_practitioner
        if 'generalPractitioner' in dataPatient and type(dataPatient['generalPractitioner']).__name__ == 'list' and len(dataPatient['generalPractitioner']) > 0:
            generalPractitionerInsert = 1
            generalPractitionerValue = []

            for genprac in dataPatient['generalPractitioner']:
                generalPractitionerID = generateUniqeID('gpr4247')
                generalPractitionerValue.append('\'' + generalPractitionerID + '\',' + \
                                                '\'' + genprac['reference'] + '\',' + \
                                                '\'' + patientID + '\'')
        else:
            generalPractitionerInsert = 0

        # patient patient
        if len(dataPatient) > 0:
            currentTime = datetime.now()
            resourceType = "Patient"
            patientValue = []
            patientValue.append('\'' + patientID + '\',' + \
                                '\'' + resourceType + '\',' + \
                                '\'' + str(currentTime) + '\',' + \
                                '' + str(dataPatient['active']) + ',' + \
                                '\'' + dataPatient['gender'] + '\',' + \
                                '\'' + dataPatient['birthDate'] + '\',' + \
                                '' + str(dataPatient['deceasedBoolean']) + ',' + \
                                '\'' + dataPatient['deceasedDateTime'] + '\',' + \
                                '\'' + dataPatient['maritalStatus']['text'] + '\',' + \
                                '' + str(dataPatient['multipleBirthBoolean']) + ',' + \
                                '' + str(dataPatient['multipleBirthInteger']) + ',' + \
                                '\'' + dataPatient['managingOrganization']['reference'] + '\'')

        else:
            errCode = 13009
            message = "Patient request is required."

        if errCode == 0:
            connDB = phoenixConn()
            cursor = connDB.cursor()

            threads = []

            #insert processing
            try:
                # Set thread
                # insert patient identifier
                def insertDataIdentifier(data):
                    for insertValue in data:
                        identifierField = 'IDENTIFIER_ID, "USE", "TYPE", "SYSTEM", "VALUE", RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.IDENTIFIER (" + identifierField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient name
                def insertDataHumanName(data):
                    for insertValue in data:
                        humanNameField = 'HUMAN_NAME_ID, "USE", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.HUMAN_NAME (" + humanNameField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient telecom
                def insertDataContactPoint(data):
                    for insertValue in data:
                        contactPointField = 'CONTACT_POINT_ID, "SYSTEM", "VALUE", "USE", RANK, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.CONTACT_POINT (" + contactPointField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient address
                def insertDataAddress(data):
                    for insertValue in data:
                        addressField = 'ADDRESS_ID, "USE", "TYPE", TEXT, LINE, CITY, DISTRICT, STATE, POSTAL_CODE, COUNTRY, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.ADDRESS (" + addressField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient photo
                def insertDataAttachment(data):
                    for insertValue in data:
                        attachmentField = 'ATTACHMENT_ID, CONTENT_TYPE, LANGUAGE, DATA, URL, SIZE, HASH, TITLE, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.ATTACHMENT (" + attachmentField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient contact
                def insertDataContact(data):
                    for insertValue in data:
                        contactField = 'CONTACT_ID, RELATIONSHIP, GENDER, ORGANIZATION, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.CONTACT (" + contactField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient communication
                def insertDataCommunication(data):
                    for insertValue in data:
                        communicationField = 'COMMUNICATION_ID, LANGUAGE, PREFERRED, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.COMMUNICATION (" + communicationField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient link
                def insertDataLink(data):
                    for insertValue in data:
                        linkField = 'LINK_ID, OTHER, TYPE, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.LINK (" + linkField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient general practitioner
                def insertDataGeneralPractitioner(data):
                    for insertValue in data:
                        generalPractitionerField = 'GENERAL_PRACTITIONER_ID, REFERENCE, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.GENERAL_PRACTITIONER (" + generalPractitionerField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert patient
                def insertDataPatient(data):
                    for insertValue in data:
                        patientField = 'PATIENT_ID, RESOURCE_TYPE, LAST_UPDATED, "ACTIVE", GENDER, BIRTHDATE, ' \
                                       'DECEASED_BOOLEAN, DECEASED_DATETIME, MARITAL_STATUS, MULTIPLE_BIRTH_BOOLEAN, ' \
                                       'MULTIPLE_BIRTH_INTEGER,MANAGING_ORGANIZATION'
                        cmd = "UPSERT INTO FHIR247.PATIENT (" + patientField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                ###Create thread1
                t = threading.Thread(target=insertDataIdentifier(identifierValue))
                threads.append(t)

                ###Create thread2
                t = threading.Thread(target=insertDataHumanName(humanNameValue))
                threads.append(t)

                # ###Create thread3
                t = threading.Thread(target=insertDataContactPoint(contactPointValue))
                threads.append(t)
                #
                # ###Create thread4
                t = threading.Thread(target=insertDataAddress(addressValue))
                threads.append(t)
                #
                # ###Create thread5
                if photoInsert:
                    t = threading.Thread(target=insertDataAttachment(attachmentValue))
                    threads.append(t)
                #
                # ###Create thread6
                t = threading.Thread(target=insertDataContact(contactValue))
                threads.append(t)
                #
                t = threading.Thread(target=insertDataHumanName(humanNameContactValue))
                threads.append(t)
                #
                t = threading.Thread(target=insertDataContactPoint(contactPointContactValue))
                threads.append(t)
                #
                t = threading.Thread(target=insertDataAddress(addressContactValue))
                threads.append(t)
                #
                # ###Create thread7
                t = threading.Thread(target=insertDataCommunication(communicationValue))
                threads.append(t)

                # ###Create thread8
                if linkInsert:
                    t = threading.Thread(target=insertDataLink(linkValue))
                    threads.append(t)

                # ###Create thread9
                if generalPractitionerInsert:
                    t = threading.Thread(target=insertDataGeneralPractitioner(generalPractitionerValue))
                    threads.append(t)

                # ###Create thread10
                t = threading.Thread(target=insertDataPatient(patientValue))
                threads.append(t)

                ###Starting thread
                for t in threads:
                    t.start()

                ###Waiting all threads is done
                for t in threads:
                    t.join()

                errCode = 200
                message = "Successful insert data."
            except OSError as err:
                errCode = 13002
                message = err

            result = {"status": errCode, "message": message}
        else:
            result = {"status": errCode, "message": message}

        return result

    else:
        result = {"status": errCode, "message": message}

    return result

def updatePatient(id):
    errCode = 0
    resourceID = id

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check patient
    checkPatientID = getPatientbyID(resourceID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    if checkPatientID['status'] > 200:
        errCode = 14002
        message = checkPatientID['message']

    # parsing request
    data = request.data
    dataPatient = json.loads(data)

    #identifier
    if 'identifier' in dataPatient and type(dataPatient['identifier']).__name__ == 'list' and len(dataPatient['identifier']) > 0:
        identifierValue = []
        for ide in dataPatient['identifier']:
            identifierValue.append('\'' + ide['use'] + '\',' + \
                              '\'' + ide['type']['text'] + '\',' + \
                              '\'' + ide['system'] + '\',' + \
                              '\'' + ide['value'] + '\'')
    else:
        errCode = 13001
        message = "Identifier request is required."

    #name
    if 'name' in dataPatient and type(dataPatient['name']).__name__ == 'list' and len(dataPatient['name']) > 0:
        humanNameValue = []
        for hum in dataPatient['name']:
            humanNameValue.append('\'' + hum['use'] + '\',' + \
                              '\'' + ' '.join(hum['prefix']) + ' ' + hum['text'] + ', ' + ','.join(hum['suffix']) + '\',' + \
                              '\'' + hum['family'] + '\',' + \
                              '\'' + '|'.join(hum['given']) + '\',' + \
                              '\'' + '|'.join(hum['prefix']) + '\',' + \
                              '\'' + '|'.join(hum['suffix']) + '\'')
    else:
        errCode = 13002
        message = "Name request is required."

    #telecom / contact point
    if 'telecom' in dataPatient and type(dataPatient['telecom']).__name__ == 'list' and len(dataPatient['telecom']) > 0:
        contactPointValue = []
        for tel in dataPatient['telecom']:
            contactPointValue.append('\'' + tel['system'] + '\',' + \
                              '\'' + tel['value'] + '\',' + \
                              '\'' + tel['use'] + '\',' + \
                              '' + str(tel['rank']) + '')
    else:
        errCode = 13003
        message = "Telecom request is required."

    #address
    if 'address' in dataPatient and type(dataPatient['address']).__name__ == 'list' and len(dataPatient['address']) > 0:
        addressValue = []
        for addr in dataPatient['address']:
            addressValue.append('\'' + addr['use'] + '\',' + \
                              '\'' + addr['type'] + '\',' + \
                              '\'' + addr['text'] + '\',' + \
                              '\'' + '|'.join(addr['line']) + '\',' + \
                              '\'' + addr['city'].upper() + '\',' + \
                              '\'' + addr['district'].upper() + '\',' + \
                              '\'' + addr['state'].upper() + '\',' + \
                              '\'' + addr['postalCode'] + '\',' + \
                              '\'' + addr['country'].upper() + '\'')
    else:
        errCode = 13004
        message = "Address request is required."

    #photo atau attachment
    if 'photo' in dataPatient and type(dataPatient['photo']).__name__ == 'list' and len(dataPatient['photo']) > 0:
        photoInsert = 1
        attachmentValue = []
        for att in dataPatient['photo']:
            attachmentValue.append('\'' + att['contentType'] + '\',' + \
                              '\'' + att['language'] + '\',' + \
                              '\'' + '' + '\',' + \
                              '\'' + att['url'] + '\',' + \
                              '\'' + att['size'] + '\',' + \
                              '\'' + att['hash'] + '\',' + \
                              '\'' + att['title'] + '\'')
    else:
        photoInsert = 0

    # patient contact
    if 'contact' in dataPatient and type(dataPatient['contact']).__name__ == 'list' and len(dataPatient['contact']) > 0:
        contactValue = []
        humanNameContactValue = []
        contactPointContactValue = []
        addressContactValue = []

        for cont in dataPatient['contact']:
            contactValue.append('\'' + cont['relationship']['text'] + '\',' + \
                                '\'' + cont['gender'] + '\',' + \
                                '\'' + cont['organization'] + '\'')

            #contact name
            humanNameContactValue.append('\'' + cont['name']['use'] + '\',' + \
                                  '\'' + ' '.join(cont['name']['prefix']) + ' ' + cont['name']['text'] + ', ' + ','.join(
                cont['name']['suffix']) + '\',' + \
                                  '\'' + cont['name']['family'] + '\',' + \
                                  '\'' + '|'.join(cont['name']['given']) + '\',' + \
                                  '\'' + '|'.join(cont['name']['prefix']) + '\',' + \
                                  '\'' + '|'.join(cont['name']['suffix']) + '\'')

            #contact telecom
            for tel in cont['telecom']:
                contactPointContactValue.append('\'' + tel['system'] + '\',' + \
                                     '\'' + tel['value'] + '\',' + \
                                     '\'' + tel['use'] + '\',' + \
                                     '' + str(tel['rank']) + '')

            #contact address
            addressContactValue.append('\'' + cont['address']['use'] + '\',' + \
                                '\'' + cont['address']['type'] + '\',' + \
                                '\'' + cont['address']['text'] + '\',' + \
                                '\'' + '|'.join(cont['address']['line']) + '\',' + \
                                '\'' + cont['address']['city'].upper() + '\',' + \
                                '\'' + cont['address']['district'].upper() + '\',' + \
                                '\'' + cont['address']['state'].upper() + '\',' + \
                                '\'' + cont['address']['postalCode'] + '\',' + \
                                '\'' + cont['address']['country'].upper() + '\'')
    else:
        errCode = 13005
        message = "Contact request is required."

    # patient communication
    if 'communication' in dataPatient and type(dataPatient['communication']).__name__ == 'list' and len(dataPatient['communication']) > 0:
        communicationValue = []

        for comm in dataPatient['communication']:
            communicationValue.append('\'' + comm['language']['text'] + '\',' + \
                                '' +  str(comm['preferred'])  + '')
    else:
        errCode = 13006
        message = "Communication request is required."

    # patient generalPractitioner
    if 'generalPractitioner' in dataPatient and type(dataPatient['generalPractitioner']).__name__ == 'list' and len(dataPatient['generalPractitioner']) > 0:
        generalPractitionerInsert = 1
        generalPractitionerValue = []

        for genprac in dataPatient['generalPractitioner']:
            generalPractitionerValue.append('\'' + genprac['reference'] + '\'')
    else:
        generalPractitionerInsert = 0

    #patient link
    if 'link' in dataPatient and type(dataPatient['link']).__name__ == 'list' and len(dataPatient['link']) > 0:
        linkInsert = 1
        linkValue = []

        for lk in dataPatient['link']:
            linkValue.append('\'' + lk['other']['reference'] + '\',' + \
                '\'' + lk['type'] + '\'')
    else:
        linkInsert = 0

    # patient patient
    if len(dataPatient) > 0:
        currentTime = datetime.now()
        lastUpdated = currentTime.strftime('%Y-%m-%d %H:%M:%S.%f')

        resourceType = "Patient"
        patientValue = []
        patientValue.append('\'' + resourceType + '\',' + \
                            '' + str(dataPatient['active']) + ',' + \
                            '\'' + dataPatient['gender'] + '\',' + \
                            '' + str(dataPatient['deceasedBoolean']) + ',' + \
                             '\'' + dataPatient['maritalStatus']['text'] + '\',' + \
                             '' + str(dataPatient['multipleBirthBoolean']) + ',' + \
                            '' + str(dataPatient['multipleBirthInteger']) + ','
                            '\'' + dataPatient['managingOrganization']['reference'] + '\'')
    else:
        errCode = 13009
        message = "Patient request is required."

    if errCode == 0:
        connDB = phoenixConn()
        cursor = connDB.cursor()

        cursor.execute("SELECT CONTACT_ID FROM FHIR247.CONTACT WHERE RESOURCE_ID = '" + resourceID + "' ")
        result = cursor.fetchone()
        contactID = result[0]

        threads = []

        #update processing
        try:
            # Set thread
            # update patient identifier
            def updateDataIdentifier(data):
                for insertValue in data:
                    identifierField = 'IDENTIFIER_ID, "USE", "TYPE", "SYSTEM", "VALUE"'
                    cmd = "UPSERT INTO FHIR247.IDENTIFIER(" + identifierField + ") SELECT identifier_id, " \
                          + insertValue + "  FROM FHIR247.IDENTIFIER WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update patient name
            def updateDataHumanName(data):
                for insertValue in data:
                    humanNameField = 'HUMAN_NAME_ID, "USE", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX'
                    cmd = "UPSERT INTO FHIR247.HUMAN_NAME(" + humanNameField + ") SELECT human_name_id, " \
                          + insertValue + " FROM FHIR247.HUMAN_NAME WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update patient telecom
            def updateDataContactPoint(data):
                for insertValue in data:
                    contactPointField = 'CONTACT_POINT_ID, "SYSTEM", "VALUE", "USE", RANK'
                    cmd = "UPSERT INTO FHIR247.CONTACT_POINT (" + contactPointField + ") SELECT CONTACT_POINT_ID, " \
                          + insertValue + " FROM FHIR247.CONTACT_POINT WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # insert patient address
            def updateDataAddress(data):
                for insertValue in data:
                    addressField = 'ADDRESS_ID, "USE", "TYPE", TEXT, LINE, CITY, DISTRICT, STATE, POSTAL_CODE, COUNTRY'
                    cmd = "UPSERT INTO FHIR247.ADDRESS (" + addressField + ") SELECT address_id, " \
                          + insertValue + " FROM FHIR247.ADDRESS WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update patient photo
            def updateDataAttachment(data):
                for insertValue in data:
                    attachmentField = 'ATTACHMENT_ID, CONTENT_TYPE, LANGUAGE, DATA, URL, SIZE, HASH, TITLE'
                    cmd = "UPSERT INTO FHIR247.ATTACHMENT (" + attachmentField + ") SELECT attachment_id, " \
                          + insertValue + " FROM FHIR247.ATTACHMENT WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update patient contact
            def updateDataContact(data):
                for insertValue in data:
                    contactField = 'CONTACT_ID, RELATIONSHIP, GENDER, ORGANIZATION'
                    cmd = "UPSERT INTO FHIR247.CONTACT (" + contactField + ") SELECT contact_id, " \
                          + insertValue + " FROM FHIR247.CONTACT WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update contact name
            def updateDataContactHumanName(data):
                for insertValue in data:
                    humanNameField = 'HUMAN_NAME_ID, "USE", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX'
                    cmd = "UPSERT INTO FHIR247.HUMAN_NAME(" + humanNameField + ") SELECT human_name_id, " \
                          + insertValue + " FROM FHIR247.HUMAN_NAME WHERE resource_id = '" + contactID + "'"
                    cursor.execute(cmd)

            # update contact telecom
            def updateDataContactTelecom(data):
                for insertValue in data:
                    contactPointField = 'CONTACT_POINT_ID, "SYSTEM", "VALUE", "USE", RANK'
                    cmd = "UPSERT INTO FHIR247.CONTACT_POINT (" + contactPointField + ") SELECT CONTACT_POINT_ID, " \
                          + insertValue + " FROM FHIR247.CONTACT_POINT WHERE resource_id = '" + contactID + "'"
                    cursor.execute(cmd)

            # insert patient address
            def updateDataContactAddress(data):
                for insertValue in data:
                    addressField = 'ADDRESS_ID, "USE", "TYPE", TEXT, LINE, CITY, DISTRICT, STATE, POSTAL_CODE, COUNTRY'
                    cmd = "UPSERT INTO FHIR247.ADDRESS (" + addressField + ") SELECT address_id, " \
                          + insertValue + " FROM FHIR247.ADDRESS WHERE resource_id = '" + contactID + "'"
                    cursor.execute(cmd)

            # update patient communication
            def updateDataCommunication(data):
                for insertValue in data:
                    communicationField = 'COMMUNICATION_ID, LANGUAGE, PREFERRED'
                    cmd = "UPSERT INTO FHIR247.COMMUNICATION (" + communicationField + ") SELECT communication_id, " \
                          + insertValue + " FROM FHIR247.COMMUNICATION WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            #update patient general practitioner
            def updateDataGeneralPractitioner(data):
                for insertValue in data:
                    generalPractitionerField = 'GENERAL_PRACTITIONER_ID, REFERENCE'
                    cmd = "UPSERT INTO FHIR247.GENERAL_PRACTITIONER (" + generalPractitionerField + ") SELECT GENERAL_PRACTITIONER_ID, " \
                          + insertValue + " FROM FHIR247.GENERAL_PRACTITIONER WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update patient link
            def updateDataLink(data):
                for insertValue in data:
                    linkField = 'LINK_ID, OTHER, TYPE'
                    cmd = "UPSERT INTO FHIR247.LINK (" + linkField + ") SELECT link_id, " \
                          + insertValue + " FROM FHIR247.LINK WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            #update patient
            def updateDataPatient(data):
                for insertValue in data:
                    birthDate =  str(datetime.strptime(dataPatient['birthDate'], '%Y-%m-%d'))
                    deceasedDateTime = str(datetime.strptime(dataPatient['deceasedDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ'))
                    patientField = 'PATIENT_ID, RESOURCE_TYPE, "ACTIVE", GENDER, ' \
                                   'DECEASED_BOOLEAN, MARITAL_STATUS, MULTIPLE_BIRTH_BOOLEAN, ' \
                                   'MULTIPLE_BIRTH_INTEGER, MANAGING_ORGANIZATION, BIRTHDATE, DECEASED_DATETIME, LAST_UPDATED'
                    cmd = "UPSERT INTO FHIR247.PATIENT (" + patientField + ") SELECT patient_id, " \
                           + insertValue + ", TO_DATE('" + birthDate + "', 'yyyy-MM-dd'), " \
                           "TO_DATE('" + deceasedDateTime + "', 'yyyy-MM-dd HH:mm:ss'), " \
                           "TO_DATE('" + lastUpdated + "', 'yyyy-MM-dd HH:mm:ss')  FROM FHIR247.PATIENT" \
                            " WHERE patient_id = '" + resourceID + "'"

                    cursor.execute(cmd)

            ###Create thread1
            t = threading.Thread(target=updateDataIdentifier(identifierValue))
            threads.append(t)

            ###Create thread2
            t = threading.Thread(target=updateDataHumanName(humanNameValue))
            threads.append(t)

            # ###Create thread3
            t = threading.Thread(target=updateDataContactPoint(contactPointValue))
            threads.append(t)

            # ###Create thread4
            t = threading.Thread(target=updateDataAddress(addressValue))
            threads.append(t)

            # ###Create thread5
            if photoInsert:
                t = threading.Thread(target=updateDataAttachment(attachmentValue))
                threads.append(t)

            # ###Create thread6
            t = threading.Thread(target=updateDataContact(contactValue))
            threads.append(t)

            t = threading.Thread(target=updateDataContactHumanName(humanNameContactValue))
            threads.append(t)

            t = threading.Thread(target=updateDataContactTelecom(contactPointContactValue))
            threads.append(t)

            t = threading.Thread(target=updateDataContactAddress(addressContactValue))
            threads.append(t)

            # ###Create thread7
            t = threading.Thread(target=updateDataCommunication(communicationValue))
            threads.append(t)

            ###Create thread8
            if generalPractitionerInsert:
                t = threading.Thread(target=updateDataGeneralPractitioner(generalPractitionerValue))
                threads.append(t)

            # ###Create thread9
            if linkInsert:
                t = threading.Thread(target=updateDataLink(linkValue))
                threads.append(t)

            # ###Create thread10
            t = threading.Thread(target=updateDataPatient(patientValue))
            threads.append(t)

            ###Starting thread
            for t in threads:
                t.start()

            ###Waiting all threads is done
            for t in threads:
                t.join()

            errCode = 200
            message = "Successful update data."
        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

def deletePatient(id):
    errCode = 0
    resourceID = id

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check patient
    checkPatientID = getPatientbyID(resourceID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    if checkPatientID['status'] > 200:
        errCode = 14002
        message = checkPatientID['message']

    connDB = phoenixConn()
    cursor = connDB.cursor()
    cursor.execute("SELECT CONTACT_ID FROM FHIR247.CONTACT WHERE RESOURCE_ID = '" + resourceID + "' ")
    data = cursor.fetchall()

    if len(data) > 0:
        errCode = 0

    if errCode == 0 :

        threads = []
        # deleted processing
        try:
            #Set thread
            #delete patient identifier
            def deleteDataIdentifier():
                cmd = "DELETE FROM FHIR247.IDENTIFIER WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            #delete patient human_name
            def deleteDataHumanName():
                cmd = "DELETE FROM FHIR247.HUMAN_NAME WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            def deleteDataHumanNameContact(data):
                for deleteValue in data:
                    contactID = deleteValue[0]
                    cmd = "DELETE FROM FHIR247.HUMAN_NAME WHERE resource_id = '" + contactID + "' "
                    cursor.execute(cmd)

            #delete patient contact_point
            def deleteDataContactPoint():
                cmd = "DELETE FROM FHIR247.CONTACT_POINT WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            #delete patient contact_point
            def deleteDataContactPointContact(data):
                for deleteValue in data:
                    contactID = deleteValue[0]
                    cmd = "DELETE FROM FHIR247.CONTACT_POINT WHERE resource_id = '" + contactID + "' "
                    cursor.execute(cmd)

            #delete patient address
            def deleteDataAddress():
                cmd = "DELETE FROM FHIR247.ADDRESS WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            #delete patient address
            def deleteDataAddressContact(data):
                for deleteValue in data:
                    contactID = deleteValue[0]
                    cmd = "DELETE FROM FHIR247.ADDRESS WHERE resource_id = '" + contactID + "' "
                    cursor.execute(cmd)

            #delete patient attachment
            def deleteDataAttachment():
                cmd = "DELETE FROM FHIR247.ATTACHMENT WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            #delete patient contact
            def deleteDataContact():
                cmd = "DELETE FROM FHIR247.CONTACT WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            #delete patient communication
            def deleteDataCommunication():
                cmd = "DELETE FROM FHIR247.COMMUNICATION WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            #delete patient link
            def deleteDataLink():
                cmd = "DELETE FROM FHIR247.LINK WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            #delete patient general_practitioner
            def deleteDataGeneralPractitioner():
                cmd = "DELETE FROM FHIR247.GENERAL_PRACTITIONER WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            #delete patient
            def deleteDataPatient():
                cmd = "DELETE FROM FHIR247.PATIENT WHERE patient_id = '" + resourceID + "' "
                cursor.execute(cmd)

            ###Create thread1
            t = threading.Thread(target=deleteDataIdentifier())
            threads.append(t)

            ###Create thread2
            t = threading.Thread(target=deleteDataHumanName())
            threads.append(t)

            ###Create thread2
            t = threading.Thread(target=deleteDataHumanNameContact(data))
            threads.append(t)

            ###Create thread3
            t = threading.Thread(target=deleteDataContactPoint())
            threads.append(t)

            ###Create thread3
            t = threading.Thread(target=deleteDataContactPointContact(data))
            threads.append(t)

            ###Create thread4
            t = threading.Thread(target=deleteDataAddress())
            threads.append(t)

            ###Create thread4
            t = threading.Thread(target=deleteDataAddressContact(data))
            threads.append(t)

            ###Create thread5
            t = threading.Thread(target=deleteDataAttachment())
            threads.append(t)

            ###Create thread6
            t = threading.Thread(target=deleteDataContact())
            threads.append(t)

            ###Create thread7
            t = threading.Thread(target=deleteDataCommunication())
            threads.append(t)

            ###Create thread8
            t = threading.Thread(target=deleteDataLink())
            threads.append(t)

            ###Create thread9
            t = threading.Thread(target=deleteDataGeneralPractitioner())
            threads.append(t)

            ###Create thread10
            t = threading.Thread(target=deleteDataPatient())
            threads.append(t)

            ###Starting thread
            for t in threads:
                t.start()

            ###Waiting all threads is done
            for t in threads:
                t.join()

            errCode = 200
            message = "Successful delete data."

        except OSError as err:
            errCode = 13002
            message = err

        result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result

#person
def getPersons():
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # checking filter parameters
    offset = request.args.get('offset')
    limit = request.args.get('limit')

    address = request.args.get('address')
    addressCity = request.args.get('address-city')
    addressCountry = request.args.get('address-country')
    addressPostalcode = request.args.get('address-postalcode')
    addressState = request.args.get('address-state')
    addressUse = request.args.get('address-use')
    birthDate = request.args.get('birthdate')
    email = request.args.get('email')
    gender = request.args.get('gender')
    identifier = request.args.get('identifier')
    link = request.args.get('link')
    name = request.args.get('name')
    organization = request.args.get('organization')
    patient = request.args.get('patient')
    practitioner = request.args.get('practitioner')
    relatedperson = request.args.get('relatedperson')
    phone = request.args.get('phone')
    telecom = request.args.get('telecom')

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    if errCode == 0:
        condition = ""
        offset_limit = ""

        if address:
            condition += " d.line LIKE '%" + address + "%' OR d.city LIKE UPPER('%" + address + "%') OR " \
                         "d.city LIKE UPPER('%" + address + "%') OR d.district LIKE UPPER('%" + address + "%') OR " \
                         "d.state LIKE UPPER('%" + address + "%') OR d.country LIKE UPPER('%" + address + "%') OR " \
                         "d.postal_code LIKE UPPER('%" + address + "%') OR d.text LIKE '%" + address + "%'" + " AND "
        if addressCity:
            condition += " d.city LIKE UPPER('%" + addressCity + "%')" + " AND "
        if addressCountry:
            condition += " d.country LIKE UPPER('%" + addressCountry + "%')" + " AND "
        if addressPostalcode:
            condition += " d.postal_code LIKE UPPER('%" + addressPostalcode + "%')" + " AND "
        if addressState:
            condition += " d.state LIKE UPPER('%" + addressState + "%')" + " AND "
        if addressUse:
            condition += " d.\"USE\" LIKE '%" + addressUse + "%'" + " AND "
        if birthDate:
            condition += " a.birthdate = TO_DATE('" + birthDate + "', 'yyyy-MM-dd')" + " AND "
        if email:
            condition += " e.system='email' AND e.\"VALUE\" LIKE '%" + email + "%'" + " AND "
        if gender:
            condition += " a.gender LIKE '%" + gender + "%'" + " AND "
        if identifier:
            condition += " c.\"VALUE\" LIKE '%" + identifier + "%'" + " AND "
        if link:
            condition += " i.target LIKE '%" + link + "%'" + " AND "
        if name:
            condition += " b.text LIKE '%" + name + "%' OR b.family LIKE '%" + name + "%' OR " \
                         "b.given LIKE '%" + name + "%' OR b.prefix LIKE '%" + name + "%' OR " \
                         "b.suffix LIKE '%" + name + "%'" + " AND "
        if organization:
            condition += " a.managing_organization LIKE '%" + organization + "%'" + " AND "
        if patient:
            condition += " i.target LIKE 'patient/%" + patient + "%'" + " AND "
        if practitioner:
            condition += " i.target LIKE 'practitioner/%" + link + "%'" + " AND "
        if relatedperson:
            condition += " i.target LIKE 'relatedperson/%" + link + "%'" + " AND "
        if phone:
            condition += " e.system='phone' AND e.\"VALUE\" LIKE '%" + phone + "%'" + " AND "
        if telecom:
            condition += " e.\"VALUE\" LIKE '%" + telecom + "%'" + " AND "

        if offset and limit:
            offset_limit = " LIMIT "+ limit +" OFFSET "+ offset
        else:
            offset = 0
            limit = 0

        if condition != '':
            condition = " WHERE " + condition[:-5]

        ##metode2 (JOIN di Phoenix)

        cmd = "SELECT a.person_id, a.resource_type, TO_CHAR(a.last_updated, \'yyyy-MM-dd HH:mm:ss\'), a.\"ACTIVE\", a.gender," \
              "TO_CHAR(a.birthdate, \'yyyy-MM-dd\'), a.managing_organization, " \
              "b.human_name_id, b.\"USE\", b.text, b.family, b.given, b.prefix, b.suffix, b.resource_id, " \
              "c.identifier_id, c.\"USE\", c.type, c.system, c.\"VALUE\", c.resource_id, " \
              "d.address_id, d.\"USE\", d.\"TYPE\", d.text, d.line, d.city, d.district, d.state, d.postal_code, d.country, d.resource_id, " \
              "e.contact_point_id, e.system, e.\"VALUE\", e.\"USE\", e.rank, e.resource_id, " \
              "f.attachment_id, f.content_type, f.language, f.data, f.url, f.size, f.hash, f.title, f.resource_id, " \
              "i.link_id, i.target, i.assurance, i.resource_id " \
              "FROM FHIR247.PERSON a " \
              "LEFT JOIN FHIR247.HUMAN_NAME b ON a.person_id = b.resource_id " \
              "LEFT JOIN FHIR247.IDENTIFIER c ON a.person_id = c.resource_id " \
              "LEFT JOIN FHIR247.ADDRESS d ON a.person_id = d.resource_id " \
              "LEFT JOIN FHIR247.CONTACT_POINT e ON a.person_id = e.resource_id " \
              "LEFT JOIN FHIR247.ATTACHMENT f ON a.person_id = f.resource_id " \
              "LEFT JOIN FHIR247.LINK i ON a.person_id = i.resource_id " + condition + " ORDER BY a.person_id " + offset_limit

        # person 0-6, human_name 7-14, identifier 15-20, address 21-31, contact_point 32-37, attachment 38-46, link 47-50

        conn = phoenixConn()
        cursor = conn.cursor()

        Person = []

        cursor.execute(cmd)
        data = result = cursor.fetchall()

        # set default value of resources
        PersonID = ""
        index = 0
        conn.close()

        for dt in data:
            # person_id 0
            if PersonID == dt[0]:
                exist = True
            else:
                PersonID = dt[0]
                exist = False
            if exist:
                # parsing human_name 7-14
                humanName = {"id": dt[7], "use": dt[8], "text": dt[9], "family": dt[10], "given": dt[11].split('|'),
                             "prefix": dt[12].split('|'), "suffix": dt[13].split('|')}
                Person[index - 1]["name"].append(humanName)
                Person[index - 1]["name"] = RemoveDuplicateArray(Person[index - 1]["name"])

                # parsing identifier 15-20
                identifier = {"id": dt[15], "use": dt[16], "type": {"text": dt[17], "coding": []}, "system": dt[18],
                              "value": dt[19]}
                Person[index - 1]["identifier"].append(identifier)
                Person[index - 1]["identifier"] = RemoveDuplicateArray(Person[index - 1]["identifier"])

                # parsing address 21-31
                address = {"id": dt[21], "use": dt[22], "type": dt[23], "text": dt[24], "line": dt[25].split('|'),
                           "city": dt[26], "district": dt[27], "state": dt[28], "postalCode": dt[29], "country": dt[30]}
                Person[index - 1]["address"].append(address)
                Person[index - 1]["address"] = RemoveDuplicateArray(Person[index - 1]["address"])

                # parsing contact_point 32-37
                telecom = {"id": dt[32], "system": dt[33], "value": dt[34], "use": dt[35], "rank": dt[36]}
                Person[index - 1]["telecom"].append(telecom)
                Person[index - 1]["telecom"] = RemoveDuplicateArray(Person[index - 1]["telecom"])

                # parsing photo/attachment 38-46
                photo = {"id": dt[38], "contentType": dt[39], "language": dt[40], "data": dt[41], "url": dt[42],
                         "size": dt[43], "hash": dt[44], "title": dt[45]}
                Person[index - 1]["photo"].append(photo)
                Person[index - 1]["photo"] = RemoveDuplicateArray(Person[index - 1]["photo"])

                # parsing link 47-51
                link = {"id": dt[47], "target": {"reference": dt[48]}, "assurance": dt[49]}
                Person[index - 1]["link"].append(link)
                Person[index - 1]["link"] = RemoveDuplicateArray(Person[index - 1]["link"])

            else:
                # person 0-6
                jsonPerson = {
                    "resourceType": dt[1],
                    "id": dt[0],
                    "meta": {"lastUpdated": dt[2], "versionId": ""},
                    "text": {"status": "", "div": ""},
                    "identifier": [],
                    "name": [],
                    "telecom": [],
                    "gender": dt[4],
                    "birthDate": dt[5],
                    "address": [],
                    "photo": [],
                    "managingOrganization": {"reference": dt[6]},
                    "active": dt[3],
                    "link": []
                }

                # parsing human_name 7-14
                humanName = {"id": dt[7], "use": dt[8], "text": dt[9], "family": dt[10], "given": dt[11].split('|'),
                             "prefix": dt[12].split('|'), "suffix": dt[13].split('|')}
                jsonPerson["name"].append(humanName)

                # parsing identifier 15-20
                identifier = {"id": dt[15], "use": dt[16], "type": {"text": dt[17], "coding": []}, "system": dt[18],
                              "value": dt[19]}
                jsonPerson["identifier"].append(identifier)

                # parsing address 21-31
                address = {"id": dt[21], "use": dt[22], "type": dt[23], "text": dt[24], "line": dt[25].split('|'),
                           "city": dt[26], "district": dt[27], "state": dt[28], "postalCode": dt[29], "country": dt[30]}
                jsonPerson["address"].append(address)

                # parsing contact_point 32-37
                telecom = {"id": dt[32], "system": dt[33], "value": dt[34], "use": dt[35], "rank": dt[36]}
                jsonPerson["telecom"].append(telecom)

                # parsing photo/attachment 38-46
                photo = {"id": dt[38], "contentType": dt[39], "language": dt[40], "data": dt[41], "url": dt[42],
                         "size": dt[43], "hash": dt[44], "title": dt[45]}
                jsonPerson["photo"].append(photo)

                # parsing link 47-51
                link = {"id": dt[47], "target": {"reference": dt[48]}, "assurance": dt[49]}
                jsonPerson["link"].append(link)

                Person.append(jsonPerson)
                index += 1

                #len(data['result'][0]['run'])  "total": len(Patient['data'][0]['id'])

            result ={"status": 200, "offset": offset, "limit": limit, "data": Person, "total": len(Person)}
        # return Patient

    else:
        result = {"status": errCode, "message": message}

    return result

def addPerson():
    errCode = 0
    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']

    if errCode == 0:
        # parsing request
        data = request.data
        dataPerson = json.loads(data)

        personID = generateUniqeID('P3R247')

        #identifier
        if 'identifier' in dataPerson and type(dataPerson['identifier']).__name__ == 'list' and len(dataPerson['identifier']) > 0:
            identifierValue = []
            for ide in dataPerson['identifier']:
                identifierID = generateUniqeID('1D3247')
                identifierValue.append('\'' + identifierID + '\',' + \
                                  '\'' + ide['use'] + '\',' + \
                                  '\'' + ide['type']['text'] + '\',' + \
                                  '\'' + ide['system'] + '\',' + \
                                  '\'' + ide['value'] + '\',' + \
                                  '\'' + personID + '\'')
        else:
            errCode = 13001
            message = "Identifier request is required."

        #name
        if 'name' in dataPerson and type(dataPerson['name']).__name__ == 'list' and len(dataPerson['name']) > 0:
            humanNameValue = []
            for hum in dataPerson['name']:
                humanNameID = generateUniqeID('HU3247')
                humanNameValue.append('\'' + humanNameID + '\',' + \
                                  '\'' + hum['use'] + '\',' + \
                                  '\'' + ' '.join(hum['prefix']) + ' ' + hum['text'] + ', ' + ','.join(hum['suffix']) + '\',' + \
                                  '\'' + hum['family'] + '\',' + \
                                  '\'' + '|'.join(hum['given']) + '\',' + \
                                  '\'' + '|'.join(hum['prefix']) + '\',' + \
                                  '\'' + '|'.join(hum['suffix']) + '\',' + \
                                  '\'' + personID + '\'')

        else:
            errCode = 13002
            message = "Name request is required."

        #telecom / contact point
        if 'telecom' in dataPerson and type(dataPerson['telecom']).__name__ == 'list' and len(dataPerson['telecom']) > 0:
            contactPointValue = []
            for tel in dataPerson['telecom']:
                telecomID = generateUniqeID('T3L247')
                contactPointValue.append('\'' + telecomID + '\',' + \
                                  '\'' + tel['system'] + '\',' + \
                                  '\'' + tel['value'] + '\',' + \
                                  '\'' + tel['use'] + '\',' + \
                                  '' + str(tel['rank']) + ',' + \
                                  '\'' + personID + '\'')
        else:
            errCode = 13003
            message = "Telecom request is required."

        #address
        if 'address' in dataPerson and type(dataPerson['address']).__name__ == 'list' and len(dataPerson['address']) > 0:
            addressValue = []
            for addr in dataPerson['address']:
                addressID = generateUniqeID('4DD247')
                addressValue.append('\'' + addressID + '\',' + \
                                  '\'' + addr['use'] + '\',' + \
                                  '\'' + addr['type'] + '\',' + \
                                  '\'' + addr['text'] + '\',' + \
                                  '\'' + '|'.join(addr['line']) + '\',' + \
                                  '\'' + addr['city'].upper() + '\',' + \
                                  '\'' + addr['district'].upper() + '\',' + \
                                  '\'' + addr['state'].upper() + '\',' + \
                                  '\'' + addr['postalCode'] + '\',' + \
                                  '\'' + addr['country'].upper() + '\',' + \
                                  '\'' + personID + '\'')
        else:
            errCode = 13004
            message = "Address request is required."

        #photo atau attachment
        if 'photo' in dataPerson and type(dataPerson['photo']).__name__ == 'list' and len(dataPerson['photo']) > 0:
            photoInsert = 1
            attachmentValue = []
            for att in dataPerson['photo']:
                attachmentID = generateUniqeID('4T7247')
                attachmentValue.append('\'' + attachmentID + '\',' + \
                                  '\'' + att['contentType'] + '\',' + \
                                  '\'' + att['language'] + '\',' + \
                                  '\'' + '' + '\',' + \
                                  '\'' + att['url'] + '\',' + \
                                  '\'' + att['size'] + '\',' + \
                                  '\'' + att['hash'] + '\',' + \
                                  '\'' + att['title'] + '\',' + \
                                  '\'' + personID + '\'')
        else:
            photoInsert = 0


        # link
        if 'link' in dataPerson and type(dataPerson['link']).__name__ == 'list' and len(dataPerson['link']) > 0:
            linkInsert = 1
            linkValue = []

            for lk in dataPerson['link']:
                linkID = generateUniqeID('l1nk247')
                linkValue.append('\'' + linkID + '\',' + \
                                 '\'' + lk['target']['reference'] + '\',' + \
                                 '\'' + lk['assurance'] + '\',' + \
                                 '\'' + personID + '\'')
        else:
            linkInsert = 0


        # person
        if len(dataPerson) > 0:
            currentTime = datetime.now()
            resourceType = "Person"
            personValue = []
            personValue.append('\'' + personID + '\',' + \
                                '\'' + resourceType + '\',' + \
                                '\'' + str(currentTime) + '\',' + \
                                '' + str(dataPerson['active']) + ',' + \
                                '\'' + dataPerson['gender'] + '\',' + \
                                '\'' + dataPerson['birthDate'] + '\',' + \
                                '\'' + dataPerson['managingOrganization']['reference'] + '\'')

        else:
            errCode = 13009
            message = "Person request is required."

        if errCode == 0:
            connDB = phoenixConn()
            cursor = connDB.cursor()

            threads = []

            #insert processing
            try:
                # Set thread
                # insert person identifier
                def insertDataIdentifier(data):
                    for insertValue in data:
                        identifierField = 'IDENTIFIER_ID, "USE", "TYPE", "SYSTEM", "VALUE", RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.IDENTIFIER (" + identifierField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert person name
                def insertDataHumanName(data):
                    for insertValue in data:
                        humanNameField = 'HUMAN_NAME_ID, "USE", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.HUMAN_NAME (" + humanNameField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert person telecom
                def insertDataContactPoint(data):
                    for insertValue in data:
                        contactPointField = 'CONTACT_POINT_ID, "SYSTEM", "VALUE", "USE", RANK, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.CONTACT_POINT (" + contactPointField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert person address
                def insertDataAddress(data):
                    for insertValue in data:
                        addressField = 'ADDRESS_ID, "USE", "TYPE", TEXT, LINE, CITY, DISTRICT, STATE, POSTAL_CODE, COUNTRY, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.ADDRESS (" + addressField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert person photo
                def insertDataAttachment(data):
                    for insertValue in data:
                        attachmentField = 'ATTACHMENT_ID, CONTENT_TYPE, LANGUAGE, DATA, URL, SIZE, HASH, TITLE, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.ATTACHMENT (" + attachmentField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert person link
                def insertDataLink(data):
                    for insertValue in data:
                        linkField = 'LINK_ID, TARGET, ASSURANCE, RESOURCE_ID'
                        cmd = "UPSERT INTO FHIR247.LINK (" + linkField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                # insert person
                def insertDataPerson(data):
                    for insertValue in data:
                        personField = 'PERSON_ID, RESOURCE_TYPE, LAST_UPDATED, "ACTIVE", GENDER, BIRTHDATE, ' \
                                       'MANAGING_ORGANIZATION'
                        cmd = "UPSERT INTO FHIR247.PERSON (" + personField + ") VALUES(" + insertValue + ")"
                        cursor.execute(cmd)

                ###Create thread1
                t = threading.Thread(target=insertDataIdentifier(identifierValue))
                threads.append(t)

                ###Create thread2
                t = threading.Thread(target=insertDataHumanName(humanNameValue))
                threads.append(t)

                # ###Create thread3
                t = threading.Thread(target=insertDataContactPoint(contactPointValue))
                threads.append(t)
                #
                # ###Create thread4
                t = threading.Thread(target=insertDataAddress(addressValue))
                threads.append(t)

                # ###Create thread5
                if photoInsert:
                    t = threading.Thread(target=insertDataAttachment(attachmentValue))
                    threads.append(t)

                # ###Create thread8
                if linkInsert:
                    t = threading.Thread(target=insertDataLink(linkValue))
                    threads.append(t)

                # ###Create thread10
                t = threading.Thread(target=insertDataPerson(personValue))
                threads.append(t)

                ###Starting thread
                for t in threads:
                    t.start()

                ###Waiting all threads is done
                for t in threads:
                    t.join()

                errCode = 200
                message = "Successful insert data."
            except OSError as err:
                errCode = 13002
                message = err

            result = {"status": errCode, "message": message}
        else:
            result = {"status": errCode, "message": message}

        return result

    else:
        result = {"status": errCode, "message": message}

    return result

def getPerson(id):
    resourceID = id
    errCode = 0

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check user
    checkPersonID = getPersonbyID(resourceID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    if checkPersonID['status'] > 200:
        errCode = 14002
        message = checkPersonID['message']

    if errCode == 0:
        cmd = "SELECT a.person_id, a.resource_type, TO_CHAR(a.last_updated, \'yyyy-MM-dd HH:mm:ss\'), a.\"ACTIVE\", a.gender," \
              "TO_CHAR(a.birthdate, \'yyyy-MM-dd\'), a.managing_organization, " \
              "b.human_name_id, b.\"USE\", b.text, b.family, b.given, b.prefix, b.suffix, b.resource_id, " \
              "c.identifier_id, c.\"USE\", c.type, c.system, c.\"VALUE\", c.resource_id, " \
              "d.address_id, d.\"USE\", d.\"TYPE\", d.text, d.line, d.city, d.district, d.state, d.postal_code, d.country, d.resource_id, " \
              "e.contact_point_id, e.system, e.\"VALUE\", e.\"USE\", e.rank, e.resource_id, " \
              "f.attachment_id, f.content_type, f.language, f.data, f.url, f.size, f.hash, f.title, f.resource_id, " \
              "i.link_id, i.target, i.assurance, i.resource_id " \
              "FROM FHIR247.PERSON a " \
              "LEFT JOIN FHIR247.HUMAN_NAME b ON a.person_id = b.resource_id " \
              "LEFT JOIN FHIR247.IDENTIFIER c ON a.person_id = c.resource_id " \
              "LEFT JOIN FHIR247.ADDRESS d ON a.person_id = d.resource_id " \
              "LEFT JOIN FHIR247.CONTACT_POINT e ON a.person_id = e.resource_id " \
              "LEFT JOIN FHIR247.ATTACHMENT f ON a.person_id = f.resource_id " \
              "LEFT JOIN FHIR247.LINK i ON a.person_id = i.resource_id " \
              "WHERE a.person_id = '"+ resourceID +"' " \
              "ORDER BY a.person_id"

        # person 0-6, human_name 7-14, identifier 15-20, address 21-31, contact_point 32-37, attachment 38-46, link 47-50

        conn = phoenixConn()
        cursor = conn.cursor()

        Person = []

        cursor.execute(cmd)
        data = result = cursor.fetchall()

        # set default value of resources
        PersonID = ""
        index = 0
        conn.close()

        for dt in data:
            # patient_id 0
            if PersonID == dt[0]:
                exist = True
            else:
                PersonID = dt[0]
                exist = False
            if exist:
                # parsing human_name 7-14
                humanName = {"id": dt[7], "use": dt[8], "text": dt[9], "family": dt[10], "given": dt[11].split('|'),
                             "prefix": dt[12].split('|'), "suffix": dt[13].split('|')}
                Person[index - 1]["name"].append(humanName)
                Person[index - 1]["name"] = RemoveDuplicateArray(Person[index - 1]["name"])

                # parsing identifier 15-20
                identifier = {"id": dt[15], "use": dt[16], "type": {"text": dt[17], "coding": []}, "system": dt[18],
                              "value": dt[19]}
                Person[index - 1]["identifier"].append(identifier)
                Person[index - 1]["identifier"] = RemoveDuplicateArray(Person[index - 1]["identifier"])

                # parsing address 21-31
                address = {"id": dt[21], "use": dt[22], "type": dt[23], "text": dt[24], "line": dt[25].split('|'),
                           "city": dt[26], "district": dt[27], "state": dt[28], "postalCode": dt[29], "country": dt[30]}
                Person[index - 1]["address"].append(address)
                Person[index - 1]["address"] = RemoveDuplicateArray(Person[index - 1]["address"])

                # parsing contact_point 32-37
                telecom = {"id": dt[32], "system": dt[33], "value": dt[34], "use": dt[35], "rank": dt[36]}
                Person[index - 1]["telecom"].append(telecom)
                Person[index - 1]["telecom"] = RemoveDuplicateArray(Person[index - 1]["telecom"])

                # parsing photo/attachment 38-46
                photo = {"id": dt[38], "contentType": dt[39], "language": dt[40], "data": dt[41], "url": dt[42],
                         "size": dt[43], "hash": dt[44], "title": dt[45]}
                Person[index - 1]["photo"].append(photo)
                Person[index - 1]["photo"] = RemoveDuplicateArray(Person[index - 1]["photo"])

                # parsing link 47-51
                link = {"id": dt[47], "target": {"reference": dt[48]}, "assurance": dt[49]}
                Person[index - 1]["link"].append(link)
                Person[index - 1]["link"] = RemoveDuplicateArray(Person[index - 1]["link"])

            else:
                # person 0-6
                jsonPerson = {
                    "resourceType": dt[1],
                    "id": dt[0],
                    "meta": {"lastUpdated": dt[2], "versionId": ""},
                    "text": {"status": "", "div": ""},
                    "identifier": [],
                    "name": [],
                    "telecom": [],
                    "gender": dt[4],
                    "birthDate": dt[5],
                    "address": [],
                    "photo": [],
                    "managingOrganization": {"reference": dt[6]},
                    "active": dt[3],
                    "link": []
                }

                # parsing human_name 7-14
                humanName = {"id": dt[7], "use": dt[8], "text": dt[9], "family": dt[10], "given": dt[11].split('|'),
                             "prefix": dt[12].split('|'), "suffix": dt[13].split('|')}
                jsonPerson["name"].append(humanName)

                # parsing identifier 15-20
                identifier = {"id": dt[15], "use": dt[16], "type": {"text": dt[17], "coding": []}, "system": dt[18],
                              "value": dt[19]}
                jsonPerson["identifier"].append(identifier)

                # parsing address 21-31
                address = {"id": dt[21], "use": dt[22], "type": dt[23], "text": dt[24], "line": dt[25].split('|'),
                           "city": dt[26], "district": dt[27], "state": dt[28], "postalCode": dt[29], "country": dt[30]}
                jsonPerson["address"].append(address)

                # parsing contact_point 32-37
                telecom = {"id": dt[32], "system": dt[33], "value": dt[34], "use": dt[35], "rank": dt[36]}
                jsonPerson["telecom"].append(telecom)

                # parsing photo/attachment 38-46
                photo = {"id": dt[38], "contentType": dt[39], "language": dt[40], "data": dt[41], "url": dt[42],
                         "size": dt[43], "hash": dt[44], "title": dt[45]}
                jsonPerson["photo"].append(photo)

                # parsing link 47-51
                link = {"id": dt[47], "target": {"reference": dt[48]}, "assurance": dt[49]}
                jsonPerson["link"].append(link)

                Person.append(jsonPerson)
                index += 1

        return Person

    else:
        result = {"status": errCode, "message": message}

    return result

def updatePerson(id):
    errCode = 0
    resourceID = id

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate (accessToken)

    # check user
    checkPersonID = getPersonbyID(resourceID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    if checkPersonID['status'] > 200:
        errCode = 14002
        message = checkPersonID['message']

    # parsing request
    data = request.data
    dataPerson = json.loads(data)

    # identifier
    if 'identifier' in dataPerson and type (dataPerson['identifier']).__name__ == 'list' and len (dataPerson['identifier']) > 0:
        identifierValue = []
        for ide in dataPerson['identifier']:
            identifierValue.append ('\'' + ide['use'] + '\',' + \
                                '\'' + ide['type']['text'] + '\',' + \
                                '\'' + ide['system'] + '\',' + \
                                '\'' + ide['value'] + '\'')
    else:
        errCode = 13001
        message = "Identifier request is required."

    # name
    if 'name' in dataPerson and type (dataPerson['name']).__name__ == 'list' and len (dataPerson['name']) > 0:
        humanNameValue = []
        for hum in dataPerson['name']:
            humanNameValue.append ('\'' + hum['use'] + '\',' + \
                                '\'' + ' '.join (hum['prefix']) + ' ' + hum['text'] + ', ' + ','.join (hum['suffix']) + '\',' + \
                                '\'' + hum['family'] + '\',' + \
                                '\'' + '|'.join (hum['given']) + '\',' + \
                                '\'' + '|'.join (hum['prefix']) + '\',' + \
                                '\'' + '|'.join (hum['suffix']) + '\'')
    else:
        errCode = 13002
        message = "Name request is required."

    # telecom / contact point
    if 'telecom' in dataPerson and type (dataPerson['telecom']).__name__ == 'list' and len (dataPerson['telecom']) > 0:
        contactPointValue = []
        for tel in dataPerson['telecom']:
            contactPointValue.append('\'' + tel['system'] + '\',' + \
                                '\'' + tel['value'] + '\',' + \
                                '\'' + tel['use'] + '\',' + \
                                '' + str (tel['rank']) + '')
    else:
        errCode = 13003
        message = "Telecom request is required."

    # address
    if 'address' in dataPerson and type (dataPerson['address']).__name__ == 'list' and len (dataPerson['address']) > 0:
        addressValue = []
        for addr in dataPerson['address']:
            addressValue.append('\'' + addr['use'] + '\',' + \
                                '\'' + addr['type'] + '\',' + \
                                '\'' + addr['text'] + '\',' + \
                                '\'' + '|'.join (addr['line']) + '\',' + \
                                '\'' + addr['city'].upper () + '\',' + \
                                '\'' + addr['district'].upper () + '\',' + \
                                '\'' + addr['state'].upper () + '\',' + \
                                '\'' + addr['postalCode'] + '\',' + \
                                '\'' + addr['country'].upper () + '\'')
    else:
        errCode = 13004
        message = "Address request is required."

    # photo atau attachment
    if 'photo' in dataPerson and type (dataPerson['photo']).__name__ == 'list' and len (dataPerson['photo']) > 0:
        photoInsert = 1
        attachmentValue = []
        for att in dataPerson['photo']:
            attachmentValue.append ('\'' + att['contentType'] + '\',' + \
                                '\'' + att['language'] + '\',' + \
                                '\'' + '' + '\',' + \
                                '\'' + att['url'] + '\',' + \
                                '\'' + att['size'] + '\',' + \
                                '\'' + att['hash'] + '\',' + \
                                '\'' + att['title'] + '\'')
    else:
        photoInsert = 0

    # link
    if 'link' in dataPerson and type (dataPerson['link']).__name__ == 'list' and len (dataPerson['link']) > 0:
        linkInsert = 1
        linkValue = []
        for lk in dataPerson['link']:
            linkValue.append('\'' + lk['target']['reference'] + '\',' + \
                                '\'' + lk['assurance'] + '\'')
    else:
        linkInsert = 0

    # person
    if len (dataPerson) > 0:
        currentTime = datetime.now()
        lastUpdated = currentTime.strftime('%Y-%m-%d %H:%M:%S.%f')

        resourceType = "Person"
        personValue = []
        personValue.append ('\'' + resourceType + '\',' + \
                                '' + str(dataPerson['active']) + ',' + \
                                '\'' + dataPerson['gender'] + '\',' + \
                                '\'' + dataPerson['managingOrganization']['reference'] + '\'')

    else:
        errCode = 13009
        message = "Person request is required."

    if errCode == 0:
        threads = []
        conn = phoenixConn()
        cursor = conn.cursor()

        # update processing
        try:
            # update person identifier
            def updateDataIdentifier(data):
                for insertValue in data:
                    identifierField = 'IDENTIFIER_ID, "USE", "TYPE", "SYSTEM", "VALUE"'
                    cmd = "UPSERT INTO FHIR247.IDENTIFIER (" + identifierField + ") SELECT identifier_id, " \
                          + insertValue + " FROM FHIR247.IDENTIFIER WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update person name
            def updateDataHumanName(data):
                for insertValue in data:
                    humanNameField = 'HUMAN_NAME_ID, "USE", TEXT, FAMILY, GIVEN, PREFIX, SUFFIX'
                    cmd = "UPSERT INTO FHIR247.HUMAN_NAME (" + humanNameField + ") SELECT human_name_id, " \
                          + insertValue + " FROM FHIR247.HUMAN_NAME WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update person telecom
            def updateDataContactPoint(data):
                for insertValue in data:
                    contactPointField = 'CONTACT_POINT_ID, "SYSTEM", "VALUE", "USE", RANK'
                    cmd = "UPSERT INTO FHIR247.CONTACT_POINT (" + contactPointField + ") SELECT contact_point_id, " \
                          + insertValue + " FROM FHIR247.CONTACT_POINT WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update person address
            def updateDataAddress(data):
                for insertValue in data:
                    addressField = 'ADDRESS_ID, "USE", "TYPE", TEXT, LINE, CITY, DISTRICT, STATE, POSTAL_CODE, COUNTRY'
                    cmd = "UPSERT INTO FHIR247.ADDRESS (" + addressField + ") SELECT address_id, " \
                          + insertValue + " FROM FHIR247.ADDRESS WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update person photo
            def updateDataAttachment(data):
                for insertValue in data:
                    attachmentField = 'ATTACHMENT_ID, CONTENT_TYPE, LANGUAGE, DATA, URL, SIZE, HASH, TITLE'
                    cmd = "UPSERT INTO FHIR247.ATTACHMENT (" + attachmentField + ") SELECT attachment_id, " \
                          + insertValue + " FROM FHIR247.ATTACHMENT WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # update person link
            def updateDataLink(data):
                for insertValue in data:
                    linkField = 'LINK_ID, TARGET, ASSURANCE'
                    cmd = "UPSERT INTO FHIR247.LINK (" + linkField + ") SELECT link_id, " \
                          + insertValue + " FROM FHIR247.LINK WHERE resource_id = '" + resourceID + "'"
                    cursor.execute(cmd)

            # # update person
            def updateDataPerson(data):
                for insertValue in data:
                    birthDate = str(datetime.strptime(dataPerson['birthDate'], '%Y-%m-%d'))

                    personField = 'PERSON_ID, RESOURCE_TYPE, "ACTIVE", GENDER, ' \
                                  'MANAGING_ORGANIZATION, BIRTHDATE, LAST_UPDATED'
                    cmd = "UPSERT INTO FHIR247.PERSON (" + personField + ") SELECT person_id, " \
                          + insertValue + ", TO_DATE('" + birthDate + "', 'yyyy-MM-dd'), " \
                          "TO_DATE('" + lastUpdated + "', 'yyyy-MM-dd HH:mm:ss') FROM FHIR247.PERSON WHERE PERSON_ID = '" + resourceID + "'"
                    cursor.execute(cmd)

            ###Create thread1
            t = threading.Thread(target=updateDataIdentifier(identifierValue))
            threads.append(t)

            ###Create thread2
            t = threading.Thread(target=updateDataHumanName(humanNameValue))
            threads.append(t)

            ###Create thread3
            t = threading.Thread(target=updateDataContactPoint(contactPointValue))
            threads.append(t)

            ###Create thread4
            t = threading.Thread(target=updateDataAddress(addressValue))
            threads.append(t)

            ###Create thread5
            if photoInsert:
                t = threading.Thread(target=updateDataAttachment(attachmentValue))
                threads.append(t)

            # ###Create thread8
            if linkInsert:
                t = threading.Thread(target=updateDataLink(linkValue))
                threads.append(t)

            # ###Create thread10
            t = threading.Thread(target=updateDataPerson(personValue))
            threads.append(t)

            ###Starting thread
            for t in threads:
                t.start()

            ###Waiting all threads is done
            for t in threads:
                t.join()

            conn.close()

            errCode = 200
            message = "Successful update data."
            result = {"status": errCode, "message": message}
        except OSError as err:
            errCode = 13002
            message = err
            result = { "status": errCode, "message": message }
    else:
        result = { "status": errCode, "message": message }

    return result

def deletePerson(id):
    errCode = 0
    resourceID = id

    # validate access token
    accessToken = request.headers['token']
    checkToken = tokenValidate(accessToken)

    # check user
    checkPersonID = getPersonbyID(resourceID)

    if checkToken['status'] > 200:
        errCode = 14001
        message = checkToken['message']
    if checkPersonID['status'] > 200:
        errCode = 14002
        message = checkPersonID['message']

    connDB = phoenixConn()
    cursor = connDB.cursor()


    if errCode == 0:

        threads = []
        conn = phoenixConn()
        cursor = conn.cursor()
        # deleted processing
        try:
            # delete identifier
            def deleteDataIdentifier():
                cmd = "DELETE FROM FHIR247.IDENTIFIER WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            # delete human_name
            def deleteDataHumanName():
                cmd = "DELETE FROM FHIR247.HUMAN_NAME WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            # delete contact_point
            def deleteDataContactPoint():
                cmd = "DELETE FROM FHIR247.CONTACT_POINT WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            # delete address
            def deleteDataAddress():
                cmd = "DELETE FROM FHIR247.ADDRESS WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            # delete attachment
            def deleteDataAttachment():
                cmd = "DELETE FROM FHIR247.ATTACHMENT WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            # delete link
            def deleteDataLink():
                cmd = "DELETE FROM FHIR247.LINK WHERE resource_id = '" + resourceID + "' "
                cursor.execute(cmd)

            # delete person
            def deleteDataPatient():
                cmd = "DELETE FROM FHIR247.PERSON WHERE person_id = '" + resourceID + "' "
                cursor.execute(cmd)

            ###Create thread1
            t = threading.Thread(target=deleteDataIdentifier())
            threads.append(t)

            ###Create thread2
            t = threading.Thread(target=deleteDataHumanName())
            threads.append(t)

            ###Create thread3
            t = threading.Thread(target=deleteDataContactPoint())
            threads.append(t)

            ###Create thread4
            t = threading.Thread(target=deleteDataAddress())
            threads.append(t)

            ###Create thread5
            t = threading.Thread(target=deleteDataAttachment())
            threads.append(t)

            ###Create thread8
            t = threading.Thread(target=deleteDataLink())
            threads.append(t)

            ###Create thread10
            t = threading.Thread(target=deleteDataPatient())
            threads.append(t)

            ###Starting thread
            for t in threads:
                t.start()

            ###Waiting all threads is done
            for t in threads:
                t.join()

            conn.close()
            errCode = 200
            message = "Successful delete data."
            result = {"status": errCode, "message": message}
        except OSError as err:
            errCode = 13002
            message = err

            result = {"status": errCode, "message": message}
    else:
        result = {"status": errCode, "message": message}

    return result
