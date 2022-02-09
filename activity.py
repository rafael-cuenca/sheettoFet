# -*- coding: utf-8 -*-
"""
Created on Tue May 30 21:03:42 2017

@author: diogo
"""

from timetable import *
from tabulate import tabulate
from copy import copy
RES = 5

class singleActivity:
    
    Id = 0
    
    def __init__(self,subject):
        
        singleActivity.Id += 1
        self.Id = singleActivity.Id       
        self.rowList = []
        self.subject = subject       
        self.time = 0.0
        self.teacherSet  = set()
        self.tagSet = set()
        self.teacherTime = {}
        self.teacherPracticalTime = {}
        self.teacherTheoreticalTime = {}        
        self.students = Student(None)
        self.numOfStudents = 0.0
        self.semesterSet = set()
        self.responsable = set()
        self.format = ""
    
    def add(self, row, time ):

        self.format = row.format
        self.responsable.add(row.responsable )
        self.numOfStudents += row.numOfStudents 
        if (time > 0):
            self.rowList.append(row)
            if not (row.teacher in self.teacherSet):
                self.teacherSet.add( row.teacher )
                self.teacherTime[ row.teacher.name ] = 0.0   
                self.teacherPracticalTime[ row.teacher.name ] = 0.0   
                self.teacherTheoreticalTime[ row.teacher.name ] = 0.0   
                self.time += time
            
            self.students += row.mainSet           
            self.teacherTime[ row.teacher.name ] += time
            if (self.time == 0): self.time = time
            if (self.subject.grad == True):
                self.semesterSet.add( int( SubGroup( str(row.mainSet) ).semester ))

    def __str__(self):

        s  = "Código da Disciplina: " + self.subject.code + "\n"
        s += "Disciplina: " + self.subject.name  + "\n"
        s += "Professor(es): "
        if ( len(self.teacherSet) < 2):
            s += " , ".join( [str(t.name) for t in self.teacherSet ] ) + "\n" 
        else:
            s += " , ".join( [ " ".join( [ str(t.name) , "".join( ["(" , str(self.teacherTime[unicode(t.name)] / self.students.size() ), " h.a. )"] ) ] )    for t in self.teacherSet ] ) + "\n"  
        s += "Turmas Agrupadas: " + str(self.students) + "\n"
        s += "Vagas oferecidas: " + str(self.numOfStudents) + "\n"
        s += "Carga Horária: " + str(self.time) + " h.a."
        return s
        
    def getXmlElement(self , gid = 0, totalTime = 0, tags = [] ):
        
        activity = et.Element("Activity")             

        self.tagSet.add( self.subject.subjectType()  )
        if (self.subject.grad == True):
            self.tagSet.add( Tag("T" + str( int(self.numOfStudents)  ) , tagType = "space"  )   )
    
        if len(self.responsable) != 1 :            
            print( "Problema na definição do responsável pela definição do horário")
            print( self )
            
        dictH = {u'Coord. Aeroespacial': 'H_Aero', u'Coord. Automotiva': 'H_Auto', u'Coord. BCT': 'H_BCT', u'Coord. Ferrovi\xe1ria e Metrovi\xe1ria': 'H_Ferro', u'Coord. Infraestrutura': 'H_Infra', u'Coord. Mecatr\xf4nica': 'H_Meca', u'Coord. Naval': 'H_Naval', u'Coord. PPGESE': 'H_PosESE',u'Coord. P\xf3s-ECM': 'H_PosECM',u'Coord. Transporte e Log\xedstica': 'H_Trans', u'Departamento': 'H_EMB'}

        for r in self.responsable : self.tagSet.add( Tag( dictH[r] ) )    

        activity.append( self.subject.getXmlElement(withComment = False, definition = False)  )
        
        for tag in self.tagSet:  activity.append( tag.getXmlElement() )

        for t in set( self.teacherSet ):
            activity.append( t.getXmlElement(withComment = False, definition = False) )
        
        for e in self.students.getXmlElements(): activity.append(e)
            
        et.SubElement( activity, "Duration" ).text = str(int( self.time  ) ) 
        et.SubElement( activity, "Total_Duration" ).text = str( int( totalTime )  if gid != 0 else int( self.time )  ) 
        et.SubElement( activity, "Id" ).text = str( self.Id )          
        et.SubElement( activity, "Activity_Group_Id" ).text = str(gid)
        et.SubElement( activity, "Active" ).text = "true"
        et.SubElement( activity, "Comments" ).text = "" + self.rowList[0].roomType

        return activity
        
