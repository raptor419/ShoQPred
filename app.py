# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import keras
from keras import backend as k_backend
from keras import backend as K
import tensorflow
import logging
import os
from logging import Formatter, FileHandler

import numpy as np
import pandas as pd
import mscripts.script
import mscripts.densenet_predictions
import mscripts.lstm_predictions
import mscripts.hilbert_predictions
from flask import Flask, request, render_template
from flask import send_from_directory
from werkzeug.utils import secure_filename

from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
# db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''

UPLOAD_FOLDER = './folder'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
FLASK_DEBUG = 1

# flag is empty for folder upload and is equal to file_upload for single file upload
flag = ""
pre_var = ""
var = ""
fileFeatures = ""
result = ""
to_predict = ""
pred_time = ""
model = ""
dn_filename = ""
age_column = []
gender_column = []
model_dict = {"3": "lstm", "4.5": "snake-dn", "6": "hilbert-dn", "7.5": "lstm", "9": "lstm", "12": "hilbert-dn"}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def transform(text_file_contents):
    return text_file_contents.replace("=", ",")


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/home.html')


@app.route('/about')
def about():
    return render_template('pages/about.html')


@app.route('/authors')
def authors():
    return render_template('pages/authors.html')


@app.route('/demo')
def demo():
    return render_template('pages/authors.html')


@app.route('/git')
def git():
    return render_template('pages/authors.html')


@app.route("/start", methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        global to_predict
        global model
        global pred_time
        global age
        global gender
        to_predict = request.form['to_predict']
        pred_time = request.form['time']
        model = model_dict[pred_time]
        age = request.form['age']
        gender = request.form['gender']
        gender = int(gender)
        print(request)

    if model == 'snake-dn':
        if flag == "file_upload" or flag == "folder_upload":
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], var))
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            return render_template("pages/startDensenets.html", data_frame=df.to_html())
        return render_template("pages/startDensenets.html")

    if model == 'lstm':
        if flag == "file_upload" or flag == "folder_upload":
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], var))
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            return render_template("pages/startDensenets.html", data_frame=df.to_html())
        return render_template("pages/startDensenets.html")

    if model == 'hilbert-dn':
        if flag == "file_upload" or flag == "folder_upload":
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], var))
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            return render_template("pages/startDensenets.html", data_frame=df.to_html())
        return render_template("pages/startDensenets.html")

@app.route("/showPreProcessing", methods=['GET', 'POST'])
def showPreProcessing():
    try:
        if model == 'snake-dn':
            if pre_var == "Processed_Dataset.npy":
                df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
                df = df.loc[:, ~df.columns.str.contains('Unnamed')]
                return render_template("pages/process_snake.html", data_frame=df.to_html())
            return render_template("pages/process_snake.html")

        if model == 'lstm':
            if pre_var == "Processed_Dataset.npy":
                print(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
                df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
                df = df.loc[:, ~df.columns.str.contains('Unnamed')]
                return render_template("pages/process_snake.html", data_frame=df.to_html())
            return render_template("pages/process_snake.html")

        if model == 'hilbert-dn':
            if pre_var == "Processed_Dataset.npy":
                print(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
                df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
                df = df.loc[:, ~df.columns.str.contains('Unnamed')]
                return render_template("pages/process_snake.html", data_frame=df.to_html())
            return render_template("pages/process_snake.html")
    except UnicodeDecodeError:
        return render_template("pages/process_snake.html")


@app.route("/showClassification", methods=['GET', 'POST'])
def showClassification():
    if model == 'snake-dn':
        if result == "prediction_result.csv":
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], result))
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            return render_template("pages/densenet_prediction.html", result=df.to_html())
        return render_template("pages/densenet_prediction.html")
    if model == 'lstm':
        if result == "prediction_result.csv":
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], result))
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            return render_template("pages/densenet_prediction.html", result=df.to_html())
        return render_template("pages/densenet_prediction.html")

    if model == 'hilbert-dn':
        if result == "prediction_result.csv":
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], result))
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            return render_template("pages/densenet_prediction.html", result=df.to_html())
        return render_template("pages/densenet_prediction.html")

