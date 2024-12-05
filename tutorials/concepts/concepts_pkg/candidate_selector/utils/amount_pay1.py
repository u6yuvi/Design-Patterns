import re
from copy import deepcopy
from nltk import flatten
# from numpy import True_
import pandas as pd
from concepts_pkg.candidate_generator.utils.utils_contourizing import iom_1d, iou_1d
from concepts_pkg.candidate_selector.utils.Invoice_number import get_centroid
# from collections import defaultdict
from decimal import *
regex_1=re.compile("[a-zA-Z][a-zA-Z :#]+[a-zA-Z:# ]$")
regex_2=re.compile("[a-zA-Z][a-zA-Z \/[\()$&:#.-]+[a-zA-Z \/\[\]()$&:#.-]$")

# leading_curr=re.compile('(USD|\$|EUR|US\$|DOLLAR|SEK|sek|US DOLLARS|s\$|R1|R1,|R|RMB)\s?(\d{1,}(?:[.,]\d{1,})*(?:[.,]\d{1,2})?)')
# trailing_curr=re.compile('(\d{1,}(?:[.,]\d{1,})*(?:[.,]\d{1,2})?)\s?(USD|\$|EUR|US\$|DOLLAR|SEK|sek|US DOLLARS|s\$|R1|R1,|R|RMB)')
trailing_curr_in_key_anchor=re.compile('(\w{1,}(?:[.,]\d{1,})*(?:[.,]\d{1,2})?)\s?(USD|\$|EUR|US\$|DOLLAR|SEK|sek|US DOLLARS|s\$|R1|R1,|R|RMB|¥)$')
lead_curr_regex = re.compile('(USD|\$|EUR|US\$|DOLLAR|SEK|sek|US DOLLARS|s\$|R1|R1,|R|£|CNH|€|RMB|¥)(\s{0,3})(\d{1,}(?:[.,]\d{1,})*(?:[.,]\d{1,2})?)') 
trailing_curr_regex=re.compile('(\d{1,}(?:[.,]\d{1,})*(?:[.,]\d{1,2})?)(\s{0,3})(£|USD|\$|EUR|US\$|DOLLAR|SEK|sek|US DOLLARS|s\$|R1|R1,|RMB|CNH|€)')
    


def can_gen_n_filter(data,clwh):
    final_dict=[]
    datas = []
    [datas.append(x) for x in data if x not in datas]
    key_text=[]
    for i in datas:
        k_tex=i['key_anchor_text']
        if k_tex not in key_text:
            key_text.append(k_tex)

            if len(i['key_anchor_text'].split()) <=8:#6:## this was 5
                k_t_y,k_b_y=i['k_top_y'],i['k_bottom_y']
                k_t_x,k_b_x=i['k_top_x'],i['k_bottom_x']
                for k in clwh:
                    for key in clwh[k]['line'].keys():
                        match=regex_1.match(clwh[k]['line'][key]['text']) 

                        if not match:
                            new_can_t_y=(clwh[k]['line'][key]['bbox']['top_left']['y'])
                            new_can_b_y=(clwh[k]['line'][key]['bbox']['bottom_right']['y'])
                            new_can_t_x=(clwh[k]['line'][key]['bbox']['top_left']['x'])
                            new_can_b_x=(clwh[k]['line'][key]['bbox']['bottom_right']['x'])

                            if (iom_1d((k_t_y,k_b_y),(new_can_t_y,new_can_b_y)) >= .64) or (iom_1d((k_t_x,k_b_x),(new_can_t_x,new_can_b_x))>.80):#it was .82 for iou_y and 1.00 for iou_x
                                i['cand_cid']=clwh[k]['contour_id']
                                i['cand_lwhlid']=clwh[k]['line'][key]['line_id']
                                i['top_x']=clwh[k]['line'][key]['bbox']['top_left']['x']
                                i['top_y']=clwh[k]['line'][key]['bbox']['top_left']['y']
                                i['bottom_x']=clwh[k]['line'][key]['bbox']['bottom_right']['x']
                                i['bottom_y']=clwh[k]['line'][key]['bbox']['bottom_right']['y']
                                i['candidate_text']=clwh[k]['line'][key]['text']
                                i['ana']=clwh[k]['line'][key]['meta']['ana']['clean_text_tags']
                                i['spv']=clwh[k]['line'][key]['meta']['spv']['clean_text_tags']
                                i['spv_tokens']=clwh[k]['line'][key]['meta']['spv']['clean_text_tokens']
                                final_dict.append(i.copy())

    final_dict2=[]
    [final_dict2.append(x) for x in final_dict if x not in final_dict2]
    return final_dict2





