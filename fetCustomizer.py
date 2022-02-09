# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 18:09:25 2017

@author: diogo
"""

from lxml.etree import Element, SubElement, tostring, parse, XMLParser
import itertools

class FetFile:
    
    def __init__(self,filename):
        
        self.parser = XMLParser(remove_blank_text=True)
        self.tree = parse(filename, parser = self.parser )
        self.root = self.tree.getroot()
        root = self.root
        self.xmlTeacherList = root.find("Teachers_List")
        self.xmlTimeConstrainList = root.find("Time_Constraints_List")
        self.xmlActivitiesList = root.find("Activities_List")
        self.xmlStudentsList = root.find("Students_List")
        self.xmlActivity_Tags_List = root.find("Activity_Tags_List")
        self.xmlRoomLst = root.find("Rooms_List")
        self.xmlBuildingLst = root.find("Buildings_List")
        self.xmlSpaceConstrainList = root.find("Space_Constraints_List")
        self.xmlSpaceList = root.find("Activities_List") 
        self.xmlTimeConstrainList = root.find("Time_Constraints_List")
        self.xmlTagLst = root.find("Activity_Tags_List")
        self.xmlSubjectLst = root.find("Subjects_List")
        
    def write(self,filename):
        
        f = open( filename ,"w") 
        f.write( tostring( self.tree , pretty_print = True, xml_declaration=True,  encoding='UTF-8').decode("utf-8") )
        f.close()
        
    def addStudentsGaps(self,gaps):
                           
        for student in gaps:
            
            base = Element("ConstraintStudentsSetMaxGapsPerWeek")
            SubElement( base, "Weight_Percentage").text = "100"
            SubElement( base, "Max_Gaps").text = str(gaps[student])
            SubElement( base, "Students").text = student
            SubElement( base, "Active").text = "true"
            SubElement( base, "Comments").text = ""
        
            if all( tostring( base ) != tostring(c) for c in self.xmlTimeConstrainList ):
                self.xmlTimeConstrainList.append(base)
    
    def addMaxDaysTeachers(self, f , maxDays):
        
        filteredList = filter( f , list( self.xmlTeacherList ) )        
        
        for teacher in filteredList :
            
            basic = Element( "ConstraintTeacherMaxDaysPerWeek" )
            SubElement( basic , "Weight_Percentage" ).text  = '100'
            SubElement( basic , "Teacher_Name" ).text  = teacher.find("Name").text
            SubElement( basic , "Max_Days_Per_Week" ).text  = str(maxDays)
            SubElement( basic,  "Active" ).text = "true"
            SubElement( basic,  "Comments" ).text = ""  
            
            if all( tostring( basic ) != tostring(c) for c in self.xmlTimeConstrainList ):
                self.xmlTimeConstrainList.append(basic)
 
    def addIndividualConstrains():
        pass

    def addRooms():
        pass
        
    def deactivateActivity(self, f ):
    
        filtered = filter( f , list( self.xmlActivitiesList ) )
    
        for activityElement in filtered:
            activityElement.find("Active").text = "false"

    def deactivateTimeRestriction(self, f ):
    
        filtered = filter( f , list( self.xmlActivitiesList ) )
    
        for activityElement in filtered:
            activityElement.find("Active").text = "false"
  
    def activateWithTag( self , tag ):
        self.activateActivity( lambda x : any([ tagXML.text == tag for tagXML in x.findall("Activity_Tag") ] ) )
    
    def deactivateWithTag( self , tag ):
        self.deactivateActivity( lambda x : any([ tagXML.text == tag for tagXML in x.findall("Activity_Tag") ] ) )
        
    def activateActivity(self, f ):
    
        filtered = filter( f , list( self.xmlActivitiesList)  )
    
        for activityElement in filtered:
            activityElement.find("Active").text = "true"

    def tagExists(self,tagName):
        return all( [ tag.find("Name").text != tagName for tag in self.xmlTagLst ] )

    def addTag(self,tagName, comment = ""):
      
        if self.tagExists(tagName):
            definitionTag = Element("Activity_Tag")        
            SubElement(definitionTag,"Name").text = tagName
            SubElement(definitionTag,"Comments").text = comment           
            self.xmlTagLst.append( definitionTag )        
        
    def setTag(self, f , tagName, comment = ""):
        
        self.addTag(tagName, comment = comment)
        
        filtered = filter( f , list( self.xmlActivitiesList ) )

        for activityElement in filtered:
           
            tagList = activityElement.findall("Activity_Tag")           
            if all( [ tag.text != tagName for tag in tagList] ):
                pos = [ list(activityElement).index(tag) for tag in tagList ]
                idx = 0 if pos == [] else max(pos)+1
                activityTag = Element("Activity_Tag")         
                activityTag.text = tagName                
                activityElement.insert(idx, activityTag )
                
    def removeTag(self, f , tagName, comment = ""):
               
        filtered = filter( f , list( self.xmlActivitiesList ) )

        for activityElement in filtered:
            for tag in activityElement.findall("Activity_Tag"):      
                if (tag.text == tagName):
                    activityElement.remove(tag)
                    
    def addPreferedTimes(self, lst, teacher = "", student = "" , subject = "", tag = "", duration = "" , active = "true", comment = "",  weight = 100):    

        if (tag != "" ): self.addTag(tag)
    
        constrain = Element("ConstraintActivitiesPreferredTimeSlots")
        SubElement(constrain,"Weight_Percentage").text = str(weight)
        SubElement(constrain,"Teacher_Name").text = teacher
        SubElement(constrain,"Students_Name").text = student
        SubElement(constrain,"Subject_Name").text = subject
        SubElement(constrain,"Activity_Tag_Name").text = tag
        SubElement(constrain,"Duration").text = ""
        SubElement(constrain,"Number_of_Preferred_Time_Slots").text = str( len( lst  ) )
        
        for datetime in lst:
            timeSlot = Element("Preferred_Time_Slot")        
            ( SubElement( timeSlot , "Preferred_Day").text , SubElement( timeSlot , "Preferred_Hour").text ) = datetime
            constrain.append(timeSlot)

        SubElement( constrain ,  "Active" ).text = active
        SubElement( constrain ,  "Comments" ).text = comment

        self.xmlTimeConstrainList.append(constrain)
        
    def addPreferredStartingTimes(self, lst, teacher = "", student = "" , subject = "", tag = "", duration = "" , weight = 100, active = "true", comment = ""):    

        if (tag != "" ): self.addTag(tag)
    
        constrain = Element("ConstraintActivitiesPreferredStartingTimes")
        SubElement(constrain,"Weight_Percentage").text = str(weight)
        SubElement(constrain,"Teacher_Name").text = teacher
        SubElement(constrain,"Students_Name").text = student
        SubElement(constrain,"Subject_Name").text = subject
        SubElement(constrain,"Activity_Tag_Name").text = tag
        SubElement(constrain,"Duration").text = ""
        SubElement(constrain,"Number_of_Preferred_Starting_Times").text = str( len( lst  ) )
        
        for datetime in lst:
            timeSlot = Element("Preferred_Starting_Time")        
            ( SubElement( timeSlot , "Preferred_Starting_Day").text , SubElement( timeSlot , "Preferred_Starting_Hour").text ) = datetime
            constrain.append(timeSlot)
            
        SubElement( constrain ,  "Active" ).text = active
        SubElement( constrain ,  "Comments" ).text = comment            

        self.xmlTimeConstrainList.append(constrain)

    def addActivityPreferredStartingTimes(self, lst, Id , weight = 100, active = "true", comment = ""):    
          
        constrain = Element("ConstraintActivityPreferredStartingTimes")
        SubElement(constrain,"Weight_Percentage").text = str(weight)
        SubElement(constrain,"Activity_Id").text = str(Id)
        SubElement(constrain,"Number_of_Preferred_Starting_Times").text = str( len( lst  ) )
        
        for datetime in lst:
            timeSlot = Element("Preferred_Starting_Time")        
            ( SubElement( timeSlot , "Preferred_Starting_Day").text , SubElement( timeSlot , "Preferred_Starting_Hour").text ) = datetime
            constrain.append(timeSlot)

        SubElement( constrain ,  "Active" ).text = active
        SubElement( constrain ,  "Comments" ).text = comment

        if all( tostring( constrain ) != tostring(c) for c in self.xmlTimeConstrainList ):
            self.xmlTimeConstrainList.append( constrain )

        self.xmlTimeConstrainList.append(constrain)

    def addActivityPreferredStartingTime(self, datetime , Id , locked = False,  weight = 100, active = "true", comment = ""):    
          
        constrain = Element("ConstraintActivityPreferredStartingTime")
        SubElement(constrain,"Weight_Percentage").text = str(weight)
        SubElement(constrain,"Activity_Id").text = str(Id)
        ( SubElement( constrain, "Preferred_Day").text , SubElement( constrain , "Preferred_Hour").text ) = datetime
        SubElement( constrain ,  "Permanently_Locked" ).text = "true" if locked else "false"
        SubElement( constrain ,  "Active" ).text = "true"
        SubElement( constrain ,  "Comments" ).text = ""  

        if all( tostring( constrain ) != tostring(c) for c in self.xmlTimeConstrainList ):
            self.xmlTimeConstrainList.append( constrain )

        SubElement( constrain ,  "Active" ).text = active
        SubElement( constrain ,  "Comments" ).text = comment
        self.xmlTimeConstrainList.append(constrain)
                   
    def addBuilding( self, building):

        if (building.find(" ") != -1): raise ValueError("You can not use spaces in Building Names")

        if not(self.buildingExists(building)):
            basic = Element( "Building" )
            SubElement( basic , "Name" ).text  = building
            SubElement( basic , "Comments" ).text  = ""
            self.xmlBuildingLst.append(basic)

    def buildingExists(self,building):
        return any( [ b.find("Name").text == building for b in self.xmlBuildingLst.findall("Building") ])

    def roomExits(self, room):
        return any( [ r.find("Name").text == room for r in self.xmlRoomLst.findall("Room") ])

    def subjectExits(self, subject):
        return any( [ s.find("Name").text == subject for s in self.xmlSubjectLst ])

    def addSubject(self, name , comment = ""):
        
        if not(self.roomExits( name )): 
            basic = Element( "Subject" )
            SubElement( basic , "Name" ).text  = name
            SubElement( basic , "Comments" ).text  = comment
            
            self.xmlSubjectLst.append(basic)

    def ungroup(self, ref):
        groupId = ref.find("Activity_Group_Id").text 
        
        if groupId != "0":
            for act in filter( lambda x : x.find("Activity_Group_Id").text == groupId , self.xmlActivitiesList ):
                act.find("Activity_Group_Id").text = "0"
                act.find("Total_Duration").text = act.find("Duration").text
            
    def addRoom(self, room, building, comment = ""):
        
        if (room.find(" ") != -1): raise ValueError("You can not use spaces in Room Names")           

        self.addBuilding(building)

        if not(self.roomExits(room)): 
            basic = Element( "Room" )
            SubElement( basic , "Name" ).text  = room
            SubElement( basic , "Building" ).text  = building
            SubElement( basic , "Capacity" ).text  = "30000"  
            SubElement( basic , "Comments" ).text  = comment
            self.xmlRoomLst.append(basic)

    def addActivityTagPreferredRooms(self, tag, roomLst, active = "true", comment = ""):
        
        self.addTag(tag)
               
        basic = Element( "ConstraintActivityTagPreferredRooms" )
        SubElement( basic , "Weight_Percentage" ).text  = "100"
        SubElement( basic , "Activity_Tag" ).text  = tag
        SubElement( basic , "Number_of_Preferred_Rooms" ).text  = str(len(roomLst))
        for room in roomLst:
            if not self.roomExits(room): raise ValueError("Room: " + room + " must be added before used in a constrain")
            SubElement( basic , "Preferred_Room").text = room

        SubElement( basic , "Active" ).text  = active
        SubElement( basic , "Comments" ).text  = comment    
            
        
        if all( tostring(basic) != tostring(c) for c in self.xmlSpaceConstrainList ):
            self.xmlSpaceConstrainList.append(basic)       

    def addStudentsMaxHoursDaily(self, hours, students, comments = "", active = "true"):

        basic = Element( "ConstraintStudentsSetMaxHoursDaily" )        
        SubElement( basic , "Weight_Percentage" ).text  = "100"       
        SubElement( basic , "Maximum_Hours_Daily" ).text  = str(hours)  
        SubElement( basic , "Students" ).text  = students
        SubElement( basic , "Active" ).text  = active
        SubElement( basic , "Comments" ).text  = comments    
        
        if all( tostring(basic) != tostring(c) for c in self.xmlTimeConstrainList ):
             self.xmlTimeConstrainList.append(basic)

    def addStudentsMinHoursDaily(self, hours, students, comments = "", emptyDays = False, active = "true"):

        basic = Element( "ConstraintStudentsSetMinHoursDaily" )        
        SubElement( basic , "Weight_Percentage" ).text  = "100"       
        SubElement( basic , "Minimum_Hours_Daily" ).text  = str(hours)  
        SubElement( basic , "Students" ).text  = students
        SubElement( basic , "Allow_Empty_Days" ).text  = "true" if emptyDays else "false"
        SubElement( basic , "Active" ).text  = active
        SubElement( basic , "Comments" ).text  = comments    
        
        if all( tostring(basic) != tostring(c) for c in self.xmlTimeConstrainList ):
             self.xmlTimeConstrainList.append(basic)     

    def addSingleActivity(self, subject, duration, teachers = [], students = [], tags = [],  comment = "", active = "true"):
        basic = Element( "Activity" )        
        for t in teachers: SubElement( basic , "Teacher" ).text  = t      
        SubElement( basic , "Subject" ).text  = subject  
        for tag in tags: SubElement( basic , "Activity_Tag" ).text  = tag  
        for s in students: SubElement( basic , "Students" ).text  = s 
        SubElement( basic , "Duration" ).text  = str(duration)
        SubElement( basic , "Total_Duration" ).text  = str(duration)
        Id = int(self.xmlActivitiesList[-1].find("Id").text) + 1 
        SubElement( basic , "Id" ).text  = str(Id)
        SubElement( basic , "Activity_Group_Id" ).text  = "0"
        SubElement( basic , "Active" ).text  = active
        SubElement( basic , "Comments" ).text  = comment
        
        self.xmlActivitiesList.append(basic)
        return Id
        
    def addActivityPreferredRoom(self, Id, room, weight = 100, locked = True,active = "true", comment = ""):
        
        basic = Element( "ConstraintActivityPreferredRoom" )
        SubElement( basic , "Weight_Percentage" ).text  =  str(weight)
        SubElement( basic , "Activity_Id" ).text  =  str(Id)
        SubElement( basic , "Room" ).text  =  room
        SubElement( basic , "Permanently_Locked" ).text  =  "true" if locked else "false"
        SubElement( basic , "Room" ).text  =  room
        SubElement( basic , "Active" ).text  = active
        SubElement( basic , "Comments" ).text  = comment    
 
        
        if all( tostring(basic) != tostring(c) for c in self.xmlSpaceConstrainList ):
            self.xmlSpaceConstrainList.append(basic)       
            
    def addActivitiesNotOverlapping(self, idList = [], weight = 100, comment = ""):

        basic = Element( "ConstraintActivitiesNotOverlapping" )        
        SubElement( basic , "Weight_Percentage" ).text  = str(weight)
        SubElement( basic , "Number_of_Activities" ).text  = str( len(idList) )
        for Id in idList: SubElement( basic , "Activity_Id" ).text = str(Id)
        SubElement( basic , "Active" ).text  = "true"
        SubElement( basic , "Comments" ).text  = comment    
        
        if all( tostring(basic) != tostring(c) for c in self.xmlTimeConstrainList ):
             self.xmlTimeConstrainList.append(basic)     

    def addTeacherMaxHoursDaily(self, teacherName, maxHours, weight = 100, comment = "", active = "true"):
        
        basic = Element( "ConstraintTeacherMaxHoursDaily" )        
        SubElement( basic , "Weight_Percentage" ).text  = str(weight)
        SubElement( basic , "Teacher_Name" ).text  =  teacherName
        SubElement( basic , "Maximum_Hours_Daily" ).text  = str(maxHours)
        SubElement( basic , "Active" ).text  = active
        SubElement( basic , "Comments" ).text  = comment    
        
        if all( tostring(basic) != tostring(c) for c in self.xmlTimeConstrainList ):
             self.xmlTimeConstrainList.append(basic)     
       
    def addTeacherNotAvailable(self, teacherName, lst, comment = "", active = "true"):
        
        constrain = Element("ConstraintTeacherNotAvailableTimes")
        SubElement(constrain,"Weight_Percentage").text = str(100)
        SubElement(constrain,"Teacher").text = teacherName
        SubElement(constrain,"Number_of_Not_Available_Times").text = str( len( lst  ) )
        
        for datetime in lst:
            timeSlot = Element("Not_Available_Time")        
            ( SubElement( timeSlot , "Day").text , SubElement( timeSlot , "Hour").text ) = datetime
            constrain.append(timeSlot)

        SubElement( constrain , "Active" ).text  = active
        SubElement( constrain ,  "Comments" ).text = comment

        if all( tostring( constrain ) != tostring(c) for c in self.xmlTimeConstrainList ):
            self.xmlTimeConstrainList.append( constrain )

        self.xmlTimeConstrainList.append(constrain)        

    def addMaxDaysBetween(self, idList, maxDays , weight = 100, consecutive = True, comments = "", active = "true"):

        constrain = Element("ConstraintMaxDaysBetweenActivities")
        SubElement(constrain,"Weight_Percentage").text = str(weight)
        SubElement(constrain,"Consecutive_If_Same_Day").text = "true" if consecutive else "false"
        SubElement(constrain,"Number_of_Activities").text = str( len(idList ))
        for Id in idList:
            SubElement(constrain,"Activity_Id").text = str(Id)
    
        SubElement(constrain,"MaxDays").text = str(maxDays)
        SubElement( constrain ,  "Active" ).text = active
        SubElement( constrain ,  "Comments" ).text = comments

        if all( tostring( constrain ) != tostring(c) for c in self.xmlTimeConstrainList ):
            self.xmlTimeConstrainList.append( constrain )

        self.xmlTimeConstrainList.append(constrain)   

    def addActivitiesSameStartingTime(self, idList, weight = 100, comments = "", active = "true"):

        constrain = Element("ConstraintActivitiesSameStartingTime")
        SubElement(constrain,"Weight_Percentage").text = str(weight)
        SubElement(constrain,"Number_of_Activities").text = str( len(idList ))
        for Id in idList:
            SubElement(constrain,"Activity_Id").text = str(Id)
    
        SubElement( constrain ,  "Active" ).text = active
        SubElement( constrain ,  "Comments" ).text = comments

        if all( tostring( constrain ) != tostring(c) for c in self.xmlTimeConstrainList ):
            self.xmlTimeConstrainList.append( constrain )

        self.xmlTimeConstrainList.append(constrain)   

    def getActivity(self,Id):
        a = list( filter( lambda a : a.find("Id").text == str(Id) , self.xmlActivitiesList.findall("Activity") ) )
        if a == []:
            return None
        else:
            return a[0]
        
def getRelated( act, actList):
    relatedList = filter( lambda x :  x.find("Subject").text == act.find("Subject").text and not set( a.text for a in x.findall("Students")  ).isdisjoint( set( a.text for a in act.findall("Students") ) ),  actList)
    return sorted( relatedList, key = lambda x : len( x.findall("Students") ) )          

def show(element):
    print( str( tostring(element, pretty_print = True)).encode("utf-8" ) )
   
def checkAny(field , values , element):
    testSet = set(values)
    elementSet = set( [ e.text for e in element.findall(field) ] )
    return not testSet.isdisjoint( elementSet )

def checkAll(field , values , element):
    testSet = set(values)
    elementSet = set( [ e.text for e in element.findall(field) ] )
    return testSet == elementSet    
    
def checkAllIn(field , values , element):
    testSet = set(values)
    elementSet = set( [ e.text for e in element.findall(field) ] )
    return elementSet.issubset(testSet) and elementSet != set()

#
#fet = FetFile("sheet20181.fet")
#
## Adiciona limite de Gaps para as turmas
#gaps = { "01601" : 0 , "01602" : 0 ,"01603" : 0 ,"01604" : 0 ,"01605" : 0 ,"01606" : 0 , "01607" : 0 , "01608" : 0 , 
#         "02601" : 0 , "02602" : 0 ,"02603" : 0 ,"02604" : 0 ,"02605" : 0 ,"02606" : 0 , "02607" : 0 , "02608" : 0 }
#
#fet.addStudentsGaps(gaps)
#
##Limita máximo dias de aula
#fet.addMaxDaysTeachers( lambda x : True,  3 )
#
##Coloca turmas alternando turnos
#
#subjectTarde = [ "EMB5007" , "EMB5029" , "EMB5039" , "EMB5012" , "EMB5630" , "EMB5600" , "EMB5626"]
#fet.setTag( lambda x : ( any( [ x.find("Subject").text == subject for subject in subjectTarde ] ) and any( [ student.text[0:2] == "02" for student in x.findall("Students") ] ) and any( [ (student.text[-1] != "G")  for student in x.findall("Students") ] )   ) , "Tarde")
#subjectManha = [ "EMB5001" , "EMB5005" , "EMB5034" , "EMB5037" , "EMB5038" , "EMB5600" , "EMB5351" , "EMB5406" , "EMB5351" , "EMB5526" , "EMB5683" , "EMB5731" , "EMB5832", "EMB5924"]
#fet.setTag( lambda x : any( [ x.find("Subject").text == subject for subject in subjectManha ] ) and all( [ ( student.text[0:2] == "01" and student.text[-1] != "G")  for student in x.findall("Students") ] ) , "Manha" )
#fet.setTag( lambda x : ( any( [ x.find("Subject").text == subject for subject in [ "EMB5600"] ] ) and all( [ student.text[0:2] == "02" for student in x.findall("Students") ] ) and any( [ (student.text[-1] != "G")  for student in x.findall("Students") ] )   ) , "Tarde")
#
#days   = ["Seg","Ter","Qua","Qui","Sex"]
#hours  = ["07:30 - 08:20","08:20 - 09:10","09:10 - 10:00","10:10 - 11:00","11:00 - 11:50","13:30 - 14:20","14:20 - 15:10","15:10 - 16:00","16:20 - 17:10","17:10 - 18:00","18:00 - 18:50","18:50 - 19:40"]
#
#fet.addPreferedTimes( list( itertools.product( days, hours[0:7] ) ) , tag = "Manha" )
#fet.addPreferedTimes( list( itertools.product( days, hours[3:10] ) ) , tag = "Tarde" )
#fet.addPreferedTimes( list( itertools.product( days, hours[1:5] ) ) , tag = "Manha" , weight =70)
#fet.addPreferedTimes( list( itertools.product( days, hours[5:9] ) ) , tag = "Tarde" , weight =70)
#
##Fixar horário da disciplina de EMB5035 para começar de manha ou no máximo as 13:30
#fet.addPreferredStartingTimes( list( itertools.product( days,  hours[0:6] ) ) ,  subject = "EMB5035")
#
##Desabilita aulas nos horários de reuniões
#hourDay = list( itertools.product( days,  hours[0:10] ) )
#hourDay.remove( ('Qui', '15:10 - 16:00') )
#hourDay.remove( ('Qui', '16:20 - 17:10') )
#
#fet.addPreferedTimes( hourDay , tag = "Aula" )
#
##Desativa horários de responsabilidade dos Coordenadores
#for curso in ["H_Aero","H_Auto","H_Ferro","H_Meca","H_Naval","H_Infra","H_Trans"]:
#    fet.deactivateActivity( lambda x : any( [ tag.text == curso for tag in x.findall("Activity_Tag") ] ) )
#
##Define máximo e minimo de horas paras as turmas da 1a Fase
#for s in [ '0160' + str(n) for n in range(1,9) ]:
#    fet.addStudentsMaxHoursDaily( 6, s)
#    fet.addStudentsMinHoursDaily( 4, s)
#
## Remove restrição de horário na disciplina EMB5012, pois não é compatível em função do LabInf
#fet.removeTag(lambda x : x.find("Subject").text == "EMB5012" and any( [ s.text == "05605" for s in x.findall("Students") ])
#,"Tarde")
#
#
#
#
#
#fet.write("teste.fet")
#
