# -*- coding: utf-8 -*-
"""
Created on Tue May 30 21:11:14 2017

@author: diogo
"""

from lxml.etree import Element, SubElement, tostring
from timetable import SubGroup, Room, Teacher, Subject

class fetXML:

        def __init__(self,filename):
            self.filename = filename
            self.xml = Element("fet", attrib={ "version": "5.29.1" })
            self.xmlActivityList = Element("Activities_List")
            
            self.xmlTimeConstrainList  = Element("Time_Constraints_List")          
            
            basic = SubElement( self.xmlTimeConstrainList , "ConstraintBasicCompulsoryTime" )
            SubElement( basic , "Weight_Percentage" ).text  = '100'
            SubElement( basic,  "Active" ).text = "true"
            SubElement( basic,  "Comments" ).text = ""            
            
            self.roomSet      = set()
            self.buildingSet  = set()
            self.tagSet       = set()
            self.teacherSet   = set()
            self.subjectSet   = set()
            self.subGroupSet   = set()     

            self.restrict  = None

        def addRestrictions(self, rest ):
            self.restrict = rest
            
        def AddRoom(self,roomDict):
            room = Room( roomDict )
            self.roomSet.add( room )  
            self.buildingSet.add( room.getBuildingName()  )

        def addBrakeConstrain(self):
            
            base = Element( "ConstraintBreakTimes" )
            SubElement( base , "Weight_Percentage" ).text = "100"
            SubElement( base , "Number_of_Break_Times" ).text = str( len(self.days) )
            for day in self.days:                           
                child = Element( "Break_Time")
                SubElement( child, "Day" ).text = day
                SubElement( child, "Hour").text = "Almoco"
                base.append(child)

            SubElement( base , "Active" ).text = "true"
            SubElement( base , "Comments" ).text = ""
            
            self.xmlTimeConstrainList.append(base)
            
        def close(self):
            f = open(self.filename,"w")
            self.xml.append(self.xmlInstitution)
            self.xml.append(self.xmlDayList)
            self.xml.append(self.xmlHourList)            
            self.xml.append(self.getSubjectElement() )
            self.xml.append(self.getTeacherElement() )
            self.xml.append(self.getStudentElement() )
            self.xml.append(self.getTagListElement() )
            self.xml.append(self.xmlActivityList)
            self.xml.append(self.getBuildingElement() )
            self.xml.append(self.getRoomElement() )
            
            self.addBrakeConstrain()
            
            self.xml.append(self.xmlTimeConstrainList )
            self.xml.append(self.getSpaceConstrainElement() )
            f.writelines( tostring(self.xml, pretty_print = True, xml_declaration=True, encoding = "utf-8" ).decode("utf-8") )
            f.close()
        
        def setInstitutionName(self,name):
            self.xmlInstitution = Element("Institution_Name")
            self.xmlInstitution.text = name
        
        def setTeachers(self, teacherStringList ):
            for teacherName in teacherStringList:
                self.addTeacher( Teacher(teacherName) )
        
        def setDays(self,days):
            self.days = days
            self.xmlDayList = Element("Days_List")
            SubElement(self.xmlDayList,"Number_of_Days").text = str( len(days) )
            for d in days:   
                xmlDay = SubElement(self.xmlDayList,"Day")
                SubElement(xmlDay,"Name").text = d
        
        def getTagListElement(self):
            xmlTagList      = Element("Activity_Tags_List")
            for tag in list( self.tagSet ):            
                xmlTagList.append( tag.getXmlDefinition() )
            return xmlTagList
        
        def getStudentElement(self):
            
            xmlStudentList = Element("Students_List")

            for course in sorted( set( [ x.course for x in self.subGroupSet ] ) ):
                year = SubElement(xmlStudentList,"Year")    
                SubElement(year,"Name").text = "Curso" + course
                SubElement(year,"Number_of_Students").text = "0"
                
                courseSubGroup = list( filter( lambda x : x.course == course, self.subGroupSet ) )
                
                for semester in sorted(set( [ x.semester for x in courseSubGroup ] )):
                                       
                    group = SubElement(year,"Group")
                    SubElement(group,"Name").text = semester + course
                    SubElement(group,"Number_of_Students").text = "0"
                    
                    generalGroup = False

                    for sub in filter( lambda x : x.semester == semester, courseSubGroup  ):
                        if ( not sub.isMaster() ):
                            if ( sub.sub != 'G' ) :
                                group.append( sub.getXmlElement() )
                            else:
                                generalGroup = True
    
                    if (generalGroup == True):
                        group = SubElement(year,"Group")
                        SubElement(group,"Name").text = semester + course + "G"
                        SubElement(group,"Number_of_Students").text = "0"                                
            
            return xmlStudentList

        def addTeacher(self, teacher):
             self.teacherSet.add(  teacher )

        def getTeacherElement(self):
            xmlTeacherList = Element("Teachers_List")
            for teacher in sorted( list( self.teacherSet ) ):            
                xmlTeacherList.append( teacher.getXmlElement() )
                
                if ( self.restrict != None ):
                    for e in self.restrict.getXmlNotAvailable( teacher ): self.xmlTimeConstrainList.append( e )
                    for e in self.restrict.getXmlMaxHours( teacher ): self.xmlTimeConstrainList.append( e )
                
            return xmlTeacherList
            
        def getSubjectElement(self):
            xmlSubjectList = Element("Subjects_List")
            for subject in sorted( list( self.subjectSet ) ):            
                xmlSubjectList.append( subject.getXmlElement(withComment=True) )
            return xmlSubjectList            
            
        def getRoomElement(self):
            xmlRoomList = Element("Rooms_List")
            for room in sorted( list( self.roomSet ) , key = lambda x : x.code ):
                xmlRoomList.append( room.getXmlElement() )
            return xmlRoomList

        def getBuildingElement(self):
            xmlBuildingList = Element("Buildings_List")
            for building in sorted( list( self.buildingSet ) ):
                e = Element("Building")
                SubElement(e,"Name").text = building
                SubElement(e,"Comments").text = ""
                xmlBuildingList.append( e )
            return xmlBuildingList

        def getSpaceConstrainElement(self):
            xmlSpaceConstrainList = Element("Space_Constraints_List")
            e = Element("ConstraintBasicCompulsorySpace")
            SubElement(e,"Weight_Percentage").text = "100"
            SubElement(e,"Active").text = "true"    
            SubElement(e,"Comments").text = ""
            xmlSpaceConstrainList.append( e )
            
