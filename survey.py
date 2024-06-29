from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)


# Primary key를 현재시간으로 생성하기 위한 함수 
def get_current_time_id():
    # 현재 시간을 정수로 변환하여 반환 (밀리초까지)
    return int(datetime.now().timestamp() * 1000)


# 각 metirc별 결과 값을 update할때 사용할 키 값
primary_key = get_current_time_id()  

# SQLite 데이터베이스 연결
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

# 데이터베이스에 테이블 생성
def create_table():
    conn = create_connection('survey.db')
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS survey (
                    id INTEGER Primary key,
                    email TEXT,
                    gender TEXT,
                    age INTEGER,
                    security_experience INTEGER,
                    m1_score INTEGER,
                    m2_basic_points INTEGER,
                    m2_additional_points INTEGER,
                    m2_score INTEGER,
                    m3_basic_points INTEGER,
                    m3_basic_points2 INTEGER,
                    m3_additional_points INTEGER,
                    m3_score INTEGER,
                    final_score INTEGER
                )
            ''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()



# 첫 번째 페이지: 시작 양식을 표시    
@app.route('/')
def survey_form():
    return render_template('survey_info.html')

# 시작양식 DB입력 후 Metrics1으로 페이지 전환
@app.route('/submit_info', methods=['POST'])
def submit_info():
    if request.method == 'POST':
        email = request.form['email']
        gender = request.form['gender']
        age = request.form['age']
        security_experience = request.form['security_experience']

        conn = create_connection('survey.db')
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute('INSERT INTO survey (id, email, gender, age, security_experience) VALUES (?, ?, ?, ?, ?)',
                            (primary_key, email, gender, age, security_experience))
                conn.commit()
                conn.close()
                print('submit_info finish!')
                return metrics1_page() # Metrics1 화면으로 이동
            except sqlite3.Error as e:
                print(f"데이터베이스 오류: {e}")
            finally:
                conn.close()
        else:
            return '데이터베이스 연결에 문제가 발생했습니다.'


# 설문조사 결과 조회 페이지
@app.route('/survey_results')
def survey_results():
    conn = create_connection('survey.db')
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute('SELECT * FROM survey')
            rows = cur.fetchall()
            conn.close()
            return render_template('survey_results.html', rows=rows)
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()
    else:
        return '데이터베이스 연결에 문제가 발생했습니다.'

# Mtrics-1 =============================================================

# SQLite 데이터베이스에서 데이터 조회
def fetch_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM sheet1")  # 테이블 이름을 적절하게 변경하세요
    rows = cur.fetchall()
    return rows

# 데이터베이스 경로
database = "questionnaires.db"  # 데이터베이스 경로를 적절하게 수정하세요


# 데이터베이스 연결
conn = create_connection(database)

if conn is not None:
    cur = conn.cursor()
    cur.execute("SELECT * FROM sheet1")  # 쿼리를 통해 데이터 가져오기
    rows = cur.fetchall()
    data_list_sheet1 = []
    for row in rows:
        data_list_sheet1.append({
            'number': row[0],
            'questions': row[1],
            'choose1': row[2],
            'choose2': row[3],
            'choose3': row[4],
            'choose4': row[5],
            'correct_answer': row[6],
            'level': row[7]
        })
#Metircs-1 문제출제 페이지
@app.route('/metrics1_page', methods=['GET', 'POST'])
def metrics1_page():
        question = create_question(data_list_sheet1)
        return render_template('metrics-1.html', question=question)

#Metircs-1 측정값 정리 
@app.route('/submit_metrics_1', methods=['GET', 'POST'])
def submit_metrics_1():
    if request.method == 'POST':
        selected_answers = []  # 선택지를 담을 리스트
        for i in range(len(data_list_sheet1)):
            answer_key = 'answer' + str(i+1)
            selected_choices = request.form.getlist(answer_key)  # 선택지들을 리스트로 받아옴
            selected_answer = ','.join(selected_choices)  # 선택지들을 하나의 문자열로 합치기
            selected_answers.append(selected_answer)  # 선택지를 리스트에 추가

        print("M1_Selected answers:", selected_answers)
        score = calculate_score(selected_answers, data_list_sheet1)
        print("M1_Score:", score)

        conn = create_connection('survey.db')
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute('UPDATE survey SET m1_score = ? WHERE id = ?', (score, primary_key))
                conn.commit() 
                print('submit_metircs_1 finish!')
                return redirect(url_for('metrics2_page')) # Metrics2_page 호출 
            except sqlite3.Error as e:
                print(f"데이터베이스 오류: {e}")
            finally:
                conn.close()
    else:
        return '데이터베이스 연결에 문제가 발생했습니다.'
 
    


