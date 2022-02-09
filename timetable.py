# -*- coding: utf-8 -*-

import numpy as np
from unicodedata import normalize
import lxml.etree as et
import hashlib 

class Room:

    def __init__(self, roomDict):
          
        self.code = roomDict['Sala'].lstrip().rstrip()
        self.bloco = self.code[0]
        self.type = roomDict['Tipo']
        self.size = int( roomDict['Capacidade'] )
        
    def getBuildingName(self):
        return "Bloco" + self.bloco
        
    def getXmlElement(self):
        e = et.Element("Room")
        et.SubElement(e,"Name").text = self.code
        et.SubElement(e,"Building").text = "Bloco" + self.bloco
        et.SubElement(e,"Capacity").text = str(30000)
        et.SubElement(e,"Comments").text = ""
        return e

class Tag:
    
    def __init__(self, tagStr, tagType = ""):
        self.name = tagStr
        self.type = tagType
        
    def __key(self):
        return self.name
        
    def __eq__(self,other):
        return self.__key() == other.__key()
    
    def __ne__(self,other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash( self.__key())

    def getXmlElement(self):
        
        e = et.Element("Activity_Tag")
        e.text = self.name
        return e        

    def getXmlDefinition(self):
        e = et.Element("Activity_Tag")
        et.SubElement(e,"Name").text = self.name
        et.SubElement(e,"Comments").text = ""
        return e

class SubGroup:
    
    def __init__(self, string):
    
        self.semester = string[0:2]
        self.course = string[2:5]
        
        if ( len(string)  == 6):
            self.sub = string[5]
        else: 
            self.sub = ""            
            
    def isMaster(self):
        return self.sub == ""
            
    def __key(self):
        return (self.course,self.semester,self.sub)
        
    def __eq__(self,other):
        
        if isinstance( other, self.__class__):
            return self.__key() == other.__key()
        else:
            return False
        
    def __ne__(self,other):

        return not self.__eq__(other)       
       
    def __hash__(self):
        return hash( self.__key() )
        
    def __str__(self):
        if (self.isMaster() ):
            return self.semester + self.course        
        else:
            return self.semester + self.course + self.sub                                   

    def getXmlElement(self):
        subgroup = et.Element("Subgroup")
        et.SubElement(subgroup,"Name").text = str(self)
        et.SubElement(subgroup,"Number_of_Students").text = "0"
        return subgroup
     
class Student:
           
    def __init__(self, string):

        if (string == None):       
            self.empty = True
            splited = []
        else:
            self.empty = False
            splited = string.lstrip().rstrip().split("/")
        
        self.classes = []

        for c in splited:
            s = c.lstrip().rstrip()
            listafases=list(range(1,11))
            listafases.append(99)
            assert any([ s[2:5] == "60" + str(c) for c in range(1,9) ] ) and  any([ s[0:2] == str(c).zfill(2) for c in listafases ] ), "Código da turma deve ser fase (2 dígitos) + curso (3 dígitos)"
            #assert any([ s[2:5] == "60" + str(c) for c in range(1,9) ] ) and  any([ s[0:2] == str(c).zfill(2) for c in range(1,11) ] ), "Código da turma deve ser fase (2 dígitos) + curso (3 dígitos)"
#            if (s != u"" ):
            self.classes.append(  s  )

    def __add__(self,a):        
        b = Student(None)    
        if (a.empty == True) and (self.empty == True):
            return b
        else:
            b.classes = list( self.toSet().union(a.toSet() ) )   
            b.empty = False
        return b

    def size(self):
        if (self.empty == False):
            return len( self.classes )
        else:
            return 1            
            
    def __hash__(self):
        return hash( u"".join( sorted(self.classes) )  )          
            
    def __str__(self):
        
        return "+".join( self.classes )

    def __eq__(self,other):
        
        if isinstance(other, self.__class__):
            return set( other.classes ) == set( self.classes ) 
        
    def __ne__(self,other):
        
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
            
    def toSet(self):
        
        return set( self.classes )
        
    def getXmlElements(self):

        element_lst = []
               
        for s in self.classes:
            xml = et.Element("Students")
            xml.text = s
            element_lst.append( xml )           
        
        return element_lst

    def isSubset(self,main):           
        return self.toSet().issubset( main.toSet()  )

class Teacher:
    
    def __init__(self, string ):
        
        self.name = string.lstrip().rstrip()
        short  = u".".join( [ self.name.split(" ")[0] , self.name.split(" ")[-1] ] )
        self.short =  short 

    def __str__(self):
        
        return self.short.__str__()

    def __eq__(self,other):
        
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        
    def __ne__(self,other):
        
        if isinstance(other, self.__class__):
            return not self.eq(other)

    def __lt__(self, other):
        return self.name.__lt__( other.name )

    def __le__(self, other):
        return self.name.__le__( other.name )
    
    def __gt__(self, other):
        return self.name.__gt__( other.name )
    
    def __ge__(self, other):
        return self.name.__ge__( other.name )
    
    def getXmlElement(self, withComment = True, definition = True):
        teacher = et.Element("Teacher")
        if (definition):
            et.SubElement(teacher,"Name").text =  self.short
        else:
            teacher.text =  self.short
        if (withComment): et.SubElement(teacher, "Comments").text = self.name 
        return teacher
        
    def __key(self):
        return (self.name , self.short)
        
    def __hash__(self):
        return hash( self.__key() )

class Subject:
           
    def __init__(self, string ):
       
        assert  len( string.split(" - ") )  > 1 , "Invalid Subject Definition" + string
        self.code, self.name = string.lstrip().rstrip().split(" - ")

        if ( self.code.find("/") != -1 ):
            self.multicode = True
            self.grad = True
            self.pos = False
        else:
            self.multicode = False           
            if (self.code[0:3] == "EMB"):
                self.grad = True
                self.codeLetters, self.codeNumber = ( self.code[0:3] , self.code[3:] ) 
            else:
                self.grad = False
                
            if (self.code[0:3] == "ECM") or (self.code[0:3] == "ESE"):  
                self.pos =  True
                self.codeLetters, self.codeNumber = ( self.code[0:3] , self.code[3:] ) 
            else:
                self.pos = False
    
    def subjectType(self):
        if (self.grad): return Tag("Aula")
        elif (self.pos): return Tag("Pos")
        raise ValueError("Código de Disciplina não reconhecido: "+ self.code)

    def __str__(self):
        if (not self.multicode):
            return self.codeLetters + self.codeNumber      
        else:
            return self.code
#        if (self.grad == True):
#            return self.code.split(" ")[1].__str__()
#        else: return self.code            
            
    def __eq__(self,other):
        
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        
    def __ne__(self,other):
        
        if isinstance(other, self.__class__):
            return not self.eq(other)
            
    def __lt__(self, other):
        return self.code.__lt__( other.code )

    def __le__(self, other):
        return self.code.__le__( other.code )
    
    def __gt__(self, other):
        return self.code.__gt__( other.code )
    
    def __ge__(self, other):
        return self.code.__ge__( other.code )     
        
    def __key(self):
        return (self.code , self.name)
        
    def __hash__(self):
        return hash( self.__key() )
            
    def getXmlElement(self,withComment = False, definition = True):
        subject = et.Element("Subject")
        if (definition):
            et.SubElement(subject,"Name").text = str(self)
        else:
            subject.text = str(self)
        if (withComment): et.SubElement(subject, "Comments").text = normalize('NFKD', self.name ).encode("ASCII","ignore")
        return subject
