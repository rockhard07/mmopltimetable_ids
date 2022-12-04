import pandas as pd
import os
import re
from openpyxl import load_workbook

class Trips:        

    def findNumberOfTrips(colName, tripType, df):
        connectingTrips_df = df.loc[(df[colName] == tripType)]
        connectingTrips_df.reset_index(inplace=True, drop=True)
        # print(connectingTrips_df)
        #number of rows in dataframe
        num_rows = connectingTrips_df.shape[0]
        # print(f"{num_rows} number of {tripType}")
        return tripType, num_rows

    def allTripsCount(tripTypesList, df):
        finalTrips = {}
        try:
            for trips in tripTypesList:
                # print (trips)
                tripType, tripCount = Trips.findNumberOfTrips('Trip_Type', trips, df)
                finalTrips[tripType]=tripCount    
            # print(finalTrips)
            # input('Press ENTER to exit')
            # print("Closing.......")    
        except KeyboardInterrupt:
            exit()

        df_combs = pd.DataFrame()
        df_combs = df_combs.append(finalTrips, ignore_index=True, sort=False)
        # Change the row indexes
        df_combs.index = ['Total_Trips']  
        # print combined dataframe
        # print("\n\n  **  Combined Data  **\n")
        # print(df_combs)
        return df_combs
         
    def cleaned_vechicle_schedule(df):
        df.columns = ['Trip_Number','Trip_Type','Main_line','First_Station','Last_Station','Departure_Time','Arrival_Time','Arrival_Time1','Time_Buffer','Crew_number']
        # rmvSpaceCols = ['Trip_Number','Trip_Type','Main_line','First_Station']
        df = df.drop(['Time_Buffer', 'Crew_number'], axis = 1)

        # converting dtypes using astype
        for column in df.columns:
            df[column] = df[column].astype(str) 
         
        # Removing whitespace       
        df['Trip_Type'] = df['Trip_Type'].apply(lambda x:x.strip() )
        df['First_Station'] = df['First_Station'].apply(lambda x:x.strip() )
        df['Last_Station'] = df['Last_Station'].apply(lambda x:x.strip() )

        # Deleteing unwanted starts
        # choice = input("Please enter the row number from where the Trip Number starts : ")
        # df = df.iloc[int(choice):]

        sort = df[df['Trip_Number'].str.contains("Trip Number", na=False)].index.tolist()

        ## Drop unwanted first few unwanted rows
        df.drop(index=df.index[:int(sort[0]+1)], axis=0, inplace=True)
        
        ## Convert everything other than numbers to nan
        df['Trip_Number'] = pd.to_numeric(df['Trip_Number'], errors = 'coerce')

        ## Drop nan rows
        df.dropna(inplace = True)
        df.reset_index(inplace=True, drop=True)
        allTrips_df = df

        df.insert(loc = 0, column = 'Train_number', value = " ")

        locationOfOnes = df.index[df['Trip_Number'] == 1].tolist()
        # print(f"Loaction of ones :- {locationOfOnes}")

        row_value = ["sort", "sort", "sort", "sort", "sort", "sort", "sort", "sort", "sort"]
        count = 0
        for i in locationOfOnes:
            if i > df.index.max()+1:
                print("Invalid row_number")
                # continue
            elif i == 0 :
                df = Trips.Insert_row_(i, df, row_value)
            else:
                count = count + 1
                i = i + count
                # Let's call the function and insert the row
                # at the second position
                df = Trips.Insert_row_(i, df, row_value)

        locationOfsort = df.index[df['Trip_Number'] == 'sort'].tolist()
        train = 0
        for i in locationOfsort:
            train = train + 1
            if train == len(locationOfsort) :
                trn = (f"Train {train}")
                df['Train_number'].loc[i:df.index.max()+1]= trn
            else :
                trn = (f"Train {train}")
                df['Train_number'].loc[i:locationOfsort[train]]= trn

        # print(df)
        ## Inserting train numbers ends here
        # %%
        ## Convert everything other than numbers to nan and drop those rows
        df['Trip_Number'] = pd.to_numeric(df['Trip_Number'], errors = 'coerce')
        df.dropna(inplace = True)
        df.reset_index(inplace=True, drop=True)
        # append_df_to_excel('tes.xlsx', df, sheet_name='te',index=True)

        # Drop Arrival time1 and mainline
        df = df.drop(['Arrival_Time1','Main_line'], axis = 1)
        return df, allTrips_df

    def up_dn_trips(df):
        drf,cleaned_df = Trips.cleaned_vechicle_schedule(df)
        cleaned_df["Departure_Time"] = pd.to_datetime(cleaned_df["Departure_Time"], format='%H:%M:%S', errors='coerce')
        cleaned_df["hour"]=pd.to_datetime(cleaned_df["Departure_Time"], format="%H:%M:%S").dt.hour
        regular_df = cleaned_df.query("`Trip_Type` == 'Regular Trip'")
        ver_df = regular_df.query("`First_Station` == 'VER'")
        gha_df = regular_df.query("`First_Station` == 'GHA'")

        ## get up and down trips count
        df_groupedVer = ver_df.groupby(by=["hour"], as_index=False)['First_Station'].count()
        df_groupedGha = gha_df.groupby(by=["hour"], as_index=False)['First_Station'].count()

        ## change column names
        df_groupedVer.rename({'First_Station': 'Ver_DN'}, axis = 1,  inplace=True)
        df_groupedGha.rename({'First_Station': 'Gha_UP'}, axis = 1,  inplace=True)

        ## Merge both dataframes
        df_grouped = pd.merge(df_groupedVer, df_groupedGha, on='hour')
        # print(df_grouped)
        
        # adding both columns for total trips
        dflist = ['Ver_DN', 'Gha_UP']
        # print (dflist)
        df_grouped["Total"] =  df_grouped[dflist].sum(axis=1)
        # print(df_grouped)
        return df_grouped        

    def Insert_row_(row_number, df, row_value):
        # Slice the upper half of the dataframe
        df1 = df[0:row_number]
    
        # Store the result of lower half of the dataframe
        df2 = df[row_number:]
    
        # Inser the row in the upper half dataframe
        df1.loc[row_number]=row_value
    
        # Concat the two dataframes
        df_result = pd.concat([df1, df2])
    
        # Reassign the index labels
        df_result.index = [*range(df_result.shape[0])]
    
        # Return the updated dataframe
        return df_result

    def trainInOut(test_df1, ttType, tripType):
        ## Dataframe for induction and withdrawal ids
        for i in range(len(test_df1)):
            if test_df1.loc[i, "dep_time"].startswith("1900-01-01 00"):
                dep = test_df1.loc[i, "dep_time"]
                # print(df.loc[i, "Departure_Time"], df.loc[i, "Trip_Number"])
                dep = re.sub('1900-01-01 00', '24', dep, 2)
                # print(f" time is {dep} and loction is {i}")
                test_df1['dep_time'] = test_df1['dep_time'].replace(test_df1.loc[i, "dep_time"], dep)
            
        test_df1 = test_df1.sort_values(by='dep_time', ascending=True)
        trnlst = test_df1['Train'].unique()
        # print(trnlst)
        # print(test_df1.columns)
        induct_id1 = []
        # print(test_df1)
        for lst in trnlst :
            lst= str(lst)
            train_df = test_df1.query("Train == @lst ")
            train_df.reset_index(inplace=True, drop=True)
            train_df['index'] = train_df.index
            induct = train_df.to_dict('records')
            location = train_df.index[train_df['trip_type'] == tripType].tolist()
            # print(train_df1)
            for row in induct:
                for lt in location:
                    if tripType == 'Pull-Out Trip':
                        if row["index"] == int(lt+1):
                            induct_id1.append({'Train' : row['Train'], 'train_id' : row['train_id'], 'dep_time' : row['dep_time'], 'arr_time' : row['arr_time'], 'first_station' : row['first_station'], 'lst_station' : row['lst_station'], 'trip_type' : row['trip_type']})
                        else :
                            continue
                    elif tripType == 'Pull-In Trip':
                        if row["index"] == int(lt-1):
                            strValue = row['train_id']
                            if ttType != 'BRR':
                                # Replace First 3 characters in string with 'XXX'
                                strValue = re.sub(r'^.{0,2}', '43', strValue)
                                # print(strValue)
                            induct_id1.append({'Train' : row['Train'], 'train_id' : strValue, 'dep_time' : row['dep_time'], 'arr_time' : row['arr_time'], 'first_station' : row['first_station'], 'lst_station' : row['lst_station'], 'trip_type' : row['trip_type']})
                        else :
                            continue        
        return induct_id1            

    # def RegTrips(cleaned_df):
    #     df = cleaned_df  
    #     # Insert column Train Id
    #     df.insert(loc = 1, column = 'Train_id', value = " ")
    #     # Filter all Regular and pullout trips from dep VER and GHA
    #     # ver_regularTrips_df = df.loc[((df['Trip_Type'] == 'Regular Trip') | (df['Trip_Type'] == 'Pull-Out Trip')) & ((df['First_Station'] == 'VER') | (df['First_Station'] == 'Depot') | (df['First_Station'] == 'GHA'))]
    #     ver_regularTrips_df = df.loc[((df['Trip_Type'] == 'Regular Trip') | (df['Trip_Type'] == 'Pull-Out Trip') | (df['Trip_Type'] == 'Pull-In Trip')) & ((df['First_Station'] == 'VER') | (df['First_Station'] == 'Depot') | (df['First_Station'] == 'GHA'))]
    #     ver_regularTrips_df.reset_index(inplace=True, drop=True)
    #     # Sort the filterred data in ascending order
    #     ver_regularTrips_df = ver_regularTrips_df.sort_values(by='Departure_Time', ascending=True)
    #     return ver_regularTrips_df

    def Startid(starid):
        # starid = int(starid)
        # print(starid)
        # print(type(starid))
        if starid == 1:
            stid = int(2)
        else : 
            stid = int(1)
        return stid  

    def ServiceID(trips,df):
        # Generating ids by checking pullout trips
        trip_id = []
        cunt = 0
        for row in trips:
            if row["Trip_Type"] == "Pull-Out Trip":
                cunt = cunt + 1
                # print(len(str(cunt)))
                if len(str(cunt)) == 1 : Train_id = f"010{cunt}01"
                else: Train_id = f"01{cunt}01"
                trip_id.append({'Train' : row['Train_number'], 'train_id' : Train_id, 'first_station' : row['First_Station'], 'lst_station' : row['Last_Station'], 'dep_time' : row['Departure_Time'], 'arr_time' : row['Arrival_Time']})
                # print (row)

        # print (trip_id)
        # print(ver_regularTrips_

        ## List of all train numbers
        lst = df['Train_number'].unique()
        # print(lst[0:4])
        ## Add trains to dictionary
        dict={}
        for train in lst:
            dict[train]={'service_id' : '0', 'trip_no' : '0'}
        # print(dict)
        return dict
    
    def Allid(trips,dict,both_or_single,gha_pltfrm,ver_pltfrm,dest_no):
        trip_id1 = []
        cut = 0
        # %%
        for row in trips:
            # if row["Trip_Type"] == "Pull-In Trip" : print(row)
            if row["Trip_Type"] == "Pull-Out Trip":
                train = row["Train_number"]
                cut = cut + 1
                dict[train]['service_id'] = cut
                dict[train]['trip_no'] = 1
                # print(len(str(cunt)))
                if len(str(cut)) == 1 : Train_id = f"010{cut}01"
                else: Train_id = f"01{cut}01"
                trip_id1.append({'Train' : row['Train_number'], 'train_id' : Train_id, 'dep_time' : row['Departure_Time'], 'arr_time' : row['Arrival_Time'], 'first_station' : row['First_Station'], 'lst_station' : row['Last_Station'], 'trip_type' : row['Trip_Type']})
                # print (row)
            elif row["Trip_Type"] == "Regular Trip" and row["First_Station"] == "VER":
                if both_or_single == 1:
                    ## for  both platforms 
                    destNo = dest_no[0] 
                    # print (f"First no : {destNo}")
                    if destNo != 1:
                        destNo = str(1).zfill(2)
                        dest_no[0] = 1
                    elif destNo != 2:
                        destNo = str(2).zfill(2)
                        dest_no[0] = 2
                
                    # print(f"Second no : {destNo}")   
                    ## both platforms end here
                else : 
                    destNo = str(gha_pltfrm).zfill(2)
                # print(destNo)    
                train = row["Train_number"]
                # print(type(train))
                trip_no = int(int(dict[train]['trip_no']) + 1)
                trip_no = str(trip_no).zfill(2)
                service_id = dict[train]['service_id']
                service_id = str(service_id).zfill(2)
                dict[train]['trip_no'] = int(trip_no)
                Train_id = f"{destNo}{service_id}{trip_no}"
                trip_id1.append({'Train' : row['Train_number'], 'train_id' : Train_id, 'dep_time' : row['Departure_Time'], 'arr_time' : row['Arrival_Time'], 'first_station' : row['First_Station'], 'lst_station' : row['Last_Station'], 'trip_type' : row['Trip_Type']})
                # print (row)
            elif row["Trip_Type"] == "Regular Trip" and row["First_Station"] == "GHA":
                train = row["Train_number"]
                # print (f"this is train trip no{dict[train]['trip_no']}")
                # print(type(int(dict[train]['trip_no'])))
                # print(type(1))
                t = int(dict[train]['trip_no'])
                # print (t)
                if t and dict[train]['service_id'] is not None : 
                    # print(f"This is the else statemeny trip no for gha {t}")
                    trip_no = int(t + 1)
                    trip_no = str(trip_no).zfill(2)
                    service_id = dict[train]['service_id']
                    service_id = str(service_id).zfill(2)
                    dict[train]['trip_no'] = int(trip_no)
                else:  
                    # print(f"This is the else statemeny trip no for gha {t}")
                    trip_no = int(t + 1)
                    trip_no = str(trip_no).zfill(2)
                    cut = cut + 1
                    service_id = cut
                    service_id = str(service_id).zfill(2)
                    dict[train]['trip_no'] = int(trip_no)  
                    dict[train]['service_id'] = cut
                if ver_pltfrm == 1 :
                    Train_id = f"42{service_id}{trip_no}"
                    # print(Train_id)
                elif ver_pltfrm == 2 :
                    Train_id = f"44{service_id}{trip_no}"
                    # print(Train_id)
                # Train_id = f"42{service_id}{trip_no}"
                # print(Train_id)
                trip_id1.append({'Train' : row['Train_number'], 'train_id' : Train_id, 'dep_time' : row['Departure_Time'], 'arr_time' : row['Arrival_Time'], 'first_station' : row['First_Station'], 'lst_station' : row['Last_Station'], 'trip_type' : row['Trip_Type']})
                # print (row)  
            elif row["Trip_Type"] == "Pull-In Trip":
                # print(row)
                train_id = "000001"
                trip_id1.append({'Train' : row['Train_number'], 'train_id' : train_id, 'dep_time' : row['Departure_Time'], 'arr_time' : row['Arrival_Time'], 'first_station' : row['First_Station'], 'lst_station' : row['Last_Station'], 'trip_type' : row['Trip_Type']})


        # print (trip_id1)
        # %%
        test_df1 = pd.DataFrame.from_dict(trip_id1)
        return test_df1


class General:
    def removeFile(filename):
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print("The file does not exist")  

if __name__ == "__main__" :
    ...
