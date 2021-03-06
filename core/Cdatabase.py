import os,sys,glob,re,platform
import pandas as pd 
import numpy as np
from mylab.process.miniscope.context_exposure.save2trials import divide_sessions_into_trials
from mylab.ana.miniscope.context_exposure.Canamini import *
from mylab.ana.miniscope.context_exposure.ana_funtions import *

from multiprocessing import Pool
from mylab.Functions import load_pkl

    
class DataBase():

    if platform.system()=='Linux':
        Trial_path = r"../../Trials"
        Session_path = r"../../Sessions"
        Celltype_path = r"../../results/celltypes"
        Context_map_file_path = r"../../Linear_Track_developing/context_map.csv"
    elif platform.system()=='Windows':
        Trial_path =r"\\10.10.47.163\qiushou\LinearTrack\Trials"
        Session_path = r"\\10.10.47.163\qiushou\LinearTrack\Sessions"
        Celltype_path = r"\\10.10.47.163\qiushou\LinearTrack\results\celltypes"
        Context_map_file_path=r"\\10.10.47.163\qiushou\LinearTrack\Linear_Track_developing\context_map.csv"

    trials = glob.glob(os.path.join(Trial_path,"*.pkl"))
    sessions = glob.glob(os.path.join(Session_path,"*.pkl"))
    celltypes = glob.glob(os.path.join(Celltype_path,"*.pkl"))

    def __init__(self):
        self.context_map = pd.read_csv(DataBase.Context_map_file_path)

    def all_trials(self,mouse_id=None,part=None,day=None,aim=None,session=None):
        mouse_ids=[]
        parts=[]
        days=[]
        sessions=[]
        trials=[]
        aims=[]
        pathes = []
        for trial in DataBase.trials:
            Mouse_id = re.findall("(\d+)_part",trial)[0]
            Part = re.findall("part(\d+)",trial)[0]
            Session = re.findall("session(\d+)",trial)[0]
            try:
                Aim = re.findall("aim_(.*)_trial",trial)[0]
            except:
                Aim = 'hc'

            try:
                Trial = re.findall("trial(\d+)",trial)[0]
            except:
                Trial = None

            try:
                Day = re.findall("index(\d+)",trial)[0]
            except:
                Day = str(00000000)

            mouse_ids.append(Mouse_id)
            parts.append(Part)
            days.append(Day)
            sessions.append(Session)
            trials.append(Trial)
            aims.append(Aim)
            pathes.append(trial)

        df = pd.DataFrame()
        df["mouse_id"] = mouse_ids
        df["part"] = parts
        df["day"] = days 
        df["session"] = sessions
        df["trial"] = trials
        df["aim"] = aims
        df["path"] = pathes

        if not mouse_id is None:
            df = df[df["mouse_id"]==str(mouse_id)]
        if not part is None:
            df = df[df["part"]==str(part)]
        if not day is None:
            df = df[df["day"]==str(day)]
        if not session is None:
            df = df[df["session"]==str(session)]
        if not aim is None:
            df = df[df["aim"]==str(aim)]
        return df

    def all_sessions(self,mouse_id=None,part=None,day=None):
        mouse_ids=[]
        parts=[]
        days=[]
        aims=[]
        for session in DataBase.sessions:
            mouse_id = re.findall("(\d+)_part",session)[0]
            part = re.findall("part(\d+)",session)[0]
            day = re.findall("day(\d+)",session)[0]
            aim = re.findall("aim_(.*).pkl",session)[0]

            mouse_ids.append(mouse_id)
            parts.append(part)
            days.append(day)
            aims.append(aim)

        df = pd.DataFrame()
        df["mouse_id"] = mouse_ids
        df["part"] = parts
        df["day"] = days
        df["aim"] = aims
        return df

    def add_order2part(self,part=1):
        """
        Aims:
            context_map contains all the information of each session in evety part
            we need to give numbers of oder to sessions when considering the same session of different mice in a certain part
            so we could know the session order and total sessions number of every mouse in a certain part
        Argumnets:
            part
        Retunr:
            specific_context_map
        """
        context_map = self.context_map[self.context_map["part"]==part]

        specific_context_map = pd.DataFrame()
        for mouse_id in set(context_map["mouse_id"]):
            part_order=[]
            part_total_number=[]
            selected_context_map = context_map[context_map["mouse_id"]==mouse_id]
            selected_context_map.sort_values(by=["index"])
            selected_context_map = selected_context_map.reset_index(drop=True)
            total_number = selected_context_map.shape[0]
            for index,row in selected_context_map.iterrows():
                part_order.append(index+1)
                part_total_number.append(total_number)
            selected_context_map["part_order"]=part_order
            selected_context_map["part_total_number"] = part_total_number
            specific_context_map = pd.concat([specific_context_map,selected_context_map])
        return specific_context_map

    def show(self):

        print("in Trials")
        df_trials = self.all_trials()
        for mouse_id in set(df_trials["mouse_id"]):
            parts = set(df_trials[df_trials["mouse_id"]==mouse_id]["part"])
            for part in parts:
                days = set(df_trials[(df_trials["mouse_id"]==mouse_id) & (df_trials["part"]==part)]["day"])
                days = sorted(days)
                print("%s parts: %s days: %s"%(mouse_id,part,days))

        print("in Sessions")
        df_session = self.all_sessions()
        for mouse_id in set(df_session["mouse_id"]):
            parts = set(df_session[df_session["mouse_id"]==mouse_id]["part"])
            for part in parts:
                days = set(df_session[(df_session["mouse_id"]==mouse_id) & (df_session["part"]==part)]["day"])
                days = sorted(days)
                print("%s parts %s days %s"%(mouse_id,part,days))

    def generate_trials(self,session):
        """
        to divide raw session into trials
        Arguments:
            session: is session*.pkl which is generaged by jupyter script
        """
        try:
            divide_sessions_into_trials(session,DataBase.Trial_path,update = False)
            return 1
        except:
            return 0 

    def save_new_session(self,mouse_id,part,day,aim):
        """
        to save trials of one mouse, one part, one day and one aim as a new session
        """
        trials = self.all_trials(mouse_id=mouse_id,part=part,day=day,aim=aim)["path"]
        if len(trials)>0:
            try:
                save_newsession(trials,savedir=DataBase.Session_path,update=False)
                return 1
            except Exception as e:
                return 0 
        else:
            print("no trials indexed")
            return 1

    def index_sessions(self,mouse_id=None,part=None,day=None,aim=None):
        sessions = DataBase.sessions
        if not mouse_id is None:
            sessions = [i for i in sessions if str(mouse_id) in i]
        if not part is None:
            sessions = [i for i in sessions if "part%s"%part in i]
        if not day is None:
            sessions = [i for i in sessions if str(day) in i]
        if not aim is None:
            sessions = [i for i in sessions if str(aim) in i]

        return sessions

    def index_celltypes(self,mouse_id=None,part=None,day=None,aim=None):
        celltypes = DataBase.celltypes
        if not mouse_id is None:
            celltypes = [i for i in celltypes if str(mouse_id) in i]
        if not part is None:
            celltypes = [i for i in celltypes if "part%s"%part in i]
        if not day is None:
            celltypes = [i for i in celltypes if str(day) in i]
        if not aim is None:
            celltypes = [i for i in celltypes if "aim_"+str(aim) in i]

        return celltypes

    def organize_celltypes(self,):
        pass