def amt_n_curr_filter(data,clwh,keyword,relax_thresh,key_y_can_y_diff_relax):

    result=[]
    cand_ptr=[]
    key_value_cenroid_x, iou_x_thresh ,len_key_anchor= -20, .2,8
    key_value_cenroid_y,iou_y_thresh = -14, .2
    len_candidate=6
    y_diff_key_n_can=108 #829#108 #63
    if relax_thresh == True:
        key_value_cenroid_x, iou_x_thresh,len_key_anchor = -34, .20, 15  #key_value_cenroid_x =-24 is ideal though
        key_value_cenroid_y ,iou_y_thresh= -22, .17
        len_candidate=15
        y_diff_key_n_can=176
        if key_y_can_y_diff_relax== True:
            y_diff_key_n_can=829

    for i in range(len(data)):
        # row=data[i]
        match=regex_2.match(data[i]['candidate_text'])

    
        if not match:
            if len(data[i]['candidate_text'].split())<=len_candidate and len(data[i]['key_anchor_text'].split())<=len_key_anchor:        
                if data[i]['candidate_text'] !="0.00" and data[i]['candidate_text'] !="1.00":


                    if not((iou_1d([data[i]['k_top_y'],data[i]['k_bottom_y']],[data[i]['top_y'],data[i]['bottom_y']]))<=iou_y_thresh and iou_1d([data[i]['k_top_x'],data[i]['k_bottom_x']],[data[i]['top_x'],data[i]['bottom_x']])<=iou_x_thresh):
    
                        k_cent_x,k_cent_y=get_centroid((data[i]['k_top_x'],data[i]['k_top_y'],data[i]['k_bottom_x'],data[i]['k_bottom_y']))
                        v_cent_x,v_cent_y=get_centroid((data[i]['top_x'],data[i]['top_y'],data[i]['bottom_x'],data[i]['bottom_y']))
                    
                        if (int(v_cent_y)-int(k_cent_y)>= key_value_cenroid_y and (int(v_cent_x)-int(k_cent_x))>= key_value_cenroid_x) and v_cent_y-k_cent_y <=y_diff_key_n_can: #was 50 changed to 63

                            text = re.sub("\s+"," ",data[i]['candidate_text'])
                            # rej_spv_tags=[ "ORG","DATE","LOC","UNIT","QUANTITY_TYPE"]
                            rej_spv_tags=[ "DATE","UNIT"]
                            # if not any(tag in rej_spv_tags for tag in data[i]['spv']):  # see if CURRENCY condition needs to be added here , that even if date tag is there still curr present in spv ,,
                            if (any(tag in rej_spv_tags for tag in data[i]['spv']) and "CURRENCY" in data[i]['spv']) or not any(tag in rej_spv_tags for tag in data[i]['spv']) :
                            
                                extract__can=[]
                                for words in range(len(data[i]['spv'])):
                                    if data[i]['spv'][words]=="CARDINAL" or data[i]['spv'][words]=="CURRENCY+CARDINAL": # or row['spv'][i]=='CURRENCY':
                                        canz=(data[i]['spv'][words])
                                        extract__can.append(canz)
                                        if data[i]["cand_lwhlid"] not in cand_ptr:
                                            result.append(data[i])
                                            cand_ptr.append(data[i]["cand_lwhlid"])

                                if not extract__can:
                
                                    lead_text_curr= re.sub("\s+|\(|\)|:"," ",data[i]['candidate_text'])
                                    canz_=lead_curr_regex.findall(lead_text_curr)
                                    candz=trailing_curr_regex.findall(lead_text_curr)
                                    if canz_ or candz:
                                        if data[i]["cand_lwhlid"] not in cand_ptr:
                                            result.append(data[i])
                                            cand_ptr.append(data[i]["cand_lwhlid"])



    final_res ,sel_can_texts, curr_line_id_list=  [],[],[]
    
    # for i in res:
    for i in result:
        if i['candidate_text'] not in sel_can_texts:
            final_res.append(i.copy())
        sel_can_texts.append(i['candidate_text'])

    results_,can_texts,amt_list,curr_list=[],[],[] ,[]        
    for ele in final_res:
        amounts=deepcopy(ele)
        
        # if 'CURRENCY' in ele['spv'] or len(candidate_)>0:
        if ('CURRENCY' in ele['spv'] or len(lead_curr_regex.findall(re.sub("\s+|\(|\)|:"," ",ele['candidate_text'])))>0) and int(ele['cand_lwhlid']) not in curr_line_id_list:
            # results_.append(clubbing_amt_cur(amounts,ele))
            amt_list.append(amounts)
            curr_list.append(ele.copy())
            # curr_line_id_list.append(int(ele['cand_lwhlid']))

        elif ('CURRENCY' in ele['k_spv'] or len(trailing_curr_in_key_anchor.findall(re.sub("\s+|\(|\)|:"," ",ele['key_anchor_text'])))>0) and int(ele['key_lwhlid']) not in curr_line_id_list :
            
            ele['candidate_text']=ele['key_anchor_text']
            ele['cand_cid']=ele['key_cid']
            ele['cand_lwhlid']=ele['key_lwhlid']
            ele['top_x']=ele['k_top_x']
            ele['top_y']=ele['k_top_y']
            ele['bottom_x']=ele['k_bottom_x']
            ele['bottom_y']=ele['k_bottom_y']
            ele['spv']=ele['k_spv']
            ele['ana']=ele['k_ana']
            # amt_n_curr.append(ele.copy())
            # results_.append(clubbing_amt_cur(amounts,ele))
            amt_list.append(amounts)
            curr_list.append(ele.copy())
            # curr_line_id_list.append(int(ele['key_lwhlid']))
            
        else:
            options={}
            k_t_y,k_b_y=ele['k_top_y'],ele['k_bottom_y']
            k_t_x,k_b_x=ele['k_top_x'],ele['k_bottom_x']
            for k in clwh:
                for key in clwh[k]['line'].keys():
                    tags=clwh[k]['line'][key]['meta']['spv']['clean_text_tags']

                    if 'CURRENCY' in tags:
                        new_can_t_y=(clwh[k]['line'][key]['bbox']['top_left']['y'])
                        new_can_b_y=(clwh[k]['line'][key]['bbox']['bottom_right']['y'])
                        new_can_t_x=(clwh[k]['line'][key]['bbox']['top_left']['x'])
                        new_can_b_x=(clwh[k]['line'][key]['bbox']['bottom_right']['x'])
                        if iom_1d((k_t_y,k_b_y),(new_can_t_y,new_can_b_y)) >= .82 or (k_t_y==new_can_t_y and k_b_y==new_can_b_y):

                            if clwh[k]['line'][key]['text'] not in can_texts and int(clwh[k]['line'][key]['line_id']) not in curr_line_id_list :
                                ele['candidate_text']=clwh[k]['line'][key]['text']
                                ele['cand_cid']=clwh[k]['contour_id']
                                ele['cand_lwhlid']=clwh[k]['line'][key]['line_id']
                                ele['top_x']=clwh[k]['line'][key]['bbox']['top_left']['x']
                                ele['top_y']=clwh[k]['line'][key]['bbox']['top_left']['y']
                                ele['bottom_x']=clwh[k]['line'][key]['bbox']['bottom_right']['x']
                                ele['bottom_y']=clwh[k]['line'][key]['bbox']['bottom_right']['y']
                                ele['spv']=clwh[k]['line'][key]['meta']['spv']['clean_text_tags']
                                ele['ana']=clwh[k]['line'][key]['meta']['ana']['clean_text_tags']
                                # can_texts.append(clwh[k]['line'][key]['text'])
                                # results_.append(clubbing_amt_cur(amounts,ele.copy()))
                                amt_list.append(amounts)
                                curr_list.append(ele.copy())
                                # curr_line_id_list.append(int(clwh[k]['line'][key]['line_id']))
                                break
                            
                        else:
                            (iou_1d((k_t_x,k_b_x),(new_can_t_x,new_can_b_x))>.800)
                            if int(clwh[k]['line'][key]['line_id'] not in curr_line_id_list):
                                near=int(abs(k_t_y - new_can_t_y))
                                options[near]=[clwh[k]['contour_id'],clwh[k]['line'][key]['line_id'],key]
            
            if len(options)>0:
                keyz=min(options.keys())
                contour_pointer, line_pointer,pointer_in_contour=(options[keyz])

                if (clwh[contour_pointer]['line'][pointer_in_contour]['text'] not in can_texts):# and clwh[contour_pointer]['line'][pointer_in_contour]['line_id'] not in curr_line_id_list:
                    ele['candidate_text']=clwh[contour_pointer]['line'][pointer_in_contour]['text']
                    ele['cand_cid']=clwh[contour_pointer]['contour_id']
                    ele['cand_lwhlid']=clwh[contour_pointer]['line'][pointer_in_contour]['line_id']
                    ele['top_x']=clwh[contour_pointer]['line'][pointer_in_contour]['bbox']['top_left']['x']
                    ele['top_y']=clwh[contour_pointer]['line'][pointer_in_contour]['bbox']['top_left']['y']
                    ele['bottom_x']=clwh[contour_pointer]['line'][pointer_in_contour]['bbox']['bottom_right']['x']
                    ele['bottom_y']=clwh[contour_pointer]['line'][pointer_in_contour]['bbox']['bottom_right']['y']
                    ele['spv']=clwh[contour_pointer]['line'][pointer_in_contour]['meta']['spv']['clean_text_tags']
                    ele['ana']=clwh[contour_pointer]['line'][pointer_in_contour]['meta']['ana']['clean_text_tags']
                    # can_texts.append(clwh[contour_pointer]['line'][pointer_in_contour]['text'])
                    
                    # results_.append(clubbing_amt_cur(amounts,ele.copy()))
                    amt_list.append(amounts.copy())
                    curr_list.append(ele.copy())
                    # curr_line_id_list.append(int(clwh[contour_pointer]['line'][pointer_in_contour]['line_id']))
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++TRIALZ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++





# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++TRIALZZ+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



    # if len(results_)>1:
    #     true_index_for_amt=regex_match_with_curr(amt_list,curr_list)
    #     try:


    if len(amt_list) > 1:
        curr_True_index=[]
        final_amt,final_curr=[],[]
        main_ids=[]
        try:
            true_index_for_amt= regex_match_with_curr(amt_list,curr_list)
            for idx_,amt_curr in enumerate(zip(amt_list,curr_list)):
                if idx_ in true_index_for_amt:
                    final_amt.append(amt_curr[0])
                    final_curr.append(amt_curr[1])

            if len(final_amt)>1:
                    # main_ids=[]
                curr_ids=[]
                for amt,curr in zip(final_amt,final_curr): 
                    curr_ids.append(int(curr["cand_lwhlid"])) 
                duplicate_ids=dict((x, indices(curr_ids,x)) for x in set(curr_ids) if curr_ids.count(x)>1)
                if duplicate_ids:
                    for dupli_ids in duplicate_ids.keys():
                        pointer_curr_list=duplicate_ids[dupli_ids]
                        curr_True_index=flatten([i for i in range(len(final_curr)) if i not in flatten([ i for i in duplicate_ids.values()])])
                        # curr_True_index=[i for i in range(len(curr_list)) if i not in pointer_curr_list]
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        pointer_=get_dict_with_values(pointer_curr_list,final_amt)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        main_key_anchor_index=(get_main_ANCHOR(final_amt,pointer_))
                        if len(main_key_anchor_index)==1:
                            curr_True_index.append(main_key_anchor_index)# get_main_ANCHOR(amt_results,USD_curr_pointer)
                        else:
                            final_max_val_index=get_max_value(final_amt,pointer_)
                            curr_True_index.append( [final_max_val_index] )
                else:
                    curr_True_index=[i for i in range(len(final_curr))]

                final_amount,final_currency=[],[]
                for i,amount_currency in enumerate(zip(final_amt,final_curr)):
                # for i, amount_currency in enumerate(zip(final_amt,final_curr)):
                    if i in flatten(curr_True_index):
                        final_amount.append(amount_currency[0])
                        final_currency.append(amount_currency[1])
            else:
                final_amount,final_currency=final_amt,final_curr

        except Exception as e:
            print(e)
            final_amount,final_currency=[],[]

 
    else:
        final_amount,final_currency=amt_list,curr_list
        
    results_=[]
    for am_,cur_ in zip(final_amount,final_currency):
        results_.append(clubbing_amt_cur(am_,cur_))
    

    return results_






