from flask import Flask, request, render_template, redirect, url_for, session, send_file
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from utils import analyze, login_required
from datetime import datetime

# database initialization
cred = credentials.Certificate(
    {
    "type": "service_account",
    "project_id": "police-a3b7d",
    "private_key_id": "ffbb692208100bb8bb4a714766ac9888cd2032b4",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCyvkQSjvT7/mss\nJ9G9Zy2dkzCTAp3Sci3NWsICIAlZLNrw3tyyMU6TIWIVJ6ypKVg30PtPwm5zVKDf\nVB25jhMTIO6klFKAU+RgvRzDakhYwLrmDB5+jvFepvjhJBiYqjNrwnaNxgT0NEJu\nEas79/Eu2AohhoqqdMOpXGMyFVut6PHRgWe0eZvzapTLVoSKsCRpqkxLVblsNuuq\nEljnNYmCqJl5WCzaepepnJowAEqjZPGpQMZxgpICQQKd4BYa9Hm0vR+SFWGAC2he\nevxwP+EfLTj1SOkQK8+GUGa0xbTx8DYifTNQ2NBEDhLmKvd0FOLr/PxzyMM1S7GL\nxrR9HkT1AgMBAAECggEACmdrbEPInBJcXUmZZROTDXpPzX7Nfj5fJCDa7Ly9+Tl/\nKki5QotULi7h7VFN34V547sqUE4vl6RJaOEV3y3B4SR9lN7SnohDjCNLKqS5E/wZ\nOjgNCQN7poLENyFJZ+QgR27I78pNki6oieJFZqGGoa9kMjyz6Dq7rilOgiUex6nk\n/ibVdaOrBpd7TRyo9hW6X+0HYpx9UY2NnlyJdrT09+f6b4bxUn1nL5mER0AY7123\nf/LCe2MmjIvmNLxQBVF++61GWL1gYdUKdWpNHe4m90xPZ9id593KWRaAkxYaf0h0\nZ9lpRJ/yA4To+hHA2d68rOdbAxLPNo94CKNxEDvEAQKBgQD0q1Dj+mSQDqsOeuTi\n4SA4KoSacvohX58W6jYyP7gTKeK1zsQ6UeOe0SSdAV2/iJAKu6jO3B149gkIquOO\nCi0Zhk9hamADPUpHhbez1E3DLlWizBGW2OnIp3laKvm6lkdxd0mKZLcZJuNi2Dq4\n27mEEUZQn4r0XQw36NlXsUWXNQKBgQC7BVy+TdOAx9tnlUGIEOi+riQ4RF4apCg3\nc2O5RZ3JPG8dxYIVg2VgqeRyK2NytobF+jzNvf+WhJU1OzTDXsrYXNngeCs5/D0g\ngMD3WLTaYErVUqS548tRe18f8CkFAKPHPkXtmGMgYJ3nVOQl1a2FQ9l7+UDJS2ga\ng0lpb0TuwQKBgCOkTT1YvYuKx3pthqhSWUo1T2ncc/mmn1tMNSbux1brVB5eB5Hj\nWgBJwUap60k6kJkvqzCvOg/j7372vf10GAvO2AN95oyyQf7XSOKGe+mB93Gmvq01\n3iCf3Pq4pfZ7a97onKrvbwjX9Gnyy+MgBw9pINAf3bMpVt1SK08uANA9AoGBAJIL\ni/Mof2PvrkxjZ/tDiR1ui+ZMrVgMnUNAHr4NuTvur68GD6GRLFeiFD172Hs6QmDU\nGytnlfIKsyIQjBGNMsZnK9V4wfjUG0AIi6gcY46s54NSuERZuOp2d0BPoRjA+SSc\nYqs59x7PlD+UMV3CUXDiHTIM4STQeAlMQMXPGHuBAoGARo2fTRBSXSqyc6AAq8c3\nky4nlWcqdDUIkbyDLNBeYPD3cXnewYLQHfdxbC7nFpdplMw3T8nCPxv/UyKFRucv\nVszKvJuop7GitPQ+cXWGjSek/LlRkuxYJ/vMbCtjeSi0ZgVOITQteQYn2RwkJ/84\nuexZCZ4Pn8820vGSlqb1QnY=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-89s8a@police-a3b7d.iam.gserviceaccount.com",
    "client_id": "102521872309692475559",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-89s8a%40police-a3b7d.iam.gserviceaccount.com"
    }
)
firebase_admin.initialize_app(cred)
db = firestore.client()

