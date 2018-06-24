import struct
import hashlib
import math
from enum import Enum
import socket
import socketserver
#from enum import enum
def md5(bt):
    hash_md5 = hashlib.md5()
    hash_md5.update(bt)
    return hash_md5.hexdigest()

class messageType(Enum):
    CONN_REQT=2
    CONN_CONF=3
    SEND_FILE=4
    SEND_REQT=5
    SEND_CONF=6
    SEND_SUCC=7

def message(msg_type,size=None, snum=None, username=None, fname=None, mname=None, lname=None, machine=None ):
    if msg_type==messageType.CONN_REQT:
       # msgtype=struct.unpack('i', val[1])
        dat=struct.pack('I', msg_type.value)+str.encode(valusername)+ str.encode(fname)+ str.encode(mname)+str.encode(lname)
    elif msg_type==messageType.CONN_CONF:
        dat=struct.pack('I', msg_type.value)+struct.pack('I', machine)
        
    
    elif msg_type==SEND_FILE:
        dat=struct.pack('I', msg_type.value)+struct.pack('I', size)+struct.pack('I', snum)
    return dat

def parseMessage(dat):
    msgtype=struct.unpack('i', dat[0:4])
    username=str.decode(dat[4:14])
    fname=str.decode(dat[14:24])
    mname=str.decode(dat[24:34])
    lname=str.decode(dat[34:44])

class earthquakeData:
    def __init__(self,npts=0,delta=0,maxv=0,minv=0,val=None, f=None):
        if f!=None:
            self.fname=f
            temp=f.read()
            self.npts=struct.unpack('L',temp[0:4])
            self.delta=struct.unpack('f',temp[4:8])
            self.maxv=struct.unpack('f',temp[8:12])
            self.minv=struct.unpack('f',temp[12:16])
            print (self.npts)
            print(self.delta)
            print(maxv)
            print(minv)
            fnum=len(temp[16:])/4
            self.val=struct.unpack('f'%self.npts,temp[16:])
        else:
            self.npts=npts
            self.delta=delta
            self.maxv=maxv
            self.minv=minv
            self.val=val
            print (self.npts)
            print(self.delta)
            print(maxv)
            print(minv)
    def saveToFile(self,fname):
        f=open(fname,"wb")
        f.write(self.packData())
        f.close()
    def packData(self):
        temp= struct.pack('i', self.npts)
        temp=temp+struct.pack('f', self.delta)
        temp=temp+struct.pack('f', self.maxv)
        temp=temp+struct.pack('f', self.minv)
        temp=temp+struct.pack('%sf'%self.npts, *self.val)
        return temp
    #4096
class Packet:
    def __init__(self, dat=None, p=None):
        if p==None:
            l=len(dat)
            self.__dat=dat
            res=[]
            self.dat_size=l
            nmb=math.ceil(l/4096)
            print("nmb"+ str(nmb))
            for ctr in range(0, nmb):
                pck_temp=self.dat[ctr*4056:(ctr+1)*4056]
                tdat=pck_temp
                l=len(tdat)
                print("4060-l="+str(4056-l))
                temp=bytes([0]*(4056-l))
                temp2=struct.pack('i',ctr)+struct.pack('i',l)+tdat+temp
                s=md5(temp2)
                s2=str.encode(s)
                temp2=temp2+s2
                print(len(temp2))
                res=res+[temp2]
            
            self.__pck=res

#            ftemp=open("pack_"+str(ctr)+".dat", "wb")
#            ftemp.write(tdat)
#            ftemp.close()
#            
            
            
        else:
            self.dat_size=0
            self.__dat=[]
            for tmp in p:
                l=int(struct.unpack('i', tmp[4:8] )[0])
             #   print("l="+str(l[0]))
        #        print(tmp)
         #       print(tmp[8:4064])
                print(tmp[8 :l])
                self.__dat=self.__dat+[tmp[8 :l]]
                self.dat_size=self.dat_size+l
                
            self.__pck=p
    @property
    def dat(self):
        return self.__dat
      #  print(fin)

    @property
    def pck(self):
        return self.__pck
        
    

class clientMachine:
    def __init__(self, username,fname,mname, lname, currData=None):
        self.username=username
        self.fname=fname
        self.mname=mname
        self.lname=lname
    #    self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.__currData=currData
    @property
    def currData(self):
        return self.__currData
    
    @currData.setter
    def currData(self, currData):
        self.__currData=currData
    
        
    def saveToFile(self,fname):
        f=open(fname,"b")
        f.write(self.__currData.packData())

    def sendData(self):
        max_length=4
        
    def askConnection(self, host, port):
    #    self.sck.connect(host, port)
        #username,fname,mname,lname 30 for whole

        dat=message(messageType.CONN_REQT, self.username,self. fname, self.mname, self.lname)
        msg=Packet(dat)
        self.sck.send(msg.pck())
        r=self.sck.recv(4096)
        temp=struct.unpack('I', Packet(p=r).dat[0:4])
        if temp==messageType.CONN_CONF:
            dat=self.__currData.packData()
            tot_dat=Packet(dat).pck
            msg=message(messageType.SEND_REQT, 4096, len(tot_dat))
            r=self.sck.recv(4096)
            temp=struct.unpack('I', Packet(p=r).dat[0:4])
            if temp==messageType.SEND_CONF:
                ctr=0
                for tdat in tot_dat:
                    self.sck.send(tdat)
#                    ftemp=open("pack_dat/pack_"+str(ctr)+".dat", "wb")
#                    ftemp.write(tdat)
#                    ftemp.close()
#                    ctr=ctr+1
            
            
        
        return tot_dat
        #ftemp=open("pack_"+str(ctr)+".dat", "wb")
        #ftemp.write(tdat)
        #ft    emp.close()
    #            self.sck.send(tdat.packData)
    

    
class serverMachine(socketserver.BaseRequestHandler):
    def __init__(self, machinename):
        self.machinename=machinename
        
    def handle(self):
        # self.request is the TCP socket connected to the client
        
        data = self.request.recv(4096)
        tdat=Packet(p=[data]).dat
        dat=tdat[0]
        msgtype=struct.unpack('i', dat[0:4])
        self.username=str.decode(dat[4:14])
        self.fname=str.decode(dat[14:24])
        self.mname=str.decode(dat[24:34])
        self.lname=str.decode(dat[34:44])
        if msgtype== messageType.CONN_REQT:
            tmp=message(messageType.CONN_CONF, machine=self.machinename)
            msg=Packet([tmp])
            self.request.send(msg.pck)
            data = self.request.recv(4096)
            tdat=Packet(p=[data]).dat[0]
            msgtype=struct.unpack('i', tdat[0:4])
            if msgtype==messageType.SEND_FILE:
                size=struct.unpack(i, tdat[4:8])
                snum=struct.unpack(i, tdat[8:12])
                tmp=message(messageType.SEND_CONF, machine=self.machinename)
                msg=Packet([tmp])
                self.request.send(msg.pck)
                print("size="+str(size)+" snum="+str(size))
                temp=[]
                for ctr in range(0, snum):
                    dat=self.request.recv(4096)
                    temp=temp+dat
                final_file=Packet(p=temp)
                ctgr=0
                for files in final_file:
                    ftemp=open("pack_"+str(ctr)+".dat", "wb")
                    ftemp.write(tdat)
                    ftemp.close()
                    ctr=ctr+1
                tmp=message
                
        
        
        
        
        
        


#eq.saveToFile("earth.dat")
#eq

#if __name__ == "__main__":
  #  main()