def get_dict_with_values(curr_True_index,amt_list): 
    pointer_={}
    for i in curr_True_index:
        pointer_[i]=amt_list[i]['candidate_text']  

    return pointer_              



def indices(lst,item):
    return [i for i, x in enumerate(lst) if x == item]

def get_max_value(amt_results,curr_pointer):#++++++++++++++++++++++++++ can be ammended with regex with reject keys
    multi_val={}
    reject_anchor_regex=re.compile('(?:^|\W)(PREPAYMENT AMOUNT|prepayment amount)(?:$|)')
    num_regex=re.compile('(\d*(\.)?(,)?(\s+)?\d+)+')
    for i in curr_pointer.keys():
        text=(amt_results[i]['candidate_text'])
        txt=re.sub("\s+|\(|\)|:|,","",text)
        num=num_regex.findall(txt)
        if num:
            digit=float(num[0][0])
            multi_val[digit]=i
    max_amt=max([i for i in multi_val.keys()])
    return multi_val[max_amt]
        
def get_main_ANCHOR(amt_results,curr_pointer):
    main_anchor=[]
    MAIN_ANCHORS=re.compile('(?:^|\W)(total amount due|total net due|net amount due|balance amount due|total payment due|payment due|balance amount|total due|balance due|amount due to| amount due|total amount)(?:$|)')
    for i in curr_pointer.keys():
        text=(amt_results[i]['key_anchor_text'])
        text=re.sub("\s+|:|\,"," ",text.lower())
        num=MAIN_ANCHORS.findall(text)
        if num:
            main_anchor.append(i)
            
    return main_anchor
            

