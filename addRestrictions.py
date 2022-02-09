#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 21:00:17 2017

@author: diogo
"""

from lxml.etree import Element, SubElement, tostring, parse, XMLParser
from fetCustomizer import *
from timetable import Teacher
import  itertools
import pandas as pd

from argparse import ArgumentParser

parser = ArgumentParser(description="Adiciona salas e restrições adicionais")
parser.add_argument('-i'     , action="store" ,dest="input" ,  type = str,   help="Nome do arquivo FET de entrada" )
parser.add_argument('-o'     , action="store", dest="output"  ,  type = str, help="Nome do arquivo FET de saída" )
parser.add_argument('-code'  , action="store", dest="code"  ,  type = str, help='Código da planilha do googledocs.')

args = parser.parse_args()

def setPracticalToInf( fet, subject,practicalGroup):
    actList = filter( lambda x: x.find("Subject").text == subject ,fet.xmlActivitiesList)
    for g in practicalGroup:
        a = filter( lambda a :  set( [s.text for s in a.findall("Students") ] ) == set( g.split("/")  ), actList )
        fet.setTag(    lambda x: x == a[-1], "LabInf" )
        fet.removeTag( lambda x: x == a[-1], "Sala" )
        a[-1].find("Active").text = "true"
        for act in a: 
            act.find("Activity_Group_Id").text = "0"
            act.find("Total_Duration").text = act.find("Duration").text
           
filename = args.input
fet = FetFile(filename)
# Acessando lista de nome dos Professores

sheet_url = lambda code, sheet_name  : "https://docs.google.com/spreadsheets/d/{key}/gviz/tq?tqx=out:csv&sheet={sheet_name}".format( key = code  , sheet_name = sheet_name )
df = pd.read_csv(sheet_url(args.code, "Salas" ) )
df.drop( [ col for col in df.columns if col.find("Unnamed: ") != -1 ], axis = 1, inplace = True )    
data =   df.to_dict("records")

#Adicionada Salas no arquivo .fet
for roomRegister in data:
    fet.addRoom( roomRegister[u"Código"],  roomRegister[u"Bloco"])

#Separa as salas por categoria
roomData =  list( filter( lambda row: row["Especifico"] == u""            ,  data)   )
infData  =  list( filter( lambda row: row["Especifico"] == u"Informática" ,  data)  )
desData  =  list( filter( lambda row: row["Especifico"] == u"Desenho"     ,  data) )
cirData  =  list( filter( lambda row: row["Especifico"] == u"Circuitos"   ,  data) ) 
mulData  =  list( filter( lambda row: row["Especifico"] == u"Multiusuário",  data) )

# Separa as salas de cada curso
courseRoomData  =  { s : list( filter( lambda row: str(row["Especifico"]).find(s) != -1 ,  data) ) for s in [u"602",u"603",u"604",u"605",u"606",u"607",u"608"] }
posData  =  list( filter( lambda row: str(row["Especifico"]).find(u"Pós") != -1 ,data )  )

# Filtra as salas compatíveis com os diversos tamanhos de turma
tagList  =  [ t.find("Name").text for t in filter( lambda tag : tag.find("Name").text[0] == "T" and tag.find("Name").text[1:].isdigit() , fet.xmlTagLst) ]
for tag in tagList:
    size = int(tag[1:])
    compatibleRooms = list( filter( lambda roomDict : size <= int(roomDict[u"Máximo"]) and size >= int(roomDict[u"Mínimo"])  , roomData + infData + desData)  ) 
    fet.addActivityTagPreferredRooms(tag, [ r[u"Código"]  for r in compatibleRooms] )

# Define a sala de Desenho
fet.addTag("Desenho")
fet.addActivityTagPreferredRooms("Desenho", [ r[u"Código"]  for r in desData] )

# Define quais salas são Laboratório de Informática
fet.addTag("LabInf")
fet.addActivityTagPreferredRooms("LabInf", [ r[u"Código"]  for r in infData] )

# Define o Laboratório de Circuitos
fet.addTag("LabCircuitos")
fet.addActivityTagPreferredRooms("LabCircuitos", [ r[u"Código"]  for r in cirData] )

# Define o Laboratório de Circuitos
fet.addTag("LabMulti")
fet.addActivityTagPreferredRooms("LabMulti", [ r[u"Código"]  for r in mulData] )

# Define quais salas podem ser utilizadas como salas de Aula (Todas menos as salas de Informática)
fet.setTag( lambda x : True, "Sala" )
sala = []
sala = roomData +  desData + posData
for course in courseRoomData:
    sala += courseRoomData[course]  

fet.addActivityTagPreferredRooms("Sala", set( [ r[u"Código"]  for r in sala ] ) )

# Define quais salas podem ser utilizadas pela pós (Todas com exceção do Laboratório de Informática e Sala de Desenho)
fet.addActivityTagPreferredRooms("H_PosECM" , [ r[u"Código"]  for r in roomData + posData] )
fet.addActivityTagPreferredRooms("H_PosESE" , [ r[u"Código"]  for r in roomData + posData] )
#
# Define quais salas podem se utilizadas pelos Cursos (Salas de uso geral mais sala de desenho + informática + específicas do curso)
courseTag = { "602" : "H_Aero", "603" : "H_Auto", "604" : "H_Ferro", "605" : "H_Meca", "606" : "H_Naval", "607" : "H_Infra", "608" : "H_Trans" }
for course in courseTag:
    fet.addActivityTagPreferredRooms(courseTag[course] , [ r[u"Código"]  for r in roomData + desData + infData + courseRoomData[course] ] )    

# Define as salas que o Departamento pode utilizar para alocação das disciplinas básicas e compartilhadas
fet.addActivityTagPreferredRooms("H_EMB", [ r[u"Código"]  for r in roomData + desData + infData  ] )

# Desativa atividades que devem ser alocadas pelos coordenadores dos cursos
for tag in courseTag.values():
    fet.deactivateWithTag(tag)

# Adiciona uma atividade de manutenção em cada um dos laboratórios de informática
fet.addSubject("Manutencao")
fet.addTag("Virtual")
idList = []

for room in [ r[u"Código"]  for r in infData]:  
    Id = fet.addSingleActivity("Manutencao",2, tags = [ "Virtual"  ])
    fet.addActivityPreferredRoom(Id, room )
    idList.append(Id)

fet.addActivitiesNotOverlapping( idList = idList )

days   = ["Seg","Ter","Qua","Qui","Sex"]
hours  = ["07:30 - 08:20","08:40 - 09:30","09:30 - 10:20","10:30 - 11:20","11:20 - 12:10","13:30 - 14:20","14:20 - 15:10","15:10 - 16:00","16:20 - 17:10","17:10 - 18:00","18:00 - 18:50","18:50 - 19:40"]

fet.addPreferedTimes(  list( itertools.product( days, hours[1:9] ) ) , subject = "Manutencao")

#Aloca a disciplina EMB5035 para a sala de desenho
fet.setTag( lambda x : x.find("Comments").text == "Sala de Desenho"  , "Desenho" )

# Configura as disciplina que possuem todos os creditos em Laboratório de Informática
fet.setTag( lambda x : x.find("Comments").text == "Laboratório Informática"  , "LabInf" )
fet.removeTag( lambda x : x.find("Comments").text == "Laboratório Informática"  , "Sala" )

# Configura as disciplinas que possuem parte dos créditos em Laboratório de Informática
SalaInfActivities = filter( lambda x : x.find("Comments").text == "Sala Comum + Laboratório de Informática", fet.xmlActivitiesList )
SalaInfActivities = sorted( SalaInfActivities, key = lambda x : len( x.findall("Students") ) )

while SalaInfActivities != []:
    
    relatedActivities = getRelated( SalaInfActivities[-1], SalaInfActivities )
    for a in relatedActivities:
        SalaInfActivities.remove(a)
        
    for a in relatedActivities[:-1]:
        fet.removeTag( lambda x : x == a , "Sala")
        fet.setTag( lambda x : x == a , "LabInf")
        fet.ungroup(a)
        
fet.activateWithTag("LabInf")

for a in filter( lambda x : x.find("Subject").text == "EMB5111" and x.find("Duration").text == "1", fet.xmlActivitiesList  ):
    a.find("Duration").text = "2"
    a.find("Total_Duration").text = "2"

fet.addActivityPreferredStartingTimes( list( itertools.product( days, [ hours[1] , hours[5] ] ) ) , a.find("Id").text )

#Limita máximo dias de aula
fet.addMaxDaysTeachers( lambda x : True,  3 )

##Desabilita aulas nos horários de reuniões
hourDay = list( itertools.product( days,  hours[0:10] ) )
hourDay.remove( ('Qui', '15:10 - 16:00') )
hourDay.remove( ('Qui', '16:20 - 17:10') )
hourDay.remove( ('Qui', '17:10 - 18:00') )

fet.addPreferedTimes( hourDay , tag = "Aula" )

# Adiciona limite de Gaps para as turmas
gaps = { "01601" : 0 , "01602" : 0 ,"01603" : 0 ,"01604" : 0 ,"01605" : 0 ,"01606" : 0 , "01607" : 0 , "01608" : 0 , 
         "02601" : 0 , "02602" : 0 ,"02603" : 0 ,"02604" : 0 ,"02605" : 0 ,"02606" : 0 , "02607" : 0 , "02608" : 0 }

fet.addStudentsGaps(gaps)

#Adiciona Turnos
fet.addTag("Manha")
fet.addTag("Tarde")

days   = ["Seg","Ter","Qua","Qui","Sex"]
hours  = ["07:30 - 08:20","08:40 - 09:30","09:30 - 10:20","10:30 - 11:20","11:20 - 12:10","13:30 - 14:20","14:20 - 15:10","15:10 - 16:00","16:20 - 17:10","17:10 - 18:00","18:00 - 18:50","18:50 - 19:40"]

fet.addPreferedTimes( list( itertools.product( days, hours[0:7] ) ) , tag = "Manha" , comment = u"Restrição que força aulas no período da manhã (07:30 - 15:10)" , active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[3:10] ) ), tag = "Tarde" , comment = u"Restrição que força aulas no período da tarde (10:30 - 18:00)" ,active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[1:5] ) ) , tag = "Manha" , weight = 70 , comment = u"Preferência para aula no período da manhã (08:40-12:10)", active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[5:9] ) ) , tag = "Tarde" , weight  =70 , comment = u"Preferência para aula no período da tarde (13:30-17:10)" , active = "false")
#
fet.addPreferedTimes( list( itertools.product( days, hours[0:7] ) ) , tag = "1aFase" , comment = u"Força período para a primeira fase (07:30 - 15:10)", active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[1:5] ) ) , tag = "1aFase" , comment = u"Preferência de período para a primeira fase (08:40-12:10)", active = "false")

fet.addPreferedTimes( list( itertools.product( days, hours[3:10] ) ), tag = "2aFase" , comment = u"Força período para a segunda fase (10:30 - 18:00)" , active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[5:9] ) ) , tag = "2aFase" , comment = u"Preferência de período para a segunda fase (13:30-17:10)" , active = "false")

fet.addPreferedTimes( list( itertools.product( days, hours[0:7] ) ) , tag = "3aFase" , comment = u"Força período para a terceira fase (07:30 - 15:10)", active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[1:5] ) ) , tag = "3aFase" , comment = u"Preferência de período para a terceira fase (08:40-12:10)", active = "false")

fet.addPreferedTimes( list( itertools.product( days, hours[3:10] ) ), tag = "4aFase" , comment = u"Força período para a quarta fase (10:30 - 18:00)" , active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[5:9] ) ) , tag = "4aFase" , comment = u"Preferência de período para a quarte fase (13:30-17:10)" , active = "false")

fet.addPreferedTimes( list( itertools.product( days, hours[0:7] ) ) , tag = "5aFase" , comment = u"Força período para a quinta fase (07:30 - 15:10)", active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[1:5] ) ) , tag = "5aFase" , comment = u"Preferência de período para a quinta fase (08:40-12:10)", active = "false")

fet.addPreferedTimes( list( itertools.product( days, hours[3:10] ) ), tag = "6aFase" , comment = u"Força período para a sexta fase (10:30 - 18:00)" , active = "false")
fet.addPreferedTimes( list( itertools.product( days, hours[5:9] ) ) , tag = "6aFase" , comment = u"Preferência de período para a sexta fase (13:30-17:10)" , active = "false")


#subjectTarde = [ "EMB5007" , "EMB5029" , "EMB5039" , "EMB5012" , "EMB5630" , "EMB5600" , "EMB5626"]
#fet.setTag( lambda x : ( any( [ x.find("Subject").text == subject for subject in subjectTarde ] ) and any( [ student.text[0:2] == "02" for student in x.findall("Students") ] ) and any( [ (student.text[-1] != "G")  for student in x.findall("Students") ] )   ) , "Tarde")
#fet.setTag( lambda x : any( [ x.find("Subject").text == subject for subject in subjectManha ] ) and all( [ ( student.text[0:2] == "01" and student.text[-1] != "G")  for student in x.findall("Students") ] ) , "Manha" )

fet.setTag( lambda x : checkAllIn( "Students", [ u"0160" + str(n) for n in range(1,9) ], x ) , "1aFase" )
fet.setTag( lambda x : checkAllIn( "Students", [ u"0260" + str(n) for n in range(1,9) ], x ) , "2aFase" )
fet.setTag( lambda x : checkAllIn( "Students", [ u"0360" + str(n) for n in range(1,9) ], x ) , "3aFase" )
fet.setTag( lambda x : checkAllIn( "Students", [ u"0460" + str(n) for n in range(1,9) ], x ) , "4aFase" )
fet.setTag( lambda x : checkAllIn( "Students", [ u"0560" + str(n) for n in range(1,9) ], x ) , "5aFase" )
fet.setTag( lambda x : checkAllIn( "Students", [ u"0660" + str(n) for n in range(1,9) ], x ) , "6aFase" )

#Fixar horário da disciplina de EMB5035 para começar de manha ou no máximo as 13:30
fet.addPreferredStartingTimes( list( itertools.product( days,  hours[0:6] ) ) ,  subject = "EMB5035")
#
#Define máximo e minimo de horas paras as turmas da 1a Fase

for s in [ group.find("Name").text for year in fet.xmlStudentsList for group in year.findall("Group") ]:
    fet.addStudentsMaxHoursDaily( 6, s, active = "false")
    fet.addStudentsMinHoursDaily( 4, s, active = "false")

ids = set( [ x.find("Id").text for x in filter( lambda x  : x.find("Subject").text == "EMB5102" , fet.xmlActivitiesList ) ] )
fet.deactivateTimeRestriction( lambda x  :  set( [ activity_id.text for activity_id in x.findall("Activity_Id") ] ) == set(ids) )

# Adiciona horários da PósECM e desabilita restrições automática destas disciplinas

for activity in filter( lambda x : any( [ tag.text == 'H_PosECM' for tag in x.findall("Activity_Tag") ] ) , fet.xmlActivitiesList ):
    iD = activity.find("Id").text
    for restriction in filter( lambda x : any( [ rId.text == iD for rId in x.findall("Activity_Id") ] ) , fet.xmlTimeConstrainList ):
        restriction.find("Active").text = "false"
    
data =   pd.read_csv(sheet_url(args.code, 'PosECM' ) ).to_dict("records")

subjectSet = set( [ row["Disciplina"] for row in data ] )

for subject in subjectSet:
    rowList = filter( lambda row : row["Disciplina"]  == subject, data)
    activityList = filter( lambda x : x.find("Subject").text == subject, fet.xmlActivitiesList)
    totalLength = sum( [ len(row["Janelas"].split(",")) for row in rowList ] )
    for row, activity in zip( rowList, activityList ):
        date = row["Dia"]
        time = row["Janelas"].split(",")[0]
        length = len(row["Janelas"].split(","))
        fet.addActivityPreferredStartingTime( (date,time) , activity.find("Id").text , comment = u"Horário pré-estabelicido da PosECM")    
        activity.find("Duration").text = str(length)
        activity.find("Total_Duration").text = str(totalLength )
        if (row["Sala"] != ""):
            fet.addActivityPreferredRoom( activity.find("Id").text, row["Sala"], comment = u"Sala pré-estabelicida da PosECM")  

# Adiciona horários da PósESE e desabilita restrições automática destas disciplinas
for activity in filter( lambda x : any( [ tag.text == 'H_PosESE' for tag in x.findall("Activity_Tag") ] ) , fet.xmlActivitiesList ):
    iD = activity.find("Id").text
    for restriction in filter( lambda x : any( [ rId.text == iD for rId in x.findall("Activity_Id") ] ) , fet.xmlTimeConstrainList ):
        restriction.find("Active").text = "false"

data =   pd.read_csv(sheet_url(args.code, 'PosESE' ) ).to_dict("records")

subjectSet = set( [ row["Disciplina"] for row in data ] )

for subject in subjectSet:
    rowList = filter( lambda row : row["Disciplina"]  == subject, data)
    activityList = filter( lambda x : x.find("Subject").text == subject, fet.xmlActivitiesList)
    totalLength = sum( [ len(row["Janelas"].split(",")) for row in rowList ] )
    for row, activity in zip( rowList, activityList ):
        date = row["Dia"]
        time = row["Janelas"].split(",")[0]
        length = len(row["Janelas"].split(","))
        fet.addActivityPreferredStartingTime( (date,time) , activity.find("Id").text , comment = u"Horário pré-estabelicido da PosESE")    
        activity.find("Duration").text = str(length)
        activity.find("Total_Duration").text = str(totalLength )
        if (row["Sala"] != ""):
            fet.addActivityPreferredRoom( activity.find("Id").text, row["Sala"] ,  comment = u"Sala pré-estabelicida da PosESE") 

# Adicionar Restriçoes Individuas dos professores     
            
data =   pd.read_csv(sheet_url(args.code, 'Respostas' ) ,  keep_default_na= False ).to_dict("records")            

days   = ["Seg","Ter","Qua","Qui","Sex"]

timeDict = { u""                                 :   [] ,
       u"Não tenho restrição"              :   [] ,
       u"Todos os dias das 7:30 às 8:20"   :  list( itertools.product( days, ["07:30 - 08:20"] ) ) ,
       u"Todos os dias das 11:00 às 11:50" :  list( itertools.product( days, ["11:20 - 12:10"] ) ) ,
       u"Todos os dias das 13:30 às 14:20" :  list( itertools.product( days, ["13:30 - 14:20"] ) ) ,
       u"Todos os dias das 17:10 às 18:00" :  list( itertools.product( days, ["17:10 - 18:00"] ) ) }     

for xmlTeacher in fet.xmlTeacherList:
    teacherName = xmlTeacher.find("Name").text
    filteredData = list( filter( lambda row : str(Teacher(row[u"Nome:"])) == teacherName , data ) ) 
    assert len( filteredData) <= 1 , "Multiplicas linhas encontradas para: " + teacherName
    if ( len( filteredData) == 1 ):
        row = filteredData[0]
        lst = timeDict[row[u"Em que horário você não gostaria de ter aulas?"]]
        fet.addTeacherNotAvailable( teacherName, lst , comment = u"Em que horário você não gostaria de ter aulas?" , active = "false")      
        maxHours = row[u"Qual o número máximo de CRÉDITOS que você está disposto a lecionar EM UM dia?"]
        if maxHours != u"Não tenho restrição" and maxHours != u"":
            fet.addTeacherMaxHoursDaily(teacherName, int(maxHours) , comment = u"Qual o número máximo de CRÉDITOS que você está disposto a lecionar EM UM dia?" , active = "false")
        data.remove(row)
    else:
        fet.addTeacherNotAvailable( teacherName, [] , comment = u"Em que horário você não gostaria de ter aulas?" , active = "false")         
        print( "Não foi encontrada resposta ao formulário para o Professor" , teacherName  )

for e in filter( lambda x : checkAny("Subject",["EMB5683"],x),  fet.xmlActivitiesList ):
    idReal = e.find("Id").text
    time = int( e.find("Duration").text )
    idVirtual = fet.addSingleActivity("EMB5683", time , tags = [ "Virtual" , "LabCircuitos" ] )        
    fet.addActivitiesSameStartingTime( [ idReal, idVirtual ] , comments = u"Introdução à Engenharia Mecatrônica também utiliza Laboratório de Circuitos")
        
fet.write( args.output )