class groupActivity(list):  

    def getFormat(self):
        
        if ( not all( [ self[0].students == a.students for a in self ] ) ):
            s = self[0].students.classes[0]
            time = []
            for a in self:
                if (s in a.students.classes):
                    time.append(str(int(a.time)))
            return "+".join(time)
        else:
            return "+".join([ str(int(a.time))  for a in self])
            
    def reFormat(self, fmt ):
        
        rule = [float(t) for t in fmt.split("+") ] 
        
        assert int( self.getTotalTime() ) == int( sum( rule ) ), "Invalid formation for this activity"

        assert all( [self[0].teacherSet == a.teacherSet for a in self ] ) , "Can not reformat, problem with teacherSet"
        assert all( [self[0].students   == a.students   for a in self ] ) , "Can not reformat, problem with Student Set"
        
        if len (self[0].teacherSet) > 1 :
            assert all( [self[0].teacherTime   == a.teacherTime   for a in self ] ) , "Can not reformat, problem with Teacher Time"
        
        while (len(self) != len(rule)):
            if (len(self) > len(rule)) : self.pop()
            elif (len(self) < len(rule)):
                self.append( copy(self[0]) )
                singleActivity.Id += 1
                self[-1].Id = singleActivity.Id

        for n in range(len(rule)):
                self[n].time = rule[n]
                                             
    def getMinSemester(self):
        m = -1
        if (self[0].subject.grad == True):
            s = []
            for a in self:
                s.append( min(a.semesterSet ) )
            return min(s)
        else:
            return -1
       
    def __init__(self, x ):

        self.append(x)        

    def toHtml(self):
        
        subject = self[0].subject
        header = u"".join( ["<p>","<b>Disciplina:</b> ",subject.code," - ",subject.name,"</p>"]) 
        data = []        
        
        if all( [ a.teacherSet == self[0].teacherSet for a in self ] ) and all( [ a.students == self[0].students for a in self ] ):
            
            dic = {}
            dic["Turmas"] = str(self[0].students)
            dic["Professor(es) (C.H.)"] = "\n".join( [ "".join( [t.name, " (", str( sum( [ a.teacherTime[unicode(t.name)] / a.students.size() for a in self ] ) ), ")" ]  ) for t in a.teacherSet ]  )
            dic["Vagas"] =  str( int(self[0].numOfStudents) )               
            dic["Carga Horária"] = str( sum( [ a.time for a in self] ) )
            data.append(dic)      
            
        else:
            for a in self:
                dic = {}
            
                dic["Turmas"] = str(a.students)
                dic["Professor(es) (C.H.)"] = "\n".join( [ "".join( [t.name, " (", str(a.teacherTime[unicode(t.name)] / a.students.size() ), ")" ]  ) for t in a.teacherSet ]  )
                dic["Vagas"] =  str( int(a.numOfStudents) )   
                dic["Carga Horária"] = str(a.time)
            
                data.append(dic)                               
            
        fields = data[0].keys()            
        tableData= [ [ t[f].decode('utf8') for f in fields ] for t in data ]   
        table = tabulate( tableData ,  headers= fields , tablefmt="html").replace(u"<table>",u"<table border=1>")
        table = table.replace("<td>","<td style=\"white-space:pre-wrap ; word-wrap:break-word;\">")            
        return u"\n".join( [header,table,u"<p></p>"])

    def __str__(self):
        s = str(self[0] ) + "\n"
        for x in self[1:]:
            s += "   |   " + "\n"
            splited = [ "   |   " + line for line in str(x).split("\n") ]
            splited[3] = splited[3].replace("   |   ","   |-> ") 
            s +="\n".join(splited) + "\n"

        return s + "\n"
        
    def getXml(self , gid = 0, totalTime = 0):
        pass

    def gid(self):
        
        if (not self.isSplited() ):
            return 0
        else:
            return self[0].Id            

    def getTeacherTotalTime(self, t):
        return sum( [ a.teacherTime[unicode(t.name)] / a.students.size() if (t in a.teacherSet) else 0 for a in self ] )

    def getTotalTime(self):
        return sum( [ x.time for x in self ]  ) 

    def isSplited(self):
        
        if (len(self) < 2):
            return False

        mainTeacherSet = self[0].teacherSet
        
        if any( [ p.teacherSet != mainTeacherSet for p in self[1:] ]  ):
            return False
            
        mainStudents = self[0].students
           
        if any( [ p.students != mainStudents for p in self[1:] ]  ):
            return False
            
        return True          
        
    def getConstrainList(self):
        constrainList = []
        if (len(self) > 1):
            constrainList.append( minDays(self[0],self[1],days = 2) )
        if (len(self) > 2):
            constrainList.append( groupActivities(self[1:] ) )
        return constrainList

def groupActivities( activityList ):
    
    if ( len(activityList) == 1):
        raise ValueError("Não é possível agrupar uma só atividade")
    elif ( len(activityList) == 2):
        constrain = et.Element("ConstraintTwoActivitiesGrouped")          
    elif ( len(activityList) == 3):
        constrain = et.Element("ConstraintThreeActivitiesGrouped")          
    else:
        raise ValueError("Não é possível agrupar mais de três atividades")

    et.SubElement( constrain, "Weight_Percentage" ).text = str(100)
    et.SubElement( constrain, "First_Activity_Id" ).text  = str( activityList[0].Id )
    et.SubElement( constrain, "Second_Activity_Id" ).text = str( activityList[1].Id )
    et.SubElement( constrain, "Active" ).text = "true"
    et.SubElement( constrain, "Comments" ).text = ""

    if ( len(activityList) == 3): et.SubElement( constrain, "Third_Activity_Id" ).text = str( activityList[2].Id )
    
    return constrain   

def minDays(a,b , days = 2):

    constrain = et.Element("ConstraintMinDaysBetweenActivities")                            
    et.SubElement( constrain, "Weight_Percentage" ).text = str(100)
    et.SubElement( constrain, "Consecutive_If_Same_Day" ).text = "false"        
    et.SubElement( constrain, "Number_of_Activities" ).text = str(2)
    et.SubElement( constrain, "Activity_Id" ).text = str( a.Id )
    et.SubElement( constrain, "Activity_Id" ).text = str( b.Id )
    et.SubElement( constrain, "MinDays" ).text = str( days )
    et.SubElement( constrain, "Active" ).text = "true"
    et.SubElement( constrain, "Comments" ).text = ""

    return constrain
       
        
        
        
        