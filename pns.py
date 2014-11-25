#!/usr/bin/env python2
# -*- encoding=UTF-8 -*-

import sys
import re
from array import *
PC=01000
mem=[0 for i in xrange(65535)]
min_adr=32766
max_adr=0


def equ(cnst):
    var=cnst.split("=")[0]
    
    exec("global "+var+";"+cnst)

def br(adr):
    return 0400+rel(adr)

def bne(adr):
    return 01000+rel(adr)

def beq(adr):
    return 01400+rel(adr)


def upd_pc():
    global PC
    global min_adr
    global max_adr
    min_adr=min(min_adr,PC)
    max_adr=max(max_adr,PC)

def org(adr):
    global PC
    PC=adr 
    upd_pc()



def rel(adr):
    global PC
    ofs=((adr/2)-((PC+2)/2)) & 0xff
    return ofs

def relm(adr):
    global PC
    ofs=((2+PC-adr)/2) & 0x2f
    return ofs
    
def main():
    global PC
    global mem
    args=sys.argv
    if len(args)<2:
	print"pns.py <filename>"
	return 0
    global in_filename
    filename=args[1]
    try:
	f=open(filename,"r")
    except IOError,err:
	print "Can't open %s" % (filename)
	quit(3)
    fl=f.readlines()
    f.close()

    pas=1
    while(pas<3):
     ln=1
     for line in fl:
	s=line;
	label_line=re.match(r'^(\w+:)',s)
	if label_line:
	    label=label_line.group(0)
	    s=re.sub(r"^\w+:","",s)
	    label=re.sub(r":.*","",label)
	    exec(label+"=PC")
	dec_number=re.match(r"\s*([0-9]+d)",s)
	if dec_number:
	    dns=dec_number.group(0)
	    dns=re.sub(r"\s+","",dns)
	    dns=re.sub(r"0+","",dns)
	    dns=re.sub(r"d\s*","",dns)
	    ons=oct(int(dns))
	    s=re.sub(r"[0-9]+d",ons,s)
	oct_number=re.match(r"^\s*([0-9]+)",s)
	if oct_number:
	    ons=oct_number.group(0)
	    ons=re.sub(r"\s+","",ons)
	    ons="0"+ons
	    s=re.sub(r"^\s*[0-9]+",ons,s)
	try:
	    r=eval(s)
	except (SyntaxError) :
	    r=None
	except (NameError):
	    if pas>1: print "error: "+str(ln),s
	    r=0
	    
	if isinstance(r,int):
	    mem[PC]=r
	    PC+=2
	    upd_pc()
	if isinstance(r,str):
	    st=r.decode('UTF-8').encode('KOI8-R')
	    if len(st) & 0x01:
		print "Warning line %d odd length of string, space added" % (ln)
		st=st+" "
	    for  i in xrange(len(st)/2):
		mem[PC]=ord(st[2*i])+256*ord(st[(2*i)+1])
		PC+=2
		upd_pc()
	ln+=1
     pas+=1
    print "begin "+oct(min_adr)+"\nend "+oct(max_adr)
    ofn=filename.split(".")[0]+".bin"
    oofn=filename.split(".")[0]+".oct"
    hfn=filename.split(".")[0]+".h"
    of=open(ofn,"w")
    oof=open(oofn,"w")
    hf=open(hfn,"w")
    of.write("%c%c" % ((min_adr & 0xff),min_adr>>8))
    of.write("%c%c" % (((max_adr-min_adr) & 0xff),(max_adr-min_adr)>>8))
    oof.write(oct(min_adr)+"\n")
    oof.write(oct(max_adr-min_adr)+"\n")
    hf.write('const uint16_t boot_rom[]={\n ')
    for i in xrange(min_adr,max_adr+1,2):
	s="%c%c" % ((mem[i] & 0xff),mem[i]>>8)
	oof.write(oct(i)+" : "+oct(mem[i])+"\n")
	of.write(s)
	hf.write("%s,\n" %(oct(mem[i])))
    of.close()
    oof.close()
    hf.write("};\n")
    
    
main()