@app.route("/pre_process")
def pre_process():
    global pre_var
    if model == 'snake-dn':
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], var))
        df = df.loc[:, ~df.columns.str.contains('Unnamed')]

        # do snake representation via snake
        array_snake = mscripts.script.snake(df)

        pre_var = "Processed_Dataset.npy"
        np.save(os.path.join(app.config['UPLOAD_FOLDER'], pre_var), array_snake)
        return render_template("pages/process_snake.html", array_snake=array_snake)
    if model == "lstm":
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], var))

        df = df.loc[:, ~df.columns.str.contains('Unnamed')]
        df = df.loc[:, ~df.columns.str.contains('ID')]

        # do snake representation via snake
        array_tesnor = mscripts.script.lstmtensor(df)
        # array_tesnor = array_tesnor.loc[:, ~array_tesnor.columns.str.contains('Unnamed')]
        print(array_tesnor)
        pre_var = "Processed_Dataset.npy"
        np.save(os.path.join(app.config['UPLOAD_FOLDER'], pre_var), array_tesnor)
        return render_template("pages/process_snake.html", array_snake=array_tesnor)

    if model == "hilbert-dn":
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], var))
        df = df.loc[:, ~df.columns.str.contains('Unnamed')]

        mscripts.script.hilbert(df)
        os.system('Rscript hilbert/hilbert_data_safeicu.R')

        array_tesnor = "Saved files and made hilbert curves"


        return render_template("pages/process_snake.html", array_snake=array_tesnor)


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    global result
    if model == 'snake-dn':
        array1 = np.load(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
        # print(array1)
        x = np.pad(array1, ((0, 0), (7, 7), (7, 7), (0, 0)), mode='constant')
        img_height = 30
        img_width = 30
        mean_calc1 = np.load('mean_shock_image_mimic.npy')
        std_calc1 = np.load('std_shock_image_mimic.npy')

        x -= mean_calc1
        # Apply featurewise_std_normalization to test-data with statistics from train data
        x /= (std_calc1 + k_backend.epsilon())

        predicted_output = mscripts.densenet_predictions.predict(x)
        filename = dn_filename
        # new_data = pd.DataFrame(columns=['Patient ID', 'Predicted Label'])
        # new_data["Patient ID"] = filename
        # new_data["Predicted Label"] = predicted_output
        new_data = pd.DataFrame({"Patient ID ": [filename],
                                 " Predicted Label": [predicted_output]})
        print(new_data)
        # new_data = new_data.append({filename: predicted_output})
        result = "prediction_result.csv"
        new_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], result))
        return render_template("pages/densenet_prediction.html", result=new_data.to_html(), shock=predicted_output*1000, ns = (1-predicted_output)*1000)

    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
    df = df.loc[:, ~df.columns.str.contains('Unnamed')]
    data1 = df.copy()

    if model == 'lstm':
        array1 = np.load(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
        print(array1)
        mean_calc1 = np.load('mean_shock_image_mimic.npy')
        std_calc1 = np.load('std_shock_image_mimic.npy')

        x -= mean_calc1
        # Apply featurewise_std_normalization to test-data with statistics from train data
        x /= (std_calc1 + k_backend.epsilon())

        predicted_output = SubDirectory.lstm_predictions.predict(x)
        filename = dn_filename
        # new_data = pd.DataFrame(columns=['Patient ID', 'Predicted Label'])
        # new_data["Patient ID"] = filename
        # new_data["Predicted Label"] = predicted_output
        new_data = pd.DataFrame({"Patient ID ": [filename],
                                 " Predicted Label": [predicted_output]})
        print(new_data)
        # new_data = new_data.append({filename: predicted_output})
        
        result = "prediction_result.csv"
        new_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], result))
        return render_template("pages/lstm_prediction.html", result=new_data.to_html())

    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
    df = df.loc[:, ~df.columns.str.contains('Unnamed')]
    data1 = df.copy()


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)


# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    # db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


## Upload helpers

