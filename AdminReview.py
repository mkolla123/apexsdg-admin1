import calendar
from datetime import datetime
import streamlit as st 
from streamlit_option_menu import option_menu
import mysql.connector

import pandas as pd
#from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
#from sqlalchemy.orm import sessionmaker
#from sqlalchemy.ext.declarative import declarative_base

db_config = {
    'host': '127.0.0.1',
    'user': 'test1',
    'password': 'test1',
    'database': 'apexsdg',
}

conn = mysql.connector.connect(**db_config)
mycursor = conn.cursor(dictionary=True)
		
page_title = "College, user info"
page_icon = ":money_with_wings:"
layout = "centered"

st.set_page_config(page_title = page_title, page_icon = page_icon, layout = layout)
st.title(page_title + " ") 

#college_id = st.session_state.college_id
#st.write(f"college id - {college_id}")
#st.session_state

cname = []
# cid = []
cid = 0
cdate = []
#df 

aclist = []
acname_list = []
aclist_objset = []
marks_id = []
marks_t = []
total_new_marks = 0

def execute_query(query, conn):
    df = pd.read_sql_query(query, conn)
    return df


def get_values_by_name(name, df):
    # Use boolean indexing to find the row
    row = df.loc[df['college_name'] == name]
    
    if not row.empty:
        return row.iloc[0]  # Return the first matching row as a Series
    else:
        return None  # Return None if the name is not found

def get_id_by_name(name, df):
    # Use boolean indexing to find the id
    id_series = df.loc[df['college_name'] == name, 'id']
    if not id_series.empty:
        return id_series.values[0]  # Return the first matching name
    else:
      return None  # Return None if the name is not found

def update_marks():
    global total_new_marks
    for x in marks_t:
        #Ech x has activity_id, current marks, new marks to be used, retrieve that.
        aid, cmrks, nmrks = x
        st.write(f"Current aid = {aid}, current marks = {cmrks}, new marks = {nmrks} ")
        markssql = """update activity_details set allocated_marks = %s where id = %s"""
        nmrkss = cmrks+nmrks
        val = (nmrkss, aid)
        mycursor.execute(markssql,val)
        #tmarkssql = """select total_marks from college_info where id = %s"""
        #mycursor.execute(tmarkssql, (cid,))
        total_new_marks += nmrks
        st.write(f"Total college marks = {total_new_marks}, new marks = {nmrkss}")
        
    
def allocate_marks(amarks,id_acd, cid):
    st.session_state.input_value = 0
    u_mrks = st.text_input("Marks for this activity", value=st.session_state.input_value, key=id_acd)
        #marks_tuple = (id_acd, mrks)
        #marks.append(marks_tuple)
    mrks = int(u_mrks)
    if mrks is not None and mrks > 0 :     
        erow = (id_acd, int(amarks),mrks)
        marks_t.append(erow)
    #st.write(marks_t)

    
def get_acdetails(id):
    #
    squery = "select * from activity_details where college_id = %s"
    college_id = (str(id),)
    mycursor.execute(squery, college_id)
    results = mycursor.fetchall()
    if results is not None:
        for res in results:
            aclist.append(res)
            #st.write(res)

def get_studentinfo(cid):
    stsql = """select student_name, sh_club_name from student_info where \
            college_id = %s"""
    val = (cid,)
    mycursor.execute(stsql, val)
    results = mycursor.fetchall()
    if results is not None:
        for res in results:
            st.write(f"Student self help clubs and the respective student names ")
            st.table(res)


def get_natintlinfo(cid):
    stsql = """select national_international_day, date from national_international_days where \
            college_id = %s"""
    val = (cid,)
    #st.write(f"College id in get nat = {cid}")
    mycursor.execute(stsql, val)
    results = mycursor.fetchall()
    if results is not None:
        for res in results:
            st.write(f"National or International days celebrated by the college ")
            st.table(res)
            
def show_data():
    index = 0
    global cid
    while index < len(aclist):
        aclist_obj=aclist[index]
        #Get the id from activity_details row, to use for updating marks later
        id_acd = aclist_obj['id']
        del aclist_obj['id']
        del aclist_obj['college_id']
        acid = aclist_obj['activity_id']
        #st.write(f"Ac id = {acid}")
        acidsql = """select activity_name from activity_table where activity_number= %s"""
        val = (str(acid),)
        mycursor.execute(acidsql, val)
        acname = mycursor.fetchone()
        #Change activity_id to activity_name for better readability to the user
        aclist_obj['activity_id'] = acname["activity_name"]
        col1, col2 = st.columns([1,4])
        amarks = aclist_obj['allocated_marks']
        acname_list.append(acname["activity_name"])
        aclist_objset.append(aclist_obj)
        #if amarks == 0:
        #with col1:
        #    allocate_marks(amarks, id_acd, cid)
        #with col2: 
        st.table(aclist_obj)
        allocate_marks(amarks, id_acd, cid)
        index += 1
    #st.table(aclist_objset)
            

    
def main(): 
    query = "select * from college_info"
    
    df = execute_query(query, conn)
    #st.write(df)  # Display the DataFrame in a table
    
    names_list = df['college_name'].tolist()

    #New code
    col1, col2 = st.columns([1,4])

    with col1: 
        option = st.selectbox(f"Which college do you want to pick ", names_list )
 
    if option is not None:
        result = get_values_by_name(option, df)
        ccid = get_id_by_name(option, df)
        #st.write(f"Id is {ccid}")
        cid = str(ccid)
        #st.write(f"Cid in MAIN = {cid}")
        #st.write(result)
    with col2: 
            st.table(result)
        #Get activity details from id
            get_acdetails(cid)
    get_studentinfo(cid)
    get_natintlinfo(cid)
    show_data()
    submitted = st.button("Submit")
    
    if submitted:
        update_marks()
        tmarkssql = """select total_marks from college_info where id = %s"""
        cidval = (cid,)
        st.write(f"Cid = {cid}")
        mycursor.execute(tmarkssql, cidval)
        ctmrkst1 = mycursor.fetchone()
        if ctmrkst1 is not None:
            ctmrkst = ctmrkst1["total_marks"]
            tmrks = int(ctmrkst)+total_new_marks
            #st.write(f"Total marks in main = {tmrks}")
            totmarkssql = """update college_info set total_marks = %s where id = %s"""
            valci = (tmrks, cid)
            mycursor.execute(totmarkssql, valci)
        conn.commit()
        mycursor.close()
        conn.close()
        st.success(f"Thank you, your response has been submitted.")
        st.session_state.clear()
        st.switch_page("pages/thanks.py")
        #st.rerun()
            

if __name__ == "__main__":
    main()

