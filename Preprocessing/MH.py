import xml.etree.ElementTree as ET
import re
from nltk import word_tokenize
import pandas as pd
import os

def read_file(file):
    tree=ET.parse('../original datasets/XML_files_minus_project-specific_mark-up_20240212/%s'%file)
    root=tree.getroot()
    text_node=root.find('{http://www.tei-c.org/ns/1.0}text')
    return text_node

def iterate_place_person(node):
    #extract all the persName and placeName
    global all_persName
    global all_placeName
    
    for child in node:
        if child.tag=='{http://www.tei-c.org/ns/1.0}persName':
            pers_str = ET.tostring(child, encoding='unicode')
            #check if <sic> exists
            sic_str=r'<ns0:sic.*?>'
            sic_result=re.search(sic_str,pers_str,flags=re.DOTALL)
            if sic_result!=None:
                #if <sic> exists, remove <corr>
                name_str=re.sub(r'<ns0:corr>.*?</ns0:corr>','',pers_str,flags=re.DOTALL) 
            else:
                name_str=pers_str
                
            expan_str=r'<ns0:expan.*?>'            
            expan_result=re.search(expan_str,name_str,flags=re.DOTALL)
            if expan_result!=None:
                #if <expan> exists, remore <expan>
                name_str=re.sub(r'<ns0:expan>.*?</ns0:expan>','',name_str,flags=re.DOTALL)
            else:
                name_str=name_str
                            
            lb_str=r'<ns0:lb.*?>'
            lb_result=re.search(lb_str,name_str,flags=re.DOTALL)
            if lb_result!=None:
                #if <lb> exists, remove <orig>
                name_str=re.sub(r'<ns0:orig>.*?</ns0:orig>','',name_str,flags=re.DOTALL)
                              
            else:
                #if no <lb>, remove <reg> 
                name_str=re.sub(r'<ns0:reg>.*?</ns0:reg>','',name_str,flags=re.DOTALL)
            
            #if <lb>, replace it with space
            space_pattern=r'\s{1,}'
            name_str=re.sub(space_pattern,' ',name_str)
            
            #for nested str
            persName=''
            pattern=r'>(.*?)<'
            
            person_result=re.findall(pattern,name_str)
            
            for i in person_result:  
                persName=persName+i 
                         
            all_persName.append(persName)
                            
        elif child.tag=='{http://www.tei-c.org/ns/1.0}placeName':              
            place_str = ET.tostring(child, encoding='unicode')
            #check if <sic> exists
            sic_str=r'<ns0:sic.*?>'
            sic_result=re.search(sic_str,place_str,flags=re.DOTALL)
            if sic_result!=None:
                #if <sic> exists, remove <corr>
                name_str=re.sub(r'<ns0:corr>.*?</ns0:corr>','',place_str,flags=re.DOTALL) 
            else:
                name_str=place_str
                
            expan_str=r'<ns0:expan.*?>'            
            expan_result=re.search(expan_str,name_str,flags=re.DOTALL)
            if expan_result!=None:
                #if <expan> exists, remore <expan>
                name_str=re.sub(r'<ns0:expan>.*?</ns0:expan>','',name_str,flags=re.DOTALL)
            else:
                name_str=name_str
                            
            lb_str=r'<ns0:lb.*?>'
            lb_result=re.search(lb_str,name_str,flags=re.DOTALL)
            if lb_result!=None:
                #if <lb> exists, remove <orig>
                name_str=re.sub(r'<ns0:orig>.*?</ns0:orig>','',name_str,flags=re.DOTALL)
            else:
                #if no <lb>, remove <reg> 
                name_str=re.sub(r'<ns0:reg>.*?</ns0:reg>','',name_str,flags=re.DOTALL) 
            
            #if <lb>, replace it with space
            space_pattern=r'\s{1,}'
            name_str=re.sub(space_pattern,' ',name_str)
                        
            #for nested str
            placeName=''
            pattern=r'>(.*?)<'
            place_result=re.findall(pattern,name_str)
            for i in place_result:  
                placeName=placeName+i 
            all_placeName.append(placeName)
        else:
            iterate_place_person(child)
            
def transcribe(node):   
#extract plain text
    global text
    text_str=ET.tostring(node, encoding='unicode')
    new_str1=re.sub(r'<ns0:expan>.*?</ns0:expan>','',text_str)
    new_str2=re.sub(r'<ns0:reg>.*?</ns0:reg>','',new_str1)
    new_str3=re.sub(r'<.*?>','',new_str2,flags=re.DOTALL)
    new_str4=new_str3.replace('&amp;','&')
    text=new_str4
    
