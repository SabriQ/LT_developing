
from mylab.ana.miniscope.context_exposure.Canamini import *
from mylab.ana.miniscope.context_exposure.ana_funtions import *
from mylab.Functions import * 

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

    if result_add is None:
        return result
    else:
        result = dict(result_add,**result)
        return result


def save_info2celltypes(celltype:str,sessionpath:str=None,recal=True):

    all_keys=['contextcells', 'contextcells2', 'contextcells3', 'rdcells', 'rdcells2', 'rdcells3'
        , 'rdcells4', 'pccells', 'pccells2', 'pccells3', 'pccells4', 'stat_info']

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

    if recal:
        size=0
    if size<100:

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
        result_add = None

    s = build_session(session)
    try:
        result = add_info2celltype(s,generate_list,result_add)
        save_pkl(result,celltype)
    except:
        with open("error_file.txt","a",encoding="utf-8") as f:
            text1 = generate_list + "\n"
            f.write(text1)
            text2 = savepath + "\n"
            f.write(text2)


def main_update_celltypes():
    """
    generate or update celltype files
    """
    celltypes = db.index_celltypes()

    celltypes = [i for i in celltypes if "celltype_2010" in i]
    # celltypes = [i for i in celltypes if "celltype_206" in i and not "206553" in i]
    # celltypes = [i for i in celltypes if "celltype_2020" in i]
    # celltypes = [i for i in celltypes if "206553" in i]
    [print(i) for i in celltypes]
    # for celltype in celltypes:
    #     save_info2celltypes(celltype)
    p = Pool(processes=8)
    p.map(save_info2celltypes,celltypes)



# def _CTX_cellids1(session:str,placebin=np.arange(8,38)):
#     """
#     add contextcells, rdcells, pccells in one time
#     """
#     s = build_session(session)
#     s.add_Trial_Num_Process()
#     s.add_Context()
#     s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])

#     contextcells = cellid_Context(s
#                    ,"S_dff"
#                    ,process=[1,2,3]
#                    ,placebin=np.arange(8,38))
#     return contextcells
# def _CTX_cellids2(session:str,placebin=np.arange(8,38)):
#     """
#     add contextcells, rdcells, pccells in one time
#     """
#     s = build_session(session)
#     s.add_Trial_Num_Process()
#     s.add_Context()
#     s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])

#     contextcells = cellid_Context(s
#                    ,"S_dff"
#                    ,process=[0,4,5]
#                    ,placebin=np.arange(8,38))
#     return contextcells

# def update_CTX_celltypys(celltype:str):

#     result = load_pkl(celltype)
#     ct = CellType(celltype)
#     session = ct.find_session()
#     try:
#         if not "contextcells2" in result.keys():
#             # process=[1,2,3]
#             contextcells2 = _CTX_cellids1(session,placebin=np.arange(8,38))
#             result["contextcells2"] = contextcells2
#         if not "contextcells3" in result.keys():
#             # process =[0,4,5]
#             contextcells3 = _CTX_cellids2(session,placebin=np.arange(8,38))
#             result["contextcells3"] = contextcells3
#         save_pkl(result,celltype)
#     except:        
#         with open("update_ctxcell.txt","a",encoding="utf-8") as f:
#             text = "contextcells2 or3:" + savepath + "\n"
#             f.write(text)

# def main_update_Contextcells_celltypes():
#     """
#     generate or update celltype files
#     """
#     celltypes = db.index_celltypes()
#     [print(i) for i in celltypes]
#     # p = Pool(processes=8)
#     # p.map(update_CTX_celltypys,celltypes)
#     for celltype in celltypes:
#         update_CTX_celltypys(celltype)
# def _RD_cellids(session:str,placebin=np.arange(8,38)):
#     """
#     independently generage rdcells
#     """
#     s = build_session(session)

#     s.add_Trial_Num_Process()
#     s.add_Context()
#     s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
#     s.add_Body_speed(scale=0.33)
#     s.add_running_direction(according="Body")

#     rdcells = cellid_RD_incontext(s
#                         ,"S_dff"
#                         ,placebin=placebin
#                         ,Body_speed=5)

#     return rdcells

# def update_RD_celltypes(session:str):
#     """
#     update the rdcells in celltype file
#     """
#     print(session)
#     if platform.system() == 'Linux':
#         savedir = r"/home/qiushou/Documents/Qs_data/syn/results/celltypes"
#     elif platform.system() == 'Windows':
#         savedir = r"\\10.10.47.163\Data_archive\qiushou\results\celltypes"

#     mouse_id,part,day,aim = mouseid_part_day_aim(session)
#     filename = "celltype_%s_part%s_day%s_aim_%s.pkl"%(mouse_id,part,day,aim)
#     savepath = os.path.join(savedir,filename)

