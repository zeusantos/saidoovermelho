import sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC=sys.argv[1]; OUT=sys.argv[2]
W,H,FPS=1080,1920,30
img=Image.open(SRC).convert("RGB")
IW,IH=img.size
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s: ImageFont.truetype(p,s)
SUN=(255,196,0); WHITE=(255,255,255)
# (start,end, crop_from, crop_to, lines[(text,font,color)], darken)
S=[(0,3.6,(750,1000,1125),(750,1250,960),[("SUA CONTA DE LUZ",f(B,78),WHITE),("NO MÍNIMO.",f(B,110),SUN)],0.0),
   (3.6,7.4,(650,1500,860),(860,1440,800),[("Projeto, instalação",f(B,70),WHITE),("e homologação",f(B,70),WHITE),("com quem entende.",f(R,58),SUN)],0.0),
   (7.4,11.0,(700,860,640),(780,780,560),[("O sol de Recife",f(B,80),WHITE),("trabalhando pra você.",f(B,70),SUN)],0.0),
   (11.0,15.0,(750,1000,1125),(750,1000,1040),None,0.62)]
DUR=15.0; XF=0.4
grad=Image.new("L",(1,H))
for y in range(H): grad.putpixel((0,y),int(max(0,(y-H*0.5)/(H*0.5))**1.4*215))
grad=grad.resize((W,H)); black=Image.new("RGB",(W,H),(0,0,0))
def ease(t): return t*t*(3-2*t)
def frame_bg(s,t):
    a,b,c0,c1,_,_=s; p=ease(min(1,max(0,(t-a)/(b-a))))
    cx,cy,w=[(c0[i]+(c1[i]-c0[i])*p)*IW/1500 for i in range(3)]; h=w*H/W
    cy=min(max(cy,h/2),IH-h/2); cx=min(max(cx,w/2),IW-w/2)
    return img.resize((W,H),Image.LANCZOS,box=(cx-w/2,cy-h/2,cx+w/2,cy+h/2))
def text(fr,lines,lt):
    al=min(1,lt/0.5); dy=int((1-ease(al))*60)
    fr=Image.composite(black,fr,grad)
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    tot=sum(l[1].size+22 for l in lines); y=H-260-tot+dy
    d.rectangle((80,y-40,80+140,y-30),fill=SUN+(int(255*al),))
    for t,fn,c in lines:
        d.text((80+3,y+3),t,font=fn,fill=(0,0,0,int(140*al)))
        d.text((80,y),t,font=fn,fill=c+(int(255*al),)); y+=fn.size+22
    return Image.alpha_composite(fr.convert("RGBA"),ov).convert("RGB")
def endcard(fr,lt,dk):
    fr=Image.blend(fr,black,dk); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    def C(t,fn,y,c,a):
        w=d.textlength(t,font=fn); d.text(((W-w)/2,y),t,font=fn,fill=c+(int(255*a),))
    a1=min(1,lt/0.6); a2=min(1,max(0,(lt-0.6)/0.6)); a3=min(1,max(0,(lt-1.3)/0.6))
    r=int(70+10*a1); cx,cy=W//2,640
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=SUN+(int(255*a1),))
    import math
    for k in range(12):
        an=k*math.pi/6; d.line((cx+math.cos(an)*(r+22),cy+math.sin(an)*(r+22),cx+math.cos(an)*(r+60),cy+math.sin(an)*(r+60)),fill=SUN+(int(255*a1),),width=10)
    C("ENERGY",f(B,130),800,WHITE,a1); C("CLEAN",f(B,130),940,SUN,a1)
    C("Energia solar residencial e comercial",f(R,46),1120,WHITE,a2)
    bw,bh,by=760,130,1330
    d.rounded_rectangle(((W-bw)/2,by,(W+bw)/2,by+bh),radius=65,fill=SUN+(int(255*a3),))
    fb=f(B,56); t="PEÇA SEU ORÇAMENTO"; w=d.textlength(t,font=fb)
    d.text(((W-w)/2,by+(bh-56)/2-6),t,font=fb,fill=(20,20,20,int(255*a3)))
    C("Simulação gratuita • Fale no WhatsApp",f(R,40),1500,WHITE,a3)
    return Image.alpha_composite(fr.convert("RGBA"),ov).convert("RGB")
def render(s,t):
    fr=frame_bg(s,t); lt=t-s[0]
    return endcard(fr,lt,s[5]) if s[4] is None else text(fr,s[4],lt)
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
  "-c:a","aac","-movflags","+faststart",OUT],stdin=subprocess.PIPE)
for i in range(int(DUR*FPS)):
    t=i/FPS; k=max(j for j,s in enumerate(S) if s[0]<=t)
    fr=render(S[k],t)
    if k+1<len(S) and t>S[k][1]-XF:
        fr=Image.blend(fr,render(S[k+1],t),ease((t-(S[k][1]-XF))/XF))
    if t>DUR-0.5: fr=Image.blend(fr,black,(t-(DUR-0.5))/0.5*0.0)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
