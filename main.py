import pandas as pd
from function import Trips, General
import streamlit as st 
import datetime # Standard Python Module
from io import BytesIO # Standard Python Modules

#---------------------Settings----------
rr = ['','DRR','URR','BRR','BFU','DFU','UFU'] 
# id = ['',1,2] 
tt_dict={}
tt_dict['DRR']={'both_or_single' : '2', 'gha_pltfrm' : '1', 'ver_pltfrm' : '1'}
tt_dict['URR']={'both_or_single' : '2', 'gha_pltfrm' : '2', 'ver_pltfrm' : '1'}
tt_dict['BRR']={'both_or_single' : '1', 'gha_pltfrm' : '0', 'ver_pltfrm' : '1'}
tt_dict['BFU']={'both_or_single' : '1', 'gha_pltfrm' : '0', 'ver_pltfrm' : '2'}
tt_dict['DFU']={'both_or_single' : '2', 'gha_pltfrm' : '1', 'ver_pltfrm' : '2'}
tt_dict['UFU']={'both_or_single' : '2', 'gha_pltfrm' : '2', 'ver_pltfrm' : '2'}

General.removeFile('t.xlsx')

st.experimental_singleton.clear()
st.set_page_config(page_title='Excel Plotter')
st.title('Timetable train id generator 📈')
st.sidebar.title('Timetable train id generator 📈')
st.sidebar.subheader('Choose excel file with vehicle schedule pasted in Sheet1')

uploaded_file = st.sidebar.file_uploader('Choose excel file', type='xlsx')

# st.sidebar.text_input("Your name", key="name")
# st.session_state.name

option = st.sidebar.selectbox(
    'Please select form below type of TT?',
     rr)

id_option = st.sidebar.selectbox(
    'Please select first train destination id from VER (01 or 02)',
    ('', '1', '2'))

# 'You selected: ', option

if uploaded_file and option and id_option:
    st.markdown('---')
    df =  pd.read_excel(uploaded_file, sheet_name="Sheet1")
    #--------------- original vehicle schedule------------
    orgVechSch = df
    # st.dataframe(orgVechSch)
    #--------------- Hourly Trips -------------------
    grouped_trips = Trips.up_dn_trips(df)
    # st.text("Hourly trips")
    st.write("Hourly trips")
    st.dataframe(grouped_trips)
    # ------------------ Cleaned vehicle Schedule----------
    df, allTrps_df  = Trips.cleaned_vechicle_schedule(df)
    st.write("Vehicle Schedule for Crew controller")
    st.dataframe(df)
    ## -----------------Get all trips using function----------
    allTripTypes = ['Connection Trip', 'Regular Trip', 'Pull-Out Trip', 'Pull-In Trip']
    allTrips = Trips.allTripsCount(allTripTypes, allTrps_df)
    st.write("Total trips")
    st.dataframe(allTrips)
    #------------ only trips starting from VER -------------
    # regularTrips_df = Trips.RegTrips(df)
    # trips1 = regularTrips_df.to_dict('records')
    # st.dataframe(regularTrips_df)
    df.reset_index(inplace=True, drop=True)
    df = df.sort_values(by='Departure_Time', ascending=True)
    trips = df.to_dict('records')
    #---------- VER first train destination id-------------
    startid= Trips.Startid(int(id_option))
    #-------------------------------------------------
    dict = Trips.ServiceID(trips,df)
    ## 1 = both @ GHA 2 = Single @ GHA
    both_or_single = int(tt_dict[option]['both_or_single'])
    # print(f"Both or single value : {both_or_single}")
    ## 1 = DN @ GHA 2 = UP @ GHA,  0 = Both platform 
    gha_pltfrm = int(tt_dict[option]['gha_pltfrm'])
    # print(f"GHA platform :- {gha_pltfrm}")
    ## 1 = VER siding 2 = VER UP
    ver_pltfrm =  int(tt_dict[option]['ver_pltfrm'])
    # print(f"VER platform :- {ver_pltfrm}")
    # dest_no = [2]
    dest_no = [int(startid)]
    # st.text(dest_no)
    ## ------------ Generating all id's----------
    allids = Trips.Allid(trips,dict,both_or_single,gha_pltfrm,ver_pltfrm,dest_no)
    st.write("All Trips with ID's")
    st.dataframe(allids)
    ## Induction and Withdrawal train and ID's
    induct_id1, tr1 = Trips.trainInOut(allids, option, 'Pull-Out Trip')
    withdraw_id1, tr2 = Trips.trainInOut(allids, option, 'Pull-In Trip')
    
    df_induct1 = pd.DataFrame.from_dict(induct_id1)    
    df_withdraw = pd.DataFrame.from_dict(withdraw_id1)
    df_induct1 = df_induct1.sort_values(by='dep_time', ascending=True)
    df_withdraw = df_withdraw.sort_values(by='dep_time', ascending=True)
    st.write("All induction trips")
    st.dataframe(df_induct1)
    st.write("All withdrawal trips")
    st.dataframe(df_withdraw)    

    # -------------------------- Download file section start-------------------
    # list of dataframes 
    dfs = [orgVechSch, grouped_trips, df, allTrips, allids, df_induct1, df_withdraw, tr1, tr2]

    # list of sheet names
    sheets = ['vehicle_schedule','hourly_trips','cleaned_df','total_trips','id_sheet','induction-ids','withdrwal_ids','tr1','tr2']  

    buffer = BytesIO()

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        for dataframe, sheet in zip(dfs, sheets):
            dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0)   
        writer.save()

        st.download_button(
            label="📥 Download Excel worksheets",
            data=buffer,
            file_name=f"{datetime.datetime.now()}.xlsx",
            mime="application/vnd.ms-excel"
        )



    
