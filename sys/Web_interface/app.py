# -*- coding: utf-8 -*-
# Author: swstorage

import os, sys, csv, datetime, flask_login, math 
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask.wrappers import Response
from workload import *
from util.db_util import *
from util.fwd import *
from util.lustre_ost import *
from util.lwfs_client import *
from auth.user import User
from auth.auth import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'XXXXXXXXXX'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return User.load_user_by_id(id)

@app.route('/')
@flask_login.login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if username == 'XXXXXX':
            if password == 'XXXXXX':
                user = User('admin')
                flask_login.login_user(user)
                return render_template('index.html')
            else:
                return render_template('login.html', msg = 'User or Password Error')
        else:
            login_result = validate_user(username, password)
            if login_result == 1:
                user = User(username)
                flask_login.login_user(user)
                return render_template('index.html')
            else:
                return render_template('login.html', msg = 'User or Password Error!')

@app.route('/logout', methods=['GET'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@flask_login.login_required
@app.route('/lustre_server', methods=['GET'])
def lustre_server():
    return render_template('lustre_server.html')

@flask_login.login_required
@app.route('/lustre_server_data', methods=['POST', 'GET'])
def lustre_server_data():
    UTC = datetime.timedelta(hours = 8)
    if request.method == 'POST':
        time_s = str(datetime.datetime.strptime(request.form['stime'], '%Y-%m-%d %H:%M:%S') - UTC)
        time_e = str(datetime.datetime.strptime(request.form['etime'], '%Y-%m-%d %H:%M:%S') - UTC)

    iobw = query_ost(time_s, time_e) 

    return jsonify(data = iobw)

@flask_login.login_required
@app.route('/lwfs_server', methods=['GET'])
def lwfs_server():
    return render_template('fwd.html')

@flask_login.login_required
@app.route('/lwfs_server_data', methods=['POST', 'GET'])
def lwfs_server_data():
    UTC = datetime.timedelta(hours = 8)
    if request.method == 'POST':
        time_s = str(datetime.datetime.strptime(request.form['stime'], '%Y-%m-%d %H:%M:%S') - UTC)
        time_e = str(datetime.datetime.strptime(request.form['etime'], '%Y-%m-%d %H:%M:%S') - UTC)

    fwd_data  = query_fwd(time_s, time_e) 

    return jsonify(data = fwd_data)

@flask_login.login_required
@app.route('/compute_node', methods=['POST','GET'])
def lwfs_client():
    return render_template('lwfs_client.html')

@flask_login.login_required
@app.route('/lwfs_client_data', methods=['POST','GET'])
def lwfs_client_data():
    s = time.time()
    if request.method == 'POST':
        jobid = request.form['jobid'].strip()
        stime = request.form['start_time'].strip()
        etime = request.form['end_time'].strip()
    username = get_info_by_jobid(jobid)['user']
    cur = int(check_user(username))
    if cur == 0:
        return '0' 
    query_data = get_search_result(jobid, stime, etime)
    #query_data = get_cache(jobid, stime, etime)
    e = time.time()
    return jsonify(data = query_data)

@flask_login.login_required
@app.route('/c_overview')
def c_overview():
    return render_template('c_overview.html')

@app.route('/select_compute_node')
def select_compute_node():
    return render_template('select_compute_node.html')

@flask_login.login_required
@app.route('/forwarding_node')
def forwarding_node():
    return render_template('fwd.html')

@flask_login.login_required
@app.route('/storage_node')
def storage_node():
    return render_template('lustre_server.html')

def check_user(uname):
    if uname == flask_login.current_user.id or flask_login.current_user.id == 'admin':
        return 1
    else:
        return 0

@flask_login.login_required
@app.route('/userspace',methods=['GET','POST'])
def userspace():
    if request.method == 'POST':
        username = request.form['username'].strip()
        stime = request.form['start_time'].strip()
        etime = request.form['end_time'].strip()
        job_name = request.form['job_name'].strip()
        
        cur = check_user(username)
        if cur == 0:
            return render_template('userspace.html', msg = 'Sorry, you are NOT authorized!')

        result = get_jobs(username, stime, etime, job_name, 0)
        job_count = get_user_job_count(username,stime,etime)
        pages = int((job_count + 30 - 1) / 30)
        current_page = 1

        page_info = {}
        page_info['username'] = username
        page_info['jobname'] = job_name
        page_info['stime'] = stime
        page_info['etime'] = etime
        page_info['pages'] = pages
        page_info['current_page'] = current_page
        return render_template('userspace.html', result=result, page_info = page_info, cuser = flask_login.current_user.id)

    else:
        if request.args.get("username"):
            username = request.args.get("username").strip()
            stime = request.args.get("stime").strip()
            etime = request.args.get("etime").strip()
            jobname = request.args.get("jobname").strip()
            pages = request.args.get("pages").strip()
            page = int(request.args.get("page"))

            result = get_jobs(username, stime, etime, jobname, (page-1)*10)
            current_page = page
            page_info = {}
            page_info['username'] = username
            page_info['stime'] = stime
            page_info['etime'] = etime
            page_info['jobname'] = jobname
            page_info['pages'] = int(pages)
            page_info['current_page'] = current_page
            return render_template('userspace.html',result = result, page_info = page_info)
        
        if request.args.get("user"):
            username = request.args.get("user").strip()
            stime = ""
            etime = ""
            jobname = ""
        
            result = get_jobs(username, stime, etime, jobname, 0)
            job_count = get_user_job_count(username, stime, etime)
            pages = int((job_count + 30 - 1) / 30)
            current_page = 1

            page_info = {}
            page_info['username'] = username
            page_info['stime'] = stime
            page_info['etime'] = etime
            page_info['pages'] = pages
            page_info['current_page'] = current_page
            return render_template('userspace.html', result = result, page_info = page_info, user = username)            
             
        return render_template('userspace.html')

@flask_login.login_required
@app.route('/job_detail', methods = ['GET', 'POST'])
def job_detail():
    if request.method == 'POST':
        jobid = request.form['quick_search'].strip()
    else:
        jobid = request.args.get("jobid")

    jobinfo = get_info_by_jobid(jobid)
    if jobinfo:
        cur = check_user(jobinfo['user'])
        if cur == 0:
            return render_template('index.html', msg = "Sorry, you are NOT authorized to view job that do not belong to you.")

        node_count = len(get_job_node_list(jobid))
        nodes = jobinfo['nodelist'].split(',')
        nlen = len(nodes)
        nodelist = []
        section = nlen / 10
        if section == 0:
            nodelist.append(nodes)
        else:
            for i in range(0, section):
                temp = nodes[i * 10 : (i + 1) * 10]
                nodelist.append(temp)
            tail = nlen % 10
            nodelist.append(nodes[section * 10 : section * 10 + tail])
        return render_template('job_detail.html', job = jobinfo, nodelist = nodelist, node_count = node_count)
    else:
        message = "Sorry, there is no such job"
        return render_template('job_detail.html', message = message)

@flask_login.login_required
@app.route('/history_job',methods=['GET','POST'])
def history_job():
    if request.method == 'POST':
        username = request.form['username'].strip()
        jobname = request.form['jobname'].strip()
        
        cur = check_user(username)
        if cur == 0:
            return render_template('history_job.html', msg = 'Sorry, you are NOT authorized!')

        result = get_history_job(username,jobname)
        if result == 'empty':
            return render_template('history_job.html', empty = "Sorry, there is no record you're querying")
        else:   
            return render_template('history_job.html', user = username, result = result)
    else:
        return render_template('history_job.html')

@flask_login.login_required
@app.route('/system_user', methods=['GET'])
def system_user():
    if flask_login.current_user.id != 'admin':
        flask_login.logout_user()
        return render_template('login.html', msg = 'Please login in as Admin')
        
    users = get_users()
    user_num = len(users)
    userlist = []
    if user_num % 10 == 0:
        section = user_num /10
    else:
        section = user_num / 10 + 1

    for i in range(0,section):
        temp = users[i * 10 : (i + 1) * 10]
        userlist.append(temp)

    return render_template('system_user.html', userlist = userlist, user_num = user_num)

if  __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
