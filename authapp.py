import streamlit as st
import random
import string
import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import re
import firebase_admin
from firebase_admin import credentials, firestore
import bcrypt
from dotenv import load_dotenv
import os
import uuid
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Firebase
if not firebase_admin._apps:
    firebase_credentials = {
        "type": "service_account",
        "project_id": "xdtestdata",
        "private_key_id": "7611cb34ba7bd659e6048bac65781a15febff517",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCQN02Kw3G7sneM\nKuadKZCjpDgn6m+ZiujRz8kPQRMWFwpWG+U/7QNnlU4Yx2Jcw3rUxcbBzGUlSnQZ\n0M74FXs0zBBVobCZKRVTGRm4ooG7/sNccrXONjXHe23I4Bmi3ZvV9xqkI/TRHOzl\nlHvygrN+kWayEhYpt3RSckSBOpe7erQpuTPjNmWDd02G+346GhNfA6nK8jaYmslD\nGI5wIim3QEqiEMW20xIYEtVSQnWN9YNIh0V4gJOZfjr+oiYaWcH2QsWB3gwt9ryz\nyseAy4EaUX+m0VBRnxc/H0nTCl1vdrGpq2CVV5v3nPAp+Ls9KfKtlEfpjwQLeXvn\nQFCE9hWzAgMBAAECggEAAUBBj3EXlPm82L3shzN7mjfL9uitNCdE0sEbLOMzH69u\newW97NqI+4aLiWJ9Y3GcqKjYiwjTXcnyDOFHUlaZXYFhqOSArCtzkGd41iWuu2s/\n1Zb3JcVJnSPgdWwgPM3wUqBUnlTjhEbcdTdfBeEFXpUzT1shzxXUz/xGxNo1w74O\n6RG22iZhTK2d2uPU7Uys+Ty8G1dQ83ND9MKVriDLgykC84gaa+JY4irBcCMAbbUB\nOEz3mpAd+D++4ioLKSExOkvOavM5c9FZIa92Ed9kmbdWeTOFCJXZcWSndU3ssJjW\nl6PDHsRdvJPs++nja2hnn0NdfsgIEjl2TDuNnVEy9QKBgQDHTof1b0Vmpr6grAq7\nibFX4S3WXPVRUOH7HpLk36DOU3GKtSURz+17hLQCh4SVRz8jLSesM9yIy8Q7469J\nP+aifOx4a4a5WcRpt+7/FDTdAntK46z4S7hq4LGK+PfzvD1MI7TrkimoXXCTc7yt\nLF4ftLlS64SyPN/G9T2Mb/w6fwKBgQC5PRQCZeCVA3xRqjkeCt/w5GlfN09lRdK9\neELRi8nLFh5na6hnIVDdt8hfj8dNm2Z6iZ1Ve7Q9EsB3YMd8onPc1WjkgBlzO2go\no8gUYDjDkMWvOnoFkcY9CJnxThQ3eyXytGjxgmXJv7NtOG5W4dFwgRRBQOYi3Bg7\nuZB04tnCzQKBgAS0Yts1TDMXHorWZM52epwzcYyM1zGbMipmV1tVuAsGxzhZ/E0G\nVnnC8SjaIBQSAXiIGVakRsFn5fLv9fRJsN0HC+Hvz9dSOiOwttCInpLU+yoSY8Pc\nrbbAJRC9vcSgHeZNNXkWEyupQP4KDlscIACpmHJPous+Kp4crd5ByndrAoGAJp2C\n9FUEkkvduLCBo6+kq3USOlUvae86VWEinMhFUt7Ti7+3pXgegXn0fWddpuIEZPsX\nH2DgW/LyyHAWZfb/rEOY0DmcFJeHySELbqP4cVxWuYa5NTwEVWjbnqAmOsKjUIsn\nbWE/kuUxpE0lQ1tj684cyNWcpBu5uYmfgZ5gwukCgYEArrpcdbDw1qoYwQRXEL7Z\nRECDjUy2uFGqLBX83VLwiSCO93M4d4uwkr7VUT6pGCnyctSO4YVFSUaRC6imWoFx\nsKIRuUp6g1GXjAkWfumvWYEg8q1ADfweNB4+B0wJIz/TdIUN+g4+0wi5Uvid8W05\n20GsoHMzfPdk6p4xXrW7U+U=\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-fbsvc@xdtestdata.iam.gserviceaccount.com",
        "client_id": "112099506661189917660",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40xdtestdata.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.set_page_config(page_title="CRM 3.3 Staging Test Data Creation Tools")

# Load external CSS
with open("style.css", "r") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# User Authentication Functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def is_user_admin(username):
    users_ref = db.collection('users')
    user_docs = users_ref.where('username', '==', username).get()
    if user_docs:
        user_data = user_docs[0].to_dict()
        return user_data.get('is_admin', False)
    return False

def register_user(username, password, is_admin=False):
    if not st.session_state.get('authenticated') or not is_user_admin(st.session_state.get('username')):
        return False, "Only admins can register new users."
    
    users_ref = db.collection('users')
    if users_ref.where('username', '==', username).get():
        return False, "Username already exists."
    
    # Make first user an admin
    existing_users = users_ref.get()
    if not existing_users:
        is_admin = True
    
    hashed_password = hash_password(password)
    user_id = str(uuid.uuid4())
    users_ref.document(user_id).set({
        'username': username,
        'password': hashed_password,
        'is_admin': is_admin
    })
    return True, f"Registration successful! User '{username}' created{' as admin' if is_admin else ''}."

def authenticate_user(username, password):
    users_ref = db.collection('users')
    user_docs = users_ref.where('username', '==', username).get()
    if not user_docs:
        return False, "User not found."
    user_data = user_docs[0].to_dict()
    if verify_password(password, user_data['password']):
        return True, user_data['username']
    return False, "Incorrect password."

# Decorator for access control
def restrict(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'authenticated' not in st.session_state or not st.session_state.authenticated:
            st.error("Please log in to access the application.")
            return
        username = st.session_state.get('username')
        users_ref = db.collection('users')
        if not users_ref.where('username', '==', username).get():
            st.error("User not found. Please log in again.")
            st.session_state.clear()
            return
        return func(*args, **kwargs)
    return wrapper

# Authentication UI
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.markdown('<div class="app-container">', unsafe_allow_html=True)
    st.markdown('<div class="header">CRM 3.3 Staging Test Data Creation Tools</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Please log in to continue.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Login</div>', unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_password")
        submit = st.form_submit_button("Login", use_container_width=True)
        if submit:
            success, message = authenticate_user(username.strip(), password.strip())
            if success:
                st.session_state.authenticated = True
                st.session_state.username = message
                st.rerun()
            else:
                st.error(message)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    is_admin = is_user_admin(st.session_state.username)
    
    if is_admin:
        st.markdown('<div class="app-container">', unsafe_allow_html=True)
        st.markdown('<div class="header">CRM 3.3 Staging Test Data Creation Tools</div>', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Admin: Register a new user.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Register New User</div>', unsafe_allow_html=True)
        with st.form("register_form"):
            new_username = st.text_input("Username", placeholder="Choose a username", key="register_username")
            new_password = st.text_input("Password", placeholder="Choose a password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", placeholder="Confirm your password", type="password", key="confirm_password")
            is_admin_user = st.checkbox("Grant admin privileges", key="is_admin_user")
            submit = st.form_submit_button("Register", use_container_width=True)
            if submit:
                if not new_username.strip() or not new_password.strip():
                    st.error("Username and password cannot be empty.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    success, message = register_user(new_username.strip(), new_password.strip(), is_admin=is_admin_user)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Application
    @restrict
    def main_app():
        if "first_load" not in st.session_state:
            st.session_state.first_load = True
            with st.spinner("## Developed by Deciman Julius"):
                import time
                time.sleep(2)
        else:
            st.session_state.first_load = False

        def format_date_yymmdd(date):
            year = str(date.year)[-2:]
            month = str(date.month).zfill(2)
            day = str(date.day).zfill(2)
            return f"{year}{month}{day}"

        def random_string(length, chars=string.ascii_letters + string.digits):
            return ''.join(random.choice(chars) for _ in range(length))

        def random_char():
            chars = string.ascii_letters
            return random.choice(chars)

        def random_name():
            names = [
                'John', 'Jane', 'Alex', 'Emma', 'Michael', 'Sarah', 'David', 'Lisa', 'Chris', 'Anna', 'James', 'Emily', 'Robert', 'Sophie', 'William', 'Olivia', 'Thomas', 'Grace', 'Daniel', 'Chloe', 'Matthew', 'Isabella', 'Andrew', 'Mia', 'Steven', 'Lily', 'Mark', 'Hannah', 'Paul', 'Julia', 'Richard', 'Amelia', 'Charles', 'Ella', 'George', 'Ava', 'Joseph', 'Charlotte', 'Edward', 'Lucy', 'Benjamin', 'Zoe', 'Samuel', 'Abigail', 'Henry', 'Sophia', 'Jack', 'Madison', 'Luke', 'Natalie', 'Ryan', 'Evelyn', 'Ethan', 'Victoria', 'Nathan', 'Isabelle', 'Adam', 'Lillian', 'Joshua', 'Scarlett', 'Peter', 'Aria', 'Jacob', 'Samantha', 'Isaac', 'Ruby', 'Liam', 'Gabriella', 'Noah', 'Harper', 'Logan', 'Avery', 'Elijah', 'Mila', 'Mason', 'Sofia', 'Caleb', 'Eleanor', 'Owen', 'Audrey', 'Dylan', 'Claire', 'Lucas', 'Violet', 'Gabriel', 'Hazel', 'Julian', 'Penelope', 'Levi', 'Stella', 'Carter', 'Layla', 'Wyatt', 'Aurora', 'Connor', 'Savannah', 'Evan', 'Brooklyn', 'Dominic', 'Addison', 'Hunter', 'Paisley', 'Nicholas', 'Aiden', 'Zachary', 'Aubrey', 'Tyler', 'Skylar', 'Brandon', 'Mackenzie', 'Jonathan', 'Leah', 'Christian', 'Lydia', 'Austin', 'Kayla', 'Colin', 'Morgan', 'Cameron', 'Hailey', 'Patrick', 'Sadie', 'Ian', 'Allison', 'Eric', 'Madelyn', 'Timothy', 'Naomi', 'Kevin', 'Autumn', 'Sean', 'Jocelyn', 'Brian', 'Jasmine', 'Justin', 'Valentina', 'Jordan', 'Katherine', 'Kyle', 'Esme', 'Aaron', 'Delilah', 'Brayden', 'Norah', 'Vincent', 'Faith', 'Tristan', 'Lauren', 'Xavier', 'Ivy', 'Devin', 'Lila', 'Elliot', 'Rose', 'Finn', 'Peyton', 'Gavin', 'Jade', 'Hayden', 'Hadley', 'Joel', 'Ember', 'Miles', 'Elise', 'Parker', 'Piper', 'Roman', 'Aria', 'Shane', 'Celeste', 'Tucker', 'Freya', 'Victor', 'June', 'Wesley', 'Marissa', 'Adrian', 'Brianna', 'Ashton', 'Tessa', 'Blake', 'Kaitlyn', 'Clayton', 'Giselle', 'Cody', 'Maeve', 'Damian', 'Iris', 'Declan', 'Juliana', 'Derek', 'Serena', 'Ezra', 'Angelina', 'Felix', 'Clara', 'Garrett', 'Adeline', 'Grayson', 'Beatrice', 'Harrison', 'Daisy', 'Hudson', 'Evangeline', 'Jace', 'Opal', 'Jasper', 'Lola', 'Jensen', 'Willow', 'Knox', 'Mabel', 'Landon', 'Esther', 'Leo', 'Cora', 'Lincoln', 'Lyric', 'Micah', 'Eloise', 'Nolan', 'Amara', 'Preston', 'Rosalie', 'Reid', 'Genevieve', 'Rhett', 'Anastasia', 'Sawyer', 'Blair', 'Silas', 'Sienna', 'Tanner', 'Marley', 'Theo', 'Nadia', 'Tobias', 'Lena', 'Trevor', 'Elsie', 'Vaughn', 'Ramona', 'Walker', 'Olive', 'Weston', 'Gemma', 'Zane', 'Astrid', 'Abel', 'Bryn', 'Alden', 'Carmen', 'Amos', 'Eliza', 'Archer', 'Fern', 'Barrett', 'Greta', 'Beckett', 'Hallie', 'Bennett', 'Ingrid', 'Brock', 'Josie', 'Cade', 'Kiera', 'Callan', 'Lacey', 'Cedric', 'Mira', 'Clark', 'Noelle', 'Colton', 'Poppy', 'Conor', 'Reese', 'Cooper', 'Selena', 'Dane', 'Talia', 'Dante', 'Uma', 'Darius', 'Vera', 'Dillon', 'Wren', 'Drake', 'Yara', 'Elias', 'Zara', 'Emmett', 'Alana', 'Everett', 'Bianca', 'Fabian', 'Cecilia', 'Flynn', 'Daphne', 'Forrest', 'Emery', 'Gideon', 'Fiona', 'Graham', 'Gloria', 'Grant', 'Helen', 'Hank', 'Imogen', 'Holden', 'Juniper', 'Hugo', 'Kinsley', 'Ivan', 'Lara', 'Jett', 'Mina', 'Jonah', 'Nora', 'Judah', 'Ophelia', 'Kane', 'Quinn', 'Keegan', 'Rhea', 'Kieran', 'Sabrina', 'Lance', 'Thea', 'Lennon', 'Vienna', 'Leon', 'Winnie', 'Malcolm', 'Xena', 'Milo', 'Yasmin', 'Neil', 'Zelda', 'Nico', 'Aisha', 'Orion', 'Bria', 'Oscar', 'Celine', 'Otto', 'Dina', 'Percy', 'Elsa', 'Quentin', 'Farah', 'Remy', 'Gia', 'Rory', 'Hana', 'Russell', 'Ida', 'Ryder', 'Jada', 'Soren', 'Kara', 'Spencer', 'Lana', 'Tate', 'Mara', 'Thane', 'Nia', 'Titus', 'Oona', 'Travis', 'Phoebe', 'Troy', 'Roxanne', 'Vance', 'Sasha', 'Walter', 'Tina', 'Warren', 'Uma', 'Wilson', 'Vera', 'Winston', 'Wendy', 'Xander', 'Xena', 'Yusuf', 'Yara', 'Zachariah', 'Zoe', 'Aaron', 'Amaya', 'Alvin', 'Anya', 'Andre', 'Aspen', 'Angelo', 'Belen', 'Arthur', 'Cali', 'Asher', 'Dana', 'Atticus', 'Eden', 'Axl', 'Faye', 'Baxter', 'Gina', 'Beau', 'Haven', 'Benson', 'Indie', 'Bodie', 'Jolie', 'Brady', 'Kaya', 'Brecken', 'Livia', 'Brody', 'Maia', 'Bryce', 'Nadine', 'Cairo', 'Oria', 'Calvin', 'Paloma', 'Camden', 'Qiana', 'Cannon', 'Riva', 'Carson', 'Sana', 'Casper', 'Tara', 'Chandler', 'Ursula', 'Chase', 'Vada', 'Chester', 'Willa', 'Cillian', 'Xyla', 'Clifford', 'Yana', 'Clyde', 'Zaria', 'Cohen', 'Alma', 'Corey', 'Brynlee', 'Cruz', 'Cleo', 'Cyrus', 'Demi', 'Dallas', 'Eira', 'Damon', 'Fiona', 'Dax', 'Gwendolyn', 'Dean', 'Hattie', 'Denver', 'Ila', 'Dexter', 'Jessa', 'Donovan', 'Kendra', 'Drew', 'Lila', 'Duke', 'Mavis', 'Easton', 'Nell', 'Eden', 'Odelia', 'Edison', 'Petra', 'Egan', 'Quincy', 'Eli', 'Raven', 'Ellis', 'Sloan', 'Elvis', 'Tatum', 'Emerson', 'Uma', 'Enzo', 'Vesper', 'Ezra', 'Wendy', 'Finnick', 'Xena', 'Fletcher', 'Yvette', 'Ford', 'Zinnia', 'Franklin', 'Avery', 'Gage', 'Blaire', 'Gareth', 'Callie', 'Gatlin', 'Delphine', 'Grady', 'Elowen', 'Gunnar', 'Frida', 'Hassan', 'Giada', 'Heath', 'Hazel', 'Hector', 'Iona', 'Homer', 'Jana', 'Idris', 'Kallie', 'Ignacio', 'Lark', 'Ira', 'Mae', 'Ismael', 'Nessa', 'Jagger', 'Oona', 'Jairo', 'Pilar', 'Jared', 'Rory', 'Jensen', 'Siena', 'Jett', 'Tia', 'Joaquin', 'Vida', 'Jonas', 'Wynter', 'Jude', 'Xena', 'Kaden', 'Yara', 'Khalil', 'Zoe'
            ]
            return random.choice(names)

        def random_id_number(dob=None):
            dob = dob or random_date_of_birth()
            yymmdd = dob[2:]
            xx = str(random.randint(1, 12)).zfill(2)
            xxxx = str(random.randint(0, 9999)).zfill(4)
            return f"{yymmdd}{xx}{xxxx}"

        def random_date_of_birth():
            end = datetime.date(2007, 4, 25)
            start = datetime.date(1990, 1, 1)
            diff = (end - start).days
            random_days = random.randint(0, diff)
            random_date = start + datetime.timedelta(days=random_days)
            return f"{random_date.year}{random_date.month:02d}{random_date.day:02d}"

        def random_transaction_id():
            letters = string.ascii_uppercase
            digits = string.digits
            return (
                random_string(3, letters) +
                random_string(5, digits) +
                random_string(1, letters)
            )

        def random_customer_id():
            random8 = str(random.randint(0, 99999999)).zfill(8)
            return f"10000{random8}"

        def parse_msisdn_output(xml_output):
            try:
                root = ET.fromstring(xml_output)
                msisdns = []
                for msisdn_elem in root.findall(".//sch:msisdn", namespaces={"sch": "http://oss.huawei.com/webservice/external/services/schema"}):
                    msisdn = msisdn_elem.text
                    if msisdn and msisdn.isdigit() and 10 <= len(msisdn) <= 12:
                        msisdns.append(msisdn)
                return msisdns
            except Exception as e:
                st.error(f"Failed to parse MSISDN XML: {str(e)}")
                return []

        def parse_iccid_imsi_output(sql_output):
            try:
                lines = sql_output.strip().split("\n")
                data = []
                for line in lines:
                    if line.strip():
                        parts = re.split(r'\s+', line.strip())
                        if len(parts) >= 3:
                            iccid, imsi, _ = parts[:3]
                            if iccid.isdigit() and 19 <= len(iccid) <= 20 and imsi.isdigit() and len(imsi) == 15:
                                data.append({"iccid": iccid, "imsi": imsi})
                return data
            except Exception as e:
                st.error(f"Failed to parse ICCID/IMSI output: {str(e)}")
                return []

        def generate_dummy_data(index):
            dob = random_date_of_birth()
            return {
                "accessSessionRequest": {
                    "accessChannel": "10050",
                    "operatorCode": "CSG",
                    "password": "PkzVHH0odLylDCRIPJM+Mw==",
                    "beId": "102",
                    "version": "1",
                    "transactionId": random_transaction_id(),
                    "remoteAddress": ""
                },
                "customerInfo": {
                    "customerId": random_customer_id(),
                    "customerFlag": "1",
                    "customerCode": random_string(8),
                    "idType": "1",
                    "idNumber": random_id_number(dob),
                    "expiryDateofcertificate": "20300101",
                    "title": "21",
                    "firstName": random_name() + random_char() * 2,
                    "middleName": "SemiAutoTest",
                    "lastName": random_char() * 4,
                    "nationality": "1458",
                    "customerLang": "2",
                    "customerLevel": "9",
                    "customerGroup": "0",
                    "race": "1",
                    "occupation": "2",
                    "customerDateofBirth": dob,
                    "customerGender": "1",
                    "maritalStatus": "0",
                    "customerStatus": "A02",
                    "customerAddressInfos": [{
                        "contactType": "3",
                        "address1": "Testing Address",
                        "address2": "CelcomDigi Hub",
                        "address3": "address3",
                        "addressCountry": "1458",
                        "addressProvince": "MYS_14",
                        "overseasProvince": "MYS_14",
                        "addressCity": "c421",
                        "addressPostCode": "02600",
                        "email1": f"dummy{index}@digi.com.my",
                        "smsNo": "60104661007",
                        "info1": "cust1",
                        "info2": "cust2",
                        "info3": "cust3",
                        "info4": "cust4",
                        "info5": "cust5"
                    }],
                    "customerRelationInfos": [{
                        "relaSeq": "1",
                        "relaType": "2",
                        "relaPriority": "1",
                        "relaName1": "REL1",
                        "relaName2": "REL2",
                        "relaName3": "REL3",
                        "relaTel1": "1",
                        "relaTel2": "1",
                        "relaTel3": "1",
                        "relaTel4": "1",
                        "relaEmail": f"rel{index}@digi.com",
                        "relaFax": "1",
                        "beginTimeForBusiDay": "1111",
                        "endTimeForBusiDay": "1111",
                        "beginTimeForWeekend": "1111",
                        "endTimeForWeekend": "1111",
                        "info1": "1",
                        "info2": "1",
                        "info3": "1"
                    }],
                    "corporationInfo": {
                        "corpNumber": "1",
                        "companyName": "COMPANY1",
                        "shortName": "COMP1",
                        "hierarchy": "1",
                        "topParentCustomerId": "1",
                        "parentCustomerId": "1",
                        "businessRegistrationNumber": "1",
                        "expiryDateofBRN": "11111111",
                        "ownershipType": "1",
                        "industrySegment": "1",
                        "businessNature": "201",
                        "phoneNumber": "60104661007",
                        "email": f"corp{index}@digi.com",
                        "fax": "1",
                        "geographicalSpread": "1",
                        "telcoProviders": "1",
                        "sow": "4",
                        "accountValue": "1",
                        "dateofIncorporation": "11111111",
                        "numberofEmployees": "1",
                        "paidupCapital": "1",
                        "salesTurnover": "1",
                        "enterpriseCustomerType": "1",
                        "remark": "CORP_REMARK",
                        "subCustomerList": [{"customerId": "1", "companyName": "SUB1"}],
                        "picInfos": [{
                            "picSeq": "1",
                            "name": "PIC1",
                            "title": "1",
                            "gender": "1",
                            "race": "1",
                            "phoneNumber": "1",
                            "email": f"pic{index}@digi.com",
                            "dateofBirth": "11111111",
                            "isNotificationPerson": "1",
                            "picType": "1",
                            "idType": "15",
                            "idNumber": "1",
                            "nationality": "1458"
                        }],
                        "accountManagerInfo": {
                            "name": "MANAGER1",
                            "phoneNumber": "1",
                            "email": f"manager{index}@digi.com",
                            "salesmanCode": "1",
                            "dealerCode": "R0001-B0001"
                        }
                    },
                    "numOfSubPerCondition": "1",
                    "info1": "info1",
                    "info2": "info2",
                    "info3": "info3",
                    "info4": "info4",
                    "info5": "info5"
                },
                "newAcctSubscriberInfos": [{
                    "accountInfo": {
                        "accountId": "4000011111",
                        "customerId": random_customer_id(),
                        "accountCode": "1",
                        "billcycleType": "04",
                        "title": "3",
                        "accountName": f"TEST_ACCOUNT_{index}",
                        "converge_flag": "",
                        "billLanguage": "2",
                        "initialCreditLimit": "10000",
                        "status": "0",
                        "creditLimitNotifyPercentages": ["4", "7"],
                        "acla": "0",
                        "noDunningFlag": "0",
                        "loyaltyCardNo": "1234567",
                        "creditTerm": "1",
                        "isAutoReload": "false",
                        "email": f"account{index}@digi.com.my",
                        "isPaymentResponsible": "true",
                        "addressInfo": [{
                            "contactType": "4",
                            "address1": "Testing Address",
                            "address2": "CelcomDigi Hub",
                            "address3": "address3",
                            "addressCountry": "1458",
                            "addressProvince": "MYS_14",
                            "overseasProvince": "MYS_14",
                            "addressCity": "c421",
                            "addressPostCode": "02600",
                            "email1": f"account{index}@digi.com.my",
                            "smsNo": "60104661007",
                            "info1": "addressinfo1",
                            "info2": "addressinfo2",
                            "info3": "addressinfo3",
                            "info4": "addressinfo4",
                            "info5": "addressinfo5"
                        }],
                        "paymentModeInfo": {
                            "paymentId": "1",
                            "paymentMode": "CASH",
                            "cardType": "1",
                            "ownerName": "OWNER1",
                            "bankCode": "CITIBANK",
                            "bankAcctNo": random_string(32) + "=",
                            "ownershipType": "1",
                            "bankIssuer": "CITIBANK",
                            "cardExpDate": "20330101"
                        },
                        "info1": "acctinfo1",
                        "info2": "60104661007",
                        "info3": "acctinfo3",
                        "info4": "acctinfo4",
                        "info5": "acctinfo5"
                    },
                    "billMediumInfos": [{
                        "billMediumId": "1003",
                        "orderedSeqId": "1"
                    }],
                    "newSubscriberInfos": {
                        "subscriberCountSeq": str(index),
                        "subscriberInfo": {
                            "subscriberId": "1",
                            "customerId": random_customer_id(),
                            "paidFlag": "",
                            "subscriberType": "1",
                            "msisdn": "",
                            "imsi": "",
                            "iccid": "",
                            "imei": "2",
                            "subscriberLanguage": "2",
                            "suspensionResumeReason": "1",
                            "subscriberSegment": "4",
                            "companyName": "compan1",
                            "companyIndustry": "20",
                            "businessNature": "202",
                            "corporateName": "corpor5",
                            "userName": "userName",
                            "subscriberStatus": "B01",
                            "createDate": "11111111111111",
                            "effectiveDate": "11111111111111",
                            "expiryDate": "11111111111111",
                            "latestActivationDate": "11111111111111",
                            "activeDate": "11111111111111",
                            "defaultAcctId": f"40000{random_string(7)}",
                            "telecomType": "",
                            "finalCLQuota": "123",
                            "tempCLQuota": "456",
                            "isUseOverPayment": "1",
                            "creditLimitNotifyPercentages": ["5"],
                            "smsNotifySettingInfos": [{
                                "eventType": "6",
                                "openFlag": "true"
                            }],
                            "tenure": "30",
                            "otherRelaAccts": [{
                                "subscriberId": "1",
                                "relaType": "2"
                            }]
                        },
                        "primaryOfferInfo": {
                            "offerId": ""
                        }
                    }
                }],
                "transactionCommonInfo": {
                    "isPendingQApproved": "true",
                    "remark": ""
                }
            }

        def generate_soap_xml(data_sets):
            envelope = ET.Element("soapenv:Envelope", {
                "xmlns:soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
                "xmlns:sch": "http://oss.huawei.com/webservice/external/services/schema",
                "xmlns:bas": "http://oss.huawei.com/webservice/external/services/basetype/"
            })
            header = ET.SubElement(envelope, "soapenv:Header")
            body = ET.SubElement(envelope, "soapenv:Body")
            create_new_subscriber = ET.SubElement(body, "sch:createNewSubscriber")
            
            access_session = ET.SubElement(create_new_subscriber, "sch:AccessSessionRequest")
            for key, value in data_sets[0]["accessSessionRequest"].items():
                if key != "remoteAddress":
                    ET.SubElement(access_session, f"bas:{key}").text = value
            access_session.append(ET.Comment(f"<bas:remoteAddress>{data_sets[0]['accessSessionRequest']['remoteAddress']}</bas:remoteAddress>"))
            
            create_request = ET.SubElement(create_new_subscriber, "sch:CreateNewSubscriberRequest")
            customer_info = ET.SubElement(create_request, "sch:customerInfo")
            
            customer_info_fields = data_sets[0]["customerInfo"]
            for key, value in customer_info_fields.items():
                if key not in ["customerAddressInfos", "customerRelationInfos", "corporationInfo", "numOfSubPerCondition", "info1", "info2", "info3", "info4", "info5"]:
                    if isinstance(value, str):
                        if key == "customerId":
                            customer_info.append(ET.Comment(f"Randomized 13-digit customerId starting with 10000 \n                    <bas:customerId>{value}</bas:customerId>"))
                        elif key == "customerCode":
                            customer_info.append(ET.Comment(f"Customer code <bas:customerCode>{value}</bas:customerCode>"))
                        else:
                            ET.SubElement(customer_info, f"bas:{key}").text = value
            
            customer_info_children = list(customer_info)
            insert_index = None
            for idx, child in enumerate(customer_info_children):
                if child.tag == "bas:customerGroup":
                    insert_index = idx
                    break
            if insert_index is None:
                insert_index = len(customer_info_children)
            customer_info.insert(insert_index, ET.Comment("Customer segment"))
            customer_segment = ET.Element("bas:customerSegment")
            customer_segment.text = "SEG1"
            customer_info.insert(insert_index + 1, customer_segment)
            
            for idx, child in enumerate(list(customer_info)):
                if child.tag == "bas:maritalStatus":
                    customer_info.insert(idx + 1, ET.Comment(f"Create date  <bas:createDate>{format_date_yymmdd(datetime.date.today())}</bas:createDate>"))
                    break
            
            for addr in data_sets[0]["customerInfo"]["customerAddressInfos"]:
                addr_info = ET.SubElement(customer_info, "bas:customerAddressInfos")
                for key, value in addr.items():
                    ET.SubElement(addr_info, f"bas:{key}").text = value
            
            for rel in data_sets[0]["customerInfo"]["customerRelationInfos"]:
                rel_info = ET.SubElement(customer_info, "bas:customerRelationInfos")
                for key, value in rel.items():
                    ET.SubElement(rel_info, f"bas:{key}").text = value
            
            corp_info = ET.SubElement(customer_info, "bas:corporationInfo")
            corp_fields_order = [
                "corpNumber", "companyName", "shortName", "hierarchy", "topParentCustomerId",
                "parentCustomerId", "subCustomerList", "businessRegistrationNumber", "expiryDateofBRN",
                "ownershipType", "industrySegment", "businessNature", "phoneNumber", "email",
                "fax", "geographicalSpread", "telcoProviders", "sow", "accountValue",
                "dateofIncorporation", "numberofEmployees", "paidupCapital", "salesTurnover",
                "enterpriseCustomerType", "remark", "picInfos", "accountManagerInfo"
            ]
            for key in corp_fields_order:
                if key in data_sets[0]["customerInfo"]["corporationInfo"]:
                    if key == "subCustomerList":
                        for sub in data_sets[0]["customerInfo"]["corporationInfo"]["subCustomerList"]:
                            sub_list = ET.SubElement(corp_info, "bas:subCustomerList")
                            for sub_key, sub_value in sub.items():
                                ET.SubElement(sub_list, f"bas:{sub_key}").text = sub_value
                    elif key == "picInfos":
                        for pic in data_sets[0]["customerInfo"]["corporationInfo"]["picInfos"]:
                            pic_info = ET.SubElement(corp_info, "bas:picInfos")
                            for pic_key, pic_value in pic.items():
                                ET.SubElement(pic_info, f"bas:{pic_key}").text = pic_value
                    elif key == "accountManagerInfo":
                        account_manager = ET.SubElement(corp_info, "bas:accountManagerInfo")
                        for am_key, am_value in data_sets[0]["customerInfo"]["corporationInfo"]["accountManagerInfo"].items():
                            ET.SubElement(account_manager, f"bas:{am_key}").text = am_value
                    else:
                        ET.SubElement(corp_info, f"bas:{key}").text = data_sets[0]["customerInfo"]["corporationInfo"][key]
            
            for key in ["numOfSubPerCondition", "info1", "info2", "info3", "info4", "info5"]:
                ET.SubElement(customer_info, f"bas:{key}").text = data_sets[0]["customerInfo"][key]
            
            for data in data_sets:
                new_acct = ET.SubElement(create_request, "sch:newAcctSubscriberInfos")
                account_info = ET.SubElement(new_acct, "bas:accountInfo")
                account_info_fields = data["newAcctSubscriberInfos"][0]["accountInfo"]
                account_fields_order = [
                    "accountId", "customerId", "accountCode", "billcycleType", "title",
                    "accountName", "converge_flag", "billLanguage", "initialCreditLimit", "status",
                    "creditLimitNotifyPercentages", "acla", "noDunningFlag", "loyaltyCardNo",
                    "creditTerm", "isAutoReload", "email", "isPaymentResponsible",
                    "addressInfo", "paymentModeInfo", "info1", "info2", "info3", "info4", "info5"
                ]
                for key in account_fields_order:
                    if key in account_info_fields:
                        if key == "accountId":
                            account_info.append(ET.Comment(f"<bas:accountId>{account_info_fields['accountId']}</bas:accountId>"))
                        elif key == "customerId":
                            account_info.append(ET.Comment(f"<bas:customerId>{account_info_fields['customerId']}</bas:customerId>"))
                        elif key == "creditLimitNotifyPercentages":
                            for p in account_info_fields["creditLimitNotifyPercentages"]:
                                ET.SubElement(account_info, "bas:creditLimitNotifyPercentages").text = p
                        elif key == "addressInfo":
                            for addr in account_info_fields["addressInfo"]:
                                addr_info = ET.SubElement(account_info, "bas:addressInfo")
                                for addr_key, addr_value in addr.items():
                                    ET.SubElement(addr_info, f"bas:{addr_key}").text = addr_value
                        elif key == "paymentModeInfo":
                            payment_mode = ET.SubElement(account_info, "bas:paymentModeInfo")
                            for pm_key, pm_value in account_info_fields["paymentModeInfo"].items():
                                if pm_key in ["bankCode", "bankAcctNo", "bankIssuer"]:
                                    payment_mode.append(ET.Comment(f"<bas:{pm_key}>{pm_value}</bas:{pm_key}>"))
                                else:
                                    ET.SubElement(payment_mode, f"bas:{pm_key}").text = pm_value
                        else:
                            ET.SubElement(account_info, f"bas:{key}").text = account_info_fields[key]
                
                for bill in data["newAcctSubscriberInfos"][0]["billMediumInfos"]:
                    bill_info = ET.SubElement(new_acct, "bas:billMediumInfos")
                    for key, value in bill.items():
                        ET.SubElement(bill_info, f"bas:{key}").text = value
                
                new_subscriber = ET.SubElement(new_acct, "bas:newSubscriberInfos")
                ET.SubElement(new_subscriber, "bas:subscriberCountSeq").text = data["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["subscriberCountSeq"]
                subscriber_info = ET.SubElement(new_subscriber, "bas:subscriberInfo")
                subscriber_info_fields = data["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["subscriberInfo"]
                subscriber_fields_order = [
                    "subscriberId", "customerId", "paidFlag", "subscriberType", "msisdn",
                    "imsi", "iccid", "imei", "subscriberLanguage", "suspensionResumeReason",
                    "subscriberSegment", "companyName", "companyIndustry", "businessNature",
                    "corporateName", "userName", "subscriberStatus", "createDate", "effectiveDate",
                    "expiryDate", "latestActivationDate", "activeDate", "defaultAcctId",
                    "telecomType", "finalCLQuota", "tempCLQuota", "isUseOverPayment",
                    "creditLimitNotifyPercentages", "smsNotifySettingInfos", "tenure", "otherRelaAccts"
                ]
                for key in subscriber_fields_order:
                    if key in subscriber_info_fields:
                        if key == "customerId":
                            subscriber_info.append(ET.Comment(f"<bas:customerId>{subscriber_info_fields['customerId']}</bas:customerId>"))
                        elif key == "defaultAcctId":
                            subscriber_info.append(ET.Comment(f"<bas:defaultAcctId>{subscriber_info_fields['defaultAcctId']}</bas:defaultAcctId>"))
                        elif key == "creditLimitNotifyPercentages":
                            for p in subscriber_info_fields["creditLimitNotifyPercentages"]:
                                ET.SubElement(subscriber_info, "bas:creditLimitNotifyPercentages").text = p
                        elif key == "smsNotifySettingInfos":
                            for sms in subscriber_info_fields["smsNotifySettingInfos"]:
                                sms_comment = ET.Comment(f"<bas:smsNotifySettingInfos><bas:eventType>{sms['eventType']}</bas:eventType><bas:openFlag>{sms['openFlag']}</bas:openFlag></bas:smsNotifySettingInfos>")
                                subscriber_info.append(sms_comment)
                        elif key == "otherRelaAccts":
                            for rel in subscriber_info_fields["otherRelaAccts"]:
                                rela_acct = ET.SubElement(subscriber_info, "bas:otherRelaAccts")
                                for rel_key, rel_value in rel.items():
                                    ET.SubElement(rela_acct, f"bas:{rel_key}").text = rel_value
                        else:
                            ET.SubElement(subscriber_info, f"bas:{key}").text = subscriber_info_fields[key]
                
                primary_offer = ET.SubElement(new_subscriber, "bas:primaryOfferInfo")
                ET.SubElement(primary_offer, "bas:offerId").text = data["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["primaryOfferInfo"]["offerId"]
            
            transaction_info = ET.SubElement(create_request, "sch:transactionCommonInfo")
            for key, value in data_sets[0]["transactionCommonInfo"].items():
                ET.SubElement(transaction_info, f"bas:{key}").text = value
            
            rough_string = ET.tostring(envelope, encoding='unicode')
            parsed = minidom.parseString(rough_string)
            pretty_xml = parsed.toprettyxml(indent="    ", encoding="UTF-8").decode("UTF-8")
            return pretty_xml

        offer_categories = {
            "411155": "Prepaid",
            "411156": "Prepaid",
            "101045": "Prepaid",
            "411158": "Prepaid",
            "214292": "Postpaid",
            "96181": "Postpaid",
            "96180": "Postpaid",
            "144882": "Postpaid"
        }

        st.markdown('<div class="app-container">', unsafe_allow_html=True)
        st.markdown('<div class="header">CRM 3.3 Staging Test Data Creation Tools</div>', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Please start creation between 10:00 AM - 5:30 PM only on Weekday.</div>', unsafe_allow_html=True)

        st.markdown('<div class="welcome-bar">', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f'<span class="welcome-text">Hello, {st.session_state.username}! 👋</span>', unsafe_allow_html=True)
        with col2:
            if st.button("Logout", key="logout_button", help="Log out and clear session"):
                st.session_state.clear()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        with st.sidebar:
            st.markdown('<div class="sidebar-title">Settings</div>', unsafe_allow_html=True)
            telecom_type = st.selectbox(
                "Telecom Type",
                options=["33 - Mobile Voice", "34 - Broadband"],
                format_func=lambda x: x,
                key="telecom_type"
            )
            telecom_type_value = telecom_type.split(" - ")[0]
            end_row = st.selectbox(
                "Number of Data Sets (max 5)",
                options=[1, 2, 3, 4, 5],
                index=0,
                key="end_row"
            )

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📱 MSISDN/ICCID",
            "⚙️ Configuration",
            "✍️ Data Input",
            "📄 SOAP XML",
            "🔍 Additional Queries"
        ])

        with tab1:
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Step 1: Retrieve MSISDN and ICCID</div>', unsafe_allow_html=True)
                col3, col4 = st.columns([1, 1])
                with col3:
                    if st.button("Get MSISDN", key="get_msisdn", use_container_width=True):
                        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sch="http://oss.huawei.com/webservice/external/services/schema" xmlns:bas="http://oss.huawei.com/webservice/external/services/basetype/">
<soapenv:Header/>
<soapenv:Body>
<sch:getPhoneNumbers>
<sch:AccessSessionRequest>
<bas:accessChannel>10805</bas:accessChannel>
<bas:operatorCode>CSG</bas:operatorCode>
<bas:password>PkzVHH0odLylDCRIPJM+Mw==</bas:password>
<bas:transactionId>202504122319934778</bas:transactionId>
</sch:AccessSessionRequest>
<sch:GetPhoneNumbersRequest>
<sch:QueryCondition>
<sch:deptId>Common</sch:deptId>
<sch:area>1</sch:area>
<sch:matchCode>601%</sch:matchCode>
<sch:msisdnLevel>0</sch:msisdnLevel>
<sch:paidFlag>1</sch:paidFlag>
<sch:telecomType>{telecom_type_value}</sch:telecomType>
<sch:subscriberType>1</sch:subscriberType>
<sch:startRow>1</sch:startRow>
<sch:endRow>{end_row}</sch:endRow>
<sch:lockFlag>0</sch:lockFlag>
</sch:QueryCondition>
</sch:GetPhoneNumbersRequest>
</sch:getPhoneNumbers>
</soapenv:Body>
</soapenv:Envelope>"""
                        st.text_area("MSISDN XML", xml, height=200, key="msisdn_xml")
                        st.session_state.show_msisdn_input = True
                        st.success("✔ Run this in SoapUI")
                
                if st.session_state.get("show_msisdn_input", False):
                    msisdn_output = st.text_area("Paste MSISDN Output Here", height=150, key="msisdn_output")
                    if msisdn_output:
                        msisdns = parse_msisdn_output(msisdn_output)
                        if msisdns:
                            st.session_state.msisdns = msisdns
                            st.success(f"Extracted {len(msisdns)} MSISDNs. They will be auto-filled in the Data Input tab.")

                with col4:
                    if st.button("Get ICCID", key="get_iccid", use_container_width=True):
                        sql = """SELECT ICCID, IMSI, RES_STATUS_ID 
FROM INVENTORY.RES_SIM
WHERE RES_STATUS_ID LIKE '2' AND IS_BIND = '0' AND DEPT_ID ='300' AND BE_ID = '102';"""
                        st.text_area("ICCID SQL", sql, height=100, key="iccid_sql")
                        st.session_state.show_iccid_input = True
                        st.success("✔ Run this in SQL")
                
                if st.session_state.get("show_iccid_input", False):
                    iccid_output = st.text_area("Paste ICCID Output Here", height=150, key="iccid_output")
                    if iccid_output:
                        iccid_imsi_data = parse_iccid_imsi_output(iccid_output)
                        if iccid_imsi_data:
                            st.session_state.iccid_imsi_data = iccid_imsi_data
                            st.success(f"Extracted {len(iccid_imsi_data)} ICCID/IMSI pairs. They will be auto-filled in the Data Input tab.")

                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Step 2: Configure Data Sets</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-text">Number of Data Sets Selected: <strong>{end_row}</strong></div>', unsafe_allow_html=True)
                if st.button("Generate Input Form", key="generate_form", use_container_width=True):
                    st.session_state.generated_data_sets_count = end_row
                    st.session_state.data_sets = [generate_dummy_data(i + 1) for i in range(end_row)]
                    
                    msisdns = st.session_state.get("msisdns", [])
                    iccid_imsi_data = st.session_state.get("iccid_imsi_data", [])
                    
                    for i in range(end_row):
                        if i < len(msisdns):
                            st.session_state[f"msisdn_{i}"] = msisdns[i]
                        else:
                            st.session_state[f"msisdn_{i}"] = ""
                        
                        if i < len(iccid_imsi_data):
                            st.session_state[f"iccid_{i}"] = iccid_imsi_data[i]["iccid"]
                            st.session_state[f"imsi_{i}"] = iccid_imsi_data[i]["imsi"]
                        else:
                            st.session_state[f"iccid_{i}"] = ""
                            st.session_state[f"imsi_{i}"] = ""
                    
                    st.success("Input form generated! Proceed to the Data Input tab.")
                st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            if "generated_data_sets_count" in st.session_state:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div class="section-title">Step 3: Enter Data for Each Set</div>', unsafe_allow_html=True)
                    data_sets = st.session_state.data_sets
                    for i in range(st.session_state.generated_data_sets_count):
                        st.markdown(f'<div class="data-set-title">Data Set {i + 1}</div>', unsafe_allow_html=True)
                        col_msisdn, col_iccid, col_imsi = st.columns(3)
                        with col_msisdn:
                            st.markdown('<span class="label">MSISDN <span class="required">*</span></span>', unsafe_allow_html=True)
                            msisdn = st.text_input("", value=st.session_state.get(f"msisdn_{i}", ""), placeholder="e.g., 601002033200", key=f"msisdn_{i}")
                        with col_iccid:
                            st.markdown('<span class="label">ICCID <span class="required">*</span></span>', unsafe_allow_html=True)
                            iccid = st.text_input("", value=st.session_state.get(f"iccid_{i}", ""), placeholder="e.g., 89601619041600000091", key=f"iccid_{i}")
                        with col_imsi:
                            st.markdown('<span class="label">IMSI <span class="required">*</span></span>', unsafe_allow_html=True)
                            imsi = st.text_input("", value=st.session_state.get(f"imsi_{i}", ""), placeholder="e.g., 502161082020265", key=f"imsi_{i}")
                        col_telecom, col_offer = st.columns(2)
                        with col_telecom:
                            st.markdown('<span class="label">Telecom Type <span class="required">*</span></span>', unsafe_allow_html=True)
                            telecom_type = st.selectbox(
                                "",
                                options=["", "33 - Mobile Voice", "34 - Broadband"],
                                format_func=lambda x: x if x else "Select Telecom Type",
                                key=f"telecomType_{i}"
                            )
                        with col_offer:
                            st.markdown('<span class="label">Offer ID <span class="required">*</span></span>', unsafe_allow_html=True)
                            offer_id = st.selectbox(
                                "",
                                options=[
                                    ("", "Select an Offer"),
                                    ("411155", "CelcomDigi Prepaid 5G Kuning (A01)"),
                                    ("411156", "CelcomDigi Prepaid 5G Kuning (A02)"),
                                    ("101045", "Digi Prepaid LiVE"),
                                    ("411158", "Raja Kombo 5G (A01)"),
                                    ("214292", "CelcomDigi Postpaid 5G 60 XV"),
                                    ("96181", "E-Reload Postpaid Plan_Agent"),
                                    ("96180", "E-Reload Postpaid Plan_Master"),
                                    ("144882", "Go Digi 78")
                                ],
                                format_func=lambda x: x[1],
                                key=f"offerId_{i}"
                            )
                        col_converge, col_paid = st.columns(2)
                        offer_id_value = offer_id[0]
                        converge_flag = "0" if offer_id_value and offer_categories.get(offer_id_value) == "Prepaid" else "1" if offer_id_value else ""
                        paid_flag = converge_flag
                        with col_converge:
                            st.markdown('<span class="label">Converge Flag</span>', unsafe_allow_html=True)
                            st.selectbox(
                                "",
                                options=["", "0 - Prepaid", "1 - Postpaid"],
                                index=["", "0 - Prepaid", "1 - Postpaid"].index(f"{converge_flag} - {'Prepaid' if converge_flag == '0' else 'Postpaid'}" if converge_flag else ""),
                                format_func=lambda x: x if x else "Select Converge Flag",
                                disabled=True,
                                key=f"converge_flag_{i}"
                            )
                        with col_paid:
                            st.markdown('<span class="label">Paid Flag</span>', unsafe_allow_html=True)
                            st.selectbox(
                                "",
                                options=["", "0 - Prepaid", "1 - Postpaid"],
                                index=["", "0 - Prepaid", "1 - Postpaid"].index(f"{paid_flag} - {'Prepaid' if paid_flag == '0' else 'Postpaid'}" if paid_flag else ""),
                                format_func=lambda x: x if x else "Select Paid Flag",
                                disabled=True,
                                key=f"paidFlag_{i}"
                            )

                    st.markdown('<div class="advanced-settings">', unsafe_allow_html=True)
                    st.markdown('<div class="section-title">Advanced Settings</div>', unsafe_allow_html=True)
                    sections = [
                        {"name": "AccessSessionRequest", "fields": data_sets[0]["accessSessionRequest"]},
                        {
                            "name": "customerInfo",
                            "fields": {
                                k: v for k, v in data_sets[0]["customerInfo"].items()
                                if k not in ["customerSegment", "createDate"] and isinstance(v, str)
                            }
                        },
                        {"name": "transactionCommonInfo", "fields": data_sets[0]["transactionCommonInfo"]}
                    ]
                    for section in sections:
                        with st.expander(section["name"], expanded=False):
                            for key, value in section["fields"].items():
                                st.text_input(
                                    key,
                                    value=value,
                                    key=f"{section['name']}_{key}"
                                )
                    st.markdown('</div>', unsafe_allow_html=True)

                    if st.button("Generate SOAP XML", key="generate_soap", use_container_width=True):
                        with st.spinner("Generating SOAP XML..."):
                            try:
                                if not isinstance(st.session_state.get("data_sets"), list):
                                    st.warning("Invalid data_sets in session state. Reinitializing.")
                                    st.session_state.generated_data_sets_count = st.session_state.get("generated_data_sets_count", 1)
                                    st.session_state.data_sets = [generate_dummy_data(i + 1) for i in range(st.session_state.generated_data_sets_count)]
                                data_sets = st.session_state.data_sets

                                expected_customer_info_keys = {
                                    "customerId", "customerFlag", "customerCode", "idType", "idNumber",
                                    "expiryDateofcertificate", "title", "firstName", "middleName", "lastName",
                                    "nationality", "customerLang", "customerLevel", "customerGroup", "race",
                                    "occupation", "customerDateofBirth", "customerGender", "maritalStatus",
                                    "customerStatus", "numOfSubPerCondition", "info1", "info2", "info3",
                                    "info4", "info5", "customerAddressInfos", "customerRelationInfos", "corporationInfo"
                                }
                                nested_keys = {"customerAddressInfos", "customerRelationInfos", "corporationInfo"}

                                for i in range(len(data_sets)):
                                    customer_info = data_sets[i]["customerInfo"]
                                    if set(customer_info.keys()) != expected_customer_info_keys:
                                        st.warning(f"Invalid keys in data_sets[{i}]['customerInfo']. Reinitializing data_sets.")
                                        st.session_state.data_sets = [generate_dummy_data(j + 1) for j in range(st.session_state.generated_data_sets_count)]
                                        data_sets = st.session_state.data_sets
                                        break
                                    for key, value in customer_info.items():
                                        if key not in nested_keys:
                                            if not isinstance(value, str):
                                                st.warning(f"Invalid value type for {key} in data_sets[{i}]['customerInfo']. Expected string, got {type(value)}. Reinitializing data_sets.")
                                                st.session_state.data_sets = [generate_dummy_data(j + 1) for j in range(st.session_state.generated_data_sets_count)]
                                                data_sets = st.session_state.data_sets
                                                break

                                for i in range(st.session_state.generated_data_sets_count):
                                    msisdn = st.session_state.get(f"msisdn_{i}", "")
                                    iccid = st.session_state.get(f"iccid_{i}", "")
                                    imsi = st.session_state.get(f"imsi_{i}", "")
                                    telecom_type = st.session_state.get(f"telecomType_{i}", "")
                                    valid_telecom_options = ["", "33 - Mobile Voice", "34 - Broadband"]
                                    if telecom_type not in valid_telecom_options:
                                        st.warning(f"Invalid Telecom Type for Data Set {i + 1}. Resetting to default.")
                                        telecom_type = ""
                                        st.session_state[f"telecomType_{i}"] = ""
                                    telecom_type_value = telecom_type.split(" - ")[0] if telecom_type else ""
                                    raw_offer_id = st.session_state.get(f"offerId_{i}", ("", ""))
                                    if not isinstance(raw_offer_id, tuple) or len(raw_offer_id) != 2:
                                        raise ValueError(f"Expected a 2-element tuple for offerId_{i}, got {raw_offer_id}")
                                    offer_id = raw_offer_id[0]

                                    if not msisdn or not msisdn.isdigit() or not (10 <= len(msisdn) <= 12):
                                        st.error(f"Invalid MSISDN for Data Set {i + 1}. Must be 10-12 digits.")
                                        break
                                    if not iccid or not iccid.isdigit() or not (19 <= len(iccid) <= 20):
                                        st.error(f"Invalid ICCID for Data Set {i + 1}. Must be 19-20 digits.")
                                        break
                                    if not imsi or not imsi.isdigit() or len(imsi) != 15:
                                        st.error(f"Invalid IMSI for Data Set {i + 1}. Must be 15 digits.")
                                        break
                                    if not telecom_type_value:
                                        st.error(f"Please select a Telecom Type for Data Set {i + 1}.")
                                        break
                                    if not offer_id:
                                        st.error(f"Please select an Offer ID for Data Set {i + 1}.")
                                        break
                                    if offer_id not in offer_categories:
                                        st.error(f"Invalid Offer ID {offer_id} for Data Set {i + 1}.")
                                        break

                                    is_prepaid = offer_categories[offer_id] == "Prepaid"
                                    converge_flag = "0" if is_prepaid else "1"
                                    paid_flag = converge_flag
                                    data_sets[i]["newAcctSubscriberInfos"][0]["accountInfo"]["converge_flag"] = converge_flag
                                    data_sets[i]["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["subscriberInfo"]["paidFlag"] = paid_flag
                                    data_sets[i]["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["subscriberInfo"]["msisdn"] = msisdn
                                    data_sets[i]["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["subscriberInfo"]["iccid"] = iccid
                                    data_sets[i]["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["subscriberInfo"]["imsi"] = imsi
                                    data_sets[i]["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["subscriberInfo"]["telecomType"] = telecom_type_value
                                    data_sets[i]["newAcctSubscriberInfos"][0]["newSubscriberInfos"]["primaryOfferInfo"]["offerId"] = offer_id

                                soap_xml = generate_soap_xml(data_sets)
                                st.session_state.soap_xml = soap_xml
                                st.success("SOAP XML generated successfully! Check the SOAP XML tab.")
                            except Exception as e:
                                st.error(f"Error generating SOAP XML: {str(e)}")

                    st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Step 4: Review and Download SOAP XML</div>', unsafe_allow_html=True)
                if "soap_xml" in st.session_state:
                    st.text_area("Generated SOAP XML", st.session_state.soap_xml, height=400, key="soap_xml_output")
                    st.download_button(
                        label="Download SOAP XML",
                        data=st.session_state.soap_xml,
                        file_name="generated_soap.xml",
                        mime="text/xml",
                        key="download_soap"
                    )
                else:
                    st.info("Generate the SOAP XML in the Data Input tab to view it here.")
                st.markdown('</div>', unsafe_allow_html=True)

        with tab5:
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Additional Queries</div>', unsafe_allow_html=True)
                st.markdown('<div class="info-text">Use these queries to retrieve additional data as needed.</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="query-section">', unsafe_allow_html=True)
                st.markdown('<span class="label">Customer Query</span>', unsafe_allow_html=True)
                customer_sql = """SELECT CUSTOMER_ID, CUSTOMER_CODE, FIRST_NAME, LAST_NAME
FROM CUSTOMER.CUSTOMER_INFO
WHERE CUSTOMER_STATUS = 'A02' AND BE_ID = '102';"""
                st.text_area("", customer_sql, height=100, key="customer_sql")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="query-section">', unsafe_allow_html=True)
                st.markdown('<span class="label">Account Query</span>', unsafe_allow_html=True)
                account_sql = """SELECT ACCOUNT_ID, CUSTOMER_ID, ACCOUNT_NAME
FROM BILLING.ACCOUNT_INFO
WHERE STATUS = '0' AND BE_ID = '102';"""
                st.text_area("", account_sql, height=100, key="account_sql")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    main_app()