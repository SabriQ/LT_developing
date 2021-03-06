
from mylab.ana.miniscope.context_exposure.Canamini import *
from mylab.ana.miniscope.context_exposure.ana_funtions import *
from mylab.Functions import * 
from mylab.ana.miniscope.context_exposure.Msvm import main_svm_score

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob,sys,os,re,platform,copy

from multiprocessing import Pool

from Cdatabase import DataBase,CellType
db = DataBase()

def mouseid_part_day_aim(session:str,):
    mouse_id = re.findall("(\d+)_part",session)[0]
    part = re.findall("part(\d+)",session)[0]
    try:
        day = re.findall("day(\d+)",session)[0]
    except:
        day = "00000000"

    try:
        aim = re.findall("aim_(.*).pkl",session)[0]
    except:
        aim = "hc"
    return mouse_id,part,day,aim


#%% -------cell types-------------

def add_info2celltype(s:AnaMini,generate_list:list):
    """
    add contextcells, rdcells, pccells in one time
    """
    s.add_Trial_Num_Process()
    s.add_Context()
    s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])

    add_result= {}
    if "contextcells" in generate_list:
        contextcells = cellid_Context(s
                       ,"S_dff"
                       ,placebin=np.arange(8,38)) 
        add_result["contextcells"] = contextcells

    if "contextcells2" in generate_list:
        contextcells2 = cellid_Context(s
                   ,"S_dff"
                   ,process=[1,2,3]
                   ,placebin=np.arange(8,38))
        add_result["contextcells2"] = contextcells2

    if "contextcells3" in generate_list:
        contextcells3 = cellid_Context(s
                   ,"S_dff"
                   ,process=[0,4,5]
                   ,placebin=np.arange(8,38))
        add_result["contextcells3"] = contextcells3

    s.add_Body_speed(scale=0.33)
    s.add_running_direction(according="Body")

    if "rdcells" in generate_list:
        rdcells = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38))
        add_result["rdcells"] = rdcells

    if "rdcells2" in generate_list:
        rdcells2 = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,Body_speed=3)
        add_result["rdcells2"] = rdcells2

    if "rdcells3" in generate_list:
        rdcells3 = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,Body_speed=5)
        add_result["rdcells3"] = rdcells3

    if "rdcells4" in generate_list:
        rdcells4 = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(4,42))
        add_result["rdcells4"] = rdcells4

    ## place cells 
    if "pccells" in generate_list:
        pccells = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,Body_speed=3)
        add_result["pccells"] = pccells


    if "pccells2" in generate_list:
        pccells2 = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(4,42)
                            ,Body_speed=3)
        add_result["pccells2"] = pccells2

    if "pccells3" in generate_list:
        pccells3 = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,process=[1,2,3]
                            ,Body_speed=3)
        add_result["pccells3"] = pccells3

    if "pccells4" in generate_list:
        pccells4 = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,process=[0,4,5]
                            ,Body_speed=3)
        add_result["pccells4"] = pccells4

    # begave state

    if "stat_info" in generate_list:
        stat_info = behave_stat_info(s)
        add_result["stat_info"]=stat_info

    # 20210128
    if "svm_score_dict" in  generate_list:
        svm_score_dict = main_svm_score(s
                                        ,"S_dff")
        add_result["svm_score_dict"] = svm_score_dict


    return add_result

    # if Result_add is None:
    #     return add_result
    # else:
    #     add_result = dict(Result_add,**add_result)
    #     return add_result

