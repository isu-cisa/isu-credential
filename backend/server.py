import os
import random, string
from datetime import date
import json
import hashlib
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, \
        login_required, login_user, current_user, logout_user
from flask_cors import CORS
from flask_moment import Moment
from apps.tangle import write_data_to_tangle
from apps.findmessages import findmessages
from apps.account import remove
from datetime import datetime

app = Flask(__name__)
CORS(app)
moment= Moment(app)

app.config['SECRET_KEY'] = 'isu2001njcndj'

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    user = User()
    user.id = username

    # Get group
    f = open("static/accounts.txt", "r")
    list_content = f.read().splitlines()
    f.close()

    for obj in list_content:
        obj_json = json.loads(obj)
        if obj_json["account"] == user.id:
            user.group = obj_json["group"]

    return user

# index page
@app.route("/")
def index():
    if current_user.is_authenticated:
        user = user_loader(current_user.id)
        return render_template('index.html', user = current_user)
    else:
        logout_user()

    return render_template('index.html')

def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign_up.html')
    else:
        # Save to account field
        form_content = request.form
        dict_user = form_content.to_dict()
        dict_user["group"] = "normal"
        account = dict_user["account"]

        if account == "":
            return json.dumps({"error_message": "account can't empty."}), 500
        try:
            with open("static/accounts.txt") as lines:
                for line in lines:
                    json_data = json.loads(line)
                    if json_data["account"] == account:
                        return json.dumps({"error_message": "account is exist."}), 400
        except:
            return json.dumps({"error_message": "can't load account data."}), 500

        fp = open("static/accounts.txt", "a")
        fp.write(json.dumps(dict_user) + "\n")
        fp.close()

    return redirect(url_for("index"))

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('sign_in.html')
    else:
        user = User()
        form_content = request.form
        
        f = open("static/accounts.txt", "r")
        list_content = f.read().splitlines()
        f.close()

        for obj in list_content:
            obj_json = json.loads(obj)
            sha1 = hashlib.sha1()
            sha1.update(form_content["password"].encode('utf-8'))
            res = sha1.hexdigest()
            if obj_json["account"] == form_content["account"] and \
                    obj_json["password"] == res:
                    user = User()
                    user.id = form_content["account"]
                    user.group = obj_json["group"]
                    login_user(user, remember = True)
        
                    if obj_json["group"] == "admin":
                        return redirect(url_for("review_check"))
                    else:
                        return redirect(url_for("personal_micro_credit_list"))

        return render_template('index.html', user = user)

@app.route('/logout')
def logout():
    logout_user()
    return render_template('sign_in.html')

# Activity information page
@app.route("/activity_info", methods=['GET', 'POST'])
@login_required
def activity_info():
    if request.method == 'GET':
        return render_template('ActivityInformation.html')
    else:
        form_content = request.form
        fp = open("static/activities.txt", "a")
        fp.write(json.dumps(form_content) + "\n")
        fp.close()
        return redirect(url_for("activity_info"))

# Write form data to blockchain
@app.route("/write_data", methods=['GET', 'POST'])
def write_data():
    if request.method == 'POST':
        form_content = request.form
        result = write_data_to_tangle(form_content)

        # Save to history
        fp = open("static/history.txt", "a")
        fp.write(str(result["bundle"]) + "\n")
        fp.close()

        return redirect(url_for("backend_credential_editor"))

# Page for student
@app.route("/credential_editor", methods=['GET', 'POST'])
@login_required
def credential_editor():
    if request.method == 'GET':
        list_credential = []
        fp = open("static/activities.txt", "r")
        list_content = fp.readlines()
        fp.close()

        for obj in list_content:
            list_credential.append(json.loads(obj))
        
        return render_template('credential_editor.html', list_credential = list_credential)
    else:
        fp = open("static/experience.txt", "a")
        form_content = request.form
        exp = form_content.to_dict()
        x = exp["activity_kind"].split("/")
        exp["id"] = ''.join(random.choice(string.ascii_letters) for x in range(4))
        exp["Date"] = x[0]
        exp["ActivityName"] = x[1]
        exp["Credit"] = x[2]
        exp["student_id"] = current_user.id
        del exp["activity_kind"]
        fp.write(json.dumps(exp) + "\n")
        fp.close()

        return redirect(url_for("personal_micro_credit_list"))

@app.route("/personal_micro_credit_list",methods=['GET', 'POST'])
@login_required
def personal_micro_credit_list():
    list_raw_experience = []
    if request.method == 'POST':
        form_content = request.form
        dict_user = form_content.to_dict()
        name = dict_user["name"]
        id_stu = dict_user["id_stu"]

        # write to award
        obj = {"name":name,"id_stu":id_stu,"date":str(date.today())}
        with open("static/award.txt", "a") as fp:
            json.dump(obj, fp)
            fp.write("\n")
        return render_template('personal_micro_credit_list.html', list_raw_experience = list_raw_experience)
    else:
        lst_output = []
        file_experience = open("static/experience_ovrview.txt", "r")
        list_raw_experience = file_experience.readlines()
        file_experience.close()

        for obj in list_raw_experience:
            obj_json = json.loads(obj)
            if obj_json["student_id"] == current_user.id:
                lst_output.append(obj)
        
        return render_template('personal_micro_credit_list.html', lst_output = lst_output)

@app.route("/personal_micro_credit_apply",methods=['GET', 'POST'])
@login_required
def personal_micro_credit_apply():
    f = open("static/experience.txt", "r")
    content = f.readlines()
    f.close()

    exp_list = []
    for obj in content:
        obj = json.loads(obj)
        if obj["student_id"] == current_user.id:
            exp_list.append(obj)
    return render_template('personal_micro_credit_apply.html',list_content = exp_list)