#     rdcells = _RD_cellids(session,placebin=np.arange(8,38))
#     if os.path.exists(savepath):
#         result = load_pkl(savepath)
#         result["rdcells3"] = rdcells

#     save_pkl(result,savepath)

# def _PC_cellids1(session:str,placebin=np.arange(8,38)):
#     """
#     independently generate pccells
#     """
#     s = build_session(session)

#     s.add_Trial_Num_Process()
#     s.add_Context()
#     s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
#     s.add_Body_speed(scale=0.33)
#     s.add_running_direction(according="Body")
#     pccells = cellid_PC_incontext(s
#                         ,"S_dff"
#                         ,placebin=placebin
#                         ,process=[1,2,3]
#                         ,Body_speed=3)
#     return pccells
# def _PC_cellids2(session:str,placebin=np.arange(8,38)):
#     """
#     independently generate pccells
#     """
#     s = build_session(session)

#     s.add_Trial_Num_Process()
#     s.add_Context()
#     s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
#     s.add_Body_speed(scale=0.33)
#     s.add_running_direction(according="Body")
#     pccells = cellid_PC_incontext(s
#                         ,"S_dff"
#                         ,placebin=placebin
#                         ,process=[0,4,5]
#                         ,Body_speed=3)
#     return pccells

# def update_PC_celltypes(celltype:str):
    
#     result = load_pkl(celltype)
#     ct = CellType(celltype)
#     session = ct.find_session()
#     try:
#         if not "pccells3" in result.keys():
#             # process=[1,2,3]
#             pccells1 = _PC_cellids1(session,placebin=np.arange(8,38))
#             result["pccells3"] = pccells1
#         if not "pccells4" in result.keys():
#             # process =[0,4,5]
#             pccells2 = _PC_cellids2(session,placebin=np.arange(8,38))
#             result["pccells4"] = pccells2
#         save_pkl(result,celltype)
#     except:        
#         with open("update_pc.txt","a",encoding="utf-8") as f:
#             text = "pccells3 or 4:" + savepath + "\n"
#             f.write(text)

# def _PC_cellids3(session:str,placebin=np.arange(8,38)):
#     """
#     independently generate pccells
#     """
#     s = build_session(session)

#     s.add_Trial_Num_Process()
#     s.add_Context()
#     s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
#     s.add_Body_speed(scale=0.33)
#     s.add_running_direction(according="Body")
#     pccells = cellid_PC_incontext(s
#                         ,"S_dff"
#                         ,placebin=placebin
#                         ,Body_speed=3)
#     return pccells

# def update_PC_celltypes3(celltype:str):
    
#     result = load_pkl(celltype)
#     ct = CellType(celltype)
#     session = ct.find_session()
#     try:
#         if not "pccells2" in result.keys():
#             # process=[1,2,3]
#             pccells1 = _PC_cellids3(session,placebin=np.arange(4,42))
#             result["pccells2"] = pccells1
#             save_pkl(result,celltype)
#     except:        
#         with open("update_pc.txt","a",encoding="utf-8") as f:
#             text = "pccells2:" + savepath + "\n"
#             f.write(text)

# def main_update_PC_celltypes():
#     """
#     generate or update celltype files
#     """
#     celltypes = db.index_celltypes()
#     [print(i) for i in celltypes]
#     p = Pool(processes=8)
#     p.map(update_PC_celltypes,celltypes)


# def update_behave_state_info(session:str):
#     print(session)

#     if platform.system() == 'Linux':
#         savedir = r"/home/qiushou/Documents/Qs_data/syn/results/celltypes"
#     elif platform.system() == 'Windows':
#         savedir = r"\\10.10.47.163\Data_archive\qiushou\results\celltypes"

#     mouse_id,part,day,aim = mouseid_part_day_aim(session)
#     filename = "celltype_%s_part%s_day%s_aim_%s.pkl"%(mouse_id,part,day,aim)
#     savepath = os.path.join(savedir,filename)

#     s = build_session(session)
#     stat_info = behave_stat_info(s)

#     if os.path.exists(savepath):
#         result = load_pkl(savepath)
#         result["stat_info"] = stat_info
#     save_pkl(result,savepath)

# def main_update_behave_state_info():
#     sessions = db.index_sessions(aim="test")
#     [print(i) for i in sessions]
#     p = Pool(processes=8)
#     p.map(update_behave_state_info,sessions)

# def main2_update_behave_state_info():
#     sessions = db.index_sessions(mouse_id=201033,part=5,day= 20200811,aim="train")
#     bug_sessions = []
#     for session in sessions:
#         try:
#             update_behave_state_info(session)
#             print("saved")
#         except Exception as e:
#             print(e)
#             bug_sessions.append(session)
#     [print(i) for i in bug_sessions]


# #%% -------cell types-------------end




if __name__ == '__main__':
    main_update_celltypes()
