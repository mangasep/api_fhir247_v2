import ruamel.yaml
import sys
from pathlib import Path
from ruamel.yaml import YAML

yaml = ruamel.yaml.YAML()


#Load the yaml files
# with open('administration/patient.yaml') as fp:
#     patient = yaml.load(fp)
# with open('administration/person.yaml') as fp:
#     person = yaml.load(fp)
# with open('reference/administrative-gender.yaml') as fp:
#     administrativeGender = yaml.load(fp)
#
# #Add the resources from test2.yaml to test1.yaml resources
# for i in person['paths']:
#     person['paths'][i]
#     patient['paths'].update(
#         {i:person['paths'][i]}
#     )
# for i in person['components']['schemas']:
#     person['components']['schemas'][i]
#     patient['components']['schemas'].update(
#         {i:person['components']['schemas'][i]}
#     )

list_of_filenames = ['administration/patient.yaml', 'administration/person.yaml']
# for path in list_of_filenames:
#     with open(path) as fp:
#         data = yaml.load(fp)
#         for i in data['paths']:
#
#
#         yaml.dump_all(data, open('api.yaml', 'w'))
#         f = open("api.yaml", "r")
#         print(f.read())

# with open('api.yaml') as fp:
#     administrativeGender = yaml.load(fp)

with YAML(output=sys.stdout) as yaml:
    yaml.explicit_start = True
    for path in list_of_filenames:
        with open(path) as fp:
            data = yaml.load(fp)

yaml.dump(data, open('api.yaml', 'w'))
f = open("api.yaml", "r")
print(f.read())


#create a new file with merged yaml
# yaml.dump_all(api, open('api.yaml', 'w'))
#
# f = open("api.yaml", "r")
# print(f.read())