# Metrics-1 정답 체크하기
def calculate_score(selected_answers, data_list):
    # 선택한 답변과 정답을 비교하여 점수 계산
    score = 0
    for i, selected in enumerate(selected_answers):
        if 'correct_answer' in data_list[i]:  # 'correct_answer' 키가 있는지 확인
            correct_answer = str(data_list[i]['correct_answer'])
            if selected == correct_answer:
                level = data_list[i].get('level', '')
                if level == 'L':
                    score += 1
                elif level == 'M':
                    score += 3
                elif level == 'H':
                    score += 5
    score = score * (100/28) #100점 만점으로 환산 
    return score

# 질문 출제하기
def create_question(data):
    question = []
    for entry in data:
        item = {}
        item['number'] = entry['number']
        item['questions'] = entry['questions']
        item['choose1'] = entry['choose1']
        item['choose2'] = entry['choose2']
        if 'choose3' in entry and entry['choose3']:
            item['choose3'] = entry['choose3']
        if 'choose4' in entry and entry['choose4']:
            item['choose4'] = entry['choose4']
        if 'correct_answer' in entry and entry['correct_answer']:
            item['correct_answer'] = entry['correct_answer']
        if 'level' in entry and entry['level']:
            item['level'] = entry['level']
        question.append(item)

    return question

# Mtrics-2 ====================================================================

# 데이터베이스 경로
database = "questionnaires.db"  

# 데이터베이스 연결
conn = create_connection(database)
if conn is not None:
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sheet2")  # 쿼리를 통해 데이터 가져오기
        rows = cur.fetchall()
        data_list_sheet2 = []
        for row in rows:
            data_list_sheet2.append({
                'category': row[0],
                'maker': row[1],
                'product': row[2],
                'CC': row[3]
            })
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        conn.close()


        
# Metrics-2 카테고리 선택 페이지 
@app.route('/metrics2_page', methods=['GET', 'POST'])
def metrics2_page():
    conn = create_connection(database)
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT category FROM sheet2 ORDER BY category ASC")  # 카테고리 데이터 가져오기
            rows = cur.fetchall()
            categories = [row[0] for row in rows]  # 카테고리 목록 가져오기
            conn.close()

            return render_template('metrics-2.html', categories=categories)
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()
    else:
        return '데이터베이스 연결에 문제가 발생했습니다.'

# 선택된 카테고리 메이커 목록 가져오기
def get_makers(selected_category):
    conn = create_connection('questionnaires.db')
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT maker FROM sheet2 WHERE category = ?", (selected_category,))
            rows = cur.fetchall()
            makers = [row[0] for row in rows]
            conn.close()
            return makers
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()
    else:
        print("데이터베이스 연결에 문제가 발생했습니다.")

# 선택한 메이커 목록 가져오기
@app.route('/select_maker', methods=['POST'])
def select_maker():
    data = request.json
    selected_category = data['selected_category']

    # 선택한 카테고리에 해당하는 메이커들 가져오기
    makers = get_makers(selected_category)
    return jsonify({'makers': makers})

# 제품 목록 가져오기
def get_products(selected_category, selected_maker):
    conn = create_connection('questionnaires.db')
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT product FROM sheet2 WHERE category = ? AND maker = ?", (selected_category, selected_maker))
            rows = cur.fetchall()
            products = [row[0] for row in rows]
            conn.close()
            return products
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()
    else:
        print("데이터베이스 연결에 문제가 발생했습니다.")