def regex_match_with_curr(amt_results,curr_results):

    USD_curr_pointer,ZAR_curr_pointer,SEK_curr_pointer,SGD_curr_pointer,EUR_curr_pointer={},{},{},{},{}
    USD_regex=re.compile('(?:^|\W)(usd|us\$|\$|us dollars|dollars|dolaars|dollar)(?:$|)')
    # USD_regex=re.compile('(?:^|\W)(USD|usdUS$|\$|US DOLLARS|us dollars|US dollars|DOLLAR)(?:$|)')
    ZAR_regex=re.compile('(?:^|\W)(zar)(?:$|)')
    SEK_regex=re.compile('(?:^|\W)(sek)(?:$|)')
    SGD_regex=re.compile('(?:^|\W)(sgd)(?:$|)')
    EUR_regex=re.compile('(?:^|\W)(€|eur)(?:$|)')

    
    MAIN_ANCHORS=re.compile('(?:^|\W)(total amount due|total net due|net amount due|balance amount due|total payment due|payment due|balance amount|total due|balance due|total amount|total amount )(?:$|)')
    True_index=[]
    curr_regex=[USD_regex,SEK_regex,SGD_regex,EUR_regex,ZAR_regex]
    curr_pointer=[USD_curr_pointer, SEK_curr_pointer, SGD_curr_pointer, EUR_curr_pointer, ZAR_curr_pointer]
    for reg_,point_ in zip(curr_regex,curr_pointer):
        for i in range(len(curr_results)):
            text=curr_results[i]['candidate_text']
            if (reg_.findall(text.lower())):
                point_[i]=reg_.findall(text.lower())

        
        if len(point_)>1:
            pointer_key_list=[i for i in point_.keys()]
            True_index=[i for i in range(len(curr_results)) if i not in pointer_key_list]
            main_key_anchor_index=(get_main_ANCHOR(amt_results,point_))
            if len(main_key_anchor_index)==1:
                True_index.append(main_key_anchor_index)# get_main_ANCHOR(amt_results,USD_curr_pointer)
            else:
                final_max_val_index=get_max_value(amt_results,point_)
                True_index.append( [final_max_val_index] )

    if len(SEK_curr_pointer)<=1 and len(USD_curr_pointer)<=1  and len(ZAR_curr_pointer)<=1 and len(SGD_curr_pointer)<=1 and len(EUR_curr_pointer)<=1:
            True_index.append( [i for i in range(len(curr_results))])
            return flatten(True_index)
    else:
        return flatten(True_index)




    

def get_valid_amt_curr_relation(True_index,USD_curr_pointer,curr_results,amt_results):

    USD_curr_pointer_key_list=[i for i in USD_curr_pointer.keys()]
    True_index=[i for i in range(len(curr_results)) if i not in USD_curr_pointer_key_list]
    amt_main_key_anchor_index=(get_main_ANCHOR(amt_results,USD_curr_pointer))
    if len(amt_main_key_anchor_index)==1:
        True_index.append(amt_main_key_anchor_index)# get_main_ANCHOR(amt_results,USD_curr_pointer)
        
    else:
    
        final_max_val_index=get_max_value(amt_results,USD_curr_pointer)
        True_index.append( [final_max_val_index] )
    return True_index



def clubbing_amt_cur(dict_1,dict_2):
    dict_2_sorted={i:dict_2[i] for i in dict_1.keys()}
    keys=dict_1.keys()
    values=zip(dict_1.values(),dict_2_sorted.values())
    dictionary=dict(zip(keys,values))
    return dictionary

if __name__=="__main__":
    print("check selector_regex")
    p = re.compile('(USD|EUR|€|\$)\s?(\d{1,3}(?:[.,]\d{3})(?:[.,]\d{2}))|(\d{1,3}(?:[.,]\d{3})(?:[.,]\d{2})?)\s?(USD|EUR|€|\$)')
    # used earlier for curr regex in currency getting block
    curr_pattern_check = re.compile('(USD|\$|EUR|US\$|DOLLAR|SEK|sek|US DOLLARS|s\$|R1|R1,|R|CNH)(\d{1,}(?:[.,]\d{1,})*(?:[.,]\d{1,2})?)')