def main_generate_trials_in_batch(session_dirs:list):
    """
    # session example:
    # sessions = glob.glob(r"D:\miniscope_result_3\Results_2020061\part234\session*.pkl")
    """
    db = DataBase()
    sessions=[]
    for session_dir in session_dirs:
        sessions.append(glob.glob(os.path.join(session_dir,"session*.pkl")))

    bug_sessions = []
    for session in sessions:
        okay =  db.generate_trials(session)
        if not okay:
            bug_sessions.append(session)
    [print(i) for i in bug_sessions]
    
def main_save_new_sessions_in_batch(mouse_ids,parts,days,aims):
    db = DataBase()
    bug_sessions=[]
    for mouse_id in mouse_ids:
        for part in parts:
            for day in days:
                for aim in aims:
                    okay = db.save_new_session(mouse_id,part,day,aim)
                    if not okay:
                        bug_sessions.append([mouse_id,part,day,aim])
    [print(i,"\r") for i in bug_sessions]


class PklSession2del():
    db = DataBase()
    def __init__(self,filepath):
        self.filepath = filepath

    def mouseid_part_day_aim(self):
        mouse_id = re.findall("(\d+)_part",self.filepath)[0]
        part = re.findall("part(\d+)",self.filepath)[0]
        try:
            day = re.findall("day(\d+)",self.filepath)[0]
        except:
            day = "00000000"

        try:
            aim = re.findall("aim_(.*).pkl",self.filepath)[0]
        except:
            aim = "hc"
        return mouse_id,part,day,aim


    def cellids(self,):
        
        s = build_session(self.filepath)

        s.add_Trial_Num_Process()
        s.add_Context()
        s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])

        contextcells = cellid_Context(s
                       ,"S_dff"
                       ,placebin=np.arange(8,38))

        s.add_Body_speed(scale=0.33)
        s.add_running_direction(according="Body")

        rdcells = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38))


        pccells = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=np.arange(8,38)
                            ,Body_speed=3)
        return contextcells,rdcells,pccells

    def RD_cellids(self,placebin=np.arange(8,38)):
        s = build_session(self.filepath)

        s.add_Trial_Num_Process()
        s.add_Context()
        s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
        s.add_Body_speed(scale=0.33)
        s.add_running_direction(according="Body")

        rdcells = cellid_RD_incontext(s
                            ,"S_dff"
                            ,placebin=placebin
                            ,Body_speed=3)

        return rdcells

    def PC_cellids(self,placebin=np.arange(8,38)):
        s = build_session(self.filepath)

        s.add_Trial_Num_Process()
        s.add_Context()
        s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
        s.add_Body_speed(scale=0.33)
        s.add_running_direction(according="Body")
        pccells = cellid_PC_incontext(s
                            ,"S_dff"
                            ,placebin=placebin
                            ,Body_speed=3)
        return pccells

    def CTX_cellids(self,):
        pass

    def save_celltypes(self):
        mouse_id,part,day,aim = self.mouseid_part_day_aim()
        filename = "celltype_%s_part%s_day%s_aim_%s.pkl"%(mouse_id,part,day,aim)
        savepath = os.path.join(db.Celltype_path,filename)

        contextcells,rdcells,pccells = self.cellids()
        result = {
        "mouse_id":mouse_id,
        "part":part,
        "day":day,
        "contextcells":contextcells,
        "rdcells":rdcells,
        "pccells":pccells
        }

        save_pkl(result,savepath)

    def update_RD_celltyes(self,):
        mouse_id,part,day,aim = self.mouseid_part_day_aim()
        filename = "celltype_%s_part%s_day%s_aim_%s.pkl"%(mouse_id,part,day,aim)
        savepath = os.path.join(db.Celltype_path,filename)

        rdcells = RD_cellids(self.filepath)
        if os.path.exists(savepath):
            result = load_pkl(savepath)
            result["rdcells3"] = rdcells

            save_pkl(result,savepath)
        else:
            print("%s doesn't exist"%savepath)

    def update_behave_state_info(self,):
        mouse_id,part,day,aim = mouseid_part_day_aim()
        filename = "celltype_%s_part%s_day%s_aim_%s.pkl"%(mouse_id,part,day,aim)
        savepath = os.path.join(db.Celltype_path,filename)

        s = build_session(self.filepath)
        stat_info = behave_stat_info(s)

        if os.path.exists(savepath):
            result = load_pkl(savepath)
            result["stat_info"] = stat_info
            save_pkl(result,savepath)
        else:
            print("%s doesn't exist"%savepath)


    def generate_Meanfr_of_Allcells_along_placebins(self):
        mouse_id,part,day,aim = self.mouseid_part_day_aim()
        s = build_session(self.filepath)

        s.add_Trial_Num_Process()
        s.add_Context()
        s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
        s.add_Body_speed(scale=0.33)

        Context_Matrix_info = SingleCell_MeanFr_in_SingleTrial_along_Placebin(s
            ,"S_dff"
            ,placebin=np.arange(8,38)
            ,Body_speed=3)

        Meanfr_of_Allcells_along_placebins = {}

        cellids = ["%s_%s"%(mouse_id,i) for i in Context_Matrix_info["cellids"] ]
        for context in Context_Matrix_info["Context_Matrix_cellids_placebins_trials"].keys():
            ave = np.nanmean(Context_Matrix_info["Context_Matrix_cellids_placebins_trials"][context],axis=2)
            df = pd.DataFrame(ave,columns=Context_Matrix_info["place_bins"],index=cellids)
            Meanfr_of_Allcells_along_placebins[context]=df

        return Meanfr_of_Allcells_along_placebins

    def generate_NormedMeanfr_of_Allcells_along_placebins_of_sessions(self,sessions):
        """
        sessions are the same session of different mice
        """
        Meanfr_of_Allcells_along_placebins_mice = []
        for session in sessions:
            Meanfr_of_Allcells_along_placebins = generate_Meanfr_of_Allcells_along_placebins(session)
            Meanfr_of_Allcells_along_placebins_mice.append(Meanfr_of_Allcells_along_placebins)
            
        all_cells = {}
        for context in Meanfr_of_Allcells_along_placebins_mice[0].keys():
            all_cells_c = pd.concat([i[context] for i in Meanfr_of_Allcells_along_placebins_mice])
            all_cells_c = all_cells_c.apply(func=lambda x:(x-np.nanmean(x))/np.nanstd(x,ddof=1),axis=1)
            print("cell firing is standarized along the placebins")
            all_cells[context]=all_cells_c
        
        return all_cells