@app.route('/select_product', methods=['POST'])
def select_product():
    data = request.json
    selected_category = data.get('selected_category')
    selected_maker = data.get('selected_maker')

    # 해당 카테고리와 메이커에 속하는 제품들 가져오기
    products = get_selected_products(selected_category, selected_maker)

    return jsonify({'products': products})

def get_selected_products(selected_category, selected_maker):
    conn = create_connection('questionnaires.db')
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT product FROM sheet2 WHERE category = ? AND maker = ?", (selected_category, selected_maker))
            rows = cur.fetchall()
            products = [row[0] for row in rows]
            conn.close()
            return products
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()
    else:
        print("데이터베이스 연결에 문제가 발생했습니다.")


# Metrics-2에서 선택한 제품들의 'CC' 인증 여부 확인 후 점수 계산하여 데이터베이스에 입력
@app.route('/submit_metrics_2', methods=['POST'])
def submit_metrics_2():
    if request.method == 'POST':
        selected_products_data = request.get_json()  # Metrics-2에서 선택한 제품들 받기
        selected_products = selected_products_data.get('selected_products')
        print("M2_Selected Products:", selected_products)

        # 'CC' 인증을 받은 제품의 수 계산
        cc_certified_count = 0
        for product in selected_products:
            cc_value = fetch_cc_value_from_db(product)  # 데이터베이스에서 해당 제품의 'CC' 값을 가져옴
            if cc_value == 'O':
                cc_certified_count += 1  # 'CC' 인증 시, 인증된 제품의 수를 증가시킴

        # 선택한 제품 중 'CC' 인증을 받은 제품의 수를 전체 선택한 제품 수로 나누어 점수 계산
        total_selected_products = len(selected_products)
        if total_selected_products > 0:
            score = (cc_certified_count / total_selected_products) * 100  # 점수 계산
        else:
            score = 0  # 선택한 제품이 없을 경우 점수를 0으로 설정

        print("CC Certified Count:", cc_certified_count)
        print("Total Selected Products:", total_selected_products)
        print("M2_basic_points :", score)

        # 데이터베이스에 점수 입력
        conn = create_connection('survey.db')
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute('UPDATE survey SET m2_basic_points = ? WHERE id = ?', (score, primary_key))
                conn.commit()
                conn.close()
                #return redirect(url_for('metrics-2-add.html'))  # 점수를 입력한 뒤 metrics-2 추가문제로 이동
                print('submit_metrics_2 finish!')
                return jsonify({"status": "success", "nextStep": "ask"}) 
            except sqlite3.Error as e:
                print(f"데이터베이스 오류: {e}")
            finally:
                conn.close()
        else:
            return '데이터베이스 연결에 문제가 발생했습니다.'



def fetch_cc_value_from_db(product):
    conn = create_connection('questionnaires.db')  
    
    if conn is not None:
        try:
            cur = conn.cursor()
            # 제품 이름을 기반으로 'CC' 값을 가져오는 쿼리
            cur.execute('SELECT CC FROM sheet2 WHERE product = ?', (product,))
            # 결과 가져오기
            result = cur.fetchone()
            print("product? : ", product)
            print("cc result ? " , result) 

            if result:
                cc_value = result[0]
                conn.close()
                return cc_value
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()

    return None



# Mtrics-2 추가문제 풀이 ====================================================================    
# metrics-2 추가문제(sheet3) 데이터베이스 연결
conn = create_connection(database)

if conn is not None:
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sheet3")  # 쿼리를 통해 데이터 가져오기
        rows = cur.fetchall()
        data_list_sheet3 = []
        for row in rows:
            data_list_sheet3.append({
                'number': row[0],
                'questions': row[1],
                'choose1': row[2],
                'choose2': row[3],
                'choose3': row[4],
                'choose4': row[5],
                'correct_answer': row[6],
                'level': row[7]
            })
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        conn.close()

# 추가 문제 페이지로 이동하는 라우트
@app.route('/metrics2_additional_page')
def metrics2_additional_page():
    # 추가 문제 페이지를 렌더링하는 로직
    question = create_question(data_list_sheet3)
    return render_template('metrics-2-add.html', question=question)

