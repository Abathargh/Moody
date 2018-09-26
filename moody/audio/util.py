'''
Created on 25 set 2018

@author: mar

'''

def differences ( l ) :
   
    diff = []
    c = 0
    
    while c < len ( l ) - 1 :
        
        diff.append( abs ( l [ c + 1 ] - l [ c ] ) )
        c += 1
        
    return diff

 
def average ( l ) :
    
    return sum(l)/len(l)