#            tagList = filter( lambda x: x.type == "space", self.tagSet )
#            
#            for tag in sorted(tagList):
#                e = Element("ConstraintActivityTagPreferredRooms")
#                SubElement(e,"Weight_Percentage").text = "100"
#                SubElement(e,"Activity_Tag").text = tag.name
#                
#                size = int( tag.name[1:] )
#                
#                roomLst = filter(lambda x : ( x.size >= size) and not (x.size > 2*size ), self.roomSet)
#                
#                SubElement(e,"Number_of_Preferred_Rooms").text = str(len(roomLst) )
#                
#                for room in roomLst:
#                    SubElement(e,"Preferred_Room").text = room.code
#                
#                SubElement(e,"Active").text = "true"
#                SubElement(e,"Comments").text = ""
#                xmlSpaceConstrainList.append( e )
                
            return xmlSpaceConstrainList
            
        def setSubjects(self , subjectStringList ):
            for subjectString in subjectStringList:
                self.subjectSet.add( Subject(subjectString) )
            
        def addGroupActivity(self, g):
                                  
            for a in g:
                self.teacherSet = self.teacherSet.union( a.teacherSet )
                self.subjectSet.add( a.subject )
                for s in a.students.classes:
                    self.subGroupSet.add( SubGroup(s) )                   
                
                self.xmlActivityList.append( a.getXmlElement( totalTime = g.getTotalTime() , gid = g.gid() )  )                
                self.tagSet     = self.tagSet.union( a.tagSet )                

            for constrain in g.getConstrainList():
                self.xmlTimeConstrainList.append(constrain)
                
            
        def setHours(self,hours = ["7:30","8:20","9:10","10:10","11:00","Almoco","13:30","14:20","15:10","16:20","17:10"]):
            self.hours = hours
            self.xmlHourList = SubElement(self.xml,"Hours_List")
            SubElement(self.xmlHourList,"Number_of_Hours").text = str( len(hours) )
            for h in hours:   
                xmlHour = SubElement(self.xmlHourList,"Hour")
                SubElement(xmlHour,"Name").text = h