#Metircs-2 측정값 정리 
@app.route('/submit_metrics_2_add', methods=['GET', 'POST'])
def submit_metrics_2_add():
    if request.method == 'POST':
        selected_answers = []  # 선택지를 담을 리스트
        for i in range(len(data_list_sheet3)):
            answer_key = 'answer' + str(i+1)
            selected_choices = request.form.getlist(answer_key)  # 선택지들을 리스트로 받아옴
            selected_answer = ','.join(selected_choices)  # 선택지들을 하나의 문자열로 합치기
            selected_answers.append(selected_answer)  # 선택지를 리스트에 추가

        print("M2_add_Selected answers:", selected_answers)
        score = calculate_score(selected_answers, data_list_sheet3)
        print("M2_add_point:", score)

        conn = create_connection('survey.db')
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute('UPDATE survey SET m2_additional_points = ? WHERE id = ?', (score, primary_key)) 
                update_m2_score(primary_key) # M2_score 평균내서 업데이트 시키기
                conn.commit() 
                print('submit_metrics_2_add finish!')
                
                return redirect(url_for('metrics3_page')) # Metrics3_page 호출 
            except sqlite3.Error as e:
                print(f"데이터베이스 오류: {e}")
            finally:
                conn.close()
    else:
        return '데이터베이스 연결에 문제가 발생했습니다.'


# M2_score 총점 계산
def update_m2_score(flag):
    print("update_m2_score start !")
    # 데이터베이스 연결
    conn = create_connection('survey.db')
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute('SELECT m2_basic_points, m2_additional_points FROM survey WHERE id = ?', (flag, )) 
            row = cur.fetchone()

            if row is not None:
                m2_basic_points, m2_additional_points = row
                # 평균 점수 계산
                if m2_additional_points is not None:
                    m2_score = (m2_basic_points + m2_additional_points) / 2
                else:
                    m2_score = m2_basic_points

                # m2_score 업데이트
                cur.execute("UPDATE survey SET m2_score = ? WHERE id = ?", (m2_score, flag))
                conn.commit()
                print("Update_m2_score finish! ")    
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()
    else:
        print("데이터베이스 연결에 문제가 발생했습니다.")


# Metrics-3 ====================================================================
# Metrics-3  페이지 

# 데이터베이스 연결
conn = create_connection('questionnaires.db')

if conn is not None:
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sheet4")  # 쿼리를 통해 데이터 가져오기
        rows = cur.fetchall()
        data_list_sheet4 = []
        for row in rows:
            data_list_sheet4.append({
                'number': row[0],
                'questions': row[1],
                'choose1': row[2],
                'choose2': row[3],
                'choose3': row[4],
                'choose4': row[5],
                'choose5': row[6],
                'choose6': row[7],
                'choose7': row[8]
            })
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        conn.close()

#Metircs-3 호기심 페이지
@app.route('/metrics3_page', methods=['GET', 'POST'])
def metrics3_page():
    update_m2_score(primary_key) # Metrics-3으로 가기전에 M2_score 평균내서 업데이트 시키기 
    question = create_question3(data_list_sheet4)
    return render_template('metrics-3-1.html', question=question)


# 질문 출제하기
def create_question3(data):
    question = []
    for entry in data:
        item = {}
        item['number'] = entry['number']
        item['questions'] = entry['questions']
        item['choose1'] = entry['choose1']
        item['choose2'] = entry['choose2']
        if 'choose3' in entry and entry['choose3']:
            item['choose3'] = entry['choose3']
        if 'choose4' in entry and entry['choose4']:
            item['choose4'] = entry['choose4']
        if 'choose5' in entry and entry['choose5']:
            item['choose5'] = entry['choose5']
        if 'choose6' in entry and entry['choose6']:
            item['choose6'] = entry['choose6']
        if 'choose7' in entry and entry['choose7']:
            item['choose7'] = entry['choose7']
        question.append(item)

    return question



