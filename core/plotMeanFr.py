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
                           ,idx=idx,save=True,show=False,savedir=r"../../results/plots")


def main_plot_single_cell_example():
    sessions = db.index_sessions()
    strs = [
        "201034_part234_day20200803_aim_BC",
        "201034_part234_day20200801_aim_ce",
        "201034_part234_day20200727_aim_ce",
        "201034_part234_day20200804_aim_AB",
        "201034_part234_day20200730_aim_ce",
        "201034_part234_day20200730_aim_lg",
        "206534_part234_day20200806_aim_ce",
        "201034_part234_day20200807_aim_ce",
        "201034_part234_day20200803_aim_A1C1",
        "201034_part234_day20200804_aim_A1B1",
        "206551_part234_day20200801_aim_ce",
        "206551_part234_day20200801_aim_lg",
        "201034_part234_day20200727_aim_lg",
        "201034_part234_day20200803_aim_AC",
        "201034_part234_day20200806_aim_ce",
        "201034_part234_day20200805_aim_ce",
        "206551_part234_day20200731_aim_ce",
        "201034_part234_day20200801_aim_lg",
        "206548_part234_day20200731_aim_ce"
    ]
    selected_sessions=[]
    for s in strs:
        session = [i for i in sessions if s in i][0]
        selected_sessions.append(session)
    # sessions = [i for i in sessions if "201034_part234_day20200803_aim_BC" in i]
    pool = Pool(4)
    pool.map(plot_single_cell_example,selected_sessions)
    # for session in selected_sessions:
    #     plot_single_cell_example(session)

if __name__ == '__main__':
    main_plot_single_cell_example()