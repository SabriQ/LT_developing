from mylab.ana.miniscope.context_exposure.ana_funtions import SingleCell_MeanFr_in_SingleTrial_along_Placebin,plot_MeanFr_along_Placebin
from mylab.ana.miniscope.context_exposure.Canamini import *
from multiprocessing import Pool
from Cdatabase import DataBase
db = DataBase()

def plot_single_cell_example(session:str):
    print(session)
    s = build_session(session)

    s.add_Trial_Num_Process()
    s.add_Context()
    s.add_alltrack_placebin_num(place_bin_nums=[4,4,30,4,4,4])
    s.add_Body_speed(scale=0.33)

    s.add_behave_forward_context(according="Enter_ctx")
    s.add_behave_choice_side()
    s.add_behave_reward()

    Context_Matrix_info = SingleCell_MeanFr_in_SingleTrial_along_Placebin(s
        ,"S_dff"
        ,Body_speed=3)

    for idx in Context_Matrix_info["cellids"]:
        print("===%s:%s==="%(Context_Matrix_info["mouse_id"],idx))
        plot_MeanFr_along_Placebin(Context_Matrix_info=Context_Matrix_info
                           ,idx=idx,save=False,show=True,savedir=r"../../results/plots")


def main_plot_single_cell_example():
    sessions = db.index_sessions()
    sessions = [i for i in sessions if "201034_part234_day20200803_aim_B1C1" in i]
    for session in sessions:
        plot_single_cell_example(session)

if __name__ == '__main__':
    main_plot_single_cell_example()