#Metircs-3-1 측정값 정리 
@app.route('/submit_metrics_3_1', methods=['GET', 'POST'])
def submit_metrics_3_1():
    if request.method == 'POST':
        selected_answers = []  # 선택지를 담을 리스트
        for i in range(len(data_list_sheet4)):
            answer_key = 'answer' + str(i+1)
            selected_choices = request.form.getlist(answer_key)  # 선택지들을 리스트로 받아옴
            selected_answer = ','.join(selected_choices)  # 선택지들을 하나의 문자열로 합치기
            selected_answers.append(selected_answer)  # 선택지를 리스트에 추가

        #print("M3_1_Selected answers :", selected_answers)
        score = calculate_score3(selected_answers, data_list_sheet4)
        print("M3_basic_point:", score)

        conn = create_connection('survey.db')
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute('UPDATE survey SET m3_basic_points = ? WHERE id = ?', (score, primary_key))
                conn.commit() 
                print('submit_metrics_3_1 finish!')
                return redirect(url_for('metrics3_2_page')) # Metrics3_@_page 호출 
            except sqlite3.Error as e:
                print(f"데이터베이스 오류: {e}")
            finally:
                conn.close()
    else:
        return '데이터베이스 연결에 문제가 발생했습니다.'
 
 
# Metrics-3-1 점수 계산하기
def calculate_score3(selected_answers, data_list):
    # 선택한 답변과 정답을 비교하여 점수 계산
    score = 0
    for i, selected in enumerate(selected_answers):
        try:
            score += int(selected)
        except ValueError:
            score += 0  # selected_answers[i] 값이 없거나 정수로 변환할 수 없는 경우, 0을 더합니다.
        
    if score != 0:
        score = (168/score) * (50/7) #50점 만점으로 환산
    else:
        score = 0 
    return score



# 데이터베이스 연결
conn = create_connection('questionnaires.db')

if conn is not None:
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sheet5")  # 쿼리를 통해 데이터 가져오기
        rows = cur.fetchall()
        data_list_sheet5 = []
        for row in rows:
            data_list_sheet5.append({
                'number': row[0],
                'questions': row[1],
                'choose1': row[2],
                'choose2': row[3],
                'choose3': row[4],
                'choose4': row[5],
                'choose5': row[6]
            })
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        conn.close()


#Metircs_3_2 정보처리지식 페이지
@app.route('/metrics3_2_page', methods=['GET', 'POST'])
def metrics3_2_page():
    question = create_question3(data_list_sheet5)
    return render_template('metrics-3-2.html', question=question)

#Metircs-3-2 측정값 정리 
@app.route('/submit_metrics_3_2', methods=['POST'])
def submit_metrics_3_2():
    
    if request.method == 'POST':
        data = request.json
        selected_answers = data.get('selected_answers', [])

        print("M3_2_Selected answers:", selected_answers)
        score = calculate_score4(selected_answers, data_list_sheet5)
        print("M3_basic_point2 :", score)

        conn = create_connection('survey.db')
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute('UPDATE survey SET m3_basic_points2 = ? WHERE id = ?', (score, primary_key))
                conn.commit() 
                print('submit_metrics_3_2 finish!')
                # 추가문제를 풀지 끝낼지 선택 
                
                return jsonify({"status": "success", "nextStep": "ask"}) 
            except sqlite3.Error as e:
                print(f"데이터베이스 오류: {e}")
            finally:
                conn.close() 
        else:
            return '데이터베이스 연결에 문제가 발생했습니다.'

# Metrics-3-2 점수 계산하기 
def calculate_score4(selected_answers, data_list):
    # 선택한 답변과 정답을 비교하여 점수 계산
    score = 0
    for i, selected in enumerate(selected_answers):
        score += int(selected_answers[i])
        
    score = (score/45) * 50 #50점 만점으로 환산 
    return score

# Mtrics-3 추가문제 풀이 ====================================================================    
# metrics-3 추가문제(sheet6) 데이터베이스 연결
conn = create_connection('questionnaires.db')

if conn is not None:
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sheet6")  # 쿼리를 통해 데이터 가져오기
        rows = cur.fetchall()
        data_list_sheet6 = []
        for row in rows:
            data_list_sheet6.append({
                'number': row[0],
                'questions': row[1],
                'choose1': row[2],
                'choose2': row[3],
                'choose3': row[4],
                'choose4': row[5],
                'correct_answer': row[6],
                'level': row[7]
            })
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        conn.close()


