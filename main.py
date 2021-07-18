import requests
import sys
import json
import warnings
import csv


if len(sys.argv) != 4:
    print("Syntax: ./main.py <FortiEMSIP> <AdminUsername> <AdminPassword>")
    exit(1)

warnings.filterwarnings("ignore")
FortiEMS = sys.argv[1]
user = sys.argv[2]
apiKey = sys.argv[3]

authBody = {
  "name": user,
  "password": apiKey
}

# Signing into EMS and getting auth cookie
result = requests.post(f'https://{FortiEMS}/api/v1/auth/signin',
                        data=authBody,
                        verify=False)

if result.status_code > 299:
    print(f"Error, got {result.status_code}")
    exit(1)

authCookie = result.cookies

# Get endpoints
print('Getting a list of endpoints')
result = requests.get(f'https://{FortiEMS}/api/v1/endpoints/index?count=100',
                        cookies=authCookie,
                        verify=False)

if result.status_code > 299:
    print(f"Error, got {result.status_code}")
    exit(1)

endpointList = result.json()['data']['endpoints']

# Continue until all endpoints are collected
while len(endpointList) < result.json()['data']['total']:
    result = requests.get(f'https://{FortiEMS}/api/v1/endpoints/index?count=100&offset={len(endpointList)}',
                          cookies=authCookie,
                          verify=False)
    if result.status_code > 299:
        print(f"Error, got {result.status_code}")
        exit(1)
    endpointList.extend(result.json()['data']['endpoints'])
    print(f'Got {len(endpointList)} endpoints')

# Save endpoints into CSV
with open('endpoints.csv', 'w', newline='', encoding='utf-8') as outfile:
    output = csv.writer(outfile, delimiter=';')
    output.writerow(['Endpoint', 'Version'])
    for endpoint in endpointList:
        version = str(endpoint['comparable_fct_version'])
        version = version.replace('00', '.')
        version = '="' + version + '"'
        name = '="' + endpoint['name'] + '"'
        output.writerow([name, version])
