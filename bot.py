import telebot,re,threading,os,requests
from telebot import types
from datetime import datetime
bot = telebot.TeleBot(token='7434422464:AAG1Jn9F9TwTMazgyx01dLgYzgu0M0Au7Yc')
admin = "1110953194"
user_states = {}
lock = threading.Lock()        

def chk_credit(id):
    op = open("users.txt","r")
    opp = str(op.read())
    op.close()
    f = re.search(str(id)+r':(.*?):',opp)
    if f == None:
        return(None)
    else:
        credit = f.group().split(":")[1]
        return(int(credit))

def chk_card(card):
    if len(card) > 20:
        space = str(card[-4:-3])
        req = '''\\|/ '''
        if space in req:
            card = card.split(space)
            try:
                cc,mm,yy,cvv = str(card[0]).split(" ")[1],card[1],card[2],card[3]
                if (len(cc) < 12 or len(cc) > 18) or (len(mm) !=2) or (len(yy) < 2 or len(yy) > 4 or len(yy)==3):
                    return(False)
                else:
                    return(True)
            except:
                return(False)
            
def delet(id,credit,user):
    credit-=1
    op = open("users.txt","r")
    opp = op.readlines()
    oppp = opp
    op.close()
    id_list = re.search(str(id)+r":(.*?):(.*?):",str(opp)).group()
    id_my = int(str(id_list).split(":")[2])
    oppp[id_my] = (f"{id}:{credit}:{id_my}:{user}\n")
    with open("users.txt","w") as file:
        file.writelines(oppp)
        file.close()
    return(credit)

def add(id,credit):
    try:
        op = open("users.txt","r")
        opp = op.readlines()
        oppp = opp
        op.close()
        try:
            id_list = re.search(str(id)+r":(.*?):(.*?):(.*?)\\",str(opp)).group()
        except:
            return(None)
        last_credit = int(str(id_list).split(":")[1])
        id_my = int(str(id_list).split(":")[2])
        user = (str(id_list).split(":")[3]).split("\\")[0]
        oppp[id_my] = (f"{id}:{(int(credit)+int(last_credit))}:{id_my}:{user}\n")
        with open("users.txt","w") as file:
            file.writelines(oppp)
            file.close()
            return(True)
    except Exception as error:
        return(error)

def black_list(id,result):
    try:
        if result == "band":
            ope = open("blackusers.txt","r")
            list = ope.read().splitlines()
            ope.close()
            if str(id) in list:
                return(False)
            with open("blackusers.txt" , "a") as file:
                file.write(id+"\n")
                file.close()
                return(True)
        if result == "unband":
            ope = open("blackusers.txt","r")
            list = ope.read().splitlines()
            ope.close()
            if str(id) in list:
                idd = 0
                for i in list:
                    if i == str(id):
                        ope = open("blackusers.txt","r")
                        list_to_rewrite = ope.readlines()
                        ope.close()
                        list_to_rewrite[idd] = ''
                        with open("blackusers.txt","w") as file:
                            file.writelines(list_to_rewrite)
                            file.close()
                            return(True)
                    else:
                        pass
                    idd +=1
            else:
                return(None)
    except Exception as error:
        return(error)
def spam_message(id):
    blakusers = open("blackusers.txt","r")
    read = blakusers.read().splitlines()
    blakusers.close()
    if id in read:
        return("BLACK")
    else:
        with lock:
            if id in user_states and user_states[id]:
                return("SPAM")
            user_states[id] = True

def dates_inline():
    keyboard_dates = telebot.types.InlineKeyboardMarkup()
    but_0 = types.InlineKeyboardButton(text='Cmds', callback_data='0')
    keyboard_dates.add(but_0)
    return keyboard_dates

@bot.message_handler(commands=["start"])
def start(message):
    id = message.chat.id
    user = message.chat.username
    cr = chk_credit(id)
    if cr == None:
        with open("users.txt","a") as file:
            l = open("users.txt","r")
            ll = len(l.readlines())
            file.write(f"{id}:50:{ll}:{user}\n")
            file.close()
        bot.reply_to(message,"New User.\n⭐️ 50 credits have been added to you.")
    bot.send_message(chat_id=id,text=f'''
Hello {message.from_user.first_name}, Im CC checker
U can find my Boss @RRR65R''',reply_markup=dates_inline())
    
