import streamlit as st
import easyocr
import cv2
import numpy as np
import pandas as pd
import re
from streamlit_option_menu import option_menu
import psycopg2
from PIL import Image



conn = psycopg2.connect(host="localhost", 
                        user="postgres", 
                        password="1234", 
                        port=5432, 
                        database="bizcard")
db = conn.cursor()

reader = easyocr.Reader(['en'])

st.set_page_config(page_title="BizcardX", page_icon="🎫",layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .sidebar .sidebar-content {
        width: 300px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(f""" <style>.stApp {{
                    background: url('https://mcdn.wallpapersafari.com/medium/51/43/YZuGTL.jpg');   
                    background-size: cover}}
                 </style>""",unsafe_allow_html=True)

title = '<p style="font-family:roboto; color:red; font-size: 48px;">BizcardX Application</p>'
st.markdown(title, unsafe_allow_html=True)



def data_extrac(extract):
    for i in range(len(extract)):
        extract[i] = extract[i].rstrip(' ')
        extract[i] = extract[i].rstrip(',')
    result = ' '.join(extract)

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    website_pattern = r'[www|WWW|wwW]+[\.|\s]+[a-zA-Z0-9]+[\.|\][a-zA-Z]+'
    phone_pattern = r'(?:\+)?\d{3}-\d{3}-\d{4}'
    phone_pattern2 = r"(?:\+91[-\s])?(?:\d{4,5}[-\s])?\d{3}[-\s]?\d{4}"
    name_pattern = r'[A-Za-z]+\b'
    designation_pattern = r'\b[A-Za-z\s]+\b'
    address_pattern = r'\d+\s[A-Za-z\s,]+'
    pincode_pattern = r'\b\d{6}\b'

    name = designation = company = email = website = primary = secondary = address = pincode = None

    try:
        email = re.findall(email_pattern, result)[0]
        result = result.replace(email, '')
        email = email.lower()
    except IndexError:
        email = None
    try:
        website = re.findall(website_pattern, result)[0]
        result = result.replace(website, '')
        website = re.sub('[WWW|www|wwW]+ ', 'www.', website)
        website = website.lower()
    except IndexError:
        webstie = None
    phone = re.findall(phone_pattern, result)
    if len(phone) == 0:
        phone = re.findall(phone_pattern2, result)
    primary = None
    secondary = None
    if len(phone) > 1:
        primary = phone[0]
        secondary = phone[1]
        for i in range(len(phone)):
            result = result.replace(phone[i], '')
    elif len(phone) == 1:
        primary = phone[0]
        result = result.replace(phone[0], '')

    try:
        pincode = int(re.findall(pincode_pattern, result)[0])
        result = result.replace(str(pincode), '')
    except:
        pincode = 0
    # name = re.findall(name_pattern, result)[0]
    name = extract[0]
    result = result.replace(name, '')
    # designation = re.findall(designation_pattern, result)[0]
    designation = extract[1]
    result = result.replace(designation, '')
    address = ''.join(re.findall(address_pattern, result))
    result = result.replace(address, '')
    company = extract[-1]
    result = result.replace(company, '')

    # print('Email:', email)
    # print('Website:', website)
    # print('Phone:', phone)
    # print('Primary:', primary)
    # print('Secondary:', secondary)
    # print('Name:', name)
    # print('Designation:', designation)
    # print('Address:', address)
    # print('Pincode:', pincode)
    # print('company:', company)
    # print('remaining:', result)

    info = [name, designation, company, email, website, primary, secondary, address, pincode, result]
    return (info)

with st.sidebar:
    
    selected = option_menu(
        menu_title="Menu",  # required
        options=["Home","---","Upload", "View or Modify", "---", "About the app"],  # required
        icons=["house","", "cloud-upload","search",  "", "envelope"],  # optional
        #menu_icon="person-vcard",  # optional
        default_index=0,  # optional
        styles={"nav-link": {"--hover-color": "#fea172"}},
        orientation="vertical",
    )
    
if selected == 'Home':
    st.subheader("Welcome to the BizCard Application! ")
    st.markdown("__<p> This application is an useful tool for businesses and individuals who can now manage business card information efficiently in one place. </p>__",unsafe_allow_html=True)

elif selected == 'Upload':
    uploaded_file = st.file_uploader("Upload a business card image file...",type=["jpg", "jpeg", "png"])
    if uploaded_file != None:
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        col1, col2, col3 = st.columns([2,1,2])
        with col3:
            st.image(image)
        with col1:
            result = reader.readtext(image, detail=0)
            info = data_extrac(result)
            #st.table(pd.Series(info, index=['Name', 'Designation', 'Company', 'Email ID', 'Website', 'Primary Contact', 'Secondary Contact', 'Address', 'Pincode', 'Other']))
            ls_name = st.text_input('Name:',info[0])
            ls_desig = st.text_input('Designation:', info[1])
            ls_Com = st.text_input('Company:', info[2])
            ls_mail = st.text_input('Email ID:', info[3])
            ls_url = st.text_input('Website:', info[4])
            ls_m1 = st.text_input('Primary Contact:', info[5])
            ls_m2 = st.text_input('Secondary Contact:', info[6])
            ls_add = st.text_input('Address:', info[7])
            ls_pin = st.number_input('Pincode:', info[8])
            a = st.button("Upload  & Extract")
            if a:
                db.execute(
                    "CREATE TABLE IF NOT EXISTS business_cards (name VARCHAR(255), designation VARCHAR(255), "
                    "company VARCHAR(255), email VARCHAR(255), website VARCHAR(255), primary_no VARCHAR(255), "
                    "secondary_no VARCHAR(255), address VARCHAR(255), pincode int, image bytea)")
                query = "INSERT INTO business_cards (name, designation, company, email, website, primary_no, secondary_no, " \
                      "address, pincode, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (ls_name, ls_desig, ls_Com, ls_mail, ls_url, ls_m1, ls_m2, ls_add, ls_pin, psycopg2.Binary(image))
                db.execute(query, val)
                conn.commit()
                st.success('Business card details stored successfully in database', icon="✅")
elif selected == 'View or Modify':
    col1, col2, col3 = st.columns([2,2,4])
    with col1:
        db.execute('select name from business_cards')
        y = db.fetchall()
        contact = [x[0] for x in y]
        contact.sort()
        selected_contact = st.selectbox('Name',contact)
    with col2:
        mode_list = ['View','Modify','Delete']
        selected_mode = st.selectbox('Mode',mode_list,index = 0)

    if selected_mode == 'View':
        col5,col6 = st.columns(2)
        with col5:
            db.execute(f"select name, designation, company, email, website, primary_no, secondary_no, "
                         f"address, pincode from business_cards where name = '{selected_contact}'")
            y = db.fetchall()
            st.table(pd.Series(y[0],index=['Name', 'Designation', 'Company', 'Email ID', 'Website', 'Primary Contact', 'Secondary Contact', 'Address', 'Pincode'],name='Card Info'))

    elif selected_mode == 'Modify':
        db.execute(f"select name, designation, company, email, website, primary_no, secondary_no, "
                     f"address, pincode from business_cards where name = '{selected_contact}'")
        info = db.fetchone()
        col5, col6 = st.columns(2)
        with col5:
            ls_name = st.text_input('Name:', info[0])
            ls_desig = st.text_input('Designation:', info[1])
            ls_Com = st.text_input('Company:', info[2])
            ls_mail = st.text_input('Email ID:', info[3])
            ls_url = st.text_input('Website:', info[4])
            ls_m1 = st.text_input('Primary Contact:', info[5])
            ls_m2 = st.text_input('Secondary Contact:', info[6])
            ls_add = st.text_input('Address:', info[7])
            ls_pin = st.number_input('Pincode:', info[8])
        a = st.button("Update")
        if a:
            query = f"update business_cards set name = %s, designation = %s, company = %s, email = %s, website = %s, " \
                    f"primary_no = %s, secondary_no = %s, address = %s, pincode = %s where name = '{selected_contact}'"
            val = (ls_name, ls_desig, ls_Com, ls_mail, ls_url, ls_m1, ls_m2, ls_add, ls_pin)
            db.execute(query, val)
            conn.commit()
            st.success('Business card details are updated successfully in database', icon="✅")

    elif selected_mode == 'Delete':
        st.markdown(
            f'__<p style="text-align:left; font-size: 20px; color: #FAA026">You are trying to remove {selected_contact} '
            f'contact from database.</P>__',
            unsafe_allow_html=True)
        warning_content = """
            **Warning:**
            This action will permanently delete the contact from the database and cannot be recovered. 
            Please review and confirm..
        """
        st.warning(warning_content)
        confirm = st.button('Confirm')
        if confirm:
            query = f"DELETE FROM business_cards where name = '{selected_contact}'"
            db.execute(query)
            conn.commit()
            st.success('Contact removed successfully from database', icon="✅")
elif selected == 'About the app':
    st.markdown('__<p style="text-align:left; font-size: 25px; color: red">About BizCard Application</P>__',
                unsafe_allow_html=True)
    st.write("The final application has a simple and intuitive user interface that guides users through the process of uploading the business card image and extracting its information."
             "The extracted information gets displayed in a clean and organized manner, and users can able to easily add it to the database with the click of a button.")

    