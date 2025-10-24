# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 15:56:15 2024

@author: liulu
"""
import csv
import pandas as pd
import numpy as np

def prerocessing():
    hipe=pd.read_csv("../original datasets/HIPE-data-v1.3-test-masked-bundle5-en.tsv", delimiter="\t", quoting=csv.QUOTE_NONE, encoding='utf-8')
    
    #drop extra columns
    hipe=hipe.drop(['NE-COARSE-METO','NE-FINE-LIT','NE-FINE-LIT','NE-FINE-METO','NE-FINE-COMP','NE-NESTED','NEL-LIT','NEL-METO','MISC'],axis=1)
    
    #drop articles in other periods
    hipe.drop(hipe.index[6139:18920],inplace=True)
    
    #drop null value
    hipe.dropna(axis=0, how='any', inplace=True)
    hipe.to_csv("../evaluation datasets/HIPE2020_new.tsv",index=False,sep='\t')
    
if __name__ == "__main__":
    prerocessing()
