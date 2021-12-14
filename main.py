import sys
from Adafruit_IO import Client, Data
from Adafruit_IO import MQTTClient
from Blockchain_Info import *
import hashlib
import json
import datetime


aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)


def gui_transaction(transaction):
    # Send the transaction to the feed 'Transaction_net'.
    test = aio.feeds(Transaction_net)
    aio.send_data(test.key, transaction)


def xac_thuc(nguoi_gui, so_tien):
    if so_du(nguoi_gui) >= int(so_tien):
        return True
    else:
        return False


def so_du(ten):
    balance = 0
    block_data = aio.data(Main_net)
    for block in block_data:
        block_info = json.loads(block.value)
        trans_info = block_info["transactions"]
        lenh = trans_info["lenh"]
        if lenh == "chuyen_tien":
            nguoi_gui = trans_info["nguoi_gui"]
            nguoi_nhan = trans_info["nguoi_nhan"]
            so_tien = trans_info["so_tien"]
            if ten == nguoi_gui:
                balance = balance - int(so_tien)
            elif ten == nguoi_nhan:
                balance = balance + int(so_tien)
    return balance


def chuyen_tien(transaction):
    if xac_thuc(transaction["nguoi_gui"], transaction["so_tien"]):
        new_block(chain, transaction, hash(chain[-1]))
    else:
        print("Transaction {0} is not valid".format(transaction))


def new_block(chain, valid_transactions, previous_hash):
    block = {
        'index': len(chain) + 1,
        'timestamp': str(datetime.datetime.now()),
        'transactions': valid_transactions,
        'previous_hash': previous_hash,
    }
    data = Data(value=json.dumps(block))
    aio.create_data(Main_net, data)

    chain.append(block)
    return block


def new_transaction(lenh, nguoi_gui, recipient, so_tien, type_coin, valid_transaction):
    transaction = {
        'lenh': lenh,
        'nguoi_gui': nguoi_gui,
        'recipient': recipient,
        'so_tien': so_tien
    }
    return json.dumps(transaction)


def last_block(chain):
    return chain[-1]


def hash(block):
    string_object = json.dumps(block, sort_keys=True)
    block_string = string_object.encode()

    raw_hash = hashlib.sha256(block_string)
    hex_hash = raw_hash.hexdigest()

    return hex_hash


def xu_ly_transaction(transaction):
    if transaction["lenh"] == "chuyen_tien":
        chuyen_tien(transaction)
    elif transaction["lenh"] == "so_du":
        print("So du cua {0} la: {1}".format(transaction["nguoi_gui"], so_du(transaction["nguoi_gui"])))
        new_block(chain, transaction,hash(chain[-1]))


def Subcribe():
    def connected(client):
        client.subscribe(Transaction_net)

    def subscribe(client, userdata, mid, granted_qos):
        print('Da ket noi thanh cong'.format(Transaction_net, granted_qos[0]))

    def disconnected(client):
        sys.exit(1)

    def message(client, Transaction_net, payload):
        print('Feed {0} vua nhan du lieu moi: {1}'.format(Transaction_net, payload))
        transaction = json.loads(payload)
        xu_ly_transaction(transaction)

    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.on_subscribe = subscribe

    client.connect()

    client.loop_blocking()

chain = []

if len(aio.data(Main_net)) == 0:
    #Tao giao dich dau tien
    transaction_1 = {"lenh": "chuyen_tien", "nguoi_gui": "Tam", "nguoi_nhan": "Bao", "so_tien": "10"}
    new_block(chain, transaction_1, previous_hash="This is the initial block that created by Bang Ngoc Bao Tam")
    
    # Tao giao dich thu hai
    transaction_2 = {"lenh": "chuyen_tien", "nguoi_gui": "Tam", "nguoi_nhan": "An", "so_tien": "10"}
    new_block(chain, transaction_2, hash(chain[0]))
    
    #Sau khi giao dich nay duoc thuc hien, Bao co 10 dong va An co 10 dong. Chi co Bao va An moi co the chuyen tien trong he thong.
else:
    for blocks in aio.data(Main_net):
        chain.append(blocks.value)

Subcribe()
