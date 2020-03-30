from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from pylibsimba import get_simba_instance, util
from pylibsimba.base.simba_base import SimbaBase
from pylibsimba.pages import PagedResponse
from pylibsimba.wallet import Wallet
import pickle
from eth_utils import to_bytes
from eth_abi import decode_abi, decode_single
import itertools 
from waste2currency.models import Customer,Waste

def home(request):
    if(request.session.has_key('name')):
        return render(request,'profile.html',{'name':request.session['name'],'email':request.session['email'],'mno':request.session['phone'],'address':request.session['address'],'balance':'Check Balance'})
    
    return render(request,'home.html')



def login(request):

    username = request.POST['email']
    pwd = request.POST['pwd']
    seed = username+pwd
    wallet = Wallet(None)
    wallet.generate_wallet(seed)
    addr = wallet.get_address()
    
    q = Customer.objects.filter(address=addr)


    
    if(len(q)==0):
        return HttpResponse("Login Unsuccessful Wallet not found")

    request.session['name'] = q[0].name
    request.session['phone'] = q[0].phone
    request.session['email'] = q[0].email
    request.session['pwd'] = q[0].password
    request.session['address'] = q[0].address
	
    return render(request,'profile.html',{'name':request.session['name'],'email':request.session['email'],'mno':request.session['phone'],'address':request.session['address'],'balance':"Check Balance"})


    

def signup(request):
	return render(request,'Signup.html');

def register(request):

    Name = request.POST['name']
    Mno = request.POST['phone']
    email = request.POST['email']
    pwd = request.POST['pwd']
    seed = email+pwd
    wallet = Wallet(None)
    wallet.generate_wallet(seed)
    addr = wallet.get_address()

    c = Customer(address = addr,name=Name,phone=Mno,email=email,password = pwd,Ecoins=1000,Fcoins=1000)


    l = len(Customer.objects.filter(address=addr))
    if l != 0 :
        return HttpResponse("Signup UnSuccessful user already exists")

    c.save()

    simba = get_simba_instance('https://api.simbachain.com/v1/w2c2/',wallet,'9bfc30e1f72bab8ed718176a64f47cb0f32123c00479552bd068578265ed406c'
,'')
    #with open('wallet.pkl','wb') as output:
        #pickle.dump(wallet,output,pickle.HIGHEST_PROTOCOL)
    #with open('simba.pkl','wb') as output:
        #pickle.dump(simba,output,pickle.HIGHEST_PROTOCOL)


    method_params = { 'name':Name , 'mno':Mno , 'addr':addr}
    resp = simba.call_method('CreateEntity',method_params)
    try:
        final_resp = simba.wait_for_success_or_error(resp.transaction_id)
        print("Successful? {}".format(final_resp))

    except Exception as e1:
        print("Failure! {}".format(e1))

    transaction_id = resp.transaction_id

    txn = simba.get_transaction(transaction_id)
    encoded = to_bytes(hexstr=txn['receipt']['logs'][0]['data'])

    decoded = decode_abi(['int'], encoded)
    print(decoded)
    if(decoded[0]==1):
        request.session['name'] = Name
        request.session['phone'] = Mno
        request.session['email'] = email
        request.session['pwd'] = pwd  
        request.session['address'] = addr

        return render(request,'profile.html',{'name':request.session['name'],'email':request.session['email'],'mno':request.session['phone'],'address':request.session['address'] , 'balance':"Check Balance"})




def logout(request):
   try:
        del request.session['name']
        del request.session['phone']
        del request.session['email']
        del request.session['pwd']  
        del request.session['address']

   except:
      pass
   return render(request,'home.html')



