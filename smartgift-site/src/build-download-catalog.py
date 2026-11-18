import json,pathlib,io,math,unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
from pypdf import PdfReader,PdfWriter
root=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((root/'dist/data/owned-giftsets.json').read_text(encoding='utf8'))
out=root/'dist/downloads';out.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Thai',r'C:\Windows\Fonts\tahoma.ttf'))
pdfmetrics.registerFont(TTFont('ThaiBold',r'C:\Windows\Fonts\tahomabd.ttf'))
W,H=A4;teal='#008b8d';orange='#ff7911';ink='#21313a'
def text(c,x,y,t,size=10,font='Thai',color=ink):
 c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,str(t))
def wrap(t,width,size=9):
 units=[]
 for char in t:
  if unicodedata.combining(char) and units:units[-1]+=char
  else:units.append(char)
 lines=[];line=''
 for unit in units:
  if line and pdfmetrics.stringWidth(line+unit,'Thai',size)>width:lines.append(line.rstrip());line=unit
  else:line+=unit
 if line:lines.append(line)
 return lines
def image(c,p,x,y,w,h):
 if not p['image']:
  text(c,x+18,y+h/2,'ติดต่อขอภาพสินค้ารุ่นนี้',11,color=teal);return
 im=Image.open(root/'dist'/p['image'].lstrip('/')).convert('RGB');im.thumbnail((750,650))
 buf=io.BytesIO();im.save(buf,format='JPEG',quality=82,optimize=True);buf.seek(0)
 c.drawImage(ImageReader(buf),x,y,w,h,preserveAspectRatio=True,anchor='c')
 c.setFillColorRGB(1,1,1,alpha=.82);c.roundRect(x+w-61,y+3,58,13,3,stroke=0,fill=1)
 text(c,x+w-57,y+7,'Smart Gift',7,color=teal)
def footer(c,page):
 c.setStrokeColorRGB(.86,.91,.91);c.line(30,31,W-30,31)
 text(c,30,20,'SmartGift Thailand  |  LINE @smartgiftthailand',8,color=teal)
 for x,label,number in [(30,'094 464 8884','+66944648884'),(140,'02 871 5599','+6628715599'),(250,'02 871 6399','+6628716399')]:
  text(c,x,8,label,8,color=teal)
  c.linkURL('tel:'+number,(x,5,x+95,16),relative=0)
 text(c,W-65,17,str(page),8)
 c.linkURL('https://line.me/R/ti/p/@smartgiftthailand',(30,17,350,29),relative=0)
full=out/'smartgift-gift-sets.pdf';c=canvas.Canvas(str(full),pagesize=A4,pageCompression=1)
c.setTitle('แค็ตตาล็อกชุดของขวัญ SmartGift Thailand');c.setAuthor('SmartGift Thailand')
text(c,35,H-60,'SmartGift',31,'ThaiBold',teal);text(c,35,H-95,'ชุดของขวัญสำหรับองค์กร',24,'ThaiBold')
text(c,35,H-127,f"{len(data['items']):,} แบบ  |  14 หมวดหมู่",15)
text(c,35,H-161,'สั่งขั้นต่ำเพียง 10 ชุดต่อแบบ',19,'ThaiBold',orange)
text(c,35,H-188,'เลือกชุดที่เหมาะกับผู้รับ พร้อมปรับโลโก้สำหรับแบรนด์คุณ',11)
text(c,35,H-225,'เลือกหมวดที่ต้องการ',13,'ThaiBold',teal)
page=2;ranges=[]
for i,cat in enumerate(data['categories']):
 total=math.ceil(cat['count']/6);ranges.append((cat,page,page+total-1));y=H-254-i*25
 text(c,35,y,cat['name'],11);text(c,365,y,f"{cat['count']} แบบ",10);text(c,470,y,f'หน้า {page}',10)
 c.linkRect('',f'cat-{cat["slug"]}',(30,y-5,W-30,y+16),relative=0,thickness=0)
 page+=total
for j,line in enumerate(['ภาพและรายการสินค้าจากแค็ตตาล็อกที่ SmartGift จัดเตรียม','สี งานโลโก้ แพ็กเกจ ราคา และกำหนดส่ง ยืนยันในใบเสนอราคา','ภาพโลโก้เป็นตัวอย่างการตกแต่งสินค้า ไม่ใช่การรับรองจากแบรนด์']):text(c,35,145-j*18,line,9,color='#61737a')
footer(c,1);c.showPage();page=2
for cat,start,end in ranges:
 products=[p for p in data['items'] if p['category']==cat['slug']]
 for offset in range(0,len(products),6):
  if offset==0:c.bookmarkPage('cat-'+cat['slug'])
  text(c,30,H-36,'SmartGift Thailand',16,'ThaiBold',teal);text(c,30,H-61,cat['name'],16,'ThaiBold')
  text(c,30,H-81,'ขั้นต่ำ 10 ชุดต่อแบบ | ขอราคาและยืนยันรายละเอียดผ่าน LINE @smartgiftthailand',8.5)
  for n,p in enumerate(products[offset:offset+6]):
   col=n%2;row=n//2;x=30+col*275;top=H-100-row*231;cw=260;ch=219
   c.setStrokeColorRGB(.86,.91,.91);c.setFillColorRGB(1,1,1);c.roundRect(x,top-ch,cw,ch,6,stroke=1,fill=1)
   image(c,p,x+7,top-155,cw-14,148)
   text(c,x+10,top-170,p['sku'],12,'ThaiBold',teal)
   summary=p['contents'].replace(' + ',' / ')
   lines=wrap(summary,cw-20,8.5)
   for k,line in enumerate(lines[:2]):text(c,x+10,top-186-k*13,line+('…' if k==1 and len(lines)>2 else ''),8.5)
  footer(c,page);c.showPage();page+=1
c.save()
reader=PdfReader(full);manifest=[{'slug':'all','name':'แค็ตตาล็อกชุดของขวัญฉบับรวม','count':len(data['items']),'url':'/downloads/'+full.name,'bytes':full.stat().st_size,'pages':len(reader.pages)}]
for cat,start,end in ranges:
 writer=PdfWriter()
 for number in range(start-1,end):writer.add_page(reader.pages[number])
 writer.add_metadata({'/Title':cat['name']+' | SmartGift Thailand','/Author':'SmartGift Thailand'})
 file=out/('smartgift-'+cat['slug']+'.pdf')
 with file.open('wb') as f:writer.write(f)
 manifest.append({'slug':cat['slug'],'name':cat['name'],'count':cat['count'],'url':'/downloads/'+file.name,'bytes':file.stat().st_size,'pages':end-start+1})
(root/'dist/data/downloads.json').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf8')
assert sum(x['count'] for x in manifest[1:])==len(data['items'])
assert len(reader.pages)==page-1
print(json.dumps({'files':len(manifest),'fullPages':len(reader.pages),'fullMB':round(full.stat().st_size/1e6,1),'sets':len(data['items'])},ensure_ascii=False))
