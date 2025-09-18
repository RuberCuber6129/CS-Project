import streamlit as st
import pandas as pd
import mysql.connector as mysql
import hashlib
from datetime import datetime, date, time, timedelta

st.set_page_config(page_title="Mayoor School Clinic", page_icon="🩺", layout="wide")

DB_HOST="localhost"
DB_PORT=3306
DB_USER="root"
DB_PASSWORD="root"
DB_NAME="mayoor_clinic_db"

SIDEBAR_CSS="""
<style>
:root { --bg:#0b1220; --panel:#121a2b; --accent:#10b981; --muted:#9ca3af; --text:#e5e7eb; }
section[data-testid="stSidebar"] > div { background: var(--bg); }
.sidebar-brand { color:#f9fafb; font-weight:800; font-size:1.25rem; letter-spacing:.3px; margin:6px 4px 14px 4px; }
.sidebar-card { background: linear-gradient(135deg,#0ea5e9 0%,#10b981 70%); color:#ecfeff; border-radius:14px; padding:14px 16px; margin: 4px 4px 18px 4px; box-shadow: 0 6px 22px rgba(0,0,0,.25); }
.sidebar-pill { display:inline-block; background: rgba(0,0,0,.18); padding:6px 10px; border-radius:999px; font-weight:700; font-size:.92rem; }
.nav-head { color:#e5e7eb; font-weight:700; margin: 6px 0 6px 6px; }
.stRadio > div[role="radiogroup"] > label { padding:8px 10px; border-radius:10px; }
.stRadio > div[role="radiogroup"] > label:hover { background: rgba(255,255,255,.06); }
.db-chip { color:#a7f3d0; font-size:.8rem; margin:10px 6px 0 6px; display:block; }
.auth-wrap { max-width: 460px; margin: 8vh auto 0 auto; padding: 18px 22px; background: var(--panel); border-radius: 16px; box-shadow: 0 8px 28px rgba(0,0,0,.35); }
.auth-title { text-align:center; color:#f9fafb; font-size:1.6rem; font-weight:900; margin-bottom:6px; }
.auth-sub { text-align:center; color:#93c5fd; font-weight:600; margin-bottom:14px; }
</style>
"""
st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def get_conn():
    return mysql.connect(host=DB_HOST,user=DB_USER,password=DB_PASSWORD,database=DB_NAME,port=DB_PORT,autocommit=True)

def run_query(conn,q,params=None):
    cur=conn.cursor(dictionary=True)
    cur.execute(q,params or ())
    rows=cur.fetchall()
    cur.close()
    return rows

def run_exec(conn,q,params=None):
    cur=conn.cursor()
    cur.execute(q,params or ())
    last=cur.lastrowid
    cur.close()
    return last

if "conn" not in st.session_state:
    try:
        st.session_state.conn=get_conn()
        st.session_state.db_status="Connected"
    except Exception as e:
        st.session_state.conn=None
        st.session_state.db_status=str(e)

if "auth" not in st.session_state:
    st.session_state.auth={"logged_in":False,"user":None}

