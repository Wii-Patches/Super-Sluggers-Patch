import sys
from PIL import Image
def grid(paths, out, cols=3, w=320):
    ims=[Image.open(p).convert('RGB') for p in paths]
    h=int(ims[0].height*w/ims[0].width); ims=[i.resize((w,h)) for i in ims]
    rows=(len(ims)+cols-1)//cols
    g=Image.new('RGB',(w*cols,h*rows))
    for i,im in enumerate(ims): g.paste(im,((i%cols)*w,(i//cols)*h))
    g.save(out)
if __name__=='__main__': grid(sys.argv[2:], sys.argv[1])
