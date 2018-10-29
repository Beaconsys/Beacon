# -*- coding: utf-8 -*-
# Author: swstorage

import os, sys, csv, datetime, flask_login
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
app.config['SECRET_KEY'] = 'm5DFi8AS34bnG'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'


@app.route('/')
@flask_login.login_required
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(id):
    return User.get_id(id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login2.html')
    else:
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        login_result = validate_user(username, password)
        if login_result == 1:
            user = User(username)
            flask_login.login_user(user)
            return render_template('index.html')
        else:
            return str(login_result)
    #if username == 'admin' and password == 'admin':
    #session['username'] = username
    #return render_template('index.html', username = username)
    #else:
    #    error = 'Invalid username/password'
    #    return render_template('login2.html', error = error)


@app.route('/logout', methods=['GET'])
@flask_login.login_required
def logout():
    #session.pop('username', None)
    flask_login.logout_user()
    return redirect(url_for('login'))


@app.route('/lustre_server', methods=['GET'])
def lustre_server():
    return render_template('lustre_server.html')


@app.route('/lustre_server_data', methods=['POST', 'GET'])
def lustre_server_data():
    UTC = datetime.timedelta(hours=8)
    if request.method == 'POST':
        time_s = str(
            datetime.datetime.strptime(request.form['stime'],
                                       '%Y-%m-%d %H:%M:%S') - UTC)
        time_e = str(
            datetime.datetime.strptime(request.form['etime'],
                                       '%Y-%m-%d %H:%M:%S') - UTC)
        print 'Start time : ' + str(time_s)
        print 'End time : ' + str(time_e)

    iobw = mcache(time_s, time_e, 0)
    #iobw = mcache(time_s, time_e)

    return jsonify(data=iobw)


@app.route('/lwfs_server', methods=['GET'])
def lwfs_server():
    return render_template('fwd.html')


@app.route('/lwfs_server_data', methods=['POST', 'GET'])
def lwfs_server_data():
    UTC = datetime.timedelta(hours=8)
    if request.method == 'POST':
        time_s = str(
            datetime.datetime.strptime(request.form['stime'],
                                       '%Y-%m-%d %H:%M:%S') - UTC)
        time_e = str(
            datetime.datetime.strptime(request.form['etime'],
                                       '%Y-%m-%d %H:%M:%S') - UTC)
        print 'Start time : ' + str(time_s)
        print 'End time : ' + str(time_e)

    fwd_data = query_fwd(time_s, time_e)

    return jsonify(data=fwd_data)


@app.route('/compute_node', methods=['POST', 'GET'])
def lwfs_client():
    return render_template('lwfs_client.html')


@app.route('/lwfs_client_data', methods=['POST', 'GET'])
def lwfs_client_data():
    s = time.time()
    if request.method == 'POST':
        jobid = request.form['jobid'].strip()
        stime = request.form['start_time'].strip()
        etime = request.form['end_time'].strip()
    query_data = get_search_result(jobid, stime, etime)
    #query_data = get_cache(jobid, stime, etime)
    e = time.time()
    print 'Running time : ' + str(round(e - s, 2)) + ' s.'
    return jsonify(data=query_data)


@app.route('/c_overview')
def c_overview():
    return render_template('c_overview.html')


@app.route('/c_iops')
def c_iops():
    return render_template('c_iops.html')


@app.route('/c_iobandwidth')
def c_iobandwidth():
    return render_template('c_iobandwidth.html')


@app.route('/select_compute_node')
def select_compute_node():
    return render_template('select_compute_node.html')


@app.route('/c_metadata')
def c_metadata():
    return render_template('c_metadata.html')


@app.route('/c_datadistribution')
def c_datadistribution():
    return render_template('c_datadistribution.html')


@app.route('/c_activeprocess')
def c_activeprocess():
    return render_template('c_activeprocess.html')


@app.route('/forwarding_node')
def forwarding_node():
    return render_template('fwd.html')


@app.route('/storage_node')
def storage_node():
    return render_template('lustre_server.html')


@app.route('/workload', methods=['GET', 'POST'])
def workload():
    if request.method == 'POST':
        stime = request.form['start_time']
        etime = request.form['end_time']
        workload = query_by_date(stime, etime)
        draw_workload()

        job_count = workload[0]
        job_corehour = workload[1]

        jmax = max(job_count)
        jmin = min(job_count)
        jsum = sum(job_count)
        javg = jsum / len(job_count)
        cmax = round(max(job_corehour), 1)
        cmin = round(min(job_corehour), 1)
        csum = round(sum(job_corehour), 1)
        cavg = round(csum / len(job_corehour), 1)

        result = {}
        result['jmax'] = jmax
        result['jmin'] = jmin
        result['jsum'] = jsum
        result['javg'] = javg
        result['cmax'] = cmax
        result['cmin'] = cmin
        result['csum'] = csum
        result['cavg'] = cavg

        return render_template(
            'workload.html',
            job_count=job_count,
            job_corehour=job_corehour,
            result=result)
    else:
        return render_template('workload.html')


@app.route('/userspace', methods=['GET', 'POST'])
def userspace():
    if request.method == 'POST':
        username = request.form['username'].strip()
        stime = request.form['start_time'].strip()
        etime = request.form['end_time'].strip()
        job_name = request.form['job_name'].strip()

        result = get_jobs(username, stime, etime, job_name, 0)
        job_count = get_user_job_count(username, stime, etime)
        #print job_count
        if job_count % 30 == 0:
            pages = job_count / 30
        else:
            pages = job_count / 30 + 1

        #print pages
        current_page = 1
        page_info = {}
        page_info['username'] = username
        page_info['stime'] = stime
        page_info['etime'] = etime
        page_info['pages'] = pages
        page_info['current_page'] = current_page
        print page_info
        return render_template(
            'userspace.html', result=result, page_info=page_info)

    else:
        if request.args.get("username"):
            username = request.args.get("username").strip()
            stime = request.args.get("stime").strip()
            etime = request.args.get("etime").strip()
            pages = request.args.get("pages").strip()
            page = int(request.args.get("page"))

            result = get_jobs(username, stime, etime, (page - 1) * 10)
            current_page = page
            page_info = {}
            page_info['username'] = username
            page_info['stime'] = stime
            page_info['etime'] = etime
            page_info['pages'] = int(pages)
            page_info['current_page'] = current_page
            print page_info
            return render_template(
                'userspace.html', result=result, page_info=page_info)

        print request.args.get("user")
        if request.args.get("user"):
            username = request.args.get("user").strip()
            stime = ""
            etime = ""

            result = get_jobs(username, stime, etime, 0)
            job_count = get_user_job_count(username, stime, etime)
            #print job_count
            if job_count % 30 == 0:
                pages = job_count / 30
            else:
                pages = job_count / 30 + 1

            #print pages
            current_page = 1
            page_info = {}
            page_info['username'] = username
            page_info['stime'] = stime
            page_info['etime'] = etime
            page_info['pages'] = pages
            page_info['current_page'] = current_page
            print page_info
            return render_template(
                'userspace.html',
                result=result,
                page_info=page_info,
                user=username)

        return render_template('userspace.html')


@app.route('/job_detail', methods=['GET', 'POST'])
def job_detail():
    if request.method == 'POST':
        jobid = request.form['quick_search'].strip()
        print jobid
        if get_job_by_idd(jobid):
            job = get_job_by_idd(jobid)[0]
            node = job[15].split(',')
            nodecount = 0
            for n in node:
                if "-" in n:
                    n1 = n.split("-")[0]
                    n2 = n.split("-")[1]
                    nodecount += int(n2) - int(n1) + 1
                else:
                    nodecount += 1

            #print node
            nlen = len(node)
            #print nlen
            nodelist = []
            section = nlen / 10
            #print section
            if section == 0:
                nodelist.append(node)
            else:
                for i in range(0, section):
                    temp = node[i * 10:(i + 1) * 10]
                    nodelist.append(temp)
                tail = nlen % 10
                nodelist.append(node[section * 10:section * 10 + tail])

            #print nodelist
            return render_template(
                'job_detail.html',
                job=job,
                nodelist=nodelist,
                nodecount=nodecount)
        else:
            message = "Sorry,there is no such job"
            return render_template('job_detail.html', message=message)
    else:
        jobid = request.args.get("jobid")
        if jobid == '':
            return render_template('index.html')
        if get_job_by_idd(jobid):
            job = get_job_by_idd(jobid)[0]
            node = job[15].split(',')
            nodecount = 0
            for n in node:
                if "-" in n:
                    n1 = n.split("-")[0]
                    n2 = n.split("-")[1]
                    nodecount += int(n2) - int(n1) + 1
                else:
                    nodecount += 1

            #print node
            nlen = len(node)
            #print nlen
            nodelist = []
            section = nlen / 10
            #print section
            if section == 0:
                nodelist.append(node)
            else:
                for i in range(0, section):
                    temp = node[i * 10:(i + 1) * 10]
                    nodelist.append(temp)
                tail = nlen % 10
                nodelist.append(node[section * 10:section * 10 + tail])

            #print nodelist
            return render_template(
                'job_detail.html',
                job=job,
                nodelist=nodelist,
                nodecount=nodecount)
        else:
            message = "Sorry,there is no such job"
            #return render_template('job_detail.html',message=message)


@app.route('/history_job', methods=['GET', 'POST'])
def history_job():
    if request.method == 'POST':
        username = request.form['username'].strip()
        jobname = request.form['jobname'].strip()

        result = get_history_job(username, jobname)
        if result == "empty":
            print "RESULT IS EMPTY"
            return render_template(
                'history_job.html',
                empty="Sorry, there is no record you're querying")
        else:
            return render_template(
                'history_job.html', user=username, result=result)
    else:
        return render_template('history_job.html')


@app.route('/system_user', methods=['GET', 'POSt'])
def system_user():
    users = get_users()
    user_num = len(users)
    userlist = []
    if user_num % 10 == 0:
        section = user_num / 10
    else:
        section = user_num / 10 + 1

    for i in range(0, section):
        temp = users[i * 10:(i + 1) * 10]
        userlist.append(temp)

    return render_template(
        'system_user.html', userlist=userlist, user_num=user_num)


@app.route('/c_error', methods=['GET', 'POST'])
def c_error():
    if request.args.get('error_file'):
        error_file = request.args.get('error_file')
        error_info = []
        for line in open('../log/' + error_file, 'r'):
            error_info.append(line)

        if len(error_info) >= 2:
            if 'None' in error_info[1]:
                error_info[
                    1] = 'Sorry, the job is still RUNNING. Please wait until it finishes'
        return render_template('c_error.html', error_info=error_info)

    return render_template('c_error.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
