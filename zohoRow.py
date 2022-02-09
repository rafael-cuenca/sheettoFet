# -*- coding: utf-8 -*-
"""
Created on Tue May 30 20:59:21 2017

@author: diogo
"""

from timetable import *
import lxml.etree as et

class zohoRow:
    
    def __init__(self,row):
        
        self.row = row        
        self.teacher = Teacher(row[u'Professor'])        
        self.subject = Subject( row[u'Código - Nome'] )        
        self.numOfTeachers = int( row[u'Número de professores'] )
        self.teacherTime =  float( row[u'Carga Did\xe1tica'] )
        self.teacherName = row[u'Professor']
        self.mainclass = self.row[u'Turma']
        self.responsable = row[u"Indicação de Horário"]                
        self.theoricalTime = float( row[u'Número créditos aula teórica'] )
        self.practicalTime = float( row[u'Número de créditos aula prática'] )
        self.format = row[u'Formato']
        self.roomType = row[u'Ambiente']
        
        if (self.subject.grad == True):
            self.setGroups()                      
            self.numOfStudents = float( row[u'Vagas'] ) / self.numOfTeachers       
    
            if (self.theoricalGroup.size() == 1) and (self.practicalGroup.size() == 1) and (self.numOfTeachers == 1):
                self.standalone = True
            else:
                self.standalone = False
        else:
            self.numOfStudents = 0            
            self.mainSet = Student(None)
            self.practicalGroup = Student(None)
            self.theoricalGroup = Student(None)    
            
    def __key(self):
        return (self.mainclass, self.numOfStudents, self.numOfTeachers, self.subject, self.practicalGroup, self.theoricalGroup, self.teacherName, self.theoricalTime, self.practicalTime )
    
    def __eq__(self, other):
        return self.__key() == other.__key()
        
    def setGroups(self):

        self.mainSet = Student( self.row[u'Turma']  )
        
        numTheorySets    = int( self.row[u'Número de turmas agrupadas aula teórica'] )
        numPracticalSets = int( self.row[u'Número de turmas agrupadas aula prática'] )
        
        if (numTheorySets  <= 1) and (self.row[u'Turmas teóricas agrupadas'].rstrip() == u""):
            self.row[u'Turmas teóricas agrupadas'] = self.row[u'Turma']                                               
            numTheorySets = 1   
            
        if (numPracticalSets <= 1) and (self.row[u'Turmas práticas agrupadas'].rstrip() == u""):    
            self.row[u'Turmas práticas agrupadas'] = self.row[u'Turma']                                               
            numPracticalSets = 1

        self.theoricalGroup = Student( self.row[u'Turmas teóricas agrupadas'] )
        self.practicalGroup = Student( self.row[u'Turmas práticas agrupadas'] )

        if (numTheorySets    != self.theoricalGroup.size() ): raise ValueError("Número de turmas teóricas e agrupamento teórico não confere. \n " + str(self) )
        if (numPracticalSets != self.practicalGroup.size() ): raise ValueError("Número de turmas práticas e agrupamento prático não confere. \n " + str(self) )
            
        if ( not self.mainSet.isSubset( self.theoricalGroup ) ):  raise ValueError("Turma não contida no agrupamento teórico. " + str(self) )
        if ( not self.mainSet.isSubset( self.practicalGroup ) ):  raise ValueError("Turma não contida no agrupamento prático  " + str(self) )        
        if ( not self.practicalGroup.isSubset( self.theoricalGroup ) ):  raise ValueError("Nem todos os códigos no agrupamento prático estão contidos no agrupamento teórico. " + str(self) )

            
    def equalGroups(self):
        return self.practicalGroup == self.theoricalGroup        
        
    def checkPracticalGroup(self):      
        return len( self.practicalGroup.classes ) == self.numPracticalSets

    def singleTeacher(self):
        return self.numOfTeachers == 1
        
    def related(self, other):
        return ( self.subject, self.theoricalGroup ) == ( other.subject, other.theoricalGroup )
        
    def __str__(self):
        s = ""
        for d in self.row.items():
            s +=  d[0] + ": " + d[1] + "\n"
        return s