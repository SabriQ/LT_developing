
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

def add_info2celltype(s:AnaMini,generate_list:list,result_add = None):
    """
    add contextcells, rdcells, pccells in one time
    """
    s.add_Trial_Num_Process()
    s.add_Context()
    s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])

    result= {}
    if "contextcells" in generate_list:
        contextcells = cellid_Context(s
                       ,"S_dff"
                       ,placebin=np.arange(8,38)) 
        result["contextcells"] = contextcells

    if "contextcells2" in generate_list:
        contextcells2 = cellid_Context(s
                   ,"S_dff"
                   ,process=[1,2,3]
                   ,placebin=np.arange(8,38))
        result["contextcells2"] = contextcells2

    if "contextcells3" in generate_list:
        contextcells3 = cellid_Context(s
                   ,"S_dff"
                   ,process=[0,4,5]
                   ,placebin=np.arange(8,38))
        result["contextcells3"] = contextcells3

    s.add_Body_speed(scale=0.33)
    s.add_running_direction(according="Body")

    if "rdcells" in generate_list:
        rdcells = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38))
        result["rdcells"] = rdcells

    if "rdcells2" in generate_list:
        rdcells2 = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,Body_speed=3)
        result["rdcells2"] = rdcells2

    if "rdcells3" in generate_list:
        rdcells3 = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,Body_speed=5)
        result["rdcells3"] = rdcells3

    if "rdcells4" in generate_list:
        rdcells4 = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(4,42))
        result["rdcells4"] = rdcells4

    ## place cells 
    if "pccells" in generate_list:
        pccells = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,Body_speed=3)
        result["pccells"] = pccells


    if "pccells2" in generate_list:
        pccells2 = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(4,42)
                            ,Body_speed=3)
        result["pccells2"] = pccells2

    if "pccells3" in generate_list:
        pccells3 = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,process=[1,2,3]
                            ,Body_speed=3)
        result["pccells3"] = pccells3

    if "pccells4" in generate_list:
        pccells4 = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,process=[0,4,5]
                            ,Body_speed=3)
        result["pccells4"] = pccells4

    # begave state

    if "stat_info" in generate_list:
        stat_info = behave_stat_info(s)
        result["stat_info"]=stat_info

    # 20210128
    if "svm_score_dict" in  generate_list:
        svm_score_dict = main_svm_score(s
                                        ,"S_dff")
        result["svm_score_dict"] = svm_score_dict


    if result_add is None:
        return result
    else:
        result = dict(result_add,**result)
        return result


def save_info2celltypes(celltype:str,sessionpath:str=None,recal=False):
    print(celltype)
    try:

        all_keys=['contextcells', 'contextcells2', 'contextcells3', 'rdcells', 'rdcells2', 'rdcells3'
            , 'rdcells4', 'pccells', 'pccells2', 'pccells3', 'pccells4', 'stat_info','svm_score_dict']

        if not sessionpath is None:
            session = sessionpath
            size = 0

            mouse_id,part,day,aim = mouseid_part_day_aim(session)
            filename = "celltype_%s_part%s_day%s_aim_%s.pkl"%(mouse_id,part,day,aim)
            celltype = os.path.join(db.Celltype_path,filename)
        else:
            
            ct = CellType(celltype)
            session = ct.find_session()
            size = os.path.getsize(celltype)

        if size <1:
            recal = True
        if recal:

            mouse_id,part,day,aim = mouseid_part_day_aim(session)

            result_add = {
            "mouse_id":mouse_id,
            "part":part,
            "day":day,
            }
            generate_list = all_keys
            print("all_keys:",generate_list)
        else:
            generate_list = [i for i in all_keys if not i in ct.keys]
            print("part of all_keys:",generate_list)
            result_add = load_pkl(celltype)
            if len(result_add.keys())==0:
                result_add = {
                    "mouse_id":mouse_id,
                    "part":part,
                    "day":day,
                    }

        
        if len(generate_list) > 0:
            s = build_session(session)

            result = add_info2celltype(s,generate_list,result_add) ## add infor mation to result according to general_list
            save_pkl(result,celltype)

        else:
            pass
    except:
        with open("error_file.txt","a",encoding="utf-8") as f:
            f.write(celltype)
            f.write("\n")

def main_update_celltypes():
    """
    generate or update celltype files
    """
    celltypes = db.index_celltypes()

    celltypes = [i for i in celltypes ]
    # celltypes = [i for i in celltypes if "celltype_206550_part5_day20200821_aim_test.pkl" in i]
    # celltypes = [i for i in celltypes if "celltype_2020" in i]
    # celltypes = [i for i in celltypes if "206553" in i]
    [print(i) for i in celltypes]
    for celltype in celltypes:
        save_info2celltypes(celltype)
    # p = Pool(processes=8)
    # p.map(save_info2celltypes,celltypes)








if __name__ == '__main__':
    main_update_celltypes()