def match(node):
    #match the text with entity
    text_str=ET.tostring(node, encoding='unicode')    
    #remove note
    text_str=re.sub(r'<ns0:note.*?</ns0:note>','',text_str)
    
    choice_pattern=r'<ns0:choice.*?</ns0:choice>'
    choice_matches=re.findall(choice_pattern, text_str,flags=re.S)
    
    sic_str=r'<ns0:sic.*?>'
    expan_str=r'<ns0:expan.*?>'
    lb_str=r'<ns0:lb.*?>'
    choice_replace_result=[]
    for all_choice in choice_matches:
        if re.search(sic_str, all_choice,flags=re.S)!=None:
            all_choice=re.sub(r'<ns0:corr>.*?</ns0:corr>','',all_choice,flags=re.S)
        else:
            all_choice=all_choice
        
        if re.search(expan_str, all_choice,flags=re.S)!=None:
            all_choice=re.sub(r'<ns0:expan>.*?</ns0:expan>','',all_choice,flags=re.S)
        else:
            all_choice=all_choice
        
        if re.search(lb_str, all_choice,flags=re.S)!=None:
            all_choice=re.sub(r'<ns0:orig>.*?</ns0:orig>','',all_choice,flags=re.S)
        else:
            all_choice=re.sub(r'<ns0:reg>.*?</ns0:reg>','',all_choice,flags=re.S)
       
        space_pattern=r'\s{1,}'
        all_choice=re.sub(space_pattern,' ',all_choice)

        pattern=r'>(.*?)<' 
        result=re.findall(pattern,all_choice)
        new_result=''
        for letter in result:
            new_result=new_result+letter
        choice_replace_result.append(new_result)
    choice_num=len(choice_replace_result)
    choice_replacements=[]
    choice_index=0
    for i in range(choice_num):
        choice_replacements.append('<ns0:choice>'+choice_replace_result[choice_index]+'</ns0:choice>')
        choice_index+=1
    for match,replacement in zip(choice_matches, choice_replacements):
        text_str=text_str.replace(match,replacement,1)
     
    #all person names change to 'persName' 
    pers_pattern=r'<ns0:persName.*?</ns0:persName>'
    pers_matches=re.findall(pers_pattern,text_str,flags=re.S)
    pers_replacements=[]
    for p in range(len(pers_matches)):
        pers_replacements.append('<ns0:persName>'+'persName'+'</ns0:persName>')
    for match, replacement in zip(pers_matches, pers_replacements):
        text_str = text_str.replace(match, replacement, 1)
    
    place_pattern=r'<ns0:placeName.*?</ns0:placeName>'
    place_matches=re.findall(place_pattern,text_str,flags=re.S)
    place_replacements=[]
    for p in range(len(place_matches)):
        place_replacements.append('<ns0:placeName>'+'placeName'+'</ns0:placeName>')
    for match, replacement in zip(place_matches, place_replacements):
        text_str = text_str.replace(match, replacement, 1)
      
    text_str=text_str.replace('&amp;','&')
    group_pattern=r'>(.*?)<' 
    group_result=re.findall(group_pattern,text_str,flags=re.S)
    
    new_group=[]
    #remove null
    for m in group_result:
        if m!='' and m.isspace() == False:
            new_group.append(m)
            
    index=0
    text_entity={}
    for i in new_group:
        inter=[]
        index+=1
        if i =='persName':
            inter.append(i)
            inter.append('IOB-pers')
            text_entity[index]=inter
        elif i == 'placeName':
            inter.append(i)
            inter.append('IOB-place')
            text_entity[index]=inter
        else:
            inter.append(i)
            inter.append('')
            text_entity[index]=inter
    
    pers_index=0
    place_index=0
    for keys, values in text_entity.items():
        if values[0]=='persName':
            values[0]=all_persName[pers_index]
            pers_index+=1
        elif values[0]=='placeName':
            values[0]=all_placeName[place_index]
            place_index+=1
        
    return text_entity
 
            
        
def token():
    text_entity=match(text_node)
    all_tokens=[]
    all_entity=[]
    
    for keys,values in text_entity.items():
        tt=values[0]
        if len(values[0])==0:
            continue
        word=word_tokenize(tt)
        
        for w in word:
            all_tokens.append(w)
        
        if values[1]=='IOB-pers':
            if len(word)==1:
                all_entity.append('B-pers')
            else:
                all_entity.append('B-pers')
                for i in range(len(word)-1):
                    all_entity.append('I-pers')
        elif values[1]=='IOB-place':
            if len(word)==1:
                all_entity.append('B-place')
            else:
                all_entity.append('B-place')
                for i in range(len(word)-1):
                    all_entity.append('I-place')
        else:
            for i in range(len(word)):                
                all_entity.append('O')

    return all_tokens,all_entity

def write_csv(file):
    all_tokens,all_entity=token()
    print(len(all_tokens),len(all_entity))
    file=file.replace('.xml','.tsv')
    dataframe = pd.DataFrame({'TOKEN':all_tokens,'NE':all_entity})
    dataframe.to_csv('../evaluation datasets/Mary Hamilton_new/%s'%file,index=False,sep='\t')
    
if __name__ == "__main__":
    path='../original datasets/XML_files_minus_project-specific_mark-up_20240212'   
    files= os.listdir(path)
    for file in files[0:1598]:  
        all_node=[]
        all_persName=[]
        all_placeName=[]
        text_node=read_file(file)
        iterate_place_person(text_node)
        write_csv(file)
    