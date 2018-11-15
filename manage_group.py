# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import requests
import json
import xlsxwriter
from csv_header import *
# Constants
GRAPH_URL_PREFIX = 'https://graph.facebook.com/'
FIELDS_CONJ = '?limit=1000&fields='
GROUPS_SUFFIX = '/groups'
GROUP_FIELDS = 'id,name,members,privacy,description,updated_time'
MEMBERS_SUFFIX = '/members'
MEMBER_FIELDS = 'email,name,id'
JSON_KEY_DATA = 'data'
JSON_KEY_PAGING = 'paging'
JSON_KEY_NEXT = 'next'
JSON_KEY_EMAIL = 'email'

# Methods
def getAllGroups(access_token, community_id):
    endpoint  = GRAPH_URL_PREFIX + community_id + GROUPS_SUFFIX + FIELDS_CONJ + GROUP_FIELDS
    return getPagedData(access_token, endpoint, [])

def getAllMembers(access_token, community_id):
    endpoint  = GRAPH_URL_PREFIX + community_id + MEMBERS_SUFFIX + FIELDS_CONJ + MEMBER_FIELDS
    return getPagedData(access_token, endpoint, [])

def getGroupMembers(access_token, group_id):
    endpoint = GRAPH_URL_PREFIX + group_id + MEMBERS_SUFFIX + FIELDS_CONJ + MEMBER_FIELDS
    return getPagedData(access_token, endpoint, [])

def addMemberToGroup(access_token, group_id, email):
    endpoint = GRAPH_URL_PREFIX + group_id + MEMBERS_SUFFIX
    headers = buildHeader(access_token)
    data = {JSON_KEY_EMAIL: email}
    result = requests.post(GRAPH_URL_PREFIX + group_id + MEMBERS_SUFFIX, headers=headers, data=data)
    return json.loads(result.text, result.encoding)

def removeMemberFromGroup(access_token, group_id, email):
    endpoint = GRAPH_URL_PREFIX + group_id + MEMBERS_SUFFIX
    headers = buildHeader(access_token)
    data = {JSON_KEY_EMAIL: email}
    result = requests.delete(GRAPH_URL_PREFIX + group_id + MEMBERS_SUFFIX, headers=headers, data=data)
    return json.loads(result.text, result.encoding)

def createNewGroup(access_token, name, description, privacy, administrator=None):
    headers = buildHeader(access_token)
    data = {
        "name": name,
        "description": description,
        "privacy": privacy,
        "admin": administrator
    }
    result = requests.post(GRAPH_URL_PREFIX + community_id + GROUPS_SUFFIX, headers=headers, data=data)
    return json.loads(result.text, result.encoding)

def getPagedData(access_token, endpoint, data):
    headers = buildHeader(access_token)
    next = endpoint
    while next:
        result = requests.get(next, headers=headers)
        result_json = json.loads(result.text)
        json_keys = result_json.keys()
        if JSON_KEY_DATA in json_keys and len(result_json[JSON_KEY_DATA]):
            data.extend(result_json[JSON_KEY_DATA])
        if JSON_KEY_PAGING in json_keys and JSON_KEY_NEXT in result_json[JSON_KEY_PAGING]:
            next = result_json[JSON_KEY_PAGING][JSON_KEY_NEXT]
        else: next = False
    return data

def getUserIDFromEmail(access_token, community_id, email):
    members = getAllMembers(access_token, community_id)
    for member in members:
        if "email" in member and member["email"] == email:
            return member["id"]
    return None

def buildHeader(access_token):
    return {'Authorization': 'Bearer ' + access_token}

def exportGroupMemgers(filename, access_token, group_id):
    data = getGroupMembers(access_token, group_id)
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    worksheet.write_row(row, col, tuple(GROUP_HEADER))
    for i in data:
        row += 1
        row_data = [i['name'], i['email'], i['id']]
        worksheet.write_row(row, col, tuple(row_data))
    workbook.close()

# Example of creating a CSV of group members
access_token = ''
community_id = ''
group_id = ''
exportGroupMemgers('FIS.xlsx', access_token, group_id)