# app instantiation
app = Flask(__name__, static_folder='static')
app.config['APP_NAME'] = 'Project Patrol'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = '435rfgt43y546_fw32th8990t4_324324643'


@app.route("/registration",methods=['GET','POST'])
@login_required
def registration():
    if request.method == 'POST':
        dataset = {
            'name':request.form['name'] ,
            'description': request.form['description'],
            'completion_date': request.form['completion_date'],
            'notes': request.form['notes'],
            'save_date': str(datetime.now()),
            'uploader': session['name']
        }
        try:
            ref = db.collection('dataset').document()
            dataset['id'] = ref.id
            file = request.files['dataset']
            if file:
                filename = f'dataset/{ref.id}.csv'
                file.save(os.path.join('static', filename))
            else:
                return redirect(request.url)
        except Exception as error:
            print(error)
            return redirect(request.url)

        ref.set(dataset)
        return redirect(url_for('registration'))
    return render_template(
        'registration.html',
        page_title=f'{app.config["APP_NAME"]} | Dataset Registration',
        user=session['name'],
        active='registration',
    )

@app.route('/analysis', methods=['GET','POST'])
@login_required
def analysis():
    datasets = []
    docs = db.collection('dataset').stream()
    for doc in docs:
        datasets.append(doc.to_dict())
    return render_template(
        'analysis.html',
        page_title=f'{app.config["APP_NAME"]} | Dataset Analysis',
        user=session['name'],
        active='analysis',
        datasets=datasets
    )

@app.route('/analyze_dataset/<id>')
@login_required
def analyze_dataset(id):
    output = analyze(f'static/dataset/{id}.csv')
    return output

@app.route('/save_analytics', methods=['POST'])
@login_required
def save_analytics():
    try:
        analytics = request.get_json()
        analytics['save_date'] = str(datetime.now())
        analytics['uploader'] = session['name']
        
        dataset_info = db.collection('dataset').document(analytics['dataset_id']).get().to_dict()
        analytics['name'] = dataset_info['name']

        ref = db.collection('history').document()
        analytics['id'] = ref.id
        ref.set(analytics)

        response = {'status':'success'}
    except:
        response = {'status':'error'}
    return response

@app.route('/history')
@login_required
def history():
    analytics = []
    docs = db.collection('history').stream()
    for doc in docs:
        analytics.append(doc.to_dict())
    return render_template(
        'history.html',
        page_title=f'{app.config["APP_NAME"]} | Analytics History',
        user=session['name'],
        active='history',
        analytics=analytics
    )

@app.route('/history/<id>')
@login_required
def history_view(id):
    data = db.collection('history').document(id).get().to_dict()
    return render_template(
        'history_view.html',
        page_title=f'{app.config["APP_NAME"]} | Analytics History',
        user=session['name'],
        active='history',
        data=data
    )


@app.route('/list')
@login_required
def list():
    list = []
    docs = db.collection('dataset').stream()
    for doc in docs:
        list.append(doc.to_dict())
    return render_template(
        'list.html',
        page_title=f'{app.config["APP_NAME"]} | Dataset List',
        user=session['name'],
        active='list',
        list=list
    )

@app.route('/list/<id>')
@login_required
def list_view(id):
    data = db.collection('dataset').document(id).get().to_dict()
    return render_template(
        'list_view.html',
        page_title=f'{app.config["APP_NAME"]} | Dataset List',
        user=session['name'],
        active='list',
        data=data
    )

@app.route('/download/<id>')
@login_required
def download (id):
    path = f'static/dataset/{id}.csv'
    return send_file(path, as_attachment=True)


@app.route("/",methods=['GET','POST'])
@app.route("/login",methods=['GET','POST'])
def login():
    if session.get('username') is not None:
        return redirect(url_for('dataset'))
    if request.method == 'POST':
        owner = db.collection('user').document(request.form['username']).get().to_dict()
        
        if owner:
            if owner['username'] == request.form['username'] and owner['password'] == request.form['password']:
                session['username'] = owner['username']
                session['name'] = owner['name']
                return redirect(url_for('registration'))
            
        return redirect(url_for('login'))
    return render_template('login.html',page_title=f'{app.config["APP_NAME"]} | Sign In')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('name', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
	app.run(debug=False)