## for uploading single file for densenet
@app.route('/upload_densenet_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        df = pd.read_csv(request.files.get('file'))
        file = request.files['file']
        filename = secure_filename(file.filename)

        hr = request.form['hr_options_file']
        resp = request.form['resp_options_file']
        spo2 = request.form['spo2_options_file']
        bp = request.form['bp_options_file']
        bp_dias = request.form['bp_dias_options_file']

        data2 = df.copy()

        hr_column = data2.iloc[:, int(hr) - 1]
        resp_column = data2.iloc[:, int(resp) - 1]
        spo2_column = data2.iloc[:, int(spo2) - 1]
        final_abp_sys_column = data2.iloc[:, int(bp) - 1]
        final_abp_dias_column = data2.iloc[:, int(bp_dias) - 1]

        list_of_columns = [hr_column, resp_column, spo2_column, final_abp_sys_column, final_abp_dias_column]
        data3 = pd.DataFrame(data=list_of_columns).T
        data3.insert(0, 'ID', filename)

        normal_file_data_frame = pd.DataFrame(data3)
        # renaming columns
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[1]: "X.HR."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[2]: "X.RESP."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[3]: "X.SpO2."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[4]: "final_abp_sys"},
                                      inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[5]: "final_abp_dias"},
                                      inplace=True)

        global dn_filename
        dn_filename = filename
        global var
        var = filename
        normal_file_data_frame.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        global flag
        flag = "file_upload"
        return render_template("pages/startDensenets.html", data_frame=normal_file_data_frame.to_html())


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# for uploading files with gender & age
@app.route('/upload_files_with_age_gender', methods=['POST'])
def upload_files_with_age_gender():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        list_of_normal_files = uploaded_files
        number_of_files = len(list_of_normal_files)
        print(number_of_files)
        normal_file_list = []
        filenames_array = []
        hr = request.form['hr_options_file']
        resp = request.form['resp_options_file']
        spo2 = request.form['spo2_options_file']
        bp = request.form['bp_options_file']
        bp_dias = request.form['bp_dias_options_file']

        age_gender_file = request.files['file_age_gender']
        filename_age_gender = secure_filename(age_gender_file.filename)
        patient_id = request.form['id_options_file']
        gender = request.form['gender_options_file']
        age = request.form['age_options_file']

        j = 0
        global flag
        flag = "folder_upload"
        for f in list_of_normal_files:
            k = f.filename
            data1 = pd.read_csv(f)
            data2 = data1.copy()
            hr_column = data2.iloc[:, int(hr) - 1]
            resp_column = data2.iloc[:, int(resp) - 1]
            spo2_column = data2.iloc[:, int(spo2) - 1]
            final_abp_sys_column = data2.iloc[:, int(bp) - 1]
            final_abp_dias_column = data2.iloc[:, int(bp_dias) - 1]
            # colname = data2.columns[int(bp)-1]

            # Creating a list of the series':
            if to_predict == 'shock':
                list_of_columns = [hr_column, resp_column, spo2_column, final_abp_sys_column, final_abp_dias_column]

            data3 = pd.DataFrame(data=list_of_columns).T

            # Adding another column for the patient ID:
            data3.insert(0, 'ID', k)
            # data3.insert(4, 'BP', final_abp_sys_column)
            normal_file_list.append(data3)

            # add filenames to a list say filenames_array
            filenames_array.append(k)
            j = j + 1

        # getting list of filenames of the files uploaded and removing extensions
        filenames_without_extension = [os.path.splitext(x)[0] for x in filenames_array]
        print(filenames_without_extension)

        global age_column
        global gender_column

        # reading the file input by user for age and gender details
        age_gender_df = pd.read_csv(age_gender_file)
        # extracting specific filenames from the age_gender_df
        age_gender_df_copy = age_gender_df[age_gender_df.iloc[:, int(patient_id) - 1].isin(filenames_without_extension)]
        patient_id_column = age_gender_df_copy.iloc[:, int(patient_id) - 1]
        # getting gender column and replacing gender by 0 for male and 1 for female
        gender_column = age_gender_df_copy.iloc[:, int(gender) - 1].tolist()
        gender_column = [0 if x == 'M' else 1 for x in gender_column]
        # getting age column and replacing age > 90 by 90
        age_column = age_gender_df_copy.iloc[:, int(age) - 1].tolist()
        age_column = np.array(age_column)
        age_column[age_column > 90] = 90

        print(patient_id_column)
        print(age_column)
        print(gender_column)

        normal_file_data_frame = pd.concat(normal_file_list, ignore_index=True)
        normal_file_data_frame = pd.DataFrame(normal_file_data_frame)

        # renaming columns
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[1]: "X.HR."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[2]: "X.RESP."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[3]: "X.SpO2."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[4]: "final_abp_sys"},
                                      inplace=True)
        if to_predict == 'shock':
            normal_file_data_frame.rename(columns={normal_file_data_frame.columns[5]: "final_abp_dias"},
                                          inplace=True)

        global var
        filename = "concatenated_dataset.csv"
        var = filename
        normal_file_data_frame.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template("pages/startModelling.html", data_frame=normal_file_data_frame.to_html())


