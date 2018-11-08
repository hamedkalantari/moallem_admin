from flask import Flask, render_template, session, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import requests, json, jalali, datetime, os

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'any random string'
BASE_URL = "http://89.163.157.7:8080"
UPLOAD_FOLDER = '/Users/hamed/Desktop'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def events():
    if session.get('logged_in', None):
        return render_template('eventsPage.html', data=False)
    return render_template('loginPage.html')


@app.route('/submit/event', methods=['POST'])
def submit_event():
    if session.get('logged_in', None):
        if request.method == "POST":
            action = request.form['action']
            try:
                day = int(request.form['day'])
                month = int(request.form['month'])
                year = int(request.form['year'])
                if action == 'select-day':
                    r = requests.get(BASE_URL + '/day?day=' + str(day) + '&month=' + str(month) + '&year=' + str(year))
                    result = json.loads(r.text)
                    if result['status'] == 'ok':
                        if result['data']['panel_events']:
                            flash("success")
                            return render_template('eventsPage.html', data=result['data']['panel_events'])
                        else:
                            flash("success")
                            return render_template('eventsPage.html', data=False)
                elif action == 'add':
                    event_dsc = request.form['event-dsc']
                    if event_dsc:
                        date = (jalali.Persian(year, month, day).gregorian_datetime() - datetime.datetime(1970, 1,
                                                                                                          1).date()).total_seconds()
                        r = requests.post(BASE_URL + "/admin/events/add",
                                          data={'timeStamp': int(date), 'event_title': event_dsc},
                                          headers={"Authorization": session['logged_in']})
                        result = json.loads(r.text)
                        if result['status'] == 'ok':
                            flash("success")
                            return render_template('eventsPage.html', data=False)
            except:
                pass
        flash("fail")
        return redirect(url_for('events'))
    return render_template('loginPage.html')


@app.route('/remove/event/<id>')
def remove_event(id):
    if session.get('logged_in', None):
        try:
            r = requests.post(BASE_URL + "/admin/events/delete",
                              data={'event_id': id},
                              headers={"Authorization": session['logged_in']})
            result = json.loads(r.text)

            if result['status'] == 'ok':
                flash("success")
                return redirect(url_for('events'))
        except:
            pass
        flash("fail")
        return redirect(url_for('events'))
    return render_template('loginPage.html')


@app.route('/submit/login', methods=['POST'])
def login():
    if request.method == "POST":
        try:
            username = request.form['username']
            password = request.form['password']
            r = requests.post(BASE_URL + "/login", data={'username': username, 'password': password, 'fcm_token': '0'})
            result = json.loads(r.text)

            if result['status'] == 'ok':
                session['logged_in'] = str(result["data"]["auth_token"])
                return redirect(url_for('events'))
        except:
            pass

    flash("fail")
    return redirect(url_for('events'))


@app.route('/logout')
def logout():
    if session.get('logged_in', None):
        del session['logged_in']
    return redirect(url_for('events'))


@app.route('/notification')
def notification():
    if session.get('logged_in', None):
        return render_template('notificationPage.html')
    return render_template('loginPage.html')


@app.route('/submit/notification', methods=['POST'])
def submit_notification():
    if session.get('logged_in', None):
        if request.method == "POST":
            try:
                text = request.form['txt']
            except Exception as err:
                pass  # failed

        return redirect(url_for('notification'))
    return render_template('loginPage.html')


@app.route('/remove/notification/<id>')
def remove_notification(id):
    if session.get('logged_in', None):
        # we should remove that

        return redirect(url_for('notification'))
    return render_template('loginPage.html')


@app.route('/projects')
def projects():
    if session.get('logged_in', None):
        r = requests.get(BASE_URL + "/banner/all")
        result = json.loads(r.text)
        print(result['data']['banners'])
        if result['status'] == 'ok':
            if result['data']['banners']:
                return render_template('projectsPage.html', data=result['data']['banners'], base_url=BASE_URL)
            else:
                return render_template('projectsPage.html')

        flash("fail")
        return redirect(url_for('projects'))
    return render_template('loginPage.html')


