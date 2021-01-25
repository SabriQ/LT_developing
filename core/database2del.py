import os,sys,glob,re,platform
import pandas as pd 
import numpy as np
from mylab.process.miniscope.context_exposure.save2trials import divide_sessions_into_trials
from mylab.ana.miniscope.context_exposure.Canamini import *

from multiprocessing import Pool
from mylab.Functions import load_pkl



if platform.system()=='Linux':
    Trials = glob.glob(r"/home/qiushou/Documents/QS_data/syn/Trials/*.pkl")
    Sessions = glob.glob(r"/home/qiushou/Documents/QS_data/syn/Sessions/*.pkl")
    context_map_file = r"/home/qiushou/Documents/QS_data/syn/developing/context_map.csv"
elif platform.system()=='Windows':
    Trials = glob.glob(r"\\10.10.47.163\Data_archive\qiushou\Trials\*.pkl")
    Sessions = glob.glob(r"\\10.10.47.163\Data_archive\qiushou\Sessions\*.pkl")
    context_map_file=r"\\10.10.47.163\Data_archive\qiushou\developing\context_map.csv"

context_map = pd.read_csv(context_map_file)


def database_trials(mouse_id=None,part=None,day=None,session=None,aim=None):
    mouse_ids=[]
    parts=[]
    days=[]
    sessions=[]
    trials=[]
    aims=[]
    pathes = []
    for trial in Trials:
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

def database_session(mouse_id=None,part=None,day=None):

    mouse_ids=[]
    parts=[]
    days=[]
    for session in Sessions:
        mouse_id = re.findall("(\d+)_part",session)[0]
        part = re.findall("part(\d+)",session)[0]
        day = re.findall("day(\d+)",session)[0]

        mouse_ids.append(mouse_id)
        parts.append(part)
        days.append(day)

    df = pd.DataFrame()
    df["mouse_id"] = mouse_ids
    df["part"] = parts
    df["day"] = days
    return df

def show():
    print("in Trials")
    df_trials = database_trials()
    for mouse_id in set(df_trials["mouse_id"]):
        parts = set(df_trials[df_trials["mouse_id"]==mouse_id]["part"])
        for part in parts:
            days = set(df_trials[(df_trials["mouse_id"]==mouse_id) & (df_trials["part"]==part)]["day"])
            days = sorted(days)
            print("%s parts %s days %s"%(mouse_id,part,days))

    print("in Sessions")
    df_session = database_session()
    for mouse_id in set(df_session["mouse_id"]):
        parts = set(df_session[df_session["mouse_id"]==mouse_id]["part"])
        for part in parts:
            days = set(df_session[(df_session["mouse_id"]==mouse_id) & (df_session["part"]==part)]["day"])
            days = sorted(days)
            print("%s parts %s days %s"%(mouse_id,part,days))

def generate_trials(sessions,savedir=r"\\10.10.47.163\Data_archive\qiushou\Trials"):
    bug_sessions = []
    for session in sessions:
        try:
            divide_sessions_into_trials(session,savedir)
        except:
            bug_sessions.append(session)
    return bug_sessions




def renameTrial(path):
    r = load_pkl(path)
    new_path = path.replace("_t","_aim_%s_t"%r["info"]["aim"])
    os.rename(path,new_path)
    print("%s done"%path)

def generate_sessions(part=1,aim="ce"):
    """
    to save trials as session in batch mode by specifing part and aim
    """
    df = database_trials(part=part,aim=aim)

    mouse_ids = list(set(df["mouse_id"]))

    for mouse_id in mouse_ids:
        days = list(set(df[df["mouse_id"]==mouse_id]["day"]))
        for day in days:
            tempdf = df[(df["mouse_id"]==mouse_id)&(df["day"]==day)]
            part = list(tempdf["part"])[0]
            aim = list(tempdf["aim"])[0]
            save_newsession(tempdf["path"],savedir=None)


def main1():
    session_dirs = glob.glob(r"D:\miniscope_result_3\Results_2020061\part234")
    bug_sessions=[]
    for session_dir in session_dirs:
        bug = generate_trials(session_dir)
        if len(bug) >0 :
            bug_sessions=bug_sessions+bug

    print("===========================")
    [print(i) for i in bug_sessions]
if __name__ == '__main__':
    # session_dirs = [i for i in glob.glob(r"D:\miniscope_result_3\*\*") if os.path.isdir(i)]
    generate_sessions(part=6,aim="lack_wall")

    



