import numpy as np, wave, sys
SR=44100; DUR=float(sys.argv[2]); CUTS=[float(x) for x in sys.argv[3].split(",")]; END=CUTS[-1]
N=int(SR*DUR); L=np.zeros(N); Rr=np.zeros(N)
BPM=112; beat=60/BPM; t=np.arange(N)/SR
def add(sig,start,gain=1.0,pan=0.0):
    i=int(start*SR); 
    if i>=N: return
    s=sig[:N-i]*gain; L[i:i+len(s)]+=s*(1-pan)/1; Rr[i:i+len(s)]+=s*(1+pan)/1
def note(m): return 440*2**((m-69)/12)
def lp(x,a): 
    y=np.empty_like(x); acc=0.0
    for k in range(len(x)): acc+=a*(x[k]-acc); y[k]=acc
    return y
rng=np.random.default_rng(7)
# chords C G Am F (midi roots)
prog=[[60,64,67,72],[55,62,67,71],[57,60,64,69],[53,60,65,69]]
bar=4*beat; nb=int(np.ceil(DUR/bar))
for b in range(nb):
    ch=prog[b%4]; st=b*bar; n=int(bar*SR)+2000; tt=np.arange(n)/SR
    pad=sum(np.sin(2*np.pi*note(m)*tt*(1+d))*0.5+np.sin(4*np.pi*note(m)*tt)*0.12 for m in ch for d in(-0.003,0.003))
    env=np.minimum(1,tt/0.35)*np.minimum(1,(n/SR-tt)/0.3)
    add(pad*env*0.035,st)
    # bass on 8ths
    for e in range(8):
        tt2=np.arange(int(beat/2*SR))/SR; fq=note(ch[0]-24)
        bs=(np.sin(2*np.pi*fq*tt2)+0.3*np.sin(4*np.pi*fq*tt2))*np.exp(-tt2*5)
        add(bs*(0.16 if e%2 else 0.10),st+e*beat/2)
    # pluck arp 16ths
    arp=ch+[ch[1]+12,ch[2]+12]
    for e in range(16):
        m=arp[(e*3)%len(arp)]+12; tt2=np.arange(int(0.35*SR))/SR; fq=note(m)
        pl=(np.sin(2*np.pi*fq*tt2)+0.4*np.sin(4*np.pi*fq*tt2)+0.15*np.sin(6*np.pi*fq*tt2))*np.exp(-tt2*14)
        add(pl*0.05,st+e*beat/4,pan=0.35 if e%2 else -0.35)
# drums
nbeats=int(DUR/beat)+1
for k in range(nbeats):
    st=k*beat
    tt2=np.arange(int(0.4*SR))/SR; fr=45+110*np.exp(-tt2*30)
    kick=np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt2*9); add(kick*0.55,st)
    hn=rng.standard_normal(int(0.06*SR)); hn=hn-lp(hn,0.25); add(hn*np.exp(-np.arange(len(hn))/SR*60)*0.06,st+beat/2,pan=0.2)
    if k%2==1:
        cl=rng.standard_normal(int(0.15*SR)); cl=cl-lp(cl,0.08); add(cl*np.exp(-np.arange(len(cl))/SR*25)*0.12,st)
# whoosh before each cut
for c in CUTS[1:]:
    n=int(0.6*SR); w=rng.standard_normal(n); tt2=np.arange(n)/SR
    w=lp(w,0.05)+lp(w,0.2)*np.linspace(0,1,n); env=np.linspace(0,1,n)**2
    add(w*env*0.35,c-0.6,pan=0.0)
# impact on end card
n=int(2.0*SR); tt2=np.arange(n)/SR
boom=np.sin(2*np.pi*np.cumsum(38+60*np.exp(-tt2*8))/SR)*np.exp(-tt2*2.2)
cy=rng.standard_normal(n); cy=(cy-lp(cy,0.3))*np.exp(-tt2*3)
add(boom*0.7+cy*0.08,END)
mix=np.stack([L,Rr],1)
# master: fade in/out, soft clip, normalize
fade=np.ones(N); fi=int(0.05*SR); fo=int(1.2*SR); fade[:fi]=np.linspace(0,1,fi); fade[-fo:]=np.linspace(1,0,fo)
mix*=fade[:,None]; mix=np.tanh(mix*1.4); mix/=np.abs(mix).max()/0.89
w=wave.open(sys.argv[1],"wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype("<i2").tobytes()); w.close()