@app.route('/submit/project', methods=['POST'])
def submit_project():
    if session.get('logged_in', None):
        if request.method == "POST":
            try:
                title = request.form['title']
                url = request.form['url']
                photo = request.files['photo']

                if photo.filename == '':
                    flash('fail')
                    return redirect(request.url)
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    photo.save('images/'+filename)
                    f = open('images/'+filename, 'rb')

                    r = requests.post(BASE_URL + "/admin/banner/add",
                                      files={'file': f},
                                      data={'title': title, 'link': url},
                                      headers={"Authorization": session['logged_in']})
                    f.close()
                    os.remove('images/'+filename)
                    result = json.loads(r.text)

                    if result['status'] == 'ok':
                        flash('success')
                        return redirect(url_for('projects'))

            except Exception as err:
                pass  # failed

        flash('fail')
        return redirect(request.url)
    return render_template('loginPage.html')


@app.route('/remove/project/<id>')
def remove_project(id):
    if session.get('logged_in', None):
        try:
            r = requests.post(BASE_URL + "/admin/banner/delete",
                              data={'banner_id': id},
                              headers={"Authorization": session['logged_in']})
            result = json.loads(r.text)

            if result['status'] == 'ok':
                flash('success')
                return redirect(url_for('projects'))
        except:
            pass

        flash('fail')
        return redirect(url_for('projects'))

    return render_template('loginPage.html')


@app.route('/stocks')
def stocks():
    if session.get('logged_in', None):
        r = requests.get(BASE_URL + "/indicator/all")
        result = json.loads(r.text)

        if result['status'] == 'ok':
            if result['data']['indicators']:
                return render_template('stocksPage.html', data=result['data']['indicators'])
            else:
                return render_template('stocksPage.html')

        flash('fail')
        return redirect(url_for('stocks'))
    return render_template('loginPage.html')


@app.route('/submit/stocks', methods=['POST'])
def submit_new_stock():
    if session.get('logged_in', None):
        if request.method == "POST":
            try:
                title = request.form['title']
                changes = request.form['changes']
                value = request.form['value']

                id = 0
                r = requests.get(BASE_URL + "/indicator/all")
                result = json.loads(r.text)
                if result['data']['indicators']:
                    for i in result['data']['indicators']:
                        if i['id'] >= id:
                            id += 1

                r = requests.post(BASE_URL + "/admin/indicator/add",
                                  data={'indicator_id': id, 'title': title, 'percent': changes, 'value': value},
                                  headers={"Authorization": session['logged_in']})

                result = json.loads(r.text)

                if result['status'] == 'ok':
                    flash('success')
                    return redirect(url_for('stocks'))

            except Exception as err:
                pass  # failed

        flash('fail')
        return redirect(url_for('stocks'))
    return render_template('loginPage.html')


@app.route('/edit/stocks/<id>', methods=['POST'])
def edit_stock(id):
    if session.get('logged_in', None):
        if request.method == "POST":
            try:
                title = request.form['title']
                changes = request.form['changes']
                value = request.form['value']

                r = requests.post(BASE_URL + "/admin/indicator/update",
                                  data={'indicator_id': id, 'title': title, 'percent': changes, 'value': value},
                                  headers={"Authorization": session['logged_in']})

                result = json.loads(r.text)

                if result['status'] == 'ok':
                    flash('success')
                    return redirect(url_for('stocks'))

            except Exception as err:
                pass  # failed

        flash('fail')
        return redirect(url_for('stocks'))
    return render_template('loginPage.html')


@app.route('/remove/stocks/<id>')
def remove_stock(id):
    if session.get('logged_in', None):
        try:
            r = requests.post(BASE_URL + "/admin/indicator/delete",
                              data={'indicator_id': id},
                              headers={"Authorization": session['logged_in']})
            result = json.loads(r.text)

            if result['status'] == 'ok':
                flash('success')
                return redirect(url_for('stocks'))
        except:
            pass

        flash('fail')
        return redirect(url_for('stocks'))
    return render_template('loginPage.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