def balance(request):

    username = request.session['email']
    pwd = request.session['pwd']
    seed = username+pwd
    wallet = Wallet(None)
    wallet.generate_wallet(seed)
    addr = wallet.get_address()
    simba = get_simba_instance('https://api.simbachain.com/v1/w2c2/',wallet,'9bfc30e1f72bab8ed718176a64f47cb0f32123c00479552bd068578265ed406c'
,'')

    method_params = { 'addr':addr}
    resp = simba.call_method('getBalance',method_params)
    try:
        final_resp = simba.wait_for_success_or_error(resp.transaction_id)
        print("Successful? {}".format(final_resp))

    except Exception as e1:
        print("Failure! {}".format(e1))

    transaction_id = resp.transaction_id

    txn = simba.get_transaction(transaction_id)
    encoded = to_bytes(hexstr=txn['receipt']['logs'][0]['data'])

    decoded = decode_abi(['int','int','int'], encoded)

    if(decoded[2]==0):
        return render(request,'profile.html',{'name':request.session['name'],'email':request.session['email'],'mno':request.session['phone'],'address':request.session['address'],'balance':'Check Balance Failed'})

    b = str(decoded[0])+" Ecoins and "+str(decoded[1])+" Fcoins"

    return render(request,'profile.html',{'name':request.session['name'],'email':request.session['email'],'mno':request.session['phone'],'address':request.session['address'],'balance':b})


def WasteForm(request):

    return render(request,'form_waste.html')


def CreateWaste(request):
    uuid = request.POST['uuid']
    wtype = request.POST['type']
    weight = request.POST['weight']

    username = request.session['email']
    pwd = request.session['pwd']
    seed = username+pwd

    wallet = Wallet(None)
    wallet.generate_wallet(seed)
    addr = wallet.get_address()

    c = Waste(uuid = uuid,wtype=wtype,weight = weight,Createdby = addr,Ownedby = addr)

    l = len(Waste.objects.filter(uuid=uuid))

    if l != 0 :
        return HttpResponse("UUID already exists")
    c.save()

    simba = get_simba_instance('https://api.simbachain.com/v1/w2c2/',wallet,'9bfc30e1f72bab8ed718176a64f47cb0f32123c00479552bd068578265ed406c'
,'')

    if wtype == 'Energy':
        wtype = 0
    elif wtype == "Fertilizer":
        wtype = 1


    method_params = { 'uuid':uuid ,'wtype':wtype,'weight':weight,'addr':addr }
    resp = simba.call_method('CreateWaste',method_params)
    try:
        final_resp = simba.wait_for_success_or_error(resp.transaction_id)
        print("Successful? {}".format(final_resp))

    except Exception as e1:
        print("Failure! {}".format(e1))

    transaction_id = resp.transaction_id

    txn = simba.get_transaction(transaction_id)
    encoded = to_bytes(hexstr=txn['receipt']['logs'][0]['data'])
    decoded = decode_abi(['int'], encoded)

    if(decoded[0]==1):
        return render(request,'profile.html',{'name':request.session['name'],'email':request.session['email'],'mno':request.session['phone'],'address':request.session['address'],'balance':'Check Balance'})
    else:
        return HttpResponse("UUID already exists") 


def RequestForm(request):

    return render(request,'request_form.html')


def SendRequest(request):
    uuid = request.POST['uuid']
    to = request.POST['to']
    username = request.session['email']
    pwd = request.session['pwd']
    seed = username+pwd
    wallet = Wallet(None)
    wallet.generate_wallet(seed)
    addr = wallet.get_address()

    l = len(Waste.objects.filter(uuid=uuid))

    if l == 0 :
        return HttpResponse("UUID does not exists")

    l = len(Customer.objects.filter(address=to))

    if l==0 :
        return HttpResponse("Destination address does not exist")


    simba = get_simba_instance('https://api.simbachain.com/v1/w2c2/',wallet,'9bfc30e1f72bab8ed718176a64f47cb0f32123c00479552bd068578265ed406c','')

    method_params = { 'to':to ,'uuid':uuid,'addr':addr }
    resp = simba.call_method('SendRequest',method_params)
    try:
        final_resp = simba.wait_for_success_or_error(resp.transaction_id)
        print("Successful? {}".format(final_resp))

    except Exception as e1:
        print("Failure! {}".format(e1))

    transaction_id = resp.transaction_id

    txn = simba.get_transaction(transaction_id)
    encoded = to_bytes(hexstr=txn['receipt']['logs'][0]['data'])
    decoded = decode_abi(['int'], encoded)

    if(decoded[0]==1):
        return render(request,'profile.html',{'name':request.session['name'],'email':request.session['email'],'mno':request.session['phone'],'address':request.session['address'],'balance':'Check Balance'})
    else:
        return HttpResponse("UUID does not belong to you") 


