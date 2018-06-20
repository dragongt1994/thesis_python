import struct
import hashlib
import math
from enum import Enum
import socket
#from enum import enum
def md5(bt):
    hash_md5 = hashlib.md5()
    hash_md5.update(bt)
    return hash_md5.hexdigest()

class messageType(Enum):
    CONN_REQT=2
    CONN_CONF=3
    SEND_FILE=4
    SEND_SUCC=5


    

class earthquakeData:
    def __init__(self,npts=0,delta=0,maxv=0,minv=0,val=None, f=None):
        if f!=None:
            f=open(fname,"b")
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
    def __init__(self, dat, p=None):
        if p==None:
            l=len(dat)
            self.__dat=dat
            print(l)
            temp=bytes([0]*(4060-l))
            temp2=struct.pack('i',l)+dat+temp
            s=md5(temp2)
            s2=str.encode(s)
            self.__pck=temp2+s2
        else:
            self.__dat=self.__pck[4:4064]
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
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
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
        self.sck.connect(host, port)
        #username,fname,mname,lname 30 for whole
        l=len(self.__currData)
        nmb=math.ceil(l/4096)
        dat=[[messageType.CONN_REQT]+str.encode(self.username)+ str.encode(self.fname)+ str.encode(self.mname)+str.encode(self.lname)+struct.pack('L', l)]
        p=Packet(dat)
        self.sck.send(p.pck())
        r=self.sck.recv(4096)
        temp=Packet(p=r).dat
        if temp==messageType.CONN_CONF:
            for ctr in range(0, nmb):
                tdat=self.currData.packData()[ctr*4096:(ctr+1)*4096]
                self.sck.send(tdat.packData)
            
            
            
            
    
a=[]    
for i in range(0, 203):
    a=a+[float(i)]
    

eq=earthquakeData(len(a), 0.01, 1,-1, a)
eq.saveToFile("earth.dat")


#if __name__ == "__main__":
  #  main()
