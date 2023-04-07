import requests as web_request
import regex as re
import json_handler.handler as handler
import time

#Time in senconds between requests
jitter = 3

#Time in seconds used for timeouts
timeoutTime = 4

#Time in seconds used for false positives
falsePositive = 30

#request limit. If this number of requests fail, the program stops. 
limite = 15

def correoRegEx(text):
    """
    It detects the writing pattern of an email using regular expresions. The following combinations are detected: 
    first name and second name, second name and first name, only first name, only second name.
    text: email used to extract the pattern
    return: a list: [prefix, if it uses the first name, expresions between names, if it uses the second name, sufix, domain]
    """
    correoCompleto = re.match(r'(.*)(name)(.*)(lname)(.*)(@.*)', text)
    if(correoCompleto):
        list = correoCompleto.groups()
        pattern = [list[0], True, list[2], True, list[4], list[5], False]
        return pattern

    #Sometimes, second name appears before
    apellidoNombre = re.match(r'(.*)(lname)(.*)(name)(.*)(@.*)', text)
    if(apellidoNombre):
        list = apellidoNombre.groups()
        print(list)
        pattern = [list[0], True, list[2], True, list[4], list[5], True]
        return pattern
    
    soloApellido = re.match(r'(.*)(lname)(.*)(@.*)', text)
    if(soloApellido):
        list = soloApellido.groups()
        print(list)
        pattern = ["", False, list[0], True, list[2], list[3], False]
        return pattern

    solonombre = re.match(r'(.*)(name)(.*)(@.*)', text)
    if(solonombre):
        list = solonombre.groups()
        print(list)
        pattern = [list[0], True, list[2], False, "", list[3], False]
        return pattern

def emailBuilder(domain, firstname = "", secondname = "", pattern = ["", True, ".", True, "", "", False]):
    """
    It builds email following a stablished pattern. It checks if the first name or the second name are used. 
    firstname: the fisrt name of the person, "" as default value. 
    secondname: the second name of the person, "" as default value. 
    return: new email. 
    """
    pattern_string = ""
    # pattern to use while building emails.
    if(pattern[1] and pattern[3] and pattern[6]):
        pattern_string = pattern[0] + secondname + pattern[2] + firstname + pattern[4] + pattern[5]
    
    elif(pattern[1] and pattern[3] and not pattern[6]):
        pattern_string = pattern[0] + firstname + pattern[2] + secondname + pattern[4] + pattern[5]

    elif(pattern[1] and not pattern[3]):
        pattern_string = pattern[0] + firstname + pattern[2] + pattern[4] + pattern[5]
    
    elif(not pattern[1] and pattern[3]):
        pattern_string = pattern[0] + pattern[2] + secondname + pattern[4] + pattern[5]
         
    else: pattern_string = pattern[0] + pattern[2] + pattern[4] + pattern[5]

    return pattern_string.lower()

def validator(employees, domain, pattern):
    """
    Iterate through and validate each email user using gmail and office validator.
    employees: a list of employees, each employees must have trivial information (first and second name)
    pattern: pattern of the email
    return: List of employees, each ecmployee is a dictionary with the following fields:
    'fname' 'lname' 'position' ['email']
    """
    validEmployees = []
    contador = 0
    contadorFalsoPositivo = 0
    ms_url = 'https://login.microsoftonline.com/common/GetCredentialType'
    for employee in employees:
        if("email" in employee):
                email_line=employee["username"]
        else:
                email_line = emailBuilder(domain, employee["fname"],employee["lname"], pattern)
        s = web_request.session()
        email_line_ = email_line.split()
        email = ' '.join(email_line_)
        body = '{"Username":"%s"}' % email
        request = web_request.post(ms_url, data=body.encode('utf-8'), timeout=timeoutTime)
        response = request.text

        #testing all valid codes
        valid_response = re.search('"IfExistsResult":0,', response)
        valid_response5 = re.search('"IfExistsResult":5,', response)
        valid_response6 = re.search('"IfExistsResult":6,', response)
        invalid_response = re.search('"IfExistsResult":1,', response)
        throttling = re.search('"ThrottleStatus":1', response)
        #in case of error we try to validate through mail.google.com
        if invalid_response:
            url = "https://mail.google.com/mail/gxlu?email=" + email + "&zx=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            request = web_request.get(url, timeout=timeoutTime)
            cook_check = str(request.cookies.get_dict())
            valid_response = re.search("'COMPASS':", cook_check)
            if valid_response:
                validuser = {
                'fname' : employee["fname"],
                'lname' : employee["lname"],
                'position' : employee["position"],
                'email' : email_line,
                'FalsePositive': "No"
                }
                validEmployees.append(validuser)
                print("[*] Valid Google email: " + email_line)
                contador = 0
            else:
                contador +=1
                if (contador > limite): break
        elif (valid_response or valid_response5 or valid_response6):
            falsoPositivo = "No"
            if(throttling):
                 falsoPositivo = "Might be"
                 
            validuser = {
                'fname' : employee["fname"],
                'lname' : employee["lname"],
                'position' : employee["position"],
                'email' : email_line,
                'FalsePositive': falsoPositivo
            }

            if(throttling):
             print("Results suggest O365 is responding with false positives.")
             contadorFalsoPositivo +=1
             if(contadorFalsoPositivo > 3):
                  print("Sleeping for 10 minutes")
                  time.sleep(600)
                  contadorFalsoPositivo = 0
             print("Sleeping for 20 seconds before trying again.")
             time.sleep(falsePositive)
            validEmployees.append(validuser)
            print("[*] Valid o365 email: " + email_line)
            contador = 0
        time.sleep(jitter)
        
    return validEmployees

