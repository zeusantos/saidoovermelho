import sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC,OUT,LOGO=sys.argv[1:4]
W,H,FPS=1080,1920,30
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s: ImageFont.truetype(p,s)
SUN=(255,196,0); WHITE=(255,255,255); black=Image.new("RGB",(W,H),(0,0,0))
def ease(t): t=min(1,max(0,t)); return t*t*(3-2*t)
# ---- logo ----
def make_logo(scale=1.0):
    w,h=int(900*scale),int(260*scale); im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    cx,cy,r=int(130*scale),h//2,int(62*scale)
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=SUN)
    for k in range(12):
        a=k*math.pi/6; d.line((cx+math.cos(a)*(r+16*scale),cy+math.sin(a)*(r+16*scale),cx+math.cos(a)*(r+48*scale),cy+math.sin(a)*(r+48*scale)),fill=SUN,width=max(2,int(9*scale)))
    # leaf-ish stroke inside sun
    d.arc((cx-r*0.55,cy-r*0.55,cx+r*0.55,cy+r*0.55),200,340,fill=(255,255,255),width=max(2,int(8*scale)))
    x=int(250*scale)
    d.text((x,int(40*scale)),"ENERGY",font=f(B,int(92*scale)),fill=WHITE)
    d.text((x,int(130*scale)),"CLEAN",font=f(B,int(92*scale)),fill=SUN)
    return im.crop(im.getbbox())
logo=make_logo(1.0); logo.save(LOGO)
wm=make_logo(0.42)
grad=Image.new("L",(1,H))
for y in range(H): grad.putpixel((0,y),int(max(0,(y-H*0.45)/(H*0.55))**1.3*225))
grad=grad.resize((W,H))
topg=Image.new("L",(1,H))
for y in range(H): topg.putpixel((0,y),int(max(0,1-y/360)*150))
topg=topg.resize((W,H))
def base(fr):
    fr=Image.composite(black,fr,topg); fr=fr.convert("RGBA"); fr.alpha_composite(wm,(50,60)); return fr
def caption(fr,lines,lt,dur):
    fr=Image.composite(black,fr.convert("RGB"),grad).convert("RGBA")
    al=ease(lt/0.4)*(1-ease((lt-(dur-0.25))/0.25)); dy=int((1-ease(lt/0.4))*60)
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    tot=sum(fn.size+20 for _,fn,_ in lines); y=H-250-tot+dy
    d.rectangle((80,y-40,220,y-28),fill=SUN+(int(255*al),))
    for t,fn,c in lines:
        d.text((83,y+3),t,font=fn,fill=(0,0,0,int(150*al))); d.text((80,y),t,font=fn,fill=c+(int(255*al),)); y+=fn.size+20
    fr.alpha_composite(ov); return fr
def endcard(fr,lt):
    fr=fr.convert("RGB").filter(ImageFilter.GaussianBlur(6*ease(lt/0.6)))
    fr=Image.blend(fr,black,0.6*ease(lt/0.6)).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    a1,a2,a3=ease(lt/0.6),ease((lt-0.5)/0.5),ease((lt-1.0)/0.5)
    sc=0.85+0.15*a1; lg=logo.resize((int(logo.width*sc),int(logo.height*sc)),Image.LANCZOS)
    lg.putalpha(lg.getchannel("A").point(lambda v:int(v*a1)))
    ov.alpha_composite(lg,((W-lg.width)//2,650-lg.height//2))
    def C(t,fn,y,c,a):
        w=d.textlength(t,font=fn); d.text(((W-w)/2,y),t,font=fn,fill=c+(int(255*a),))
    C("Energia solar residencial e comercial",f(R,46),860,WHITE,a2)
    C("Recife e Região Metropolitana",f(R,40),925,SUN,a2)
    bw,bh,by=780,130,1150
    d.rounded_rectangle(((W-bw)/2,by,(W+bw)/2,by+bh),radius=65,fill=SUN+(int(255*a3),))
    fb=f(B,56); t="PEÇA SEU ORÇAMENTO"; w=d.textlength(t,font=fb)
    d.text(((W-w)/2,by+(bh-56)/2-6),t,font=fb,fill=(20,20,20,int(255*a3)))
    C("Simulação gratuita • Fale no WhatsApp",f(R,40),1320,WHITE,a3)
    fr.alpha_composite(ov); return fr
# segments: (src_start, src_end, speed, lines or "END")
SEG=[(0.0,2.3,0.85,[("CONTA DE LUZ",f(B,92),WHITE),("PESANDO NO BOLSO?",f(B,80),SUN)]),
     (2.3,4.1,0.75,[("A gente instala",f(B,80),WHITE),("energia solar",f(B,80),WHITE),("no seu telhado.",f(B,80),SUN)]),
     (6.4,7.8,0.6,[("Projeto  •  Instalação",f(B,64),WHITE),("Homologação",f(B,64),WHITE),("tudo com a gente.",f(R,58),SUN)]),
     (7.8,8.8,0.4,"END")]
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
  "-c:a","aac","-movflags","+faststart",OUT],stdin=subprocess.PIPE)
for a,b,sp,lines in SEG:
    dec=subprocess.Popen(["ffmpeg","-loglevel","error","-ss",str(a),"-t",str(b-a),"-i",SRC,"-vf",f"setpts=PTS/{sp},fps={FPS},scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
    frames=[]; n=0; dur=(b-a)/sp; last=None
    while True:
        raw=dec.stdout.read(W*H*3)
        if len(raw)<W*H*3: break
        fr=Image.frombytes("RGB",(W,H),raw); lt=n/FPS; n+=1; last=fr
        out=endcard(fr,lt) if lines=="END" else caption(base(fr),lines,lt,dur)
        p.stdin.write(out.convert("RGB").tobytes())
    if lines=="END":  # hold end card 1.5s more on frozen last frame
        for k in range(45):
            p.stdin.write(endcard(last,n/FPS+k/FPS).convert("RGB").tobytes())
p.stdin.close(); p.wait()
