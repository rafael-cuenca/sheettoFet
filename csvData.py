# -*- coding: utf-8 -*-
"""
Created on Tue May 30 20:51:50 2017

@author: diogo
"""


def unique(lst):
    return list( set(lst) )

class csvData(list):

    def __init__(self, iterable):
        
        super(csvData,self).__init__(iterable)        
        
    def removeBy(self,fieldname,name):
        for x in self.filterBy(fieldname,name):
            self.remove( x )
        
    def filterBy(self,fieldname,name):
        return csvData( filter( lambda line : line[fieldname] == name , self) )

    def sortBy(self,fieldname):
        self.sort( key = lambda line : line[fieldname]  )

    def getBy(self,fieldname):
        return [ line[fieldname] for line in self ]
        
    def getByUnique(self,fieldname):
        return np.unique( self.getBy(fieldname) ).tolist()