# 추가 문제 페이지로 이동하는 라우트
@app.route('/metrics3_additional_page')
def metrics3_additional_page():
    # 추가 문제 페이지를 렌더링하는 로직
    question = create_question(data_list_sheet6)
    return render_template('metrics-3-add.html', question=question)


#Metircs-3-add 측정값 정리 
@app.route('/submit_metircs_3_additional', methods=['GET', 'POST'])
def submit_metircs_3_additional():
    if request.method == 'POST':
        selected_answers = []  # 선택지를 담을 리스트
        for i in range(len(data_list_sheet6)):
            answer_key = 'answer' + str(i+1)
            selected_choices = request.form.getlist(answer_key)  # 선택지들을 리스트로 받아옴
            selected_answer = ','.join(selected_choices)  # 선택지들을 하나의 문자열로 합치기
            selected_answers.append(selected_answer)  # 선택지를 리스트에 추가

        print("M3_add_Selected answers:", selected_answers)
        score = calculate_score(selected_answers, data_list_sheet6)
        print("M3_add_points:", score)

        conn = create_connection('survey.db')
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute('UPDATE survey SET m3_additional_points = ? WHERE id = ?', (score, primary_key))
                conn.commit() 
                print('submit_metrics_3_add finish!')
                return redirect(url_for('result_page')) # result_page 호출 
            except sqlite3.Error as e:
                print(f"데이터베이스 오류: {e}")
            finally:
                conn.close()
    else:
        return '데이터베이스 연결에 문제가 발생했습니다.'


# M3_score 총점 계산
def update_m3_score(flag):
    print("update_m3_score start !")
    # 데이터베이스 연결
    conn = create_connection('survey.db')
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute('SELECT m3_basic_points, m3_basic_points2, m3_additional_points FROM survey WHERE id = ?', (flag, )) 
            row = cur.fetchone()

            if row is not None:
                m3_basic_points, m3_basic_points2, m3_additional_points = row
                # 평균 점수 계산
                if m3_additional_points is not None:
                    m3_score = ((m3_basic_points + m3_basic_points)/2 + m3_additional_points) / 2
                else:
                    m3_score = (m3_basic_points + m3_basic_points2)/2

                # m3_score 업데이트
                cur.execute("UPDATE survey SET m3_score = ? WHERE id = ?", (m3_score, flag))
                conn.commit()
                print("Update_m3_score finish! ")    
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()
    else:
        print("데이터베이스 연결에 문제가 발생했습니다.")



def update_final_score():
    print("update_final_score start !")
    # 데이터베이스 연결
    conn = create_connection('survey.db')
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute('SELECT m1_score, m2_score, m3_score FROM survey WHERE id = ?', (primary_key, )) 
            row = cur.fetchone()

            if row:
                # 점수가 None이면 0으로 처리
                m1_score = row[0] if row[0] is not None else 0
                m2_score = row[1] if row[1] is not None else 0
                m3_score = row[2] if row[2] is not None else 0

                # 최종 점수 계산
                final_score = round((m1_score + m2_score + m3_score) / 3)
            else:
                final_score = 0  # row가 None인 경우 (데이터가 없는 경우)

            
            # final_score 업데이트
            cur.execute("UPDATE survey SET final_score = ? WHERE id = ?", (final_score, primary_key))
            conn.commit()
            print("Update_final_score finish! ")    
        except sqlite3.Error as e:
            print(f"데이터베이스 오류: {e}")
        finally:
            conn.close()
    else:
        print("데이터베이스 연결에 문제가 발생했습니다.")

    return final_score

@app.route('/result_page')
def result_page():
    update_m3_score(primary_key) # Result 로 가기전에 M3_score 평균내서 업데이트 시키기
    final_score = update_final_score() # 최종점수 합계
    return render_template('result.html', score=final_score)

if __name__ == '__main__':
    create_table()  # 테이블이 없을 경우 생성
    app.run(debug=True)
