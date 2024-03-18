import numpy as np
import threading
import time
import zmq
from radar_format import *

np.random.seed(0)

WavDir = 300 
WavPrd = 500 # m
WavSpd = 3   # m/s

MaxRng = 5000 # m
RngRes = 7.5  # m
Hgt = 200 # m
BW = 20   # degrees
DP = 10   # degrees

BlankA = 120
BlankB = 240

RotRate = 8  #  RPM
RotUpdt = 30 # update per sec

PRF = 25000  # Hz
INT = 16     # integration
DFT = 64     # DFT size
MxV = 2**16 * DFT * INT / 8
NsVs = 75
Fs = 9.3e9
c = 3e8

running = True
azimuth = int(0)

class Field(object):

    def __init__(self):
        self.rng = np.arange(int(MaxRng/RngRes)) * RngRes + 1
        da = 180*np.arcsin(Hgt/self.rng)/np.pi
        da[np.isnan(da)] = np.max(da[~np.isnan(da)])
        da -= DP
        dw = np.sinc(da*np.pi/4/BW/2)
        dw -= np.min(dw)
        dw *= 1/self.rng**2
        dw /= np.max(dw)
        self.prof = MxV * dw
        self.rng -= 1

    def getMag(self, tm, angle):
        ang = angle - WavDir
        prd = WavPrd / (np.cos(ang*np.pi/180)+1e-15)
        wphs = 2*np.pi*(self.rng/prd+tm*WavSpd/WavPrd)
        awht = .64-.46*np.cos(2*angle*np.pi/180+np.pi)
        wave = awht * self.prof * np.sin(wphs)
        wave = (wave + (MxV / NsVs) * np.random.randn(len(self.rng))).astype(np.float32)
        return wave
        

class AzimuthSim(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.current = np.random.randint(360*100)/100

    def run(self):
        global azimuth
        while running:
            time.sleep(1/RotUpdt)
            self.current += 360. * RotRate / 60. / RotUpdt
            azimuth = int(2**15 * (self.current % 360) / 360) 

            
class RadProducer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.ant = 0
        self.time = 0.
        self.field = Field()
        self.socket = zmq.Context().socket(zmq.PUB)
        self.socket.bind("tcp://*:%s" % MOMENT_PORT)
        
    def run(self):
        while running:
            time.sleep(DFT*INT/PRF)
            self.time += DFT*INT/PRF
            self.ant = (self.ant + 1) % 4
            cazi = (360 * azimuth / 2**15 + 90 * self.ant) % 360
            doblank = False
            if BlankA > BlankB:
                if cazi > BlankA or cazi < BlankB:
                    doblank = True
            else:
                if cazi > BlankA and cazi < BlankB:
                    doblank = True
            if not doblank:
                wave = self.field.getMag(self.time, cazi)
                sec = int(self.time)
                tic = int((self.time-sec) * 31.25e6)
                s = MAG_TYPE
                s += struct.pack('<HHHHIIII', HDR,self.ant,azimuth,0,sec,tic,len(wave),0)
                s += wave.tobytes()
                self.socket.send(s)
        self.socket.close()

# class RadSubscriber(threading.Thread):

#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.socket = zmq.Context().socket(zmq.SUB)
#         self.socket.connect("tcp://localhost:%s" % MOMENT_PORT)
#         self.socket.setsockopt(zmq.SUBSCRIBE, MAG_TYPE)
#         self.poller = zmq.Poller()
#         self.poller.register(self.socket, zmq.POLLIN)
        
#     def run(self):
#         while running:
#             rsv = dict(self.poller.poll(.5))
#             if rsv:
#                 if rsv.get(self.socket) == zmq.POLLIN:
#                     s = self.socket.recv()
#                     s = s[len(MAG_TYPE)::]
#                     [ant, azi, sec, tic, sps, data] = unpackRadData(s)
#                     print("ant %d,\tazimuth %f,\tsec %d,\ttic %d" % (ant, azi, sec, tic))
#         self.socket.close()
        
# sthread = RadSubscriber()        
athread = AzimuthSim()
rthread = RadProducer()

# sthread.start()
athread.start()
rthread.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

running = False

# sthread.join()
athread.join()
rthread.join()