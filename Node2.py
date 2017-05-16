import random as rnd
import numpy as np
import time as time
from scipy import stats

payload = 10

# -- We conceptually divide the nodes into 2 categories:
#    - STORAGE NODE: generic node that can only store and forward pkts
#    - SENSOR NODE: node that can actually sense the environment and generate pktts. It can also store and forward
#    (NOTE: class SENSOR extends class STORAGE)

#-- STORAGE NODE SPECIFICATIONS ---------------------------------------------------------------------------------
class Storage(object):

    def __init__(self, ID, X, Y, d, n, k, c1,pid):
        self.C1 = c1                                # parameter C1
        self.ID = ID                                # ID of the node
        self.X = X                                  # position
        self.Y = Y                                  # position
        self.neighbor_list = []                     # list of references for neighbor nodes
        self.node_degree = 0                        # number of neighbors
        self.out_buffer = []                        # outgoing packets buffer
        self.dim_buffer = 0                         # number of pkt in the outgoing queue
        self.code_degree = d                        # degree of the node, define how many pkts to encode
        self.ID_list = []                           # ID list of encoded pkts, saved for decoding purposes
        self.storage = np.zeros(payload, dtype=np.int64) # initialization of storage variable [0,..,0]
        self.num_encoded = 0                        # num. of encoded pkts, used to stop encoding process if it reaches d

        self.n = n                                  # number of nodes in the network
        self.k = k                                  # number of sensors in the network
        self.visits = np.zeros(n)                   # n-dim list which purpose is to count pkts visits to the node
                                                    # it should be k-dim since only k nodes generate pkts but for
                                                    # computational reason it isn't. OPEN QUESTION
        self.already_coded = np.zeros(n)
        self.code_prob = self.code_degree / self.k
        self.pid = pid                              # steady state probability pi greco d, see formula 5 paper 1
        self.metropolis_prob = 0                    # variable containing the transition probabilities computed through the metropolis algorithm.
        self.number_random_walk = 0                 # parameter b, formula 3 paper 1
        self.received_from_dissemination = []       # variable containing the pkt received from the dissemination
        self.already_received = np.zeros(n)         # keep trace of the already received pkts, in order not to save them both


    def get_pos(self):                              # return positions, DEPRECATED
        return self.X, self.Y

    def neighbor_write(self, neighbor):             # connect node with neighbors
        self.neighbor_list.append(neighbor)         # list of reference for neighbors node
        self.node_degree += 1                       # increase neighbor number at each insertion

    def send_pkt(self, mode):                       # send function used to move messages between nodes
        if self.dim_buffer > 0:                     # if buffer non empty --> we can send something
            if mode == 0:                           # mode 0 = uniform at random selection
                neighbor = rnd.choice(self.neighbor_list)
                pkt = self.out_buffer.pop(0)        # extract one pkt from the output buffer
                self.dim_buffer -= 1                # reduce number of queued pkts
                return neighbor.receive_pkt(pkt)    # pass pkt to neighbor and return 1 if blocked or 0 if not blocked
            elif mode == 1:                         # mode 1 = metropolis algo (ancora da implementare per paper 1)
                indicies = np.arange(0, self.node_degree)    # vector of indicies representing one neighbor
                custm = stats.rv_discrete(name='custm', values=(indicies, self.metropolis_prob))
                                                    # creation of obj custm, see documentation
                neighbor_idx = custm.rvs()          # randomly sample element from custm, following the distribution
                neighbor = self.neighbor_list[neighbor_idx]   # computed through the metropolis algorithm
                pkt = self.out_buffer.pop(0)        # extract one pkt from the output buffer
                self.dim_buffer -= 1                # reduce number of queued pkts
                return neighbor.receive_pkt2(pkt)   # pass pkt to neighbor and return 1 if blocked or 0 if not blocked

        else:                                       # empty buffer
            return 0

    def receive_pkt(self, pkt):                     # define what to do on pkt receiving
        self.visits[pkt.ID-1] += 1                  # increase number of visits this pkt has done in this very node

        if self.visits[pkt.ID - 1] == 1:            # if it is the first time the pkt reaches this very node ...
                if self.num_encoded < self.code_degree: #...and we still have to encode something
                    prob = rnd.random()             # generate a random number in the range [0,1)
                    if prob <= self.code_prob:      # if generated number less or equal to coding probability
                      self.ID_list.append(pkt.ID)        # save ID of node who generated the coded pkt
                      self.storage = self.storage ^ pkt.payload # code procedure(XOR)
                      self.num_encoded += 1              # increase num of encoded pkts
                pkt.counter += 1                    # increase pkt counter then put it in the outgoing buffer
                self.out_buffer.append(pkt)         # else, if pkt is at its first visit, or it haven't reached C1nlog10(n)
                self.dim_buffer += 1
                return 0                            # NOTE: this procedure has to be done even if the pkt has already visited
                                                    # the node! That is to say: if pkt x has visited node v before
                                                    # BUT c(x)<C1nlog(n), v accepts it with Prob=0, BUT it forwards it
        if self.visits[pkt.ID-1] > 1:
            if pkt.counter >= self.C1 * self.n * np.log10(self.n):  # if packet already visited the node
                                                    # and its counter is greater than C1nlog10(n) then, discard it
                return 1                            # pkt dropped
            else:
                pkt.counter += 1                    # increase pkt counter then put it in the outgoing buffer
                self.out_buffer.append(pkt)         # else, if pkt is at its first visit, or it haven't reached C1nlog10(n)
                self.dim_buffer += 1
                return 0                            # NOTE: this procedure has to be done even if the pkt has already visited
                                                    # the node! That is to say: if pkt x has visited node v before
                                                    # BUT c(x)<C1nlog(n), v accepts it with Prob=0, BUT it forwards it

    def receive_pkt2(self, pkt):
        return 1






    # def receive_pkt(self, pkt):                     # define what to do on pkt receiving
    #     self.visits[pkt.ID-1] += 1                  # increase number of visits this pkt has done in this very node
    #     # CODING PROCEDURE ------------------------------
    #     if self.already_coded[pkt.ID - 1] == 0:            # if it is the first time the pkt reaches this very node ...
    #             if self.num_encoded < self.code_degree: #...and we still have to encode something
    #                 prob = rnd.random()             # generate a random number in the range [0,1)
    #                 if prob <= self.code_prob:      # if generated number less or equal to coding probability
    #                     self.ID_list.append(pkt.ID)        # save ID of node who generated the coded pkt
    #                     self.storage = self.storage ^ pkt.payload # code procedure(XOR)
    #                     self.num_encoded += 1              # increase num of encoded pkts
    #                     self.already_coded[pkt.ID - 1] +=1
    #     if self.visits[pkt.ID-1]== 1:
    #             pkt.counter += 1                    # increase pkt counter then put it in the outgoing buffer
    #             self.out_buffer.append(pkt)         # else, if pkt is at its first visit, or it haven't reached C1nlog10(n)
    #             self.dim_buffer += 1
    #             return 0                            # NOTE: this procedure has to be done even if the pkt has already visited
    #                                                 # the node! That is to say: if pkt x has visited node v before
    #                                                 # BUT c(x)<C1nlog(n), v accepts it with Prob=0, BUT it forwards it
    #     else: #if self.visits[pkt.ID-1] > 1:
    #         if pkt.counter >= self.C1 * self.n * np.log10(self.n):  # if packet already visited the node
    #                                                 # and its counter is greater than C1nlog10(n) then, discard it
    #             return 1                            # pkt dropped
    #         else:
    #             pkt.counter += 1                    # increase pkt counter then put it in the outgoing buffer
    #             self.out_buffer.append(pkt)         # else, if pkt is at its first visit, or it haven't reached C1nlog10(n)
    #             self.dim_buffer += 1
    #             return 0                            # NOTE: this procedure has to be done even if the pkt has already visited
    #                                                 # the node! That is to say: if pkt x has visited node v before
                                                    # BUT c(x)<C1nlog(n), v accepts it with Prob=0, BUT it forwards it


    def storage_info(self):
        return self.num_encoded, self.ID_list, self.storage       #return code degree of the node, list of ID XORed pkts
                                                                  #and the result of the XOR operation