def render_auth():
    st.markdown(f"<div class='auth-wrap'><div class='auth-title'>Mayoor School Clinic</div><div class='auth-sub'>Secure Access</div></div>", unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,1])
    with c2:
        tabs=st.tabs(["Login","Register"])
        with tabs[0]:
            u=st.text_input("Username",key="login_u")
            p=st.text_input("Password",type="password",key="login_p")
            if st.button("Login",use_container_width=True):
                rows=run_query(st.session_state.conn,"SELECT staff_id,name,role,password_hash,is_active FROM staff WHERE username=%s",(u,))
                if rows and rows[0]["is_active"]==1 and rows[0]["password_hash"]==sha256(p):
                    st.session_state.auth={"logged_in":True,"user":{"staff_id":rows[0]["staff_id"],"name":rows[0]["name"],"role":rows[0]["role"]}}
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        with tabs[1]:
            name=st.text_input("Full Name",key="reg_name")
            contact=st.text_input("Contact",key="reg_contact")
            uname=st.text_input("Username",key="reg_uname")
            pwd=st.text_input("Password",type="password",key="reg_pwd")
            cpwd=st.text_input("Confirm Password",type="password",key="reg_cpwd")
            role_choice=st.selectbox("Role",["nurse","support"])
            if st.button("Create Account",use_container_width=True):
                if pwd!=cpwd:
                    st.error("Passwords do not match")
                else:
                    exists=run_query(st.session_state.conn,"SELECT staff_id FROM staff WHERE username=%s",(uname,))
                    if exists:
                        st.error("Username already taken")
                    else:
                        sid=run_exec(st.session_state.conn,"INSERT INTO staff(name,role,contact,username,password_hash,is_active) VALUES(%s,%s,%s,%s,%s,1)",(name,role_choice,contact,uname,sha256(pwd)))
                        st.session_state.auth={"logged_in":True,"user":{"staff_id":sid,"name":name,"role":role_choice}}
                        st.success("Account created")
                        st.rerun()

conn=st.session_state.get("conn",None)
if not st.session_state.auth["logged_in"]:
    if not conn:
        st.error("Database connection failed. Set credentials in code.")
        st.stop()
    render_auth()
    st.stop()

role=st.session_state.auth["user"]["role"]
uid=st.session_state.auth["user"]["staff_id"]

with st.sidebar:
    st.markdown('<div class="sidebar-brand">Mayoor School Clinic</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-card"><span class="sidebar-pill">{st.session_state.auth["user"]["name"]} ({st.session_state.auth["user"]["role"]})</span></div>', unsafe_allow_html=True)
    nav_labels={"Dashboard":"🏠 Dashboard","Students":"👩‍🎓 Students","Visits":"📝 Visits","Medications":"💊 Medications","Dispense":"📦 Dispense","Teachers":"👩‍🏫 Teachers","Requests":"📮 Requests","Appointments":"📅 Appointments","Notifications":"🔔 Notifications","Reports":"📈 Reports","Staff":"👥 Staff","Logout":"🚪 Logout"}
    order=["Dashboard","Students","Visits","Medications","Dispense","Teachers","Requests","Appointments","Notifications","Reports"]
    if role=="admin":
        order+=["Staff"]
    order+=["Logout"]
    st.markdown('<div class="nav-head">Navigation</div>', unsafe_allow_html=True)
    page_lbl=st.radio("",[nav_labels[k] for k in order],index=0,label_visibility="collapsed")
    page=[k for k,v in nav_labels.items() if v==page_lbl][0]
    st.markdown(f'<span class="db-chip">DB: {st.session_state.get("db_status","-")}</span>', unsafe_allow_html=True)

if page=="Logout":
    st.session_state.auth={"logged_in":False,"user":None}
    st.rerun()

if page=="Dashboard":
    col1,col2,col3,col4=st.columns(4)
    col1.metric("Students",run_query(conn,"SELECT COUNT(*) c FROM students")[0]["c"])
    col2.metric("Medications",run_query(conn,"SELECT COUNT(*) c FROM medications")[0]["c"])
    col3.metric("Visits Today",run_query(conn,"SELECT COUNT(*) c FROM clinic_visits WHERE DATE(visit_date_time)=CURDATE()")[0]["c"])
    col4.metric("Open Requests",run_query(conn,"SELECT COUNT(*) c FROM teacher_requests WHERE status='Pending'")[0]["c"])
    st.subheader("Upcoming Appointments")
    ap=run_query(conn,"SELECT a.appt_id,a.appt_datetime,a.appt_type,a.status,s.name student FROM appointments a JOIN students s ON s.student_id=a.student_id WHERE a.appt_datetime>=NOW() ORDER BY a.appt_datetime LIMIT 50")
    st.dataframe(pd.DataFrame(ap),use_container_width=True)

