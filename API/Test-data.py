import requests

url = "http://0.0.0.0:5247/v2/Patient"

payload = "{\n\t\"identifier\": [\n\t\t{\n\t\t\t\"use\": \"usual\",\n\t\t\t\"type\": {\n\t\t\t\t\"text\": \"nsstring\",\n\t\t\t\t\"coding\": [\n\t\t\t\t\t{\n\t\t\t\t\t\t\"code\": \"string\",\n\t\t\t\t\t\t\"system\": \"string\",\n\t\t\t\t\t\t\"display\": \"string\"\n\t\t\t\t\t}\n\t\t\t\t]\n\t\t\t},\n\t\t\t\"system\": \"string\",\n\t\t\t\"value\": \"string\"\n\t\t}\n\t],\n\t\"active\": false,\n\t\"name\": [\n\t\t{\n\t\t\t\"use\": \"usual\",\n\t\t\t\"text\": \"Joko\",\n\t\t\t\"family\": \"string\",\n\t\t\t\"given\": [\n\t\t\t\t\"string\"\n\t\t\t],\n\t\t\t\"prefix\": [\n\t\t\t\t\"Mr\"\n\t\t\t],\n\t\t\t\"suffix\": [\n\t\t\t\t\"SH\"\n\t\t\t]\n\t\t}\n\t],\n\t\"telecom\": [\n\t\t{\n\t\t\t\"system\": \"phone\",\n\t\t\t\"value\": \"08977352\",\n\t\t\t\"use\": \"home\",\n\t\t\t\"rank\": 0\n\t\t}\n\t],\n\t\"gender\": \"male\",\n\t\"birthDate\": \"2019-04-05\",\n\t\"deceasedBoolean\": true,\n\t\"deceasedDateTime\": \"2019-06-18T02:07:28.946Z\",\n\t\"address\": [\n\t\t{\n\t\t\t\"use\": \"home\",\n\t\t\t\"type\": \"postal\",\n\t\t\t\"text\": \"string\",\n\t\t\t\"line\": [\n\t\t\t\t\"string\"\n\t\t\t],\n\t\t\t\"city\": \"Gondokusuman\",\n\t\t\t\"district\": \"Daerah Istimewa Yogyakarta\",\n\t\t\t\"state\": \"string\",\n\t\t\t\"postalCode\": \"string\",\n\t\t\t\"country\": \"string\"\n\t\t}\n\t],\n\t\"maritalStatus\": {\n\t\t\"text\": \"string\",\n\t\t\"coding\": [\n\t\t\t{\n\t\t\t\t\"code\": \"string\",\n\t\t\t\t\"system\": \"string\",\n\t\t\t\t\"display\": \"string\"\n\t\t\t}\n\t\t]\n\t},\n\t\"multipleBirthBoolean\": true,\n\t\"multipleBirthInteger\": 0,\n\t\"photo\": [\n\t\t{\n\t\t\t\"contentType\": \"string\",\n\t\t\t\"language\": \"string\",\n\t\t\t\"data\": \"string\",\n\t\t\t\"url\": \"string\",\n\t\t\t\"size\": \"string\",\n\t\t\t\"hash\": \"string\",\n\t\t\t\"title\": \"string\"\n\t\t}\n\t],\n\t\"contact\": [\n\t\t{\n\t\t\t\"relationship\": {\n\t\t\t\t\"text\": \"Y\",\n\t\t\t\t\"coding\": [\n\t\t\t\t\t{\n\t\t\t\t\t\t\"code\": \"string\",\n\t\t\t\t\t\t\"system\": \"string\",\n\t\t\t\t\t\t\"display\": \"string\"\n\t\t\t\t\t}\n\t\t\t\t]\n\t\t\t},\n\t\t\t\"name\": {\n\t\t\t\t\"use\": \"usual\",\n\t\t\t\t\"text\": \"Nugroho\",\n\t\t\t\t\"family\": \"string\",\n\t\t\t\t\"given\": [\n\t\t\t\t\t\"string\"\n\t\t\t\t],\n\t\t\t\t\"prefix\": [\n\t\t\t\t\t\"string\"\n\t\t\t\t],\n\t\t\t\t\"suffix\": [\n\t\t\t\t\t\"string\"\n\t\t\t\t]\n\t\t\t},\n\t\t\t\"telecom\": [\n\t\t\t\t{\n\t\t\t\t\t\"system\": \"phone\",\n\t\t\t\t\t\"value\": \"0872412\",\n\t\t\t\t\t\"use\": \"home\",\n\t\t\t\t\t\"rank\": 0\n\t\t\t\t}\n\t\t\t],\n\t\t\t\"address\": {\n\t\t\t\t\"use\": \"home\",\n\t\t\t\t\"type\": \"postal\",\n\t\t\t\t\"text\": \"string\",\n\t\t\t\t\"line\": [\n\t\t\t\t\t\"string\"\n\t\t\t\t],\n\t\t\t\t\"city\": \"Babarsari\",\n\t\t\t\t\"district\": \"Daerah Istimewa Yogyakarta\",\n\t\t\t\t\"state\": \"string\",\n\t\t\t\t\"postalCode\": \"string\",\n\t\t\t\t\"country\": \"string\"\n\t\t\t},\n\t\t\t\"gender\": \"female\",\n\t\t\t\"organization\": \"string\"\n\t\t}\n\t],\n\t\"communication\": [\n\t\t{\n\t\t\t\"language\": {\n\t\t\t\t\"text\": \"English\",\n\t\t\t\t\"coding\": [\n\t\t\t\t\t{\n\t\t\t\t\t\t\"code\": \"string\",\n\t\t\t\t\t\t\"system\": \"string\",\n\t\t\t\t\t\t\"display\": \"string\"\n\t\t\t\t\t}\n\t\t\t\t]\n\t\t\t},\n\t\t\t\"preferred\": true\n\t\t}\n\t],\n\t\"generalPractitioner\": [\n\t\t{\n\t\t\t\"reference\": \"Organization/1234\"\n\t\t}\n\t],\n\t\"managingOrganization\": \n\t\t{\n\t\t\"reference\": \"Organization/123\"\n\t},\n\t\"link\": [\n\t\t{\n\t\t\t\"other\": {\n\t\t\t\t\"reference\": \"Organization/123\"\n\t\t\t},\n\t\t\t\"type\": \"oi\"\n\t\t}\n\t]\n}"
headers = {'content-type': 'application/json'}

i = 1
while i < 500:
    response = requests.request("POST", url, data=payload, headers=headers)
    i+=1

    print(i)

#print(response.text)