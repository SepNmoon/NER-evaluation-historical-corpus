# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 15:08:29 2024

@author: liulu
"""

import csv
import spacy
import os

def read_file(file_path):
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        tsv_reader = csv.reader(file, delimiter='\t')
        index=0
        for row in tsv_reader:
            if index>0:
                data.append(row)
            index+=1
    return data


#convert iob to format spacy can process
def iob_to_spacy_format(iob_lines):
    data = []
    sentence = []
    entities = []
    current_entity = None
    start = 0
    
    for line in iob_lines:
        if line.strip() == "":  
            if sentence:
                data.append((" ".join(sentence), {"entities": entities}))
            sentence = []
            entities = []
            current_entity = None
            start = 0
            continue
        word, label = line.strip().split()
        sentence.append(word)
        word_start = start
        word_end = start + len(word)
        
        if label.startswith("B-"):  
            if current_entity:
                entities.append((current_entity[0], current_entity[1], current_entity[2]))
            current_entity = [word_start, word_end, label[2:]]
        
        elif label.startswith("I-") and current_entity:  
            current_entity[1] = word_end
        elif label == "O":  
            if current_entity:
                entities.append((current_entity[0], current_entity[1], current_entity[2]))
                current_entity = None
        start = word_end + 1 
        
    if sentence:
        data.append((" ".join(sentence), {"entities": entities}))
    
    return data
    
def spacy_predict(test_data):
    for text, annotations in test_data:
        doc = nlp(text)
        #print("Entities in '%s':" % doc)
        true_entities = annotations['entities']
        #print(true_entities)
        
        pred_entities=[]
        for ent in doc.ents:
            #print(ent.text, ent.label_)
            if ent.label_=='PERSON':
                #print(ent.text)
                temp=[]
                temp.append(ent.start_char)
                temp.append(ent.end_char)
                temp.append(ent.label_)
                pred_entities.append(temp)
            elif ent.label_=='GPE':
                temp=[]
                temp.append(ent.start_char)
                temp.append(ent.end_char)
                temp.append(ent.label_)
                pred_entities.append(temp)
            elif ent.label_=='LOC':
                temp=[]
                temp.append(ent.start_char)
                temp.append(ent.end_char)
                temp.append(ent.label_)
                pred_entities.append(temp)

        
        return true_entities, pred_entities, doc


def score(mode):
    all_correct=all_per_correct+all_place_correct
    all_relevant=all_per_relevant+all_place_relevant
    all_retrive=all_per_retrive+all_place_retrive
    all_partial=all_per_partial+all_place_partial
    all_partial_type=all_per_partial_type+all_place_partial_type
    all_partial_weak=all_per_partial_weak+all_place_partial_weak
    if mode=='strict':
        per_precision=all_per_correct/all_per_retrive
        per_recall=all_per_correct/all_per_relevant        
        place_precision=all_place_correct/all_place_retrive
        place_recall=all_place_correct/all_place_retrive         
        micro_precision=all_correct/all_retrive
        micro_recall=all_correct/all_relevant
        #print(all_per_correct,all_per_retrive)
    elif mode=='type':
        per_precision=(all_per_correct+0.5*all_per_partial)/all_per_retrive
        per_recall=(all_per_correct+0.5*all_per_partial)/all_per_relevant
        place_precision=(all_place_correct+0.5*all_place_partial)/all_place_retrive
        place_recall=(all_place_correct+0.5*all_place_partial)/all_place_relevant
        micro_precision=(all_correct+0.5*all_partial)/all_retrive
        micro_recall=(all_correct+0.5*all_partial)/all_relevant
        #print(all_per_correct,all_per_partial,all_per_retrive)
    elif mode=='partial':
        per_precision=(all_per_correct+0.5*all_per_partial_type+0.25*all_per_partial_weak)/all_per_retrive
        per_recall=(all_per_correct+0.5*all_per_partial_type+0.25*all_per_partial_weak)/all_per_relevant
        place_precision=(all_place_correct+0.5*all_place_partial_type+0.25*all_place_partial_weak)/all_place_retrive
        place_recall=(all_place_correct+0.5*all_place_partial_type+0.25*all_place_partial_weak)/all_place_relevant
        micro_precision=(all_correct+0.5*all_partial_type+0.25*all_partial_weak)/all_retrive
        micro_recall=(all_correct+0.5*all_partial_type+0.25*all_partial_weak)/all_relevant
        #print(all_per_correct,all_per_partial_type,all_per_retrive)
    elif mode=='lenient':
        per_precision=(all_per_correct+all_per_partial)/all_per_retrive
        per_recall=(all_per_correct+all_per_partial)/all_per_relevant
        place_precision=(all_place_correct+all_place_partial)/all_place_retrive
        place_recall=(all_place_correct+all_place_partial)/all_place_relevant
        micro_precision=(all_correct+all_partial)/all_retrive
        micro_recall=(all_correct+all_partial)/all_relevant
    elif mode=='ultra-lenient':
        per_precision=(all_per_correct+all_per_partial_type+all_per_partial_weak)/all_per_retrive
        per_recall=(all_per_correct+all_per_partial_type+all_per_partial_weak)/all_per_relevant
        place_precision=(all_place_correct+all_place_partial_type+all_place_partial_weak)/all_place_retrive
        place_recall=(all_place_correct+all_place_partial_type+all_place_partial_weak)/all_place_relevant
        micro_precision=(all_correct+all_partial_type+all_partial_weak)/all_retrive
        micro_recall=(all_correct+all_partial_type+all_partial_weak)/all_relevant
       
    per_f=(2*per_precision*per_recall)/(per_precision+per_recall)
    place_f=(2*place_precision*place_recall)/(place_precision+place_recall)    
    macro_f=(per_f+place_f)/2
    micro_f=(2*micro_precision*micro_recall)/(micro_precision+micro_recall)
    
    
    return per_precision,per_recall,per_f,place_precision,place_recall,place_f,macro_f,micro_f


def data_display(true_entities, pred_entities,test_data):
    #print(true_entities, pred_entities)

    combine_entities=[]    
    correct_true=[]
    correct_pred=[]
    for te in true_entities:
        for pe in pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:   
                correct_true.append(te)
                correct_pred.append(pe)
                temp1=[]
                temp1.append(te[0])
                temp1.append(te[1])
                temp1.append(test_data[0][0][te[0]:te[1]])
                temp1.append(te[2])
                temp2=[]
                temp2.append(pe[0])
                temp2.append(pe[1])
                temp2.append(test_data[0][0][pe[0]:pe[1]])
                temp2.append(pe[2])
                temp=[]
                temp.append(temp1)
                temp.append(temp2)
                combine_entities.append(temp)
                break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):   
                correct_true.append(te)
                correct_pred.append(pe)
                temp1=[]
                temp1.append(te[0])
                temp1.append(te[1])
                temp1.append(test_data[0][0][te[0]:te[1]])
                temp1.append(te[2])
                temp2=[]
                temp2.append(pe[0])
                temp2.append(pe[1])
                temp2.append(test_data[0][0][pe[0]:pe[1]])
                temp2.append(pe[2])
                temp=[]
                temp.append(temp1)
                temp.append(temp2)
                combine_entities.append(temp)
                
    for entity in true_entities:        
        if entity not in correct_true:                
            temp1=[]
            temp1.append(entity[0])
            temp1.append(entity[1])
            temp1.append(test_data[0][0][entity[0]:entity[1]])
            temp1.append(entity[2])
            temp2=[]
            temp2.append('O')
            temp=[]
            temp.append(temp1)
            temp.append(temp2)
            combine_entities.append(temp)
            #print(temp)
           
    for entity in pred_entities:
        if entity not in correct_pred:
            temp1=[]
            temp1.append('O')
            temp2=[]
            temp2.append(entity[0])
            temp2.append(entity[1])
            temp2.append(test_data[0][0][entity[0]:entity[1]])
            temp2.append(entity[2])
            temp=[]
            temp.append(temp1)
            temp.append(temp2)
            combine_entities.append(temp)

    return combine_entities

def strict(true_entities, pred_entities):
    per_correct=[]
    per_incorrect=[]
    place_correct=[]
    place_incorrect=[]

    for te in true_entities:
        for pe in  pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:
                if te[2]=='pers' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):
                if (te[2]=='pers' and pe[2]=='PERSON') or (te[2]=='pers' and (pe[2]=='GPE' or pe[2]=='LOC')):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    
                elif (te[2]=='place' and (pe[2]=='GPE' or pe[2]=='LOC')) or (te[2]=='place' and pe[2]=='PERSON'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
   
    per_true_entities=[]
    place_true_entities=[]
    for entity in true_entities:
        if entity[2]=='pers':
            per_true_entities.append(entity)
        elif entity[2]=='place':
            place_true_entities.append(entity)
    
    per_pred_entities=[]
    place_pred_entities=[]
    for entity in pred_entities:
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='LOC' or entity[2]=='GPE':
            place_pred_entities.append(entity)            
    
    per_miss= per_true_entities.copy()       
    for entity in per_correct:            
            per_miss.remove(entity[0])            
    for entity in per_incorrect:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
    
    per_spurius=per_pred_entities.copy()
    for entity in per_correct:
        per_spurius.remove(entity[1])
    for entity in per_incorrect:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
   
    for entity in place_incorrect:
        if entity[1][2]=='PERSON':
            try:
                per_spurius.remove(entity[1])
            except ValueError:
                pass
    
    place_miss= place_true_entities.copy()       
    for entity in place_correct:            
            place_miss.remove(entity[0])            
    for entity in place_incorrect:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
   
    place_spurius=place_pred_entities.copy()
    for entity in place_correct:
            place_spurius.remove(entity[1])

    for entity in place_incorrect:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    
    for entity in per_incorrect:
        if entity[1][2]=='GPE' or entity[1][2]=='LOC':
            try:
                place_spurius.remove(entity[1])
            except ValueError:
                pass

    per_correct=len(per_correct)
    per_incorrect=len(per_incorrect)
    per_miss=len(per_miss)
    per_spurius=len(per_spurius)
    per_partial=0
    
    place_correct=len(place_correct)
    place_incorrect=len(place_incorrect)
    place_miss=len(place_miss)
    place_spurius=len(place_spurius)
    place_partial=0

    global all_per_correct,all_per_incorrect,all_per_partial,all_per_miss,all_per_spurius
    
    all_per_correct=all_per_correct+per_correct
    all_per_incorrect=all_per_incorrect+per_incorrect
    all_per_partial=all_per_partial+per_partial
    all_per_miss=all_per_miss+per_miss
    all_per_spurius=all_per_spurius+per_spurius
    
    global all_place_correct,all_place_incorrect,all_place_partial,all_place_miss,all_place_spurius
    
    all_place_correct=all_place_correct+place_correct
    all_place_incorrect=all_place_incorrect+place_incorrect
    all_place_partial=all_place_partial+place_partial
    all_place_miss=all_place_miss+place_miss
    all_place_spurius=all_place_spurius+place_spurius
    
    global all_per_relevant,all_per_retrive,all_place_relevant,all_place_retrive
    per_relevant=0
    per_retrive=0
    place_relevant=0
    place_retrive=0
    for te in true_entities:
        if te[2]=='pers':
            per_relevant+=1
        elif te[2]=='place':
            place_relevant+=1
    
    all_per_relevant=all_per_relevant+per_relevant
    all_place_relevant=all_place_relevant+place_relevant
    
    for pe in pred_entities:
        if pe[2]=='PERSON':
            per_retrive+=1
        elif (pe[2]=='GPE' or pe[2]=='LOC'):
            place_retrive+=1
    
    all_per_retrive=all_per_retrive+per_retrive
    all_place_retrive=all_place_retrive+place_retrive
    
def type_match(true_entities, pred_entities,test_data):
    
    per_correct=[]
    per_incorrect=[]
    per_partial=[]
    place_correct=[]
    place_incorrect=[]
    place_partial=[]
    
    for te in true_entities:
        for pe in pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:
                if te[2]=='pers' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):  
                if te[2]=='pers' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial.append(temp)        
                elif te[2]=='pers' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp) 
                    
                elif te[2]=='place' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial.append(temp)
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    
    per_true_entities=[]
    place_true_entities=[]
    for entity in true_entities:
        if entity[2]=='pers':
            per_true_entities.append(entity)
        elif entity[2]=='place':
            place_true_entities.append(entity)
    
    per_pred_entities=[]
    place_pred_entities=[]
    for entity in pred_entities:
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='LOC' or entity[2]=='GPE':
            place_pred_entities.append(entity)
               
    per_miss= per_true_entities.copy()       
    for entity in per_correct:
        try:           
            per_miss.remove(entity[0])    
        except ValueError:
            pass
    for entity in per_incorrect:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
    for entity in per_partial:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass

    per_spurius=per_pred_entities.copy()
    for entity in per_correct:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in per_partial:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass                
    
    for entity in place_incorrect:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass

    place_miss= place_true_entities.copy()       
    for entity in place_correct:
        try:            
            place_miss.remove(entity[0])
        except ValueError:
            pass
            
    for entity in place_incorrect:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
        
    for entity in place_partial:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
    
    place_spurius=place_pred_entities.copy()
    for entity in place_correct:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in place_partial:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in per_incorrect:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    
    '''
    true_incorrect=[]
    pred_incorrect=[]
    #print(per_incorrect)
    for per_group in per_incorrect:
        true_incorrect.append(per_group[0])
        pred_incorrect.append(per_group[1])
    
    conjoined_entities=data_display(true_incorrect, pred_incorrect, test_data)
    
    for i in conjoined_entities:
        print(i)
    '''    
    per_correct=len(per_correct)
    per_incorrect=len(per_incorrect)
    per_miss=len(per_miss)
    per_spurius=len(per_spurius)
    per_partial=len(per_partial)
        
    place_correct=len(place_correct)
    place_incorrect=len(place_incorrect)
    place_miss=len(place_miss)
    place_spurius=len(place_spurius)
    place_partial=len(place_partial)
    
    global all_per_correct
    global all_per_incorrect
    global all_per_partial
    global all_per_miss
    global all_per_spurius
    
    all_per_correct=all_per_correct+per_correct
    all_per_incorrect=all_per_incorrect+per_incorrect
    all_per_partial=all_per_partial+per_partial
    all_per_miss=all_per_miss+per_miss
    all_per_spurius=all_per_spurius+per_spurius
    
    global all_place_correct
    global all_place_incorrect
    global all_place_partial
    global all_place_miss
    global all_place_spurius
    
    all_place_correct=all_place_correct+place_correct
    all_place_incorrect=all_place_incorrect+place_incorrect
    all_place_partial=all_place_partial+place_partial
    all_place_miss=all_place_miss+place_miss
    all_place_spurius=all_place_spurius+place_spurius
    
    global all_per_relevant,all_per_retrive,all_place_relevant,all_place_retrive
    per_relevant=0
    per_retrive=0
    place_relevant=0
    place_retrive=0
    for te in true_entities:
        if te[2]=='pers':
            per_relevant+=1
        elif te[2]=='place':
            place_relevant+=1

    all_per_relevant=all_per_relevant+per_relevant
    all_place_relevant=all_place_relevant+place_relevant
    
    for pe in pred_entities:
        if pe[2]=='PERSON':
            per_retrive+=1
        elif (pe[2]=='GPE' or pe[2]=='LOC'):
            place_retrive+=1
    
    all_per_retrive=all_per_retrive+per_retrive
    all_place_retrive=all_place_retrive+place_retrive
    
def partial_match(true_entities, pred_entities,test_data):
    conjoined_entities=data_display(true_entities, pred_entities, test_data)
    per_correct=[]
    per_partial_type=[]
    per_partial_weak=[]
    place_correct=[]
    place_partial_type=[]
    place_partial_weak=[]
    
    for te in true_entities:
        for pe in pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:                
                if te[2]=='pers' and pe[2]=='PERSON':
                    
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_weak.append(temp)  
                    break
                elif te[2]=='place' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_weak.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]): 
                
                if te[2]=='pers' and pe[2]=='PERSON':
                    
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_type.append(temp)
                    #break
                elif te[2]=='pers' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_weak.append(temp)
                elif te[2]=='place' and (pe[2]=='GPE' or pe[2]=='LOC'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_type.append(temp)
                    #break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_weak.append(temp)
                    #break
    
    per_true_entities=[]
    place_true_entities=[]
    
    for entity in true_entities:
        if entity[2]=='pers':
            per_true_entities.append(entity)
        elif entity[2]=='place':
            place_true_entities.append(entity)
    
    per_pred_entities=[]
    place_pred_entities=[]
    
    for entity in pred_entities:
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='GPE' or entity[2]=='LOC':
            place_pred_entities.append(entity)
    
    per_miss= per_true_entities.copy()      
    for entity in per_correct:
        try:           
            per_miss.remove(entity[0])    
        except ValueError:
            pass
    for entity in per_partial_type:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
    for entity in per_partial_weak:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
        
    per_spurius=per_pred_entities.copy()
    for entity in per_correct:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in per_partial_type:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass    
    for entity in place_partial_weak:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass        
   

    place_miss= place_true_entities.copy()       
    for entity in place_correct:
        try:            
            place_miss.remove(entity[0])
        except ValueError:
            pass            
    for entity in place_partial_type:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
    for entity in place_partial_weak:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
        
    
    place_spurius=place_pred_entities.copy()
    for entity in place_correct:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    
    for entity in place_partial_type:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    
    for entity in per_partial_weak:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    
    
    '''
    conjoined_entities=data_display(true_entities, pred_entities, test_data)
    #print(conjoined_entities)
    for i in conjoined_entities:
        
        if i[0]==['O'] and i[1][3]=='PERSON':
            print(i)
    '''
    

    per_correct=len(per_correct)
    per_incorrect=0
    per_partial_type=len(per_partial_type)
    per_partial_weak=len(per_partial_weak)    
    per_miss=len(per_miss)
    per_spurius=len(per_spurius)
      
    
    place_correct=len(place_correct)
    place_incorrect=0   
    place_partial_type=len(place_partial_type)
    place_partial_weak=len(place_partial_weak)
    place_miss=len(place_miss)
    place_spurius=len(place_spurius)
    
    global all_per_correct
    global all_per_incorrect
    global all_per_partial_type
    global all_per_partial_weak
    global all_per_miss
    global all_per_spurius
    
    all_per_correct=all_per_correct+per_correct
    all_per_incorrect=all_per_incorrect+per_incorrect
    all_per_partial_type=all_per_partial_type+per_partial_type
    all_per_partial_weak=all_per_partial_weak+per_partial_weak
    all_per_miss=all_per_miss+per_miss
    all_per_spurius=all_per_spurius+per_spurius
    
    global all_place_correct
    global all_place_incorrect
    global all_place_partial_type
    global all_place_partial_weak
    global all_place_miss
    global all_place_spurius
    
    all_place_correct=all_place_correct+place_correct
    all_place_incorrect=all_place_incorrect+place_incorrect
    all_place_partial_type=all_place_partial_type+place_partial_type
    all_place_partial_weak=all_place_partial_weak+place_partial_weak
    all_place_miss=all_place_miss+place_miss
    all_place_spurius=all_place_spurius+place_spurius
    
    global all_per_relevant,all_per_retrive,all_place_relevant,all_place_retrive
    per_relevant=0
    per_retrive=0
    place_relevant=0
    place_retrive=0
    for te in true_entities:
        if te[2]=='pers':
            per_relevant+=1
        elif te[2]=='place':
            place_relevant+=1

    all_per_relevant=all_per_relevant+per_relevant
    all_place_relevant=all_place_relevant+place_relevant
    
    for pe in pred_entities:
        if pe[2]=='PERSON':
            per_retrive+=1
        elif (pe[2]=='GPE' or pe[2]=='LOC'):
            place_retrive+=1
    
    
    all_per_retrive=all_per_retrive+per_retrive
    all_place_retrive=all_place_retrive+place_retrive
    
    #conjoined_entities=data_display(true_entities, pred_entities, test_data)
    #print(conjoined_entities)
  
def read_corpora(corpus,mode):
    if corpus=='MH':
        path='../evaluation datasets/Mary Hamilton_new'
        files= os.listdir(path)
        for file in files[0:1589]:
            print(file)
            tsv_data=read_file('../evaluation datasets/Mary Hamilton_new/%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)

            test_data=iob_to_spacy_format(iob_data)    
            true_entities, pred_entities, doc=spacy_predict(test_data)
            #data_display(true_entities, pred_entities, test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities)
            elif mode=='lenient':
                type_match(true_entities, pred_entities,test_data)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities,test_data)

    elif corpus=='HIPE':
        file='../evaluation datasets/HIPE2020_new.tsv'
        tsv_data=read_file(file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)          
        test_data=iob_to_spacy_format(iob_data)
        true_entities, pred_entities, doc=spacy_predict(test_data)
        data_display(true_entities, pred_entities, test_data)    
 
        if mode=='strict':
            strict(true_entities, pred_entities)
        elif mode=='type':
            type_match(true_entities, pred_entities,test_data)
        elif mode=='partial':
            partial_match(true_entities, pred_entities)
        elif mode=='lenient':
            type_match(true_entities, pred_entities,test_data)
        elif mode=='ultra-lenient':
            partial_match(true_entities, pred_entities,test_data)
        
    elif corpus=='sloane':
        path='../evaluation datasets/Sloane_new'
        files= os.listdir(path)
        for file in files[0:2]:
            print(file)
            tsv_data=read_file('../evaluation datasets/Sloane_new/%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_spacy_format(iob_data)    
            true_entities, pred_entities, doc=spacy_predict(test_data)
            #data_display(true_entities, pred_entities, test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities,test_data)
            elif mode=='partial':
                partial_match(true_entities, pred_entities)
            elif mode=='lenient':
                type_match(true_entities, pred_entities,test_data)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities,test_data)
                
    elif corpus=='old bailey':
        path='../evaluation datasets/Old Bailey_new'
        files= os.listdir(path)
        for file in files[0:499]:
            print(file)
            tsv_data=read_file('../evaluation datasets/Old Bailey_new/%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_spacy_format(iob_data)    
            true_entities, pred_entities, doc=spacy_predict(test_data)
            #data_display(true_entities, pred_entities, test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities)
            elif mode=='lenient':
                type_match(true_entities, pred_entities,test_data)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities,test_data)
    per_precision,per_recall,per_f,place_precision,place_recall,place_f,macro_f,micro_f=score(mode) 
    print('Results of %s mode'%(mode))
    print('Person:\nPrecision:%f\nRecall:%f\nF1:%f'%(per_precision,per_recall,per_f))
    print('Location:\nPrecision:%f\nRecall:%f\nF1:%f'%(place_precision,place_recall,place_f))    
    print('Macro F1 score: %f'%macro_f)
    print('Micro F1 score: %f'%micro_f)
    


def evaluation_corpora(mode):      
    path='../evaluation datasets/Mary Hamilton_new'
    files= os.listdir(path)
    for file in files[0:1589]:
        print(file)
        tsv_data=read_file('../evaluation datasets/Mary Hamilton_new/%s'%file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)

        test_data=iob_to_spacy_format(iob_data)    
        true_entities, pred_entities, doc=spacy_predict(test_data)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities,test_data)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities,test_data)
    file='../evaluation datasets/HIPE2020_new.tsv'
    tsv_data=read_file(file)
    iob_data=[]
    for data in tsv_data:
        iob_element=data[0]+' '+data[1]
        iob_data.append(iob_element)          
    test_data=iob_to_spacy_format(iob_data)
    true_entities, pred_entities, doc=spacy_predict(test_data)
    if mode=='strict':
        strict(true_entities, pred_entities)  
    elif mode=='type' or mode=='lenient':
        type_match(true_entities, pred_entities,test_data)
    elif mode=='partial' or mode=='ultra-lenient':
        partial_match(true_entities, pred_entities,test_data)
    path='../evaluation datasets/Sloane_new'
    files= os.listdir(path)
    for file in files[0:2]:
        print(file)
        tsv_data=read_file('../evaluation datasets/Sloane_new/%s'%file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)
        test_data=iob_to_spacy_format(iob_data)    
        true_entities, pred_entities, doc=spacy_predict(test_data)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities,test_data)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities,test_data)
    path='../evaluation datasets/Old Bailey_new'
    files= os.listdir(path)
    for file in files[0:499]:
        print(file)
        tsv_data=read_file('../evaluation datasets/Old Bailey_new/%s'%file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)
        test_data=iob_to_spacy_format(iob_data)    
        true_entities, pred_entities, doc=spacy_predict(test_data)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities,test_data)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities,test_data)

        
    per_precision,per_recall,per_f,place_precision,place_recall,place_f,macro_f,micro_f=score(mode)
    print('Results of %s mode'%(mode))
    print('Person:\nPrecision:%f\nRecall:%f\nF1:%f'%(per_precision,per_recall,per_f))
    print('Location:\nPrecision:%f\nRecall:%f\nF1:%f'%(place_precision,place_recall,place_f))
    print('Macro F1 score: %f'%macro_f)
    print('Micro F1 score: %f'%micro_f)
        
    
if __name__ == "__main__":    
    
    all_per_correct=0
    all_per_incorrect=0
    all_per_partial=0
    all_per_miss=0
    all_per_spurius=0
    all_per_partial_type=0
    all_per_partial_weak=0
    
    all_place_correct=0
    all_place_incorrect=0
    all_place_partial=0
    all_place_miss=0
    all_place_spurius=0
    all_place_partial_type=0
    all_place_partial_weak=0
    
    all_per_relevant=0 #all person annotations in gold standard corpus
    all_per_retrive=0 #all person annotations produced by Spacy
    all_place_relevant=0
    all_place_retrive=0
    
    nlp = spacy.load("en_core_web_sm")
    
    #evaluation results for each dataset
    read_corpora('HIPE','ultra-lenient')
    #evaluation results for overall corpus
    evaluation_corpora('ultra-lenient')
    
    
       



    

    

