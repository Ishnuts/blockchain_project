# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 11:52:16 2023

@author: Tonya
"""

#-----------------------------------------------------------------------
#							Import packages
#----------------------------------------------------------------------- 
import socket
import json
import threading
from time import sleep,time
import hashlib
import argparse

#-----------------------------------------------------------------------
#						Constants and variables
#-----------------------------------------------------------------------

globalDifficulty = 5
time_genesis = 1681057193
localhost = "127.0.0.1"







def block_encoder(block):
    if isinstance(block, Block):
        return (block.__dict__)
    else:
        type_name = block.__class__.__name__
        raise TypeError(f"Object of type {type_name} is not serializable")


#-----------------------------------------------------------------------
#				Class Miner with its functions and procedures
#-----------------------------------------------------------------------
class Miner:
    
    def __init__(self, address, port, known_miner=None): 
        self.address = address
        self.port = port
        self.known_miners = list()
        if known_miner is not None:
            self.connect_to(known_miner)
        self.blockchain = Blockchain()
        self.wallet = Wallet(f'0x{self.port}')
        self.is_mining = False

    def start(self):
        mineThread = threading.Thread(target=self.mine , args=())
        listenThread = threading.Thread(target=self.listen , args=())
        mineThread.start()
        listenThread.start()

    def listen(self):
        self.is_listening = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #The arguments passed to socket() are constants used to specify the address family and socket type. AF_INET is the Internet address family for IPv4. SOCK_STREAM is the socket type for TCP, the protocol that will be used to transport messages in the network.
        self.server_socket.bind((self.address, self.port))  #The bind() method is used to associate the socket with a specific network interface and port number:
        self.server_socket.listen(1) #A listening socket does just what its name suggests. It listens for connections from clients.
        print(f"[{self.port}] Listening on {self.address}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept() # address renamed to cleint_adress
            client_local_address = client_socket.getsockname() # to get the local address and not the remote one            
            print(f"[{self.port}] Accepted connection")
            message = client_socket.recv(4096).decode()
            print(f"[{self.port}] Received Message")
            if(message == "\"stop_listening\""):
                print(f"[{self.port}] Stopped listening")
                client_socket.close()
                return
            self.handle_message(message, client_socket)
            client_socket.close()

    def mine(self):
        self.is_mining = True
        while True:
            if self.is_mining:
                print(f"[{self.port}] Mining...")
                block = self.blockchain.initialize_block(self.wallet.wallet_address)
                block.mine_block()
                if not self.blockchain.verify_block(block):
                    print(f"[{self.port}] Blockchain state changed while mining, mining next block")
                    continue
                if not self.is_mining:
                    return
                self.blockchain.add_block(block)
                print(f"[{self.port}] Added Block: {block}")
                self.broadcast_block(json.dumps({"type": "new_block", "block" : block}, default=block_encoder))
            else:
                print(f"[{self.port}] Stopped mining")
                return
    
    def stop_mining(self):
        self.is_mining = False
        
    def stop_listening(self):
        self.send_to_miner((self.address, self.port), "stop_listening")

    def connect_to(self, miner):
        print(f"[{self.port}] Connecting to {miner.address}:{miner.port}")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #The arguments passed to socket() are constants used to specify the address family and socket type. AF_INET is the Internet address family for IPv4. SOCK_STREAM is the socket type for TCP, the protocol that will be used to transport messages in the network.
        client_socket.connect((miner.address,miner.port))
        message = {"type": "register", "address": self.address, "port": self.port,"known_miners": self.known_miners}
        client_socket.send(json.dumps(message).encode())
        try:
            response = client_socket.recv(4096).decode()
        except socket.timeout:
            print("Timed out waiting for data")
        self.handle_message(response)
        client_socket.close()


    
    def add_miners_known_by_register(self,message): #Add the knowed miners of the one whos connecting (including himself) to the one who is accepting the connection 
        if (message["address"], message["port"]) not in self.known_miners:
            self.known_miners.append((message["address"], message["port"])) #add the adresss of the connecting miner to the self.known_miners
        
        for miner in message["known_miners"]: #add to known_miners the miners which are known by the miner which is connecting
            miner_tuple = (miner[0], miner[1])
            if miner_tuple not in self.known_miners and miner_tuple != (self.address, self.port):
                self.known_miners.append(miner_tuple)
        #print(f"[{self.port}] Current known_miners: {self.known_miners} ")
 
 
 
    def handle_message(self, message, caller_socket=None):
        message = json.loads(message) #converting the message from string to dict (to manipulate fields)
        
        if message["type"] == "register":
            #print(f"[{self.port}] Received registration from {message['address']}:{message['port']}")
            self.add_miners_known_by_register(message)

            self.broadcast_new_miner(json.dumps({"type": "new_miner", "address": message['address'], "port": message['port'],"known_miners":self.known_miners}))
            self.send_miner_list(message['address'], message['port'], caller_socket)
                # sleep(2) #attendre que celui qui recoi recoit de send  tout avant de passer à la suite 

        elif message["type"] == "new_miner":
            
            #print(f"[{self.port}] Received new miner announcement from {message['address']}:{message['port']}")
            if self.port!=message['port'] and (message['address'], message['port']) not in self.known_miners:
                self.known_miners.append((message["address"], message["port"]))
                #print(f"[{self.port}] added new miner to known miners: {message['address']}:{message['port']}")
            
            for miner in message["known_miners"]:
                miner_tuple = (miner[0], miner[1])
                if miner_tuple not in self.known_miners and miner_tuple != (self.address, self.port):
                    self.known_miners.append(miner_tuple)

        elif message["type"] == "send_transaction":
            transaction = message["data"]
            self.blockchain.add_transaction(transaction)
            print(f"[{self.port}] Received transaction from wallet: {transaction}")
            self.broadcast_transaction(json.dumps({"type": "broadcasted_transaction", "data": message["data"]}))

        elif message["type"] == "miner_list":
            #print(f"[{self.port}] Received miner list from {message['address']}:{message['port']}")
            for miner in message['data']:
                if miner[1] != self.port and (miner[0], miner[1]) not in self.known_miners:
                    self.known_miners.append((miner[0], miner[1]))
                    
        elif message["type"] == "broadcasted_transaction":
            transaction = message["data"]
            self.blockchain.add_transaction(transaction)
            #print(f"[{self.port}] Added broadcasted_transaction: {transaction}")
        elif message["type"] == "new_block":
            block_message = message["block"]
            block = Block(block_message["timestamp"], block_message["transactions"], block_message["previous_hash"], block_message["nonce"], block_message["hash"])
            if self.blockchain.verify_block(block):
                self.blockchain.add_block(block)
                print(f"[{self.port}] Added new block: {block}")
            else:
                print(f"[{self.port}] Invalid block: {block}")
        elif message["type"] == "print_state":
            print(f"[{self.port}] Printing state")
            print(f"[{self.port}] Known miners: {self.known_miners}")
            print(f"[{self.port}] Blockchain de Taille [{len(self.blockchain.chain)}]: {self.blockchain}")
        else:
            print(f"[{self.port}] Unknown message type: {message['type']}")



    def send_miner_list(self, address, port, caller_socket=None): 
        personlied_Known_miners=self.known_miners.copy() #so we dont modify the attribute know_miners of our object
        personlied_Known_miners.append((self.address,self.port))
        message = {"type": "miner_list", "data": personlied_Known_miners, "address": self.address, "port": self.port}
        caller_socket.send(json.dumps(message).encode())
  

    def send_to_miner(self, miner, message): #core function for sending the message 
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creation d'un socket pour chaque miners_knowed
            client_socket.connect(miner)
            print(f"[{self.port}] Sending to {miner} ")
            client_socket.send(json.dumps(message).encode())
            client_socket.close()
        except Exception as e:
            print(f"[{self.port}] Failed to broadcast to {miner}: {e}")
  
    def broadcast_new_miner(self, message):
        message = json.loads(message)
        message["known_miners"].append((self.address, self.port))

        for miner in self.known_miners:
            if message["address"]==miner[0] and message['port'] == miner[1]:
                
                print(f"[{self.port}] Broadcasting to registering miner, skipping")
            else:
                self.send_to_miner(miner, message)
                print(f"{[self.port]} Broadcast new miner to our list of known miners")


    def broadcast_transaction(self, message):
        message = json.loads(message)
        for miner in self.known_miners:                
            self.send_to_miner(miner, message)
        #print(f"{[self.port]} broadcast_transaction: " + json.dumps(message))

    def broadcast_block(self, message):
        message = json.loads(message)
        for miner in self.known_miners:                
            self.send_to_miner(miner, message)
        #print(f"{[self.port]} broadcast_block: " + json.dumps(message))

 
 
#-----------------------------------------------------------------------
#	Class Wallet with its constructor and sending transaction function
#-----------------------------------------------------------------------

class Wallet: #A wallet that connect itself to a miner and send its transaction

    wallet_address : str
    value : int
    
    def __init__(self, address, value=0):
        self.wallet_address = address
        self.value = 0

    def send_transaction(self, transaction: dict, miner_ip, miner_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((miner_ip, miner_port))
            message = {"type": "send_transaction", "data": transaction}
            #print(f"send_transaction message: {message}")
            sock.send(json.dumps(message).encode())


#-----------------------------------------------------------------------
#				Class Block with its constructor and functions 
#-----------------------------------------------------------------------

class Block:
    def __init__(self, timestamp, transactions, previous_hash, nonce=0, hash=None):
        self.timestamp = int(timestamp)
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        if hash == None:
            self.hash = self.calculate_hash()
        else:
            self.hash = hash


    def calculate_hash(self):
        return hashlib.sha256((str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)).encode()).hexdigest()


    def mine_block(self, difficulty=globalDifficulty):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def __str__(self):
        return f"hash: {self.hash[:10]} prevHash: {self.previous_hash[:10]}| tx: {self.transactions}"



#-----------------------------------------------------------------------
#		Class Block  with its constructor, functions and procedure
#-----------------------------------------------------------------------


class Blockchain:
    def __init__(self, difficulty=globalDifficulty):
        self.chain = []
        self.pending_transactions = []
        self.mining_reward = 100
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(time_genesis, [], "0")
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def verify_block(self, block): #verify if the block is valid
        if block.previous_hash != self.get_latest_block().hash:
            #print(f"Block not verified cause previous hash not equal")
            #print(f"{block.previous_hash[:10]} != {self.get_latest_block().hash[:10]}")
            return False
        if block.calculate_hash() != block.hash:
            #print("Block not verified cause hash not equal")
            #print(f"{block.calculate_hash()[:10]} != {self.get_latest_block().hash[:10]}")
            return False
        if block.hash[:self.difficulty] != "0" * self.difficulty:
            #print("Block not verified cause hash not valid")
            #print(f"{block.hash[:self.difficulty]} != {'0' * self.difficulty}")
            return False
        return True

    def add_block(self, block):
        self.chain.append(block)
    
    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def initialize_block(self, miner_address):
        reward_transaction = {'source_address': "system", "destination_address" : miner_address, "amount" : self.mining_reward}
        self.pending_transactions.append(reward_transaction)
        block_transactions = self.pending_transactions.copy()
        self.pending_transactions = []
        block = Block(time(), block_transactions, self.get_latest_block().hash)
        return block

    def __str__(self):
        string = ""
        for i, block in enumerate(self.chain):
            string += f"[{i}] [{block.__str__()}]\n"
        return string


#-----------------------------------------------------------------------
#	function to handle our main miner thread with command line arguments
#-----------------------------------------------------------------------
   
def main_cli(mode, address, ports):

    if mode == "miner":
        miners = []
        for port in ports:
            port = int(port)
            miner = Miner(address, port)
            miners.append(miner)

        for miner in miners:
            miner_thread = threading.Thread(target=miner.start, args=())
            miner_thread.start()
        
        first_miner = miners[0]
        for miner in miners[1:]:
            first_miner.connect_to(miner)

    elif mode == "print":
        minerPrint = Miner("PRINT", "PRINT")
        print(f"\n ================== PRINT MINER {int(ports[0])} STATE  ==================\n")
        minerPrint.send_to_miner((address, int(ports[0])), {"type":"print_state"})
        print("Blockchain state printed on miner's terminal")
    
    
#-----------------------------------------------------------------------
#		Setting up command line arguments options in Main Function
#-----------------------------------------------------------------------
if __name__=="__main__":
    # main()
    parser = argparse.ArgumentParser(description='Ce programme permet de simuler un réseau de mineurs et de wallet minant des blocs et effectuant des transactions')
    parser.add_argument('-M', '--mode', help="Change program mode ['miner' | 'wallet | print']", required=True) 
    parser.add_argument('-a', '--address', help="address", required=False) 
    parser.add_argument('-p', '--port', nargs="+", help='[Required] port', required=True)
    parser.add_argument('-wa', '--walletAddress', help="wallet address (ex: '0x00001')", required=False)
    parser.add_argument('-d', '--destinationAddress', help="--destination-address (ex:'0x00002'))", required=False)
    parser.add_argument('-v', '--value', help="transaction value", required=False)
    
    args = vars(parser.parse_args())

    if args["mode"] == "miner" or args["mode"] == "print":
        mode = args["mode"]
        address = args["address"] if args["address"] else localhost
        ports = args["port"] if args["port"] else ["1000"]
        main_cli(mode, address, ports)
    elif args["mode"] == "wallet":
        wallet = Wallet(args["walletAddress"]) if args["walletAddress"] else "0x00001"
        destination = args["destinationAddress"] if args["destinationAddress"] else "0x00002"
        value = args["value"] if args["value"] else 1
        miner_address = args["address"] if args["address"] else localhost
        miner_port = args["port"][0] if args["port"][0] else "1000"
        transaction = {
            'source_address': args["walletAddress"],
            'destination_address': destination,
            'amount': value,
        }
        wallet.send_transaction(transaction, miner_address, int(miner_port))
        print(f"\n ================== TRANSACTION SENT FROM WALLET {args['walletAddress']} to {args['destinationAddress']} ==================\n")
        print("Wallet transaction printed on miner's terminal \n")
        exit(0)
    else:
        print("Unknown mode")
        exit(1)
        