def AcceptForm(request):
    return render(request,'accept_form.html')

def AcceptRequest(request):

    uuid = request.POST['uuid']
    frm = request.POST['from']
    username = request.session['email']
    pwd = request.session['pwd']
    seed = username+pwd
    wallet = Wallet(None)
    wallet.generate_wallet(seed)
    addr = wallet.get_address()

    l = len(Waste.objects.filter(uuid=uuid))

    if l == 0 :
        return HttpResponse("UUID does not exists")

    l = len(Customer.objects.filter(address=frm))

    if l==0 :
        return HttpResponse("Address does not exist")

    w = (Waste.objects.filter(uuid=uuid))[0]


    simba = get_simba_instance('https://api.simbachain.com/v1/w2c2/',wallet,'9bfc30e1f72bab8ed718176a64f47cb0f32123c00479552bd068578265ed406c','')

    method_params = {'uuid':uuid,'addr':addr }

    resp = simba.call_method('AcceptRequest',method_params)
    try:
        final_resp = simba.wait_for_success_or_error(resp.transaction_id)
        print("Successful? {}".format(final_resp))

    except Exception as e1:
        print("Failure! {}".format(e1))

    transaction_id = resp.transaction_id

    txn = simba.get_transaction(transaction_id)
    encoded = to_bytes(hexstr=txn['receipt']['logs'][0]['data'])
    decoded = decode_abi(['int'], encoded)

    if(decoded[0]==1):
        w.Ownedby = addr
        w.save()
        return render(request,'profile.html',{'name':request.session['name'],'email':request.session['email'],'mno':request.session['phone'],'address':request.session['address'],'balance':'Check Balance'})
    elif(decoded[0]==-1):
        return HttpResponse("No Request Received")
    elif(decoded[0]==0):
        return HttpResponse("Insufficient Balance") 


def transactions(request):

    username = request.session['email']
    password = request.session['pwd']
    seed = username+password
    wallet = Wallet(None)
    wallet.generate_wallet(seed)
    addr = wallet.get_address()
    simba = get_simba_instance('https://api.simbachain.com/v1/w2c2/',wallet,'9bfc30e1f72bab8ed718176a64f47cb0f32123c00479552bd068578265ed406c','')

    method_params = {'addr':addr}
    result_pages = simba.get_method_transactions('CreateWaste', method_params)

    res = result_pages.data()
    timestamp = []
    uuid = []
    wtype = []
    weight = []
    status = []

    for t in res:
        param = t['payload']['inputs']
        if( param['addr'] == addr ):
            timestamp.append(t['timestamp'])
            uuid.append(param['uuid'])
            #wtype.append(param['wtype'])
            if (param['wtype']=='0'):
                wtype.append('Energy')
            elif (param['wtype']=='1'):
                wtype.append('Fertilizer')
            weight.append(param['weight'])

            data = t['receipt']['logs'][0]['data']
            encoded = to_bytes(hexstr=data)
            decoded = decode_abi(['int'], encoded)
            if(decoded[0]==1):
                status.append("Successful")
            elif(decoded[0]==0):
                status.append("Failed")

    row1 = zip(timestamp, uuid, wtype,weight,status)


    result_pages = simba.get_method_transactions('SendRequest', method_params)

    res = result_pages.data()
    timestamp = []
    to = []
    uuid = []
    wtype = []
    weight = []
    status = []

    for t in res:

        param = t['payload']['inputs']
        if(param['addr']==addr):
            timestamp.append(t['timestamp'])
            to.append(param['to'])
            uuid.append(param['uuid'])
            w = (Waste.objects.filter(uuid = param['uuid']))[0]
            wtype.append(w.wtype)
            weight.append(w.weight)
            data = t['receipt']['logs'][0]['data']
            encoded = to_bytes(hexstr=data)
            decoded = decode_abi(['int'], encoded)
            if(decoded[0]==1):
                status.append("Successful")
            elif(decoded[0]==0):
                status.append("Failed")

    row2 = zip(timestamp,uuid,to,wtype,weight,status)



    result_pages = simba.get_method_transactions('AcceptRequest', method_params)

    res = result_pages.data()
    timestamp = []
    uuid = []
    wtype = []
    weight = []
    status = []

    for t in res:

        param = t['payload']['inputs']
        if(param['addr']==addr):
            timestamp.append(t['timestamp'])
            uuid.append(param['uuid'])
            w = (Waste.objects.filter(uuid = param['uuid']))[0]
            wtype.append(w.wtype)
            weight.append(w.weight)
            data = t['receipt']['logs'][0]['data']
            encoded = to_bytes(hexstr=data)
            decoded = decode_abi(['int'], encoded)
            if(decoded[0]==1):
                status.append("Successful")
            elif(decoded[0]==0):
                status.append("Failed")

    row3 = zip(timestamp,uuid,wtype,weight,status)


    return render(request,'transactions.html',{'row1':row1 ,'row2':row2 , 'row3':row3 })