# for uploading files without gender & age
@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        list_of_normal_files = uploaded_files
        normal_file_list = []
        hr = request.form['hr_options']
        resp = request.form['resp_options']
        spo2 = request.form['spo2_options']
        bp = request.form['bp_options']
        bp_dias = request.form['bp_dias_options']

        j = 0
        global flag
        flag = "folder_upload"
        for f in list_of_normal_files:
            k = f.filename
            data1 = pd.read_csv(f)
            data2 = data1.copy()

            hr_column = data2.iloc[:, int(hr) - 1]
            resp_column = data2.iloc[:, int(resp) - 1]
            spo2_column = data2.iloc[:, int(spo2) - 1]
            final_abp_sys_column = data2.iloc[:, int(bp) - 1]
            final_abp_dias_column = data2.iloc[:, int(bp_dias) - 1]
            # colname = data2.columns[int(bp)-1]

            # Creating a list of the series':
            if to_predict == 'shock':
                list_of_columns = [hr_column, resp_column, spo2_column, final_abp_sys_column, final_abp_dias_column]
            elif to_predict == 'ahe':
                list_of_columns = [hr_column, resp_column, spo2_column, final_abp_sys_column]
            elif to_predict == 'los':
                list_of_columns = [hr_column, resp_column, spo2_column, final_abp_sys_column]

            data3 = pd.DataFrame(data=list_of_columns).T

            # Adding another column for the patient ID:
            data3.insert(0, 'ID', k)
            # data3.insert(4, 'BP', final_abp_sys_column)
            normal_file_list.append(data3)
            j = j + 1

        normal_file_data_frame = pd.concat(normal_file_list, ignore_index=True)
        normal_file_data_frame = pd.DataFrame(normal_file_data_frame)

        # renaming columns
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[1]: "X.HR."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[2]: "X.RESP."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[3]: "X.SpO2."}, inplace=True)
        normal_file_data_frame.rename(columns={normal_file_data_frame.columns[4]: "final_abp_sys"},
                                      inplace=True)
        if to_predict == 'shock':
            normal_file_data_frame.rename(columns={normal_file_data_frame.columns[5]: "final_abp_dias"},
                                          inplace=True)

        global var
        filename = "concatenated_dataset.csv"
        var = filename
        normal_file_data_frame.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template("pages/startModelling.html", data_frame=normal_file_data_frame.to_html())


### Download

@app.route("/download")
def download():
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), var, as_attachment=True)


@app.route("/download_result")
def download_result():
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), result, as_attachment=True)