def build_CellType(celltype_filepath):
    return CellType(celltype_filepath)

class CellType():
    db = DataBase()
    def __init__(self,filepath):
        self.filepath = filepath
        self.context_map = CellType.db.context_map

    @property
    def keys(self):
        return load_pkl(self.filepath).keys()
        
    @property
    def result(self):
        return load_pkl(self.filepath)

    def mouseid_part_day_aim(self):
        mouse_id = re.findall("(\d+)_part",self.filepath)[0]
        part = re.findall("part(\d+)",self.filepath)[0]
        try:
            day = re.findall("day(\d+)",self.filepath)[0]
        except:
            day = "00000000"

        try:
            aim = re.findall("aim_(.*).pkl",self.filepath)[0]
        except:
            aim = "hc"
        return mouse_id,part,day,aim
    
    def find_session(self):
        mouse_id,part,day,aim = self.mouseid_part_day_aim()
        session_path = CellType.db.index_sessions(mouse_id,part,day,aim)
        return session_path[0]

    def csi(self,contexts=[0,1]):
        if contexts[0] > contexts[1]:
            contexts = sorted(contexts)
        r = load_pkl(self.filepath)
        csi = r["contextcells"]["ctx%s_%s"%(contexts[0],contexts[1])]["CSI"]
        csi.index = ["%s_%s"%(r["mouse_id"],i) for i in csi.index]
        return csi

    def rdsi(self,context=0):
        r = load_pkl(self.filepath)
        rdsi = r["rdcells2"]["context_%s"%context]["ctx_rd_RDSI"]
        rdsi.index = ["%s_%s"%(r["mouse_id"],i) for i in rdsi.index]
        return rdsi

    def si(self,context=0):
        r = load_pkl(self.filepath)
        si = r["pccells"]["context_%s"%context]["observed_SIs"]
        si.index = ["%s_%s"%(r["mouse_id"],i) for i in si.index]
        return si

    def MaxFr_placebin(self,context=0):
        """
        consider running forward and backward as the same
        """
        Meanfr_along_placebins = session(self.find_session()).generate_Meanfr_of_Allcells_along_placebins()
        maxfr_placebins = Meanfr_along_placebins["context%s"%context].idxmax(axis=1)
        return maxfr_placebins

    def trial_length(self):
        """
        """
        session = self.find_session()
        s = build_session(session)
        behavelog_time = s.result["behavelog_time"]
        return pd.Series(behavelog_time["P_r_exit"] - behavelog_time["P_nose_poke"],name="trial_length")

    def specific_ids(self,contexts=[0,1]):
        if contexts[0] > contexts[1]:
            contexts = sorted(contexts)
            
        r = load_pkl(self.filepath)
        
        total_cell_num = r["contextcells"]["meanfr_df"].shape[1]
        contextcell_ids = {}
        contextcells_0 = r["contextcells"]["ctx%s_%s"%(contexts[0],contexts[1])]["context%s_cells"%contexts[0]]
        contextcells_1 = r["contextcells"]["ctx%s_%s"%(contexts[0],contexts[1])]["context%s_cells"%contexts[1]]
    #     noncontextcells = r["contextcells"]["ctx%s_%s"%(contexts[0],contexts[1])]["non_context_cells"]
     
        contextcell_ids["ctx%scells"%contexts[0]] = ["%s_%s"%(r["mouse_id"],i) for i in contextcells_0]
        contextcell_ids["ctx%scells"%contexts[1]] = ["%s_%s"%(r["mouse_id"],i) for i in contextcells_1]
    #     contextcell_ids["nonctxcells"] = ["%s_%s"%(r["mouse_id"],i) for i in noncontextcells]
 
        rdcell_ids = {}
        # print("rdcells: try body_speed> 3cm/s")
        rdcell_ids["context%s_leftcells"%contexts[0]] = ["%s_%s"%(r["mouse_id"],i) for i in r["rdcells2"]["context_%s"%contexts[0]]["left_cells"]]
        rdcell_ids["context%s_rightcells"%contexts[0]] = ["%s_%s"%(r["mouse_id"],i) for i in r["rdcells2"]["context_%s"%contexts[0]]["right_cells"]]
    #     rdcell_ids["context%s_nonrdcells"%contexts[0]] = ["%s_%s"%(r["mouse_id"],i) for i in r["rdcells"]["context_%s"%contexts[0]]["non_rd_cells"]]

        rdcell_ids["context%s_leftcells"%contexts[1]] = ["%s_%s"%(r["mouse_id"],i) for i in r["rdcells2"]["context_%s"%contexts[1]]["left_cells"]]
        rdcell_ids["context%s_rightcells"%contexts[1]] = ["%s_%s"%(r["mouse_id"],i) for i in r["rdcells2"]["context_%s"%contexts[1]]["right_cells"]]
    #     rdcell_ids["context%s_nonrdcells"%contexts[1]] = ["%s_%s"%(r["mouse_id"],i) for i in r["rdcells"]["context_%s"%contexts[1]]["non_rd_cells"]]

        pccell_ids = {}
        
        pccell_ids["context%s_pccells"%contexts[0]] = ["%s_%s"%(r["mouse_id"],i) for i in r["pccells"]["context_%s"%contexts[0]]["place_cells"]]
        pccell_ids["context%s_pccells"%contexts[1]] = ["%s_%s"%(r["mouse_id"],i) for i in r["pccells"]["context_%s"%contexts[1]]["place_cells"]]

        return contextcell_ids, rdcell_ids,pccell_ids,total_cell_num
if __name__ == '__main__':
    pass