# -- SENSOR NODE SPECIFICATIONS ---------------------------------------------------------------------------------------
class Sensor(Storage):

    def __init__(self, ID, X, Y, d, n, k, c1, pid):
        self.C1 = c1                                # parameter C1
        self.ID = ID                                # ID of the node
        self.X = X                                  # position
        self.Y = Y                                  # position
        self.neighbor_list = []                     # list of references for neigbor nodes
        self.node_degree = 0                        # number of neighbors
        self.out_buffer = []                        # outgoing packets buffer
        self.dim_buffer = 0                         # number of pkt in the outgoing queue
        self.code_degree = d                        # degree of the node, define how many pkts to encode
        self.ID_list =[]                            # ID list of encoded pkts, saved for decoding purposes
        self.storage = np.zeros(payload, dtype=np.int64)  # initialization of storage variable [0,..,0]
        self.num_encoded = 0                        # num. of encoded pkts, used to stop encoding process if it reaces d
        self.n = n                                  # number of nodes in the network
        self.k = k                                  # number of sensors in the network
        self.visits = np.zeros(n)                   # n-dim list which purpose is to count pkts visits to the node
                                                    # it should be k-dim since only k nodes generate pkts but for
                                                    # computational reason it isn't. OPEN QUESTION
        self.already_coded = np.zeros(n)
        self.code_prob = self.code_degree / self.k
        self.pid = pid                              # steady state probability pi greco d, see formula 5 paper 1
        self.metropolis_prob = 0                    # variable containing the transition probabilities computed through the metropolis algorithm.
        self.number_random_walk = 0                 # parameter b, formula 3 paper 1
        self.received_from_dissemination = []       # variable containing the pkt received from the dissemination
        self.already_received = np.zeros(n)         # keep trace of the already received pkts, in order not to save them both

    def spec(self):     # DEPRECATED
        print 'Sensor ID is %d and its position is (x=%d, y=%d) ' % (self.ID, self.X, self.Y)

    def pkt_gen(self):
        pkt = Pkt(self.ID, payload)         # generate a PKT object
        self.out_buffer.append(pkt)         # set generated pkt as ready to be sent adding it to the outgoing buffer
        prob = rnd.random()                 # generate a random number in the range [0,1)
        if prob <= self.code_prob:          # if generated number less or equal to coding probability
            self.ID_list.append(pkt.ID)     # save ID of node who generated the coded pkt
            self.storage = self.storage ^ pkt.payload  # code procedure(XOR)
            self.num_encoded += 1           # increase num of encoded pkts
            self.already_coded[pkt.ID - 1] += 1 #store the knowledge of the fact that the pkt with this ID is already been coded in thi node
        self.dim_buffer = 1
        return pkt.payload

    def pkt_gen2(self):
        pkt = Pkt(self.ID, payload)         # generate a PKT object
        for i in xrange(self.number_random_walk):   # mette in coda lo stesso pacchetto tante quante sono le random walk che deve generare
            self.out_buffer.append(pkt)     # set generated pkt as ready to be sent adding it to the outgoing buffer
        self.dim_buffer = self.number_random_walk   # set the dim of the buffer to the number of queued pkts = number of random walk

        prob = rnd.random()                 # generate a random numener [0,1]
        if prob <= self.pid:
            self.ID_list.append(pkt.ID)     # save ID of node who generated the coded pkt [node itself]
            self.received_from_dissemination.append(pkt)    # use a list to keep all received pkts
            self.already_received[pkt.ID - 1] += 1          # store the knowledge of the fact that the pkt with this
                                                            # ID is already been coded in thi node
            self.dim_buffer -= 1                            # decrease the number of queued pkts
            self.out_buffer.pop(0)                          # remove an instance of the generated pkt
        return pkt.payload                                  # return the pkt payload


    def pkt_gen3(self):
        pkt = Pkt(self.ID, payload)         # generate a PKT object
        self.storage = pkt.payload
        return pkt.payload

# -- PKT SPECIFICATIONS -----------------------------------------------------------------------------------------------
class Pkt(object):
    def __init__(self, ID, pay):
        self.ID = ID
        self.counter = 0
        self.payload = np.zeros(pay, dtype=np.int64)
        for i in xrange(pay):
            self.payload[i] = np.random.randint(0, 2)