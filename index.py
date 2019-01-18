import xml.etree.ElementTree as ET
import requests
import re
import getpass
import os
import sys

session = requests.Session()

# Setting ASP.NET_SessionId and WS.AuthCookie for use to retrieve rooster xml
def getCookies(username, password):

  headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://metime.mcdonalds.com.au/Account?ContentSuffix=Home&returnUrl=%2F%23%2FHome',
    'AppName': 'learningCloud',
    'Content-Type': 'application/json;charset=utf-8',
    'Connection': 'keep-alive',
  }

  data = '{"loginDataJson":"{\\"UserName\\":\\"'+username+'\\",\\"Password\\":\\"'+password+'\\"}","environmentDataJson":"{}"}'

  session.post(
    'https://metime.mcdonalds.com.au/CloudAPI/AccountV1/Login', 
    headers=headers, 
    data=data
  )

def getRoster():

  headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://metime.mcdonalds.com.au/',
    'BrowserSize': 'sm',
    'IsCordovaApp': 'false',
    'AppName': 'learningCloud',
    'Connection': 'keep-alive',
  }

  shiftList = []

  response = session.post('https://metime.mcdonalds.com.au/CloudAPI/RostersV1/GetUserRosters', headers=headers)
  # print(response.json()['Data'])
  # print(shifts)
  for roster in response.json()['Data']:
    for shift in ET.fromstring(roster['RosterXml']):
        shiftList.append(Shift(shift.attrib))

  return(shiftList)

class Shift:

  def __init__(self, attrib):
    self.metimeID = attrib['emp_metime_num']
    # Convert date format yyyymmdd to dd/mm/yyyy
    self.date = strDate(attrib['emp_rost_date'])
    self.hours = attrib['emp_rost_hrs']
    self.start = attrib['emp_rost_time_str']
    self.end = attrib['emp_rost_time_end']
    self.storeID = attrib['emp_hme_str_no']
    self.station = attrib['emp_rost_stn']
    # The date that the roster was released until
    self.rosterEnd = attrib['emp_wk_end_dt']
    self.country = attrib['ctry_code']
    self.shiftRaw = attrib

  def prettyPrint(self):
    indent = 0
    epicPrint('### {} ###$$', self.date, indent, color='7')
    indent += 1
    epicPrint('Start:$$ {}', self.start, indent)
    epicPrint('End:$$ {}', self.end, indent)
    epicPrint('Hours:$$ {}', self.hours, indent)
    epicPrint('Station:$$ {}', self.station, indent)

  def html(self):
    shiftData = [("Start", self.start), ("Finish", self.end), ("Hours", self.hours), ("Station", self.station)]
    string = '<div class="shift">\n\n\t<b class="date">{date}</b>\n\t'.format(date=self.date) + ''.join(['<b class="title">{title}: </b><info class="{title}">{info}</info>\n\t'.format(title=data[0], info=data[1]) for data in shiftData]) + "\n</div>\n"
    return(string)

def strDate(date):
  return(re.sub(r'(\d{4})(\d{2})(\d{2})', r'\3/\2/\1', date))

def epicPrint(string, var, indent, tabstop='  ', color='82'):
  string = string.replace('$$', '\033[0m')
  print('\033[38;5;'+color+'m', ''.join([tabstop for i in range(indent)]), string.format(var))

def getVariable(envName, argPos, inpMsg, isPwd=False):
  try:
    variable = os.environ[envName]
  except KeyError:
    try:
      variable = sys.argv[argPos]
    except IndexError:
      variable = getpass.getpass(inpMsg) if isPwd else input(inpMsg)
  return(variable)

## Main ##
if __name__ is '__main__':
    username = getVariable('metimeID', 1, 'Metime ID: ')
    password = getVariable('metimePwd', 2, 'Metime Password: ', isPwd=True)
    getCookies(username, password)
    for shift in getRoster():
      # print(shift.html())
      shift.prettyPrint()