def TrackForm(request):

    return render(request,'TrackForm.html')


def track(request):

    uuid = request.POST['uuid']
    uuid_filter = uuid
    username = request.session['email']
    password = request.session['pwd']
    seed = username+password
    wallet = Wallet(None)
    wallet.generate_wallet(seed)    
    simba = get_simba_instance('https://api.simbachain.com/v1/w2c2/',wallet,'9bfc30e1f72bab8ed718176a64f47cb0f32123c00479552bd068578265ed406c','')
    method_params = {'uuid':uuid}
    result_pages = simba.get_method_transactions('CreateWaste', method_params)

    res = result_pages.data()
    timestamp = []
    uuid = []
    by = []
    wtype = []
    weight = []
    status = []

    for t in res:

        param = t['payload']['inputs']
        if(param['uuid']==uuid_filter):
            timestamp.append(t['timestamp'])
       
            uuid.append(param['uuid'])
            #wtype.append(param['wtype'])
            if (param['wtype']=='0'):
                wtype.append('Energy')
            elif (param['wtype']=='1'):
                wtype.append('Fertilizer')
            weight.append(param['weight'])
            by.append(param['addr'])
            data = t['receipt']['logs'][0]['data']
            encoded = to_bytes(hexstr=data)
            decoded = decode_abi(['int'], encoded)
            if(decoded[0]==1):
                status.append("Successful")
            elif(decoded[0]==0):
                status.append("Failed")

    row1 = zip(timestamp, uuid,by, wtype,weight,status)

    result_pages = simba.get_method_transactions('AcceptRequest', method_params)
    res = result_pages.data()
    timestamp = []
    to = []
    uuid = []
    wtype = []
    weight = []
    status = []

    for t in res:

        param = t['payload']['inputs']
        if(param['uuid']==uuid_filter):

            timestamp.append(t['timestamp'])
            uuid.append(param['uuid'])
            to.append(param['addr'])
            w = (Waste.objects.filter(uuid = param['uuid']))[0]
            wtype.append(w.wtype)
            weight.append(w.weight)
            data = t['receipt']['logs'][0]['data']
            encoded = to_bytes(hexstr=data)
            decoded = decode_abi(['int'], encoded)
            if(decoded[0]==1):
                status.append("Successful")
            elif(decoded[0]==0):
                status.append("Failed")

    row2 = zip(timestamp,uuid,to,wtype,weight,status)
    return render(request,'track.html',{'row1':row1,'row2':row2})