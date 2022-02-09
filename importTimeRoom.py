#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fetCustomizer import *
from argparse import ArgumentParser

from copy import copy
import sys
import locale

default_stdout = sys.stdout
default_stderr = sys.stderr

reload(sys)

sys.stdout = default_stdout
sys.stderr = default_stderr

sys.setdefaultencoding('utf8')
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

parser = ArgumentParser(description="Copia restrições de um arquivo FET para outro se atividade for compatível")

parser.add_argument('-old'  , action="store", dest="oldfile" ,  type = str, help="Arquivo do semestre anterior que possui as restrições")
parser.add_argument('-new'  , action="store", dest="newfile" ,  type = str, help="Arquivo do semestre atual para qual as restrições serão importadas")
parser.add_argument('-out'  , action="store", dest="output"  ,  type = str, help="Arquivo de saida com os dados do semestra atual mas com as restrições do semestre anterior")

args = parser.parse_args()

fetOld = FetFile( args.oldfile )
fetNew = FetFile( args.newfile )

TimesList = filter( lambda e : e.tag == "ConstraintActivityPreferredStartingTime" and e.find("Active").text == "true", fetOld.xmlTimeConstrainList )
RoomsList = filter( lambda e : e.tag == "ConstraintActivityPreferredRoom"and e.find("Active").text == "true" , fetOld.xmlSpaceConstrainList )

getSingle = lambda field , x : x.find(field).text
getMulti  = lambda field , x : set( e.text for e in x.findall(field) )

basicTags = set( ["LabInf","Desenho","Sala"] )

emb_activities = filter( lambda x: checkAny( "Activity_Tag", ["H_EMB"], x) , fetNew.xmlActivitiesList )

for a in emb_activities:
    
    matchList = filter( lambda x : getSingle("Subject",x) == getSingle("Subject",a) and getMulti("Students",x) == getMulti("Students",a) and  getMulti("Teacher",x) == getMulti("Teacher",a) and getMulti("Activity_Tag", a ).intersection( basicTags) == getMulti("Activity_Tag", x ).intersection( basicTags) , fetOld.xmlActivitiesList )
    idNew =  getSingle("Id", a )
    
    if ( matchList != [] ):
        fetNew.setTag( lambda x : x == a, "horarioImportado")
        aOld = matchList[0]
        idOLd = getSingle("Id", aOld)
        matchTimeList  = filter( lambda e : getSingle("Activity_Id", e ) == idOLd , TimesList )
        matchRoomList =  filter( lambda e : getSingle("Activity_Id", e ) == idOLd , RoomsList )
        assert (len(matchTimeList) == 1) and (len(matchRoomList) == 1), "Erro, deve haver uma e somente uma restrição para a atividade"
        xmlRoom = copy( matchRoomList[0] )
        xmlRoom.find("Activity_Id").text = idNew
        xmlRoom.find("Active").text = "false"
        xmlRoom.find("Comments").text = u"Sala importada do semestre anterior (Turmas e Professor iguais)"
        xmlTime = copy( matchTimeList[0] )
        xmlTime.find("Activity_Id").text = idNew
        xmlTime.find("Active").text = "false"
        xmlTime.find("Comments").text = u"Horário importado do semestre anterior (Turmas e Professor iguais)"
        fetOld.xmlActivitiesList.remove(aOld)
        fetNew.xmlTimeConstrainList.append( xmlTime )
        fetNew.xmlSpaceConstrainList.append( xmlRoom)
        print "------------------------------------------------ "
        print tostring(a, pretty_print = True)
        print tostring(xmlTime, pretty_print = True)
        print tostring(xmlRoom, pretty_print = True)
        print "------------------------------------------------ \n\n"
               
for a in filter( lambda x : checkAny( "Students", [ "0160"+ str(n) for n in range(1,9) ] , x) , emb_activities ):
    matchList = filter( lambda x : getSingle("Subject",x) == getSingle("Subject",a) and getMulti("Students",x) == getMulti("Students",a) and getMulti("Activity_Tag", a ).intersection( basicTags) == getMulti("Activity_Tag", x ).intersection( basicTags) , fetOld.xmlActivitiesList )
    idNew =  getSingle("Id", a )

    if ( matchList != [] ):
        fetNew.setTag( lambda x : x == a, "horarioImportado")
        aOld = matchList[0]
        idOLd = getSingle("Id", aOld)
        matchTimeList  = filter( lambda e : getSingle("Activity_Id", e ) == idOLd , TimesList )
        matchRoomList =  filter( lambda e : getSingle("Activity_Id", e ) == idOLd , RoomsList )
        assert (len(matchTimeList) == 1) and (len(matchRoomList) == 1), "Erro, deve haver uma e somente uma restrição para a atividade"
        xmlRoom = copy( matchRoomList[0] )
        xmlRoom.find("Activity_Id").text = idNew
        xmlRoom.find("Active").text = "false"
        xmlRoom.find("Comments").text = u"Sala importada do semestre anterior (Turmas iguais mas professores diferentes)"
        xmlTime = copy( matchTimeList[0] )
        xmlTime.find("Activity_Id").text = idNew
        xmlTime.find("Active").text = "false"
        xmlTime.find("Comments").text = u"Horário importado do semestre anterior (Turmas iguais mas professores diferentes)"
        fetOld.xmlActivitiesList.remove(aOld)
        fetNew.xmlTimeConstrainList.append( xmlTime )
        fetNew.xmlSpaceConstrainList.append( xmlRoom)

fetNew.write( args.output)