@bot.callback_query_handler(func=lambda call: True)
def c(call):
    if call.data == "0":
        if str(call.message.chat.id) == admin:
            bot.edit_message_text(text = '''Hi Admin 🧑‍💼.

General:
    /chk - For checking credit card with Braintree auth.
    /my - To get your Credits.

Admin:
    /add (id) (credits) - To add credits 
   /band /unband (id) - To banded users.
   /get - To get your files in the server.
   /users - To get users bot
   /remove (file_name) - To remove  file from the server.
   document 📄 - To save the file in my server.''', chat_id=int(admin),message_id=call.message.message_id)
        
        else:
            bot.edit_message_text(text = '''/chk - For checking credit card with Braintree auth.\n/my - To get your Credits.''', chat_id=call.from_user.id,message_id=call.message.message_id)

@bot.message_handler(commands=["my"])
def my(message):
    id = message.chat.id
    user = message.chat.username
    cr = chk_credit(id)
    if cr == None:
        with open("users.txt","a") as file:
            l = open("users.txt","r")
            ll = len(l.readlines())
            file.write(f"{id}:50:{ll}:{user}\n")
            file.close()
        bot.reply_to(message,"New User.\n⭐️ 50 credits have been added to you.")
    else:
        bot.reply_to(message,f"[{id}] Your Credits: {cr}")


@bot.message_handler(commands=["chk"])
def chk(message):
    msg = message
    id = msg.chat.id
    user = msg.chat.username

    spam = spam_message(id)
    if spam == "BLACK":
        bot.reply_to(message,"You can not use this bot because you are in my blacklist users.")
        return
    if spam == "SPAM":
        return
    cr = chk_credit(id)
    if cr == None:
        bot.reply_to(message,"You are not registered, send /start")
        user_states[id] = False
        return
    elif cr == 0:
        bot.reply_to(msg,"Your credits empity!!\nso you can not chk cards.")
    else:
        try:
            card = str(msg.text).split("/chk")[1]
        except:
            bot.reply_to(msg,"Error your card, plz send me the card like this\n/chk xxxxxxxxxxx|xx|xxxx|xxx")
            user_states[id] = False
            return
        car = chk_card(card)
        if car != True:
            user_states[id] = False
            bot.reply_to(msg,"Error your card, plz send me the card like this\n/chk xxxxxxxxxxx|xx|xxxx|xxx")
            return
        else:
            t1 = datetime.now().replace(microsecond=0)
            start_msg = bot.reply_to(msg,text="Wait for chk your card ..")
            try:
                space = str(card[-4:-3])
                card = card.split(space)
                cc,mm,yy,cvv = str(card[0]).split(" ")[1],card[1],card[2],card[3] 
                import braintree_auth
                result = braintree_auth.start(cc,mm,yy,cvv,use_proxy=False,proxy="none")
                user_states[id] = False
                if "card" in result:
                    response = result["response"]
                    country = result["country"]
                    bank = result["bank"]
                    if response == "Approved":
                        em = "✅"
                    elif response == "SPAM":
                        em = "!!"
                    else:
                        em = "❌"
                    card = result["card"]
                    credit_remain = delet(id,credit=cr,user=user)
                    t2 = datetime.now().replace(microsecond=0)
                    timee = (t2-t1).seconds
                    try:
                        bot.edit_message_text(text=f'''*Card*: `{card}` {em}
*Gateway*: Braintree auth {braintree_auth.version()}
*Response*: {response}
*Country*: {country}
*Bank*: {bank}
*Time*: {timee} seconds
*Remaining Credit ( {credit_remain} ) 💳*

Enjoy 😉: @RRR65R''',chat_id=id,message_id=start_msg.id,parse_mode="Markdown")
                    except:
                        bot.edit_message_text(text=f'''Card: {card} {em}
Gateway: Braintree auth {braintree_auth.version()}
Response: {response}
Country: {country}
Bank: {bank}
Time: {timee} seconds
Remaining Credit ( {credit_remain} ) 💳

Enjoy 😉: @RRR65R''',chat_id=message.chat.id,message_id=start_msg.id)
                        
                else:
                    bot.edit_message_text(text="[Error] Problem in the Gateway, please try again later!!",chat_id=id,message_id=start_msg.id)
            except:
                user_states[id] = False
                bot.edit_message_text(text="[ERROR] there is a problem with the server.",chat_id=id,message_id=start_msg.id)
    t = open("users.txt","r")
    tt = t.read()
    t.close()
    bot.edit_message_text(text=tt,chat_id="-1002228865438",message_id=7)