elif page=="Students":
    st.subheader("Add Student")
    with st.form("f_add_stu"):
        name=st.text_input("Name")
        grade=st.text_input("Grade/Class")
        gender=st.selectbox("Gender",["Male","Female","Other"])
        dob=st.date_input("Date of Birth",value=date(2012,1,1))
        parent=st.text_input("Parent/Guardian")
        contact=st.text_input("Parent Contact")
        address=st.text_input("Address")
        blood=st.text_input("Blood Group")
        allergies=st.text_area("Allergies")
        chronic=st.text_area("Chronic Conditions")
        vacc=st.text_input("Vaccination Status","Up-to-date")
        height=st.number_input("Height (cm)",min_value=0.0,step=0.1)
        weight=st.number_input("Weight (kg)",min_value=0.0,step=0.1)
        bmi=None
        if height>0 and weight>0:
            bmi=round(weight/((height/100)**2),2)
            st.info(f"Calculated BMI: {bmi}")
        if st.form_submit_button("Save"):
            run_exec(conn,"INSERT INTO students(name,grade_class,gender,date_of_birth,parent_name,parent_contact,address,blood_group,allergies,chronic_conditions,vaccination_status,height_cm,weight_kg,bmi) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,grade,gender,dob,parent,contact,address,blood,allergies,chronic,vacc,height,weight,bmi))
            st.success("Saved")
    st.subheader("Search / List Students")
    q=st.text_input("Search by name or class or contact")
    if st.button("Search") or q:
        rows=run_query(conn,"SELECT * FROM students WHERE name LIKE %s OR grade_class LIKE %s OR parent_contact LIKE %s",(f"%{q}%",f"%{q}%",f"%{q}%"))
    else:
        rows=run_query(conn,"SELECT * FROM students ORDER BY student_id DESC LIMIT 100")
    df=pd.DataFrame(rows)
    st.dataframe(df,use_container_width=True)
    if not df.empty:
        st.download_button("Download CSV",df.to_csv(index=False).encode(),"students.csv","text/csv")

elif page=="Visits":
    st.subheader("Log Clinic Visit")
    stu=run_query(conn,"SELECT student_id,name FROM students ORDER BY name")
    tch=run_query(conn,"SELECT teacher_id,name FROM teachers ORDER BY name")
    stu_map={f"{r['name']} (#{r['student_id']})":r['student_id'] for r in stu}
    tch_map={"None":None}
    tch_map.update({f"{r['name']} (#{r['teacher_id']})":r['teacher_id'] for r in tch})
    s_sel=st.selectbox("Student",list(stu_map.keys()) if stu_map else ["No students"])
    t_sel=st.selectbox("Reported By (Teacher)",list(tch_map.keys()))
    vdate=st.date_input("Visit Date",value=date.today())
    vtime=st.time_input("Visit Time",value=time(9,0))
    symptoms=st.text_area("Symptoms")
    diagnosis=st.text_input("Diagnosis")
    treatment=st.text_area("Treatment/Medication Given")
    notes=st.text_area("Notes")
    referred=st.checkbox("Referred Out")
    if st.button("Save Visit"):
        if stu_map:
            dt=datetime.combine(vdate,vtime)
            run_exec(conn,"INSERT INTO clinic_visits(student_id,visit_date_time,reported_by,symptoms,diagnosis,treatment_given,notes,referred_out) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(stu_map[s_sel],dt,tch_map[t_sel],symptoms,diagnosis,treatment,notes,1 if referred else 0))
            st.success("Saved")
    st.subheader("Recent Visits")
    vs=run_query(conn,"SELECT v.visit_id,v.visit_date_time,s.name student,v.symptoms,v.diagnosis,v.treatment_given,v.referred_out FROM clinic_visits v JOIN students s ON s.student_id=v.student_id ORDER BY v.visit_id DESC LIMIT 100")
    d=pd.DataFrame(vs)
    st.dataframe(d,use_container_width=True)
    if not d.empty:
        st.download_button("Download CSV",d.to_csv(index=False).encode(),"visits.csv","text/csv")

elif page=="Medications":
    st.subheader("Add / Update Medications")
    with st.form("f_add_med"):
        mname=st.text_input("Name")
        form=st.selectbox("Dosage Form",["tablet","syrup","ointment","other"])
        stock=st.number_input("Unit Stock",value=0,step=1)
        exp=st.date_input("Expiry Date",value=date.today()+timedelta(days=365))
        sup=st.text_input("Supplier")
        if st.form_submit_button("Save"):
            run_exec(conn,"INSERT INTO medications(name,dosage_form,unit_stock,expiry_date,supplier) VALUES(%s,%s,%s,%s,%s)",(mname,form,stock,exp,sup))
            st.success("Saved")
    meds=run_query(conn,"SELECT * FROM medications ORDER BY name")
    md=pd.DataFrame(meds)
    st.dataframe(md,use_container_width=True)
    if not md.empty:
        st.download_button("Download CSV",md.to_csv(index=False).encode(),"medications.csv","text/csv")

elif page=="Dispense":
    st.subheader("Dispense Medicine")
    meds=run_query(conn,"SELECT med_id,name,unit_stock FROM medications ORDER BY name")
    stu=run_query(conn,"SELECT student_id,name FROM students ORDER BY name")
    m_map={f"{r['name']} (stock {r['unit_stock']})":(r['med_id'],r['unit_stock']) for r in meds}
    s_map={f"{r['name']} (#{r['student_id']})":r['student_id'] for r in stu}
    m_sel=st.selectbox("Medicine",list(m_map.keys()) if m_map else ["No medicines"])
    s_sel=st.selectbox("Student",list(s_map.keys()) if s_map else ["No students"])
    qty=st.number_input("Quantity",value=1,step=1,min_value=1)
    dte=st.date_input("Date",value=date.today())
    tme=st.time_input("Time",value=datetime.now().time())
    if st.button("Dispense"):
        if m_map and s_map:
            mid,stk=m_map[m_sel]
            if qty<=stk:
                dt=datetime.combine(dte,tme)
                run_exec(conn,"INSERT INTO medication_dispense(med_id,student_id,date_dispensed,quantity,administered_by) VALUES(%s,%s,%s,%s,%s)",(mid,s_map[s_sel],dt,qty,uid))
                run_exec(conn,"UPDATE medications SET unit_stock=unit_stock-%s WHERE med_id=%s",(qty,mid))
                st.success("Dispensed")
            else:
                st.error("Not enough stock")
    st.subheader("Dispense Log")
    log=run_query(conn,"SELECT d.dispense_id,d.date_dispensed,m.name med,s.name student,d.quantity FROM medication_dispense d JOIN medications m ON m.med_id=d.med_id JOIN students s ON s.student_id=d.student_id ORDER BY d.dispense_id DESC LIMIT 100")
    ld=pd.DataFrame(log)
    st.dataframe(ld,use_container_width=True)
    if not ld.empty:
        st.download_button("Download CSV",ld.to_csv(index=False).encode(),"dispense_log.csv","text/csv")

elif page=="Teachers":
    st.subheader("Manage Teachers")
    with st.form("f_add_teacher"):
        tname=st.text_input("Name")
        subj=st.text_input("Subject")
        contact=st.text_input("Contact")
        if st.form_submit_button("Save"):
            run_exec(conn,"INSERT INTO teachers(name,subject,contact) VALUES(%s,%s,%s)",(tname,subj,contact))
            st.success("Saved")
    tchs=run_query(conn,"SELECT * FROM teachers ORDER BY name")
    st.dataframe(pd.DataFrame(tchs),use_container_width=True)

elif page=="Requests":
    st.subheader("Teacher Requests")
    stu=run_query(conn,"SELECT student_id,name FROM students ORDER BY name")
    tch=run_query(conn,"SELECT teacher_id,name FROM teachers ORDER BY name")
    s_map={f"{r['name']} (#{r['student_id']})":r['student_id'] for r in stu}
    t_map={f"{r['name']} (#{r['teacher_id']})":r['teacher_id'] for r in tch}
    s_sel=st.selectbox("Student",list(s_map.keys()) if s_map else ["No students"])
    t_sel=st.selectbox("Teacher",list(t_map.keys()) if t_map else ["No teachers"])
    reason=st.text_input("Reason")
    dte=st.date_input("Request Date",value=date.today())
    tme=st.time_input("Request Time",value=datetime.now().time())
    if st.button("Create Request"):
        if s_map and t_map:
            dt=datetime.combine(dte,tme)
            run_exec(conn,"INSERT INTO teacher_requests(teacher_id,student_id,request_date,reason,status) VALUES(%s,%s,%s,%s,'Pending')",(t_map[t_sel],s_map[s_sel],dt,reason))
            st.success("Saved")
    st.subheader("Open Requests")
    req=run_query(conn,"SELECT r.req_id,r.request_date,r.reason,r.status,s.name student,t.name teacher FROM teacher_requests r JOIN students s ON s.student_id=r.student_id JOIN teachers t ON t.teacher_id=r.teacher_id WHERE r.status='Pending' ORDER BY r.request_date")
    df=pd.DataFrame(req)
    st.dataframe(df,use_container_width=True)
    rid=st.number_input("Request ID to mark Completed",value=0,step=1)
    if st.button("Mark Completed"):
        if rid>0:
            run_exec(conn,"UPDATE teacher_requests SET status='Completed' WHERE req_id=%s",(int(rid),))
            st.success("Updated")

elif page=="Appointments":
    st.subheader("Appointments")
    stu=run_query(conn,"SELECT student_id,name FROM students ORDER BY name")
    s_map={f"{r['name']} (#{r['student_id']})":r['student_id'] for r in stu}
    s_sel=st.selectbox("Student",list(s_map.keys()) if s_map else ["No students"])
    dte=st.date_input("Date",value=date.today())
    tme=st.time_input("Time",value=time(10,0))
    atype=st.selectbox("Type",["vision","dental","physical","general"])
    tr=run_query(conn,"SELECT teacher_id,name FROM teachers ORDER BY name")
    tr_map={"None":None}
    tr_map.update({f"{r['name']} (#{r['teacher_id']})":r['teacher_id'] for r in tr})
    t_sel=st.selectbox("Requested By Teacher",list(tr_map.keys()))
    if st.button("Create Appointment"):
        if s_map:
            dt=datetime.combine(dte,tme)
            run_exec(conn,"INSERT INTO appointments(student_id,appt_datetime,appt_type,requested_by_teacher_id,status) VALUES(%s,%s,%s,%s,'Scheduled')",(s_map[s_sel],dt,atype,tr_map[t_sel]))
            st.success("Saved")
    ap=run_query(conn,"SELECT a.appt_id,a.appt_datetime,a.appt_type,a.status,s.name student FROM appointments a JOIN students s ON s.student_id=a.student_id ORDER BY a.appt_datetime DESC LIMIT 100")
    st.dataframe(pd.DataFrame(ap),use_container_width=True)

elif page=="Notifications":
    st.subheader("Parent Notifications")
    vs=run_query(conn,"SELECT v.visit_id, CONCAT(s.name,' | ',DATE_FORMAT(v.visit_date_time,'%Y-%m-%d %H:%i')) txt,s.student_id sid,s.parent_contact pc FROM clinic_visits v JOIN students s ON s.student_id=v.student_id ORDER BY v.visit_id DESC LIMIT 100")
    opts={f"Visit #{r['visit_id']} - {r['txt']}":(r["visit_id"],r["sid"],r["pc"]) for r in vs}
    v_key=list(opts.keys())[0] if opts else None
    v_sel=st.selectbox("Visit",list(opts.keys()) if opts else ["None"])
    method=st.selectbox("Method",["Call","SMS","Email","Note Sent"])
    contact=st.text_input("Contact", value=(opts[v_sel][2] if opts and v_sel in opts else ""))
    message=st.text_input("Message","Student visited clinic.")
    dte=st.date_input("Date",value=date.today())
    tme=st.time_input("Time",value=datetime.now().time())
    if st.button("Log Notification"):
        if opts and v_sel in opts:
            dt=datetime.combine(dte,tme)
            visit_id,student_id,_=opts[v_sel]
            run_exec(conn,"INSERT INTO parent_notifications(student_id,visit_id,method,contact,message,notified_at) VALUES(%s,%s,%s,%s,%s,%s)",(student_id,visit_id,method,contact,message,dt))
            st.success("Logged")
    log=run_query(conn,"SELECT n.notif_id,n.notified_at,s.name student,n.method,n.contact,n.message FROM parent_notifications n JOIN students s ON s.student_id=n.student_id ORDER BY n.notif_id DESC LIMIT 100")
    st.dataframe(pd.DataFrame(log),use_container_width=True)

elif page=="Reports":
    st.subheader("Reports")
    c1,c2=st.columns(2)
    start=c1.date_input("Start",value=date.today()-timedelta(days=30))
    end=c2.date_input("End",value=date.today())
    if st.button("Generate"):
        v=run_query(conn,"SELECT DATE(visit_date_time) d, COUNT(*) c FROM clinic_visits WHERE DATE(visit_date_time) BETWEEN %s AND %s GROUP BY DATE(visit_date_time) ORDER BY d",(start,end))
        df_v=pd.DataFrame(v)
        st.write("Visits per Day")
        st.dataframe(df_v,use_container_width=True)
        vc=run_query(conn,"SELECT diagnosis, COUNT(*) c FROM clinic_visits WHERE DATE(visit_date_time) BETWEEN %s AND %s GROUP BY diagnosis ORDER BY c DESC",(start,end))
        st.write("Common Diagnoses")
        st.dataframe(pd.DataFrame(vc),use_container_width=True)
        mu=run_query(conn,"SELECT m.name, SUM(d.quantity) qty FROM medication_dispense d JOIN medications m ON m.med_id=d.med_id WHERE DATE(d.date_dispensed) BETWEEN %s AND %s GROUP BY m.name ORDER BY qty DESC",(start,end))
        st.write("Medicine Usage")
        st.dataframe(pd.DataFrame(mu),use_container_width=True)
        vlist=run_query(conn,"SELECT v.visit_id,v.visit_date_time,s.name student,v.symptoms,v.diagnosis,v.treatment_given FROM clinic_visits v JOIN students s ON s.student_id=v.student_id WHERE DATE(v.visit_date_time) BETWEEN %s AND %s ORDER BY v.visit_id DESC",(start,end))
        csv=pd.DataFrame(vlist).to_csv(index=False).encode()
        st.download_button("Download Visit Details CSV",csv,"visit_details.csv","text/csv")

elif page=="Staff":
    st.subheader("Staff")
    if role!="admin":
        st.info("Only admin can manage staff.")
    else:
        with st.form("f_add_staff"):
            name=st.text_input("Name")
            srole=st.selectbox("Role",["nurse","admin","support"])
            contact=st.text_input("Contact")
            uname=st.text_input("Username")
            pwd=st.text_input("Password",type="password")
            if st.form_submit_button("Create"):
                run_exec(conn,"INSERT INTO staff(name,role,contact,username,password_hash,is_active) VALUES(%s,%s,%s,%s,%s,1)",(name,srole,contact,uname,sha256(pwd)))
                st.success("Saved")
        st.subheader("Staff List")
        st.dataframe(pd.DataFrame(run_query(conn,"SELECT staff_id,name,role,contact,username,is_active FROM staff ORDER BY staff_id DESC")),use_container_width=True)