def onlyGmail(employees, domain, pattern):
    """
    Iterate through and validate each email user using gmail validator.
    employees: a list of employees, each employees must have trivial information (first and second name)
    pattern: pattern of the email
    return: List of employees, each ecmployee is a dictionary with the following fields:
    'fname' 'lname' 'position' ['email']
    """
    validEmployees = []
    contador = 0
    for employee in employees:
        if("email" in employee):
            email_line=employee["username"]
        else:
            email_line = emailBuilder(domain, employee["fname"],employee["lname"], pattern)
        s = web_request.session() 
        email_line_ = email_line.split()
        email = ' '.join(email_line_)
        # print('[+] Validating email: ' + email_line + '...')
        url = "https://mail.google.com/mail/gxlu?email=" + email + "&zx=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        request = web_request.get(url, timeout=timeoutTime)
        cook_check = str(request.cookies.get_dict())
        valid_response = re.search("'COMPASS':", cook_check)
        if valid_response:
            validuser = {
            'fname' : employee["fname"],
            'lname' : employee["lname"],
            'position' : employee["position"],
            'email' : email_line
            }
            validEmployees.append(validuser)
            print("[*] Valid Google email: " + email_line)
            contador = 0
        else:
             contador +=1
             if (contador > limite): break
        time.sleep(jitter)
    return validEmployees



def onlyOffice(employees, domain, pattern):
    """
    Iterate through and validate each email user using office validator.
    employees: a list of employees, each employees must have trivial information (first and second name)
    pattern: pattern of the email
    return: List of employees, each ecmployee is a dictionary with the following fields:
    'fname' 'lname' 'position' ['email']
    """
    validEmployees = []
    contador = 0
    contadorFalsoPositivo=0
    ms_url = 'https://login.microsoftonline.com/common/GetCredentialType'
    for employee in employees:
        if("email" in employee):
                email_line=employee["username"]
        else:
                email_line = emailBuilder(domain, employee["fname"],employee["lname"], pattern)
        s = web_request.session()
        email_line_ = email_line.split()
        email = ' '.join(email_line_)
        body = '{"Username":"%s"}' % email
        request = web_request.post(ms_url, data=body.encode('utf-8'), timeout=timeoutTime)
        response = request.text

        #testing all valid codes
        valid_response = re.search('"IfExistsResult":0,', response)
        valid_response5 = re.search('"IfExistsResult":5,', response)
        valid_response6 = re.search('"IfExistsResult":6,', response)
        invalid_response = re.search('"IfExistsResult":1,', response)
        throttling = re.search('"ThrottleStatus":1', response)
        if(invalid_response): 
            contador +=1
            if (contador > limite): break
        elif (valid_response or valid_response5 or valid_response6):
            falsoPositivo = "No"
            if(throttling):
                 falsoPositivo = "Might be"
            validuser = {
                'fname' : employee["fname"],
                'lname' : employee["lname"],
                'position' : employee["position"],
                'email' : email_line,
                'FalsePositive': falsoPositivo
            }

            validEmployees.append(validuser)
            print("[*] Valid o365 email: " + email_line)
            contador = 0
        if(throttling):
             print("Results suggest O365 is responding with false positives.")
             contadorFalsoPositivo +=1
             if(contadorFalsoPositivo > 3):
                  print("Sleeping for 10 minutes")
                  time.sleep(600)
                  contadorFalsoPositivo = 0
             print("Sleeping for 20 seconds before trying again.")
             time.sleep(falsePositive)
        time.sleep(jitter)
    return validEmployees


def start(input_filename):
    # meta, input, output = handler.read_json(input_filename)
    meta, input, output = handler.read_json(input_filename)

    pattern = correoRegEx(input["domain"])

    # Estructura de control que elige si utilizar el validador de office o de gmail
    validEmployees = []
    if(input["mail_provider"] == "google"):
        print("[+] Validating emails against Google")
        validEmployees = onlyGmail(input["employees"], input['domain'], pattern)
    elif(input["mail_provider"] == "o365"):
        print("[+] Validating emails against O365")
        validEmployees = onlyOffice(input["employees"], input['domain'], pattern)
    else:
        print("[+] Validating emails against Google and O365")
        validEmployees = validator(input["employees"], input['domain'], pattern)

    output["employees"] = validEmployees
    handler.write_json(input_filename, meta, input, output)
    print("[+] Done! Valid emails saved in " + input_filename)

if __name__ == '__main__':
    fileName ="data_scrapper.json"
    start(fileName)