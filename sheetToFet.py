#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 17:09:29 2017

@author: diogo
"""

def printDict(d):
    for key, value in d.iteritems():
        print( key,": ",value)
    
from zohoRow import zohoRow
from fetXML import fetXML
from timetable import *
from csvData import csvData, unique
from activity import singleActivity, groupActivity
from argparse import ArgumentParser
import pandas as pd

parser = ArgumentParser(description="Converte planilha google para uma arquivo FET")
parser.add_argument('-o'     , action="store" ,dest="file" ,  type = str, help="Nome do arquivo de saida" )
parser.add_argument('-code'  , action="store", dest="code"  ,  type = str, help='Código da planilha do googledocs.')
args = parser.parse_args()

sheet_url = lambda code, sheet_name  : "https://docs.google.com/spreadsheets/d/{key}/gviz/tq?tqx=out:csv&sheet={sheet_name}".format( key = code  , sheet_name = sheet_name )

fetFileName = args.file
fet = fetXML( fetFileName )

# Acrescenta dados inicias
fet.setInstitutionName("UFSC")
fet.setDays(["Seg","Ter","Qua","Qui","Sex"])
fet.setHours(["07:30 - 08:20","08:40 - 09:30","09:30 - 10:20","10:30 - 11:20","11:20 - 12:10","Almoco","13:30 - 14:20","14:20 - 15:10","15:10 - 16:00","16:20 - 17:10","17:10 - 18:00","18:00 - 18:50","18:50 - 19:40"])

# Adiciona os professores
teacherStringList = pd.read_csv("Professores.csv"  , header = None , usecols = (0,), encoding = "utf-8" )[0].tolist()
#teacherStringList = pd.read_csv(sheet_url(args.code, "Professores" ) , header = None , usecols = (0,), encoding = "utf-8" )[0].tolist()
teacherStringList.remove(u'A definir')

fet.setTeachers( teacherStringList )

subjectStringList = pd.read_csv('Disciplinas.csv' , header = None , usecols = (0,))[0].tolist()
#subjectStringList = pd.read_csv(sheet_url(args.code, 'Disciplinas' ) , header = None , usecols = (0,))[0].tolist()
fet.setSubjects( subjectStringList )

df = pd.read_csv("Dados.csv"  )
#df = pd.read_csv(sheet_url(args.code, "Dados" ) )
df.drop( [ col for col in df.columns if col.find("Unnamed: ") != -1 ], axis = 1, inplace = True )
    
data = csvData( df.to_dict("records") )

# Descarta linhas de disciplina não ofertados, ou o professor não foi definido corretamente
data.removeBy(u"Professor",u'ZZ - N\xe3o ofertada')
data.removeBy(u"Professor",u'A definir')
data.removeBy(u"Indicação de Horário",u'preencher')
data.removeBy(u"Código - Nome",u'EMB5322 - Trabalho de Conclusão de Curso')
data.removeBy(u"Código - Nome",u'EMB5323 - Estágio Curricular Obrigatório')
data.removeBy(u"Código - Nome",u'EMB5523 - Estágio Curricular Obrigatório')
data.removeBy(u"Código - Nome",u'EMB5620 - Estágio Curricular Obrigatório')
data.removeBy(u"Código - Nome",u'EMB5722 - Estágio Curricular Obrigatório')
data.removeBy(u"Código - Nome",u'EMB5823 - Estágio Curricular Obrigatório')
data.removeBy(u"Código - Nome",u'EMB5921 - Estágio Curricular Obrigatório')
data.removeBy(u"Código - Nome",u'EMB5200 - Trabalho de Conclusão de Curso')
data.removeBy(u"Código - Nome",u'EMB5322 - Trabalho de Conclusão de Curso')
data.removeBy(u"Código - Nome",u'EMB5421 - Trabalho de Conclusão de Curso')
data.removeBy(u"Código - Nome",u'EMB5522 - Trabalho de Conclusão de Curso')
data.removeBy(u"Código - Nome",u'EMB5619 - Trabalho de Conclusão de Curso')
data.removeBy(u"Código - Nome",u'EMB5721 - Trabalho de Conclusão de Curso')
data.removeBy(u"Código - Nome",u'EMB5822 - Trabalho de Conclusão de Curso')
data.removeBy(u"Código - Nome",u'EMB5920 - Trabalho de Conclusão de Curso')
zohoList = [] 

for row in data:
    try:
        zohoList.append( zohoRow(row) )
    except ValueError as e:
       print( "Não foi possível interpretar corretamente a linha abaixo, esta será ignorada!!" )
       print( e.message     )
       printDict(row)

subjectList = unique( [ z.subject for z in zohoList ] )

globalList = []

for subject in sorted( subjectList ):
   
    thisSubjectList = list( filter( lambda z : z.subject == subject, zohoList) )
    theoricalGroupList = unique( [ z.theoricalGroup for z in thisSubjectList ] )
        
    for theoricalGroup in theoricalGroupList:    

        thisTheoricalGroupList = list( filter( lambda z : z.theoricalGroup == theoricalGroup, thisSubjectList) )
        practicalGroupList = unique( [ z.practicalGroup for z in thisTheoricalGroupList ] )
              
        if (theoricalGroup != sum( practicalGroupList,  Student(None)  ) ) :  raise ValueError("Combinação dos grupos práticos não forma o grupo teórico\n" + "".join( [ str(t) for t in thisTheoricalGroupList ]) )  

        actTheoretical = singleActivity(subject)
        g = groupActivity(actTheoretical)
        for practicalGroup in practicalGroupList:
            
            thisPracticalGroupList = list( filter( lambda z : z.practicalGroup == practicalGroup, thisTheoricalGroupList) )
            mainSetList = unique( [ z.mainSet for z in thisPracticalGroupList ] )

            if (practicalGroup != sum( mainSetList ,  Student(None)  ) ) :  raise ValueError("Combinação das turmas não forma o grupo prático\n" + "".join( [ str(t) for t in thisPracticalGroupList ]) )  
        
            actPractical = singleActivity(subject)
            for mainSet in mainSetList:
                
                 thisMainSetList = list( filter( lambda z : z.mainSet == mainSet , thisPracticalGroupList)    )
                 for row in thisMainSetList:
                     
                     actPractical.add(row, row.practicalTime)                        
                     actTheoretical.add(row, row.theoricalTime)
                             
                     if (row.numOfTeachers != len(thisMainSetList)):
                         raise ValueError("Númeror de professores informado não conside com o descrito.\n" + str(row) )
                     
            if (actPractical.time > 0):
                g.append(actPractical)

        if (actTheoretical.time == 0): g.remove(actTheoretical)

#        if (actTheoretical.time == 4):
#            actTheoretical.time = 
#            g.append(actTheoretical)
        
        if (g.getTotalTime() == 0) : raise ValueError("Disciplina com 0 (zero) créditos.\n" + str(g) )

        if ( g[0].format != g.getFormat() ) and (g[0].format != "") and (g[0].format != "V"):
            g.reFormat( g[0].format )
            
        fet.addGroupActivity(g)

        globalList.append(g)

fet.close()


# Acessando 
