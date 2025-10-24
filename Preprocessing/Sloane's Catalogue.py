# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 21:29:20 2024

@author: liulu
"""
import xml.etree.ElementTree as ET
import re
from nltk import word_tokenize
import pandas as pd
import os

def read_file(file):
    tree=ET.parse('../original datasets/Sloane/%s'%file)
    root=tree.getroot()   
    text_node=root.find('{http://www.tei-c.org/ns/1.0}text')
    body_node=text_node.find('{http://www.tei-c.org/ns/1.0}body')

    return body_node

def iterate_place_person(node):
    
    
    for child in node:
        if child.tag=='{http://www.tei-c.org/ns/1.0}persName' or child.tag=='{http://www.tei-c.org/ns/1.0}name':
            pers_str = ET.tostring(child, encoding='unicode')
            special_patterns=[r'&amp;',r'&apos;',r'&lt;',r'&gt;',r'&quot;'] 
            replace_patterns=['&','\'','<','>','"']
            for i in range(len(replace_patterns)):
                pers_str=re.sub(special_patterns[i],replace_patterns[i],pers_str)
            persName=''
            pattern=r'>(.*?)<'
            person_result=re.findall(pattern,pers_str,flags=re.S)
            
            for i in person_result:  
                i=i.replace('\n','')
                persName=persName+i          
                space_pattern=r'\s{1,}'
                persName=re.sub(space_pattern,' ',persName)
            
            all_persName.append(persName) 
            
        elif child.tag=='{http://www.tei-c.org/ns/1.0}placeName':
            
            place_str = ET.tostring(child, encoding='unicode')
            special_patterns=[r'&amp;',r'&apos;',r'&lt;',r'&gt;',r'&quot;'] 
            replace_patterns=['&','\'','<','>','"']
            for i in range(len(replace_patterns)):
                pers_str=re.sub(special_patterns[i],replace_patterns[i],place_str)
            placeName=''
            pattern=r'>(.*?)<'
            place_result=re.findall(pattern,place_str,flags=re.S)
            for i in place_result:
                i=i.replace('\n','')
                placeName=placeName+i
                space_pattern=r'\s{1,}'             
                placeName=re.sub(space_pattern,' ',placeName)
            all_placeName.append(placeName)

        else:
            iterate_place_person(child)


def match(node):
    body_str=ET.tostring(node, encoding='unicode')
    pers_pattern=r'<ns0:persName>.*?</ns0:persName>'
    pers_matches=re.findall(pers_pattern,body_str,flags=re.S)    
    
    pers_replacements=[]
    for p in range(len(pers_matches)):
        pers_replacements.append('<ns0:persName>'+' persName '+'</ns0:persName>')
    for match, replacement in zip(pers_matches, pers_replacements):
        body_str = body_str.replace(match, replacement, 1)
    
    pers_pattern=r'<ns0:name>.*?</ns0:name>'
    pers_matches=re.findall(pers_pattern,body_str,flags=re.S)
    pers_replacements=[]
    for p in range(len(pers_matches)):
        pers_replacements.append('<ns0:persName>'+' persName '+'</ns0:persName>')
    for match, replacement in zip(pers_matches, pers_replacements):
        body_str = body_str.replace(match, replacement, 1)
    
    place_pattern=r'<ns0:placeName.*?</ns0:placeName>'
    place_matches=re.findall(place_pattern,body_str,flags=re.S)
    
    place_replacements=[]
    for p in range(len(place_matches)):
        place_replacements.append('<ns0:placeName>'+' placeName '+'</ns0:placeName>')
    for match, replacement in zip(place_matches, place_replacements):
        body_str = body_str.replace(match, replacement, 1)
    
    special_patterns=['&amp;','&apos;','&lt;','&gt;','&quot;'] 
    replace_patterns=['&','\'','<','>','"']
    
    for i in range(len(replace_patterns)):
        body_str=re.sub(special_patterns[i],replace_patterns[i],body_str)

    group_pattern=r'>(.*?)<' 
    group_result=re.findall(group_pattern,body_str,flags=re.S)

    new_group=[]
    #remove null
    text=''
    for m in group_result:
        m=m.replace('\n',' ')
        space_pattern=r'\s{1,}' #去掉换行后莫名奇妙的空格                
        m=re.sub(space_pattern,' ',m)
        if m!='' and m.isspace() == False:
            new_group.append(m)
        text=text+m
    
    pers_pattern=r'persName'
    pers_matches=re.findall(pers_pattern,text,flags=re.S)
    for match,replacement in zip(pers_matches, all_persName):
        real_text=text.replace(match,replacement,1)
    
    place_pattern=r'placeName'
    place_matches=re.findall(place_pattern,real_text,flags=re.S)
    for match,replacement in zip(place_matches, all_placeName):
        real_text=real_text.replace(match,replacement,1)
    
    return text,real_text
    
def token():   
    text,real_text=match(body_node)
    all_token=[] 
    all_entity=[]   
    
    tokens=word_tokenize(text)
    pers_index=0
    place_index=0
     
    for t in tokens:
        if t=='persName':
            p_tokens=word_tokenize(all_persName[pers_index])
            for p in p_tokens:
                all_token.append(p)
            if len(p_tokens)==1:
                all_entity.append('B-pers')
            else:
                all_entity.append('B-pers')
                for i in range(len(p_tokens)-1):
                    all_entity.append('I-pers')   
            pers_index+=1
        elif t=='placeName':
            p_tokens=word_tokenize(all_placeName[place_index])
            for p in p_tokens:
                all_token.append(p)
            if len(p_tokens)==1:
                all_entity.append('B-place')
            else:
                all_entity.append('B-place')
                for i in range(len(p_tokens)-1):
                    all_entity.append('I-place')   
            place_index+=1
        else:
            all_token.append(t)
            all_entity.append('O')
    
    return all_token,all_entity
     
def write_csv(file):
    all_token,all_entity=token()
    file=file.replace('.xml','.tsv')
    dataframe = pd.DataFrame({'TOKEN':all_token,'NE':all_entity})
    dataframe.to_csv("../evaluation datasets/Sloane_new/%s"%file,index=False,sep='\t')   

if __name__ == "__main__":
    path='../original datasets/Sloane'   
    files= os.listdir(path)
    for file in files[0:2]:
        all_persName=[]
        all_placeName=[]        
        body_node=read_file(file)
        iterate_place_person(body_node)
        write_csv(file)
    
    
    
    
    