@app.route("/feedback", methods=['GET'])
@login_required
def feedback():
    exp = ""
    ActivityName = request.args.get("ActivityName")
    Date = request.args.get("Date")
    f = open("static/experience.txt", "r")
    content = f.readlines()
    f.close()

    for obj in content:
        obj = json.loads(obj)
        if obj["student_id"] == current_user.id and obj["ActivityName"] == ActivityName and obj["Date"] == Date:
            exp = obj["experience"]

    return render_template('feedback.html',exp = exp)

# Backend for teacher
@app.route("/backend_credential_editor")
def backend_credential_editor():
    return render_template('backend_credential_editor.html')

@app.route("/verify_list")
@login_required
def verify_list():
    file_experience = open("static/experience_ovrview.txt", "r")
    list_raw_experience = file_experience.readlines()
    file_experience.close()

    file_account = open("static/accounts.txt", "r")
    list_raw_account = file_account.readlines()
    file_account.close()

    list_review = []

    for obj_exp in list_raw_experience:
        obj_exp = json.loads(obj_exp)

        # find name
        for obj_acc in list_raw_account:
            obj_acc = json.loads(obj_acc)

            if obj_exp["student_id"] == obj_acc["account"]:
                obj_exp["name"] = obj_acc["name"]

                if "status" in obj_exp:
                    if obj_exp["status"] != "審核中":
                        list_review.append(obj_exp)

    return render_template('verify_list.html',list_review = list_review)


@app.route("/review_check")
@login_required
def review_check():
    file_experience = open("static/experience.txt", "r")
    list_raw_experience = file_experience.readlines()
    file_experience.close()

    file_account = open("static/accounts.txt", "r")
    list_raw_account = file_account.readlines()
    file_account.close()

    list_review = []

    for obj_exp in list_raw_experience:
        obj_exp = json.loads(obj_exp)

        # find name
        for obj_acc in list_raw_account:
            obj_acc = json.loads(obj_acc)

            if obj_exp["student_id"] == obj_acc["account"]:
                obj_exp["name"] = obj_acc["name"]

                if "status" not in obj_exp:
                    obj_exp["status"] = "審核中"

                list_review.append(obj_exp)

    return render_template('review_check.html',list_review = list_review)

@app.route("/new_data", methods=['GET', 'POST'])
def new_data():
    if request.method == 'POST':
        fp = open("static/new_data.txt", "a")
        fp.write(str(request.form) + "\n")
        fp.close()

        return str(request.form)

@app.route("/backend")
def backend():
    list_user = []
    f = open("static/accounts.txt", "r")
    list_content = f.read().splitlines()
    f.close()

    for obj in list_content:
        list_user.append(json.loads(obj))

    return render_template('backend.html',list_user = list_user)

@app.route("/backend_account_manage", methods=["GET"])
def backend_account_manage():
    remove_account = request.args.get("remove")

    if remove_account != None:
        remove(remove_account)

    return redirect(url_for("index"))

@app.route("/review_readonly")
def review_readonly():
    return render_template('review_readonly.html')

@app.route("/review_check_url",methods=['GET', 'POST'])
@login_required
def review_check_url():
        if request.method == 'POST':
            form_content = request.form
            dict_obj = form_content.to_dict()
            
            if dict_obj["audit_result"] != "Not_yet":
                list_output = []
                file_experience = open("static/experience.txt", "r")
                list_content = file_experience.readlines()
                file_experience.close()

                # remove old
                obj_keep = {}
                for obj in list_content:
                    obj_json = json.loads(obj)
                    if obj_json["id"] == dict_obj["cre_id"]:
                        obj_keep = obj_json
                        list_content.remove(obj)

                # add new
                if dict_obj["audit_result"] == "pass":
                    # TODO: credential hash
                    result = write_data_to_tangle(str(date.today()))
                    obj_keep["status"] = str(result["bundle"])
                else:
                    obj_keep["status"] = dict_obj["audit_result"]

                # write
                os.remove("static/experience.txt")
                with open('static/experience.txt', 'a') as file_experience:
                    for obj in list_content:
                        obj = json.loads(obj)
                        file_experience.write(json.dumps(obj))
                        file_experience.write("\n")

                if "status" in obj_keep:
                    with open('static/experience_ovrview.txt', 'a') as file_experience:
                        file_experience.write(json.dumps(obj_keep))
                        file_experience.write("\n")

            return redirect(url_for("review_check"))

        exp = ""
        ActivityName = request.args.get("ActivityName")
        Date = request.args.get("Date")
        student_id = request.args.get("student_id")
        cre_id = request.args.get("id")

        f = open("static/experience.txt", "r")
        content = f.readlines()
        f.close()

        for obj in content:
            obj = json.loads(obj)
            if obj["student_id"] == student_id and obj["ActivityName"] == ActivityName and obj["Date"] == Date:
                exp = obj["experience"]
        
        return render_template('review_check_url.html',cre_id = cre_id, exp = exp)


@app.route("/award_of_review")
def award_of_review():
    # read award
    f = open("static/award.txt", "r")
    list_content = f.readlines()
    f.close()

    list_obj = []
    for obj in list_content:
        list_obj.append(json.loads(obj))
    return render_template('award_of_review.html', list_obj = list_obj)

@app.route("/dashboard")
def dashboard():
    f = open("static/history.txt", "r")
    content = f.readlines()
    f.close()

    return render_template('dashboard.html',title=content)

if __name__ == "__main__":
    app.run(debug = True, threaded = True, host = "0.0.0.0", port = 5001)