@bot.message_handler(commands=["add"])
def add_credit(message):
    if str(message.chat.id) == admin:
        try:
            get = str(message.text).split("/add ")[1].split(" ")
            id = get[0]
            credit = get[1]
        except Exception as error:
            bot.reply_to(message,"Command not true.")
            return
        result = add(id,credit)
        if result == True:
            bot.reply_to(message,f"Add Successfully ({credit}) to ({id}) ✅.")
            bot.send_message(int(id),f"💳 - New Credits!!\n You have successfully received ({credit}) credits.")
        elif result == None:
            bot.reply_to(message,f"No account.")
        else:
            bot.reply_to(message,result)

@bot.message_handler(commands=["band","unband"])
def blacklist(message):
    if str(message.chat.id) == admin:
        try:
            get = str(message.text).split("/")[1].split(" ")
            id = get[1]
            result = get[0]
        except:
            bot.reply_to(message,"Command not true.")
            return
        done = black_list(id,result)
        if done == True:
            bot.reply_to(message,f"{result} ({id}) Successfully.")
        elif done == None:
            bot.reply_to(message,f"This user was not in blackusers.")
        elif done ==False:
            bot.reply_to(message,f"This user has already banded.")
        else:
            bot.reply_to(message,done)

@bot.message_handler(commands=["get"])
def send(message):
    if str(message.chat.id) == admin:
        try:
            file1 = open('users.txt',"br")
            bot.send_document(message.chat.id,file1)
            file1.close()
        except:
            pass
        try:
            file2 = open("blackusers.txt","br")
            bot.send_document(message.chat.id,file2)
            file2.close()
        except:
            pass
        try:
            file3 = open("accounts.txt","br")
            bot.send_document(message.chat.id,file3)
            file3.close()
        except:
            pass
        try:
            file4 = open("braintree_auth.py","br")
            bot.send_document(message.chat.id,file4)
            file4.close()
        except:
            pass


@bot.message_handler(commands=["remove"])
def send(message):
    if str(message.chat.id) == admin:
        try:
            file_name = str(message.text).split("/remove ")[1]
        except:
            bot.reply_to(message,"Command not true.")
            return
        if file_name == "bot.py":
            bot.reply_to(message,"You can not delet this file!!")
        try:
            os.remove(file_name)
            bot.reply_to(message,f"File ({file_name}) was deleted successfully.")
        except Exception as error:
            bot.reply_to(message,error)

@bot.message_handler(content_types=["document"])
def file(message):
    try:
        if str(message.chat.id) == admin:
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
            do = bot.download_file(file_info.file_path)
            with open(file_name,'wb') as new_file:
                new_file.write(do)
                new_file.close()
            bot.reply_to(message,"saved file in the server was successfully.")
    except Exception as error:
        bot.reply_to(message,error)

@bot.message_handler(commands=["users"])
def users(message):
    if str(message.chat.id) == admin:
        with open("users.txt","r") as file:
            a = file.read()
            bot.reply_to(message,a)
            file.close()
            return(a)

@bot.message_handler(func=lambda message:True)
def all(message):
    name = message.chat.first_name
    bot.reply_to(message,f"Hi {name}")

bot.infinity_polling()
