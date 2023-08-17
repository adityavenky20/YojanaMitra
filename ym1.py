from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__, template_folder=r'templates')
app.secret_key = 'your_secret_key_here'  

data = pd.read_csv('YMSD.csv')
login_data = pd.read_csv('login.csv')
user_data = pd.read_csv('UserData.csv')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    global user_data
    output = ""

    if request.method == 'POST':
        username = session.get('username')
        if username:
            state = request.form['state']
            age = int(request.form['age'])
            gender = request.form['gender']
            income = int(request.form['income'])

            user_entry = pd.DataFrame({
                'Username': [username],
                'State': [state],
                'Age': [age],
                'Gender': [gender],
                'Income': [income]
            })

            #user_data.to_csv('UserData.csv', mode='a', header=not pd.read_csv('UserData.csv').empty, index=False)
            user_data = user_data.append(user_entry, ignore_index=True)
            user_data.to_csv('UserData.csv', index=False)

            filtered_data = data[(data['State'] == state) &
                                 (data['Minimum Age'] <= age) &
                                 (data['Maximum Age'] >= age) &
                                 (data['Income Level'] >= income)]

            if not filtered_data.empty:
                output += "<h2>Eligible Schemes:</h2>"
                output += "<table border='1'>"
                output += "<tr><th>Scheme Name</th><th>Benefits</th><th>Documents Required</th><th>Link</th></tr>"
                #for index, row in filtered_data.iterrows():
                 #   output += "<tr><td>{}</td><td>{}</td><td>{}</td><td><a href='{}' >Link</a></td></tr>".format(
                  #      row['Scheme Name'], row['Benefits'], row['Documents Required'], row['Link'])
                for index, row in filtered_data.iterrows():
                    output += "<tr><td>{}</td><td>{}</td><td>{}</td><td><a href='{}' target='_blank'>Link</a></td></tr>".format(
                        row['Scheme Name'], row['Benefits'], row['Documents Required'], row['Link']
                    )
                output += "</table>"
            else:
                output += "<h3>No schemes found for the given criteria.</h3>"

    return render_template('ymio1.html', output=output)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = login_data[(login_data['Username'] == username) & (login_data['Password'] == password)]
    
    if not user.empty:
        session['username'] = username
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error_message="Incorrect username or password.")

@app.route('/signup', methods=['POST'])
def signup():
    global login_data
    username = request.form['username']
    password = request.form['password']
    is_agent = request.form.get('is_agent', False)

    new_user = pd.DataFrame({'Username': [username], 'Password': [password], 'IsAgent': ['Yes' if is_agent else 'No']})
    login_data = login_data.append(new_user, ignore_index=True)
    login_data.to_csv('login.csv', index=False)

    return render_template('login.html', success_message="Account created successfully. You can now log in.")

if __name__ == '__main__':
    app.run(debug=True)
