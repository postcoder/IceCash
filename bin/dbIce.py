#!/usr/bin/python
# -*- coding: utf-8
import my
import os
import re

class trsc(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('idtrsc','d')
        self.addfield('nkassa','d')
        self.addfield('puttime','D')
        self.addfield('date','D')
        self.addfield('time','t')
        self.addfield('type','d')
        self.addfield('nkkm','d')
        self.addfield('ncheck','d')
        self.addfield('idkassir','d')
        self.addfield('ParamS','s')
        self.addfield('ParamI','d')
        self.addfield('ParamF1','f')
        self.addfield('ParamF2','f')
        self.addfield('ParamF3','f')

        self.record=['nkassa','date','time','type','nkkm','ncheck','idkassir','ParamS','ParamI','ParamF1','ParamF2','ParamF3']
        self.record_unload=['idtrsc','date','time','type','nkkm','ncheck','idkassir','ParamS','ParamI','ParamF1','ParamF2','ParamF3']

    def query_add(self,values):
        struct=self.set_values(self.record,values)
        return self.query_insert(struct)
    def query_select_from(self,id_trsc,nkassa):
        return self.query_select(self.record_unload)+" where idtrsc>"+id_trsc+" and nkassa="+nkassa

class price(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('shk','s')
        self.addfield('name','s')
        self.addfield('cena','f')
        self.addfield('ostatok','f')
        self.addfield('sheme','d')
        self.addfield('real','d')
        self.addfield('section','d')
        self.addfield('max_skid','f')
        self.addfield('type','d')
        self.addfield('minprice','f')
        self.addfield('maxprice','f')
        self.addfield('warning','d')

    def query_add(self,values):
        struct=self.set_all_values(values)
        return self.query_insert(struct)

    def query_find(self,fd,code):
        return self.query_all_select()+" where %s=%s" % (fd,str(code))

class price_shk(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('id','d')
        self.addfield('shk','s')
        self.addfield('name','s')
        self.addfield('cena','f')
        self.addfield('koef','f')

    def query_add(self,values):
        struct=self.set_all_values(values)
        return self.query_insert(struct)

    def query_find(self,code):
        return self.query_all_select()+" where shk=%s" % str(code)

class discount_card(my.table):
    def __init__ (self,dbname):
        my.table.__init__(self,dbname)
        self.addfield('number','d')
        self.addfield('name','s')
        self.addfield('text','s')
        self.addfield('isclose','d')
        self.addfield('type','d')
        self.addfield('procent','f')
        self.record=['number','procent']

    def query_find(self,card):
        return self.query_all_select()+" where number=%s" % str(card)
    
    def query_add(self,values):
        struct=self.set_values(self.record,values)
        return self.query_insert(struct)

class db(my.db):
    def __init__ (self):
        my.db.__init__(self,'IceCash','localhost','icecash','icecash1024')
        self.table_trsc=trsc('trsc')
        self.table_price=price('price')
        self.table_price_shk=price_shk('price_shk')
        self.table_discount_card=discount_card('discount_card')

    def load_price(self,fname):
        try:
            f = open(fname,'r')
        except:
            return 1
        line = f.readline()
        line=line.rstrip("\n\r")
        if line!='##@@&&':
            f.close()
            return 1
        if line=='@':
            f.close()
            return 1
        print "dbIce:clear_price:",self.clear_price()
        for line in f.readlines():
            if line=='':
                continue
            arr=line.split(';')
            code=arr[0]
            pref = code[0]
            if re.match(r'^#(\d)*$',code):
                (code,shk,n1,n2,cena)=arr[0:5]
                code=code.lstrip('#')
                n1=n1.decode('cp1251').encode('utf8')
                self.add_price_shk((code,shk,n1,cena,1))
            elif re.match(r'^(\d)*$',code):
                (code,shk,n1,n2,cena,ost,sheme,real,sect,k0,_type,k2,minp,maxp)=arr[0:14]
                n1=n1.decode('cp1251').encode('utf8')
                self.add_price((code,shk,n1,cena,ost,sheme,real,sect,k0,_type,minp,maxp,0))
        f.close()
        f=open(fname,'r+')
        f.readline()
        f.write("@")
        f.close()
        return 0

    def load_discount(self,fname):
        try:
            f = open(fname,'r')
        except:
            return 1
        #line=line.rstrip("\r\n")
        print "dbIce:clear_discount:",self.clear_discount()
        for line in f.readlines():
            if line=='':
                continue
            arr=line.split(';')
            if len(arr)>=2:
                self.add_discount((arr[0],arr[1]))
        f.close()
        os.remove(fname);
        return 0

    def unload_trsc(self,fname,id_trsc,nkassa):
        try:
            f = open(fname,'w')
        except:
            return 1
        f.write("#\r\n1\r\n0\r\n");
        print self.table_trsc.query_select_from(id_trsc,nkassa)
        t = self.get(self.table_trsc.query_select_from(id_trsc,nkassa))
        for line in t:
            rec=[]
            for i in line:
                rec.append(i)
            rec[1]=my.mydt2normdt(line[1])
            l=";".join(["%s" % str(v) for v in rec])
            l=l+"\r\n"
            f.write(l)
        f.close()
        return 0

    def add_trsc(self,values):
        return self.run(self.table_trsc.query_add(values))

    def add_discount(self,values):
        return self.run(self.table_discount_card.query_add(values))

    def add_price(self,values):
        return self.run(self.table_price.query_add(values))

    def add_price_shk(self,values):
        try:
            self.run(self.table_price_shk.query_add(values))
            return 0
        except:
            return 1

    def find_price_code(self,code):
        r=self.get(self.table_price.query_find('id',code))
        if not len(r):
            n=[]
        else:
            d=["%s" % v for v in r[0]]
            #d[2]=d[2].encode('utf8')
            n=d
        return n

    def find_price_shk(self,code):
        r=self.get(self.table_price.query_find('shk',code))
        if not len(r):
            n=self.get("select * from price_shk where shk=%s" % code)
            if not len(n):
                return []
            r=self.get(self.table_price.query_find('id',n[0][0]))
            if not len(r):
                return []
            d=["%s" % v for v in r[0]]
            d[1:3]=n[0][1:3]
            #d[2]=d[2].encode('utf8')
            return d
        else:
            d=["%s" % v for v in r[0]]
            #d[2]=d[2].encode('utf8')
            n=d
        return n

    def clear_price(self):
        self.run('delete from price_shk')
        return self.run('delete from price')

    def clear_discount(self):
        return self.run('delete from discount_card')

    def find_discount_card(self,card):
        r=self.get(self.table_discount_card.query_find(card))
        if not len(r):
            n=[]
        else:
            d=["%s" % v for v in r[0]]
            #d[2]=d[2].encode('utf8')
            #d[3]=d[3].encode('utf8')
            n=d
        return n
    