@app.route("/prediction")
def prediction():
    global result
    if model == 'snake-dn':
        array1 = np.load(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))
        # print(array1)
        x = np.pad(array1, ((0, 0), (7, 7), (7, 7), (0, 0)), mode='constant')
        img_height = 30
        img_width = 30
        mean_calc1 = np.load('mean_std/Shock4.5hr/mean_calc4.5hr.csv.npy')
        std_calc1 = np.load('mean_std/Shock4.5hr/mean_calc4.5hr.csv.npy')

        x -= mean_calc1
        # Apply featurewise_std_normalization to test-data with statistics from train data
        x /= (std_calc1 + k_backend.epsilon())

        predicted_output = mscripts.densenet_predictions.predict(x,pred_time,age,gender)
        filename = dn_filename
        # new_data = pd.DataFrame(columns=['Patient ID', 'Predicted Label'])
        # new_data["Patient ID"] = filename
        # new_data["Predicted Label"] = predicted_output
        new_data = pd.DataFrame({"Patient ID ": [filename],
                                 " Predicted Label": [predicted_output]})
        print(new_data)
        # new_data = new_data.append({filename: predicted_output})
        result = "prediction_result.csv"
        new_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], result))
        return render_template("pages/densenet_prediction.html", result=new_data.to_html(), shock=predicted_output*1000, ns = (1-predicted_output)*1000)

    if model == "lstm":
        array1 = np.load(os.path.join(app.config['UPLOAD_FOLDER'], pre_var))

        x = array1

        print(x,x.shape)

        mean_1 = np.load('mean_std/Shock'+pred_time+'hr/mean_hr_tr.npy')
        mean_2 = np.load('mean_std/Shock'+pred_time+'hr/mean_resp_tr.npy')
        mean_3 = np.load('mean_std/Shock'+pred_time+'hr/mean_sp_tr.npy')
        mean_4 = np.load('mean_std/Shock'+pred_time+'hr/mean_sys_tr.npy')
        mean_5 = np.load('mean_std/Shock'+pred_time+'hr/mean_dias_tr.npy')

        std_1 = np.load('mean_std/Shock'+pred_time+'hr/std_hr_tr.npy')
        std_2 = np.load('mean_std/Shock'+pred_time+'hr/std_resp_tr.npy')
        std_3 = np.load('mean_std/Shock'+pred_time+'hr/std_sp_tr.npy')
        std_4 = np.load('mean_std/Shock'+pred_time+'hr/std_sys_tr.npy')
        std_5 = np.load('mean_std/Shock'+pred_time+'hr/std_dias_tr.npy')

        x_1 = x[0,:]
        x_2 = x[1,:]
        x_3 = x[2,:]
        x_4 = x[3,:]
        x_5 = x[4,:]
        
        x_1 = (x_1 - mean_1)/(std_1)
        x_2 = (x_2 - mean_2)/(std_2)
        x_3 = (x_3 - mean_3)/(std_3)
        x_4 = (x_4 - mean_4)/(std_4)
        x_5 = (x_5 - mean_5)/(std_5)

        x[0] = x_1
        x[1] = x_2
        x[2] = x_3
        x[3] = x_4
        x[4] = x_5

        print(x,x.shape)


        x = np.reshape(x,(1,x.shape[0],x.shape[1]))
        predicted_output = mscripts.lstm_predictions.predict(x,pred_time,age,gender)
        filename = dn_filename
        # new_data = pd.DataFrame(columns=['Patient ID', 'Predicted Label'])
        # new_data["Patient ID"] = filename
        # new_data["Predicted Label"] = predicted_output
        new_data = pd.DataFrame({"Patient ID ": [filename],
                                 " Predicted Label": [predicted_output]})
        print(new_data)
        # new_data = new_data.append({filename: predicted_output})
        
        result = "prediction_result.csv"
        new_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], result))
        return render_template("pages/densenet_prediction.html", result=new_data.to_html(), shock=predicted_output*1000, ns = (1-predicted_output)*1000)

    if model == "hilbert-dn":

        path_tr = 'hilbert/'

        X_tr1 = pd.read_csv(path_tr+"dia_hilbert.csv")
        X_tr2 = pd.read_csv(path_tr+"hr_hilbert.csv")
        X_tr3 = pd.read_csv(path_tr+"rr_hilbert.csv")
        X_tr4 = pd.read_csv(path_tr+"spo_hilbert.csv")
        X_tr5 = pd.read_csv(path_tr+"sys_hilbert.csv")

        X_tr = np.dstack((np.array(X_tr1), np.array(X_tr2), np.array(X_tr3), np.array(X_tr4), np.array(X_tr5)))

        img_height = 16
        img_width = 16

        X_tr = np.reshape(X_tr,(-1,img_height, img_width, 5))

        X_tr = np.array(X_tr)
        X_tr = np.pad(X_tr, ((0,0), (7,7), (7,7), (0,0)), mode='constant')


        img_height = 30
        img_width = 30

        mean_calc1 = np.load('mean_std/Shock'+pred_time+'hr/mean_calc'+pred_time+'hr.csv.npy')
        std_calc1 = np.load('mean_std/Shock'+pred_time+'hr/std_calc'+pred_time+'hr.csv.npy')

        X_tr -= mean_calc1
        X_tr /= (std_calc1 + K.epsilon())

        predicted_output = mscripts.hilbert_predictions.predict(X_tr,pred_time,age,gender)
        filename = dn_filename
        # new_data = pd.DataFrame(columns=['Patient ID', 'Predicted Label'])
        # new_data["Patient ID"] = filename
        # new_data["Predicted Label"] = predicted_output
        new_data = pd.DataFrame({"Patient ID ": [filename],
                                 " Predicted Label": [predicted_output]})
        print(new_data)
        # new_data = new_data.append({filename: predicted_output})
        
        result = "prediction_result.csv"
        new_data.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], result))
        return render_template("pages/densenet_prediction.html", result=new_data.to_html(), shock=predicted_output*1000, ns = (1-predicted_output)*1000)

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