def save_info2_new_celltypes2(session:str):
    """
    according to session to save new celltype file.
    """
    print(session)
    try:

        all_keys=['contextcells', 'contextcells2', 'contextcells3', 'rdcells', 'rdcells2', 'rdcells3'
            , 'rdcells4', 'pccells', 'pccells2', 'pccells3', 'pccells4', 'stat_info','svm_score_dict']

        mouse_id,part,day,aim = mouseid_part_day_aim(session)
        filename = "celltype_%s_part%s_day%s_aim_%s.pkl"%(mouse_id,part,day,aim)
        celltype = os.path.join(db.Celltype_path,filename)

        session_info = {
        "mouse_id":mouse_id,
        "part":part,
        "day":day,
        }

        generate_list = all_keys
        print("all_keys:",generate_list)


        s = build_session(session)
        add_result = add_info2celltype(s,generate_list) ## add information to result according to general_list
        result = {**session_info,**add_result }
        save_pkl(result,celltype)

    except Exception as e:
        print(e)
        with open("error_file.txt","a",encoding="utf-8") as f:
            f.write(celltype)
            f.write("\n")

def save_info2celltypes(celltype:str):
    """
    add new info to celltype files
    """
    try:
        ct = CellType(celltype)
        session = ct.find_session()
        mouse_id,part,day,aim = mouseid_part_day_aim(session)
        all_keys=['contextcells', 'contextcells2', 'contextcells3', 'rdcells', 'rdcells2', 'rdcells3'
                , 'rdcells4', 'pccells', 'pccells2', 'pccells3', 'pccells4', 'stat_info','svm_score_dict'] #,'svm_score_dict'

        result = ct.result
        session_info = {
            "mouse_id":mouse_id,
            "part":part,
            "day":day,
            }


        if isinstance(result,set):
            generate_list = all_keys
            result = {}

            s = build_session(session)
            add_result = add_info2celltype(s,generate_list)
            result = {**session_info,**add_result}
            save_pkl(result,celltype)
        else:
            if not "mouse_id" in result.keys():
                add_result = {**session_info,**add_result}


            generate_list = [i for i in all_keys if not i in result.keys()]


            if len(generate_list)>0:
                print("generate_list: ",generate_list)
                s = build_session(session)
                add_result = add_info2celltype(s,generate_list)
                new_result = {**result,**add_result}
                save_pkl(new_result,celltype)
            else:
                print("Already the newest!")
    except Exception as e:
        save_pkl(result,celltype)
        print(e)
        print("%s error"%celltype)
        with open("error_file.txt","a",encoding="utf-8") as f:
            f.write(celltype)
            f.write("\n")

def update_info2celltypes(celltype:str,update_list:list=["stat_info"]):
    """
    update the existed info in celltype file
    """
    try:
        ct = CellType(celltype)
        session = ct.find_session()
        result = ct.result

        generate_list = [i for i in update_list if i in result.keys()]

        if not len(generate_list) == 0:
            s = build_session(session)
            update_result = add_info2celltype(s,generate_list)
            new_result = {**result,**update_result}
            print("%s is updated"%generate_list)
            save_pkl(new_result,celltype)

        else:
            print("%s has no item to update")
    except Exception as e:
        try:
            save_pkl(result,celltype)
        except:
            pass
        print(e)
        print("%s error"%celltype)
        with open("update_error_file.txt","a",encoding="utf-8") as f:
            f.write(celltype)
            f.write("\n")

def main_update_celltypes():
    
    """
    generate or update celltype files
    """
    celltypes = db.index_celltypes()

    # celltypes = [i for i in celltypes if "celltype_206550_part5_day20200821_aim_test.pkl" in i]
    # celltypes = [i for i in celltypes if "celltype" in i and  "part1" in i]
    # celltypes = [i for i in celltypes if "206553" in i]
    [print(i) for i in celltypes]
    # for celltype in celltypes:
    #    print(celltype)
    #    update_info2celltypes(celltype)
       # sys.exit()
    p = Pool(processes=8)
    p.map(save_info2celltypes,celltypes)
    # save_info2celltypes2(session=r"\\10.10.47.163\qiushou\LinearTrack\Sessions\206552_part6_day20200906_aim_lack_wall.pkl"))








if __name__ == '__main__':
    main_update_celltypes()
