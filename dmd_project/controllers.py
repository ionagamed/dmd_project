from flask import Blueprint, render_template, request

from dmd_project import models


queries = Blueprint('queries', 'queries')


@queries.route('/')
def queries_index():
    return render_template('layout.html')


@queries.route('/query/1')
def query_1_page():
    return render_template(
        'query/1.html',
        result=models.query_1()
    )


@queries.route('/query/2', methods=['GET', 'POST'])
def query_2_page():
    if request.method == 'GET':
        return render_template('query/2.html')
    elif request.method == 'POST':
        return render_template(
            'query/2.html',
            result=models.query_2(request.form['date'])
        )


@queries.route('/query/3')
def query_3_page():
    return render_template(
        'query/3.html',
        result=models.query_3()
    )


@queries.route('/query/4', methods=['GET', 'POST'])
def query_4_page():
    customer_choices = models.customer_choices()
    if request.method == 'GET':
        return render_template('query/4.html', customers=customer_choices)
    elif request.method == 'POST':
        return render_template(
            'query/4.html',
            customers=customer_choices,
            result=models.query_4(int(request.form['customer_id']))
        )


@queries.route('/query/5', methods=['GET', 'POST'])
def query_5_page():
    if request.method == 'GET':
        return render_template('query/5.html')
    elif request.method == 'POST':
        return render_template(
            'query/5.html',
            result=models.query_5(request.form['date'])
        )


@queries.route('/query/6')
def query_6_page():
    return render_template(
        'query/6.html',
        r=models.query_6()
    )


@queries.route('/query/7')
def query_7_page():
    return render_template(
        'query/7.html',
        result=models.query_7()
    )


@queries.route('/query/8', methods=['GET', 'POST'])
def query_8_page():
    if request.method == 'GET':
        return render_template('query/8.html')
    elif request.method == 'POST':
        return render_template(
            'query/8.html',
            result=models.query_8(request.form['date'])
        )


@queries.route('/query/9')
def query_9_page():
    return render_template(
        'query/9.html',
        result=models.query_9()
    )


@queries.route('/query/10')
def query_10_page():
    return render_template(
        'query/10.html',
        result=models.query_10()
    )


@queries.route('/custom', methods=['GET', 'POST'])
def custom_query():
    if request.method == 'GET':
        return render_template('query/custom.html')
    elif request.method == 'POST':
        return render_template(
            'query/custom.html',
            result=models.custom(request.form['query'])
        )
