import pandas as pd
import streamlit as st
import psycopg2
import datetime
from streamlit_option_menu import option_menu

conn = psycopg2.connect(
    dbname="yours",
    user="yours",
    password="yours",
    host="yours",
    port='yours'
)


def group_timetable():
    st.title("Расписание")
    st.header('Введите название группы')
    name_group = st.text_input('Название...').upper()
    if name_group:
        cur = conn.cursor()
        cur.execute("SELECT * FROM team WHERE name_team = %s", (name_group,))
        group = cur.fetchone()
        if group is None:
            st.write("Такой группы не существует!")
        else:
            current_month = datetime.datetime.now().month
            if current_month in [9, 10, 11, 12]:
                type_semester = 'a'
            elif current_month in [2, 3, 4, 5]:
                type_semester = 's'
            else:
                type_semester = None

            cur.execute("SELECT * FROM get_timetable(%s, %s);", (name_group, type_semester))
            table_group = cur.fetchall()
            df = pd.DataFrame(table_group,
                              columns=['День недели', 'Время', 'Аудитория', 'Тип занятия', 'Предмет', 'Должность',
                                       'Фамилия', 'Имя', 'Отчество', 'Тип недели'])

            weekdays = df['День недели'].unique()
            week_types = [("h", "Верхняя неделя"), ("d", "Нижняя неделя")]
            week_types.insert(0, ("...", "..."))
            type_of_week = st.selectbox('Выберите тип недели', options=week_types, format_func=lambda x: f"{x[1]}")[
                0]
            if type_of_week != "...":
                st.subheader('Верхняя неделя' if type_of_week == 'h' else 'Нижняя неделя')
                df_week = df[df['Тип недели'] == type_of_week].drop(columns=['Тип недели'])
                for weekday in weekdays:
                    st.write('')
                    st.subheader(weekday)
                    df_weekday = df_week[df_week['День недели'] == weekday].drop(columns=['День недели'])
                    st.markdown(df_weekday.to_html(index=False), unsafe_allow_html=True)
            pd.set_option('display.width', None)
        cur.close()


def teacher_timetable():
    st.title("Мое расписание")
    cur = conn.cursor()

    current_month = datetime.datetime.now().month
    if current_month in [9, 10, 11, 12]:
        type_semester = 'a'
    elif current_month in [2, 3, 4, 5]:
        type_semester = 's'
    else:
        type_semester = None

    cur.execute("SELECT * FROM get_timetable_by_teacher(%s, %s);", (st.session_state['user'][0], type_semester))
    table_teacher = cur.fetchall()
    df = pd.DataFrame(table_teacher,
                      columns=['День недели', 'Время', 'Аудитория', 'Группа', 'Предмет', 'Тип недели'])

    week_types = [("h", "Верхняя неделя"), ("d", "Нижняя неделя")]
    week_types.insert(0, ("...", "..."))
    type_of_week = st.selectbox('Выберите тип недели', options=week_types, format_func=lambda x: f"{x[1]}")[0]
    if type_of_week != "...":
        st.subheader('Верхняя неделя' if type_of_week == 'h' else 'Нижняя неделя')
        df_week = df[df['Тип недели'] == type_of_week].drop(columns=['Тип недели'])
        st.markdown(df_week.to_html(index=False), unsafe_allow_html=True)
    pd.set_option('display.width', None)
    cur.close()


if 'user' not in st.session_state: st.session_state['user'] = None
if st.session_state['user'] is None:
    # Создайте боковое поле с навигацией только для неавторизированных пользователей
    with st.sidebar:
        noname_choice = option_menu("Навигация", ["Расписание групп", "Авторизация"],
                                    icons=['house', "list-task", 'gear'], menu_icon="cast", default_index=1)

    if noname_choice == "Расписание групп":
        group_timetable()
    elif noname_choice == "Авторизация":
        st.title("Авторизация")
        user_id = st.text_input("Введите ID")
        password = st.text_input("Введите пароль", type="password")

        if st.button("Войти"):
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM employee WHERE employee_id = %s AND password_employee = crypt(%s, password_employee)",
                (user_id, password))
            user = cur.fetchone()
            cur.close()

            if user:
                st.session_state['user'] = user

elif st.session_state['user'][5] == 'a':
    with st.sidebar:
        admin_choice = option_menu("Навигация",
                                   ["Расписание групп", "Добавление", "Обновление", "Удаление", "Направление",
                                    "Учебный план", "Откат", "Выйти"],
                                   icons=['list-task', 'plus', 'gear', 'trash', 'arrow-right', 'book', 'arrow-left',
                                          'door-open'],
                                   menu_icon="cast",
                                   default_index=1)

    if admin_choice == "Расписание групп":
        st.title("Расписание")
        st.header('Введите название группы')
        name_group = st.text_input('Название...').upper()
        if name_group:
            cur = conn.cursor()
            cur.execute("SELECT * FROM team WHERE name_team = %s", (name_group,))
            group = cur.fetchone()
            if group is None:
                st.write("Такой группы не существует!")
            else:
                # Let the user choose the semester
                semester_types = [("a", "Осенний семестр"), ("s", "Весенний семестр")]
                semester_types.insert(0, ("...", "..."))
                type_semester = \
                    st.selectbox('Выберите семестр', options=semester_types, format_func=lambda x: f"{x[1]}")[0]
                if type_semester != "...":
                    cur.execute("SELECT * FROM get_timetable(%s, %s);", (name_group, type_semester))
                    table_group = cur.fetchall()
                    df = pd.DataFrame(table_group,
                                      columns=['День недели', 'Время', 'Аудитория', 'Тип занятия', 'Предмет',
                                               'Должность',
                                               'Фамилия', 'Имя', 'Отчество', 'Тип недели'])

                    weekdays = df['День недели'].unique()
                    week_types = [("h", "Верхняя неделя"), ("d", "Нижняя неделя")]
                    week_types.insert(0, ("...", "..."))
                    type_of_week = \
                        st.selectbox('Выберите тип недели', options=week_types, format_func=lambda x: f"{x[1]}")[0]
                    if type_of_week != "...":
                        st.subheader('Верхняя неделя' if type_of_week == 'h' else 'Нижняя неделя')
                        df_week = df[df['Тип недели'] == type_of_week].drop(columns=['Тип недели'])
                        for weekday in weekdays:
                            st.write('')
                            st.subheader(weekday)
                            df_weekday = df_week[df_week['День недели'] == weekday].drop(columns=['День недели'])
                            st.markdown(df_weekday.to_html(index=False), unsafe_allow_html=True)
                    pd.set_option('display.width', None)
            cur.close()
    elif admin_choice == "Добавление":
        st.header('Добавление')
        choice = st.selectbox('Куда добавить?', ('Выбирай', 'Сотрудник(employee)', 'Преподаватель(lecturer)',
                                                 'Аудитория(audience)', 'Группа(team)', 'Расписание(timetable)'))
        if choice == 'Выбирай':
            pass
        elif choice == 'Сотрудник(employee)':
            last_name = st.text_input("Введите фамилию")
            first_name = st.text_input("Введите имя")
            second_name = st.text_input("Введите отчество")
            password = st.text_input("Введите пароль")
            status = st.text_input("Введите статус")
            if st.button("Добавить сотрудника"):
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO employee (first_name, second_name, last_name, password_employee, status) VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')), %s)",
                    (first_name, second_name, last_name, password, status))
                conn.commit()
                cur.close()
                st.success("Сотрудник успешно добавлен!")
        elif choice == 'Преподаватель(lecturer)':
            cur = conn.cursor()
            cur.execute(
                "SELECT employee_id, first_name, second_name, last_name FROM employee WHERE status = 't' AND employee_id NOT IN (SELECT employee_id FROM lecturer);")
            employees = cur.fetchall()
            if employees:
                cur.execute("SELECT job_position_id, name_job_position FROM job_position;")
                job_positions = cur.fetchall()
                cur.close()
                employee_id = st.selectbox('Выберите сотрудника', options=employees,
                                           format_func=lambda x: f"{x[1]} {x[2]} {x[3]}")[0]
                job_position_id = \
                    st.selectbox('Выберите должность', options=job_positions, format_func=lambda x: f"{x[1]}")[0]
                if st.button("Добавить преподавателя"):
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO lecturer (employee_id, job_position_id) VALUES (%s, %s)",
                        (employee_id, job_position_id))
                    conn.commit()
                    cur.close()
                    st.success("Преподаватель успешно добавлен!")
            else:
                st.write("Сотрудников нет, которых можно назначить преподавателем!")
        elif choice == 'Аудитория(audience)':
            number_audience = st.text_input('Введите номер аудитории')
            if st.button("Добавить аудиторию"):
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO audience (number_audience) VALUES (%s)",
                    (number_audience,))
                conn.commit()
                cur.close()
                st.success("Аудитория успешно добавлена!")
        elif choice == 'Группа(team)':
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM direction ORDER BY direction_id ASC;")
            direction = cur.fetchall()
            id_of_direction = st.selectbox('Выберите направление', options=direction, format_func=lambda x: f"{x[1]}")[
                0]
            number_of_course = st.selectbox('Номер курса', (1, 2, 3, 4))
            group_name = st.text_input('Добавить группу').upper()
            if st.button('Добавить'):
                cur.execute(
                    "INSERT INTO team (name_team, course, direction_id) VALUES (%s, %s, %s)",
                    (group_name, number_of_course, id_of_direction)
                )
                conn.commit()
                st.success("Группа успешно добавлена!")
            cur.close()
        elif choice == 'Расписание(timetable)':
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM direction ORDER BY direction_id ASC;")
            direction = cur.fetchall()
            direction.insert(0, (None, "..."))
            id_of_direction = st.selectbox('Выберите направление', options=direction, format_func=lambda x: f"{x[1]}")[
                0]
            if id_of_direction is not None:
                courses = list(range(1, 5))
                courses.insert(0, "...")
                number_of_course = st.selectbox('Номер курса', courses)
                if number_of_course != "...":
                    semesters = list(range((number_of_course - 1) * 2 + 1, number_of_course * 2 + 1))
                    semesters.insert(0, "...")
                    semester = st.selectbox('Выберите семестр', semesters)
                    if semester != "...":
                        # Determine the type of semester based on the selected semester
                        type_semester = 'a' if semester % 2 != 0 else 's'
                        options = ["...", "Добавить занятие", "Выбрать занятие и добавить в расписание"]
                        action = st.selectbox('Выберите действие', options)
                        if action == "Добавить занятие":
                            cur.execute(
                                "SELECT * FROM study_plan WHERE direction_id = %s AND semester_study_plan = %s ORDER BY study_plan_id ASC;",
                                (id_of_direction, semester))
                            subjects = cur.fetchall()
                            id_of_subject = \
                                st.selectbox('Выберите предмет', options=subjects, format_func=lambda x: f"{x[3]}")[0]
                            cur.execute(
                                "SELECT lecturer.lecturer_id, job_position.name_job_position, employee.first_name, employee.second_name, employee.last_name FROM lecturer INNER JOIN job_position ON lecturer.job_position_id = job_position.job_position_id INNER JOIN employee ON lecturer.employee_id = employee.employee_id;")
                            lecturers = cur.fetchall()
                            id_of_lecturer = st.selectbox('Выберите преподавателя', options=lecturers,
                                                          format_func=lambda x: f"({x[1]}) {x[2]} {x[3]} {x[4]}")[0]
                            cur.execute("SELECT * FROM type_lesson ORDER BY type_lesson_id ASC;")
                            types = cur.fetchall()
                            id_of_type = \
                                st.selectbox('Выберите тип предмета', options=types, format_func=lambda x: f"{x[1]}")[0]
                            if st.button('Добавить'):
                                cur.execute(
                                    "INSERT INTO lesson (study_plan_id, type_lesson_id, lecturer_id) VALUES (%s, %s, %s)",
                                    (id_of_subject, id_of_type, id_of_lecturer)
                                )
                                conn.commit()
                                st.success("Дисциплина успешно добавлена!")
                        if action == "Выбрать занятие и добавить в расписание":
                            cur.execute(
                                "SELECT * FROM team WHERE direction_id = %s AND course = %s ORDER BY name_team ASC;",
                                (id_of_direction, number_of_course))
                            teams = cur.fetchall()
                            teams.insert(0, (None, "..."))
                            id_of_team = \
                                st.selectbox('Выберите группу', options=teams, format_func=lambda x: f"{x[1]}")[0]
                            if id_of_team is not None:
                                cur.execute(
                                    "SELECT lesson.lesson_id, type_lesson.name_lesson, study_plan.subject_study_plan, job_position.name_job_position, employee.first_name, employee.second_name, employee.last_name FROM lesson INNER JOIN study_plan ON lesson.study_plan_id = study_plan.study_plan_id INNER JOIN type_lesson ON lesson.type_lesson_id = type_lesson.type_lesson_id INNER JOIN lecturer ON lesson.lecturer_id = lecturer.lecturer_id INNER JOIN job_position ON lecturer.job_position_id = job_position.job_position_id INNER JOIN employee ON lecturer.employee_id = employee.employee_id WHERE study_plan.direction_id = %s AND study_plan.semester_study_plan = %s ORDER BY lesson.lesson_id ASC;",
                                    (id_of_direction, semester))
                                subjects = cur.fetchall()
                                id_of_subject = \
                                    st.selectbox('Выберите предмет', options=subjects,
                                                 format_func=lambda
                                                     x: f"{x[1][:3]}: {x[2]} - ({x[3]}) {x[4]} {x[5]} {x[6]}")[0]
                                cur.execute("SELECT * FROM audience ORDER BY audience_id ASC;")
                                audiences = cur.fetchall()
                                id_of_audience = \
                                    st.selectbox('Выберите аудиторию', options=audiences,
                                                 format_func=lambda x: f"{x[1]}")[0]
                                cur.execute("SELECT * FROM weekday ORDER BY weekday_id ASC;")
                                weekdays = cur.fetchall()
                                id_of_weekday = \
                                    st.selectbox('Выберите день недели', options=weekdays,
                                                 format_func=lambda x: f"{x[1]}")[0]
                                cur.execute("SELECT * FROM course ORDER BY course_id ASC;")
                                courses = cur.fetchall()
                                id_of_course = \
                                    st.selectbox('Выберите время курса', options=courses,
                                                 format_func=lambda x: f"{x[1]}")[0]
                                week_types = [("h", "Верхняя неделя"), ("d", "Нижняя неделя")]
                                week_types.insert(0, ("...", "..."))
                                type_of_week = st.selectbox('Выберите тип недели', options=week_types,
                                                            format_func=lambda x: f"{x[1]}")[0]
                                if st.button('Добавить'):
                                    cur.execute(
                                        "INSERT INTO timetable (lesson_id, weekday_id, course_id, audience_id, type_week, type_semester) VALUES (%s, %s, %s, %s, %s, %s)",
                                        (id_of_subject, id_of_weekday, id_of_course, id_of_audience, type_of_week,
                                         type_semester)
                                    )
                                    conn.commit()
                                    st.success("Дисциплина успешно добавлена в расписание!")
                                    cur.execute("SELECT MAX(timetable_id) FROM timetable;")
                                    last_timetable_id = cur.fetchone()[0]
                                    cur.execute(
                                        "INSERT INTO timetable_team (timetable_id, team_id) VALUES (%s, %s)",
                                        (last_timetable_id, id_of_team)
                                    )
                                    conn.commit()
                                    st.success("Запись успешно добавлена в timetable_team!")
                            cur.close()
    elif admin_choice == 'Обновление':
        st.header('Обновление')
        choice = st.selectbox('Что обновить?', ('Выбирай', 'Сотрудник(employee)', 'Преподаватель(lecturer)',
                                                'Аудитория(audience)', 'Группа(team)', 'Расписание(timetable)'))
        if choice == 'Выбирай':
            pass
        elif choice == 'Сотрудник(employee)':
            st.title("Обновление данных сотрудника")

            # Получаем список сотрудников
            cur = conn.cursor()
            cur.execute("SELECT employee_id, first_name, second_name, last_name FROM employee")
            employees = cur.fetchall()
            cur.close()

            # Создаем выпадающий список с именами сотрудников
            employee_list = [(emp[0], f"{emp[1]} {emp[2]} {emp[3]}") for emp in employees]
            employee_list.insert(0, ("...", "..."))
            selected_employee_id = \
                st.selectbox('Выберите сотрудника', options=employee_list, format_func=lambda x: f"{x[1]}")[0]

            if selected_employee_id != "...":
                # Получаем текущие данные сотрудника
                cur = conn.cursor()
                cur.execute(
                    "SELECT first_name, second_name, last_name, password_employee, status FROM employee WHERE employee_id = %s",
                    (selected_employee_id,))
                current_data = cur.fetchone()
                cur.close()

                # Поля для ввода новых данных
                last_name = st.text_input("Введите фамилию", value=current_data[2])
                first_name = st.text_input("Введите имя", value=current_data[0])
                second_name = st.text_input("Введите отчество", value=current_data[1])
                password = st.text_input("Введите пароль", value=current_data[3])
                status = st.text_input("Введите статус", value=current_data[4])

                if st.button("Обновить данные сотрудника"):
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE employee SET first_name = %s, second_name = %s, last_name = %s, password_employee = crypt(%s, gen_salt('bf')), status = %s WHERE employee_id = %s",
                        (first_name, second_name, last_name, password, status, selected_employee_id))
                    conn.commit()
                    cur.close()
                    st.success("Данные сотрудника успешно обновлены!")
        elif choice == 'Преподаватель(lecturer)':
            st.title("Обновление данных преподавателя")

            # Получаем список преподавателей
            cur = conn.cursor()
            cur.execute("SELECT employee_id, first_name, second_name, last_name FROM employee WHERE status = 't'")
            employees = cur.fetchall()
            cur.close()

            # Создаем выпадающий список с именами преподавателей
            employee_list = [(emp[0], f"{emp[1]} {emp[2]} {emp[3]}") for emp in employees]
            employee_list.insert(0, ("...", "..."))
            selected_employee_id = \
                st.selectbox('Выберите преподавателя', options=employee_list, format_func=lambda x: f"{x[1]}")[0]

            if selected_employee_id != "...":
                # Получаем текущие данные преподавателя
                cur = conn.cursor()
                cur.execute("SELECT job_position_id FROM lecturer WHERE employee_id = %s", (selected_employee_id,))
                current_job_position_id = cur.fetchone()[0]
                cur.close()

                # Получаем список должностей
                cur = conn.cursor()
                cur.execute("SELECT job_position_id, name_job_position FROM job_position;")
                job_positions = cur.fetchall()
                cur.close()

                # Создаем выпадающий список с должностями
                job_position_list = [(jp[0], jp[1]) for jp in job_positions]
                job_position_list.insert(0, ("...", "..."))
                selected_job_position_id = \
                    st.selectbox('Выберите должность', options=job_position_list, format_func=lambda x: f"{x[1]}")[0]

                if st.button("Обновить данные преподавателя"):
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE lecturer SET job_position_id = %s WHERE employee_id = %s",
                        (selected_job_position_id, selected_employee_id))
                    conn.commit()
                    cur.close()
                    st.success("Данные преподавателя успешно обновлены!")
        elif choice == 'Аудитория(audience)':
            st.title("Обновление данных аудитории")

            # Получаем список аудиторий
            cur = conn.cursor()
            cur.execute("SELECT audience_id, number_audience FROM audience")
            audiences = cur.fetchall()
            cur.close()

            # Создаем выпадающий список с номерами аудиторий
            audience_list = [(aud[0], aud[1]) for aud in audiences]
            audience_list.insert(0, ("...", "..."))
            selected_audience_id = \
                st.selectbox('Выберите аудиторию', options=audience_list, format_func=lambda x: f"{x[1]}")[0]

            if selected_audience_id != "...":
                # Получаем текущие данные аудитории
                cur = conn.cursor()
                cur.execute("SELECT number_audience FROM audience WHERE audience_id = %s", (selected_audience_id,))
                current_number_audience = cur.fetchone()[0]
                cur.close()

                # Поле для ввода нового номера аудитории
                number_audience = st.text_input('Введите номер аудитории', value=current_number_audience)

                if st.button("Обновить данные аудитории"):
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE audience SET number_audience = %s WHERE audience_id = %s",
                        (number_audience, selected_audience_id))
                    conn.commit()
                    cur.close()
                    st.success("Данные аудитории успешно обновлены!")
        elif choice == 'Группа(team)':
            st.title("Обновление данных группы")

            cur = conn.cursor()
            cur.execute("SELECT team_id, name_team FROM team")
            teams = cur.fetchall()
            cur.close()

            # Создаем выпадающий список с названиями групп
            team_list = [(team[0], team[1]) for team in teams]
            team_list.insert(0, ("...", "..."))
            selected_team_id = st.selectbox('Выберите группу', options=team_list, format_func=lambda x: f"{x[1]}")[0]

            if selected_team_id != "...":
                # Получаем текущие данные группы
                cur = conn.cursor()
                cur.execute("SELECT name_team, course, direction_id FROM team WHERE team_id = %s", (selected_team_id,))
                current_data = cur.fetchone()
                cur.close()

                # Получаем список направлений
                cur = conn.cursor()
                cur.execute("SELECT direction_id, name_direction FROM direction ORDER BY direction_id ASC;")
                directions = cur.fetchall()
                cur.close()

                # Создаем выпадающий список с направлениями
                direction_list = [(dir[0], dir[1]) for dir in directions]
                direction_list.insert(0, ("...", "..."))
                selected_direction_id = \
                    st.selectbox('Выберите направление', options=direction_list, format_func=lambda x: f"{x[1]}")[0]

                # Поля для ввода новых данных
                group_name = st.text_input('Введите название группы', value=current_data[0]).upper()
                number_of_course = st.selectbox('Номер курса', (1, 2, 3, 4), index=current_data[1] - 1)

                if st.button("Обновить данные группы"):
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE team SET name_team = %s, course = %s, direction_id = %s WHERE team_id = %s",
                        (group_name, number_of_course, selected_direction_id, selected_team_id))
                    conn.commit()
                    cur.close()
                    st.success("Данные группы успешно обновлены!")

        elif choice == 'Расписание(timetable)':
            cur = conn.cursor()
            cur.execute("SELECT * FROM direction ORDER BY direction_id ASC;")
            direction = cur.fetchall()
            direction.insert(0, (None, "..."))
            id_of_direction = st.selectbox('Выберите направление', options=direction, format_func=lambda x: f"{x[1]}")[
                0]
            if id_of_direction is not None:
                courses = list(range(1, 5))
                courses.insert(0, "...")
                number_of_course = st.selectbox('Номер курса', courses)
                if number_of_course != "...":
                    semesters = list(range((number_of_course - 1) * 2 + 1, number_of_course * 2 + 1))
                    semesters.insert(0, "...")
                    semester = st.selectbox('Выберите семестр', semesters)
                    if semester != "...":
                        options = ["...", "Обновить занятие", "Выбрать занятие и обновить в расписании"]
                        action = st.selectbox('Выберите действие', options)
                        if action == "Обновить занятие":
                            cur.execute(
                                "SELECT lesson.lesson_id, type_lesson.name_lesson, study_plan.subject_study_plan, job_position.name_job_position, employee.first_name, employee.second_name, employee.last_name FROM lesson INNER JOIN study_plan ON lesson.study_plan_id = study_plan.study_plan_id INNER JOIN type_lesson ON lesson.type_lesson_id = type_lesson.type_lesson_id INNER JOIN lecturer ON lesson.lecturer_id = lecturer.lecturer_id INNER JOIN job_position ON lecturer.job_position_id = job_position.job_position_id INNER JOIN employee ON lecturer.employee_id = employee.employee_id WHERE study_plan.direction_id = %s AND study_plan.semester_study_plan = %s ORDER BY lesson.lesson_id ASC;",
                                (id_of_direction, semester))
                            lessons = cur.fetchall()
                            lessons.insert(0, (None, "..."))
                            id_of_lesson = st.selectbox('Выберите занятие для обновления', options=lessons,
                                                        format_func=lambda
                                                            x: f"{x[1][:3]}: {x[2]} - ({x[3]}) {x[4]} {x[5]} {x[6]}" if
                                                        x[0] is not None else x[1])[0]
                            if id_of_lesson is not None:
                                cur.execute(
                                    "SELECT * FROM study_plan WHERE direction_id = %s AND semester_study_plan = %s ORDER BY study_plan_id ASC;",
                                    (id_of_direction, semester))
                                subjects = cur.fetchall()
                                id_of_subject = st.selectbox('Выберите новый предмет', options=subjects,
                                                             format_func=lambda x: f"{x[3]}")[0]
                                cur.execute(
                                    "SELECT lecturer.lecturer_id, job_position.name_job_position, employee.first_name, employee.second_name, employee.last_name FROM lecturer INNER JOIN job_position ON lecturer.job_position_id = job_position.job_position_id INNER JOIN employee ON lecturer.employee_id = employee.employee_id;")
                                lecturers = cur.fetchall()
                                id_of_lecturer = st.selectbox('Выберите нового преподавателя', options=lecturers,
                                                              format_func=lambda x: f"({x[1]}) {x[2]} {x[3]} {x[4]}")[0]
                                cur.execute("SELECT * FROM type_lesson ORDER BY type_lesson_id ASC;")
                                types = cur.fetchall()
                                id_of_type = st.selectbox('Выберите новый тип предмета', options=types,
                                                          format_func=lambda x: f"{x[1]}")[0]
                                if st.button('Обновить'):
                                    cur.execute(
                                        "UPDATE lesson SET study_plan_id = %s, type_lesson_id = %s, lecturer_id = %s WHERE lesson_id = %s",
                                        (id_of_subject, id_of_type, id_of_lecturer, id_of_lesson))
                                    conn.commit()
                                    st.success("Дисциплина успешно обновлена!")
                        if action == "Выбрать занятие и обновить в расписании":
                            cur.execute(
                                "SELECT timetable.timetable_id, lesson.lesson_id, type_lesson.name_lesson, study_plan.subject_study_plan, job_position.name_job_position, employee.first_name, employee.second_name, employee.last_name, weekday.name_weekday, course.time_course, audience.number_audience, timetable.type_week FROM timetable INNER JOIN lesson ON timetable.lesson_id = lesson.lesson_id INNER JOIN study_plan ON lesson.study_plan_id = study_plan.study_plan_id INNER JOIN type_lesson ON lesson.type_lesson_id = type_lesson.type_lesson_id INNER JOIN lecturer ON lesson.lecturer_id = lecturer.lecturer_id INNER JOIN job_position ON lecturer.job_position_id = job_position.job_position_id INNER JOIN employee ON lecturer.employee_id = employee.employee_id INNER JOIN weekday ON timetable.weekday_id = weekday.weekday_id INNER JOIN course ON timetable.course_id = course.course_id INNER JOIN audience ON timetable.audience_id = audience.audience_id WHERE study_plan.direction_id = %s AND study_plan.semester_study_plan = %s ORDER BY timetable.timetable_id ASC;",
                                (id_of_direction, semester))
                            timetables = cur.fetchall()
                            timetables.insert(0, (None, "..."))
                            id_of_timetable = st.selectbox('Выберите расписание для обновления', options=timetables,
                                                           format_func=lambda
                                                               x: f"{x[8]} | {x[9]} | {x[10]} | {x[2][:3]}.{x[3]} | {x[4]} {x[5][:1]}.{x[6][:1]}.{x[7]} | неделя({x[11]})" if
                                                           x[0] is not None else x[1])[0]

                            if id_of_timetable is not None:
                                cur.execute(
                                    "SELECT * FROM team WHERE direction_id = %s AND course = %s ORDER BY name_team ASC;",
                                    (id_of_direction, number_of_course))
                                teams = cur.fetchall()
                                teams.insert(0, (None, "..."))
                                id_of_team = \
                                    st.selectbox('Выберите группу', options=teams, format_func=lambda x: f"{x[1]}")[0]
                                if id_of_team is not None:
                                    cur.execute(
                                        "SELECT lesson.lesson_id, type_lesson.name_lesson, study_plan.subject_study_plan, job_position.name_job_position, employee.first_name, employee.second_name, employee.last_name FROM lesson INNER JOIN study_plan ON lesson.study_plan_id = study_plan.study_plan_id INNER JOIN type_lesson ON lesson.type_lesson_id = type_lesson.type_lesson_id INNER JOIN lecturer ON lesson.lecturer_id = lecturer.lecturer_id INNER JOIN job_position ON lecturer.job_position_id = job_position.job_position_id INNER JOIN employee ON lecturer.employee_id = employee.employee_id WHERE study_plan.direction_id = %s AND study_plan.semester_study_plan = %s ORDER BY lesson.lesson_id ASC;",
                                        (id_of_direction, semester))
                                    subjects = cur.fetchall()
                                    id_of_subject = st.selectbox('Выберите новый предмет', options=subjects,
                                                                 format_func=lambda
                                                                     x: f"{x[1][:3]}.{x[2]} - {x[3]} {x[4][:1]}.{x[5][:1]}.{x[6]}")[
                                        0]
                                    cur.execute("SELECT * FROM audience ORDER BY audience_id ASC;")
                                    audiences = cur.fetchall()
                                    id_of_audience = st.selectbox('Выберите новую аудиторию', options=audiences,
                                                                  format_func=lambda x: f"{x[1]}")[0]
                                    cur.execute("SELECT * FROM weekday ORDER BY weekday_id ASC;")
                                    weekdays = cur.fetchall()
                                    id_of_weekday = st.selectbox('Выберите новый день недели', options=weekdays,
                                                                 format_func=lambda x: f"{x[1]}")[0]
                                    cur.execute("SELECT * FROM course ORDER BY course_id ASC;")
                                    courses = cur.fetchall()
                                    id_of_course = st.selectbox('Выберите новое время курса', options=courses,
                                                                format_func=lambda x: f"{x[1]}")[0]
                                    week_types = [("h", "Верхняя неделя"), ("d", "Нижняя неделя")]
                                    week_types.insert(0, ("...", "..."))
                                    type_of_week = st.selectbox('Выберите новый тип недели', options=week_types,
                                                                format_func=lambda x: f"{x[1]}")[0]
                                    if st.button('Обновить'):
                                        cur.execute(
                                            "UPDATE timetable SET lesson_id = %s, weekday_id = %s, course_id = %s, audience_id = %s, type_week = %s WHERE timetable_id = %s",
                                            (id_of_subject, id_of_weekday, id_of_course, id_of_audience, type_of_week,
                                             id_of_timetable))
                                        conn.commit()
                                        st.success("Дисциплина успешно обновлена в расписании!")
                                        cur.execute("UPDATE timetable_team SET team_id = %s WHERE timetable_id = %s",
                                                    (id_of_team, id_of_timetable))
                                        conn.commit()
                                        st.success("Запись успешно обновлена в timetable_team!")
                                    cur.close()
    elif admin_choice == 'Удаление':
        st.header('Удаление')
        choice = st.selectbox('Что удалить?', (
        'Выбирай', 'Сотрудник(employee)', 'Аудитория(audience)', 'Группа(team)', 'Расписание(timetable)'))
        if choice == 'Выбирай':
            pass
        elif choice == 'Сотрудник(employee)':
            cur = conn.cursor()
            cur.execute(
                "SELECT employee_id, first_name, second_name, last_name FROM employee ORDER BY employee_id ASC;")
            employees = cur.fetchall()
            employees.insert(0, (None, "...", "...", "..."))
            id_of_employee = st.selectbox('Выберите сотрудника', options=employees,
                                          format_func=lambda x: f"{x[1]} {x[2]} {x[3]}" if x[0] is not None else x[1])[
                0]
            if id_of_employee is not None:
                if st.button("Удалить сотрудника"):
                    cur.execute("DELETE FROM employee WHERE employee_id = %s", (id_of_employee,))
                    conn.commit()
                    st.success("Сотрудник успешно удален!")
            cur.close()
        elif choice == 'Аудитория(audience)':
            cur = conn.cursor()
            cur.execute("SELECT * FROM audience ORDER BY audience_id ASC;")
            audiences = cur.fetchall()
            if audiences:
                audience_id = st.selectbox('Выберите аудиторию', options=audiences, format_func=lambda x: f"{x[1]}")[0]
                if st.button("Удалить аудиторию"):
                    cur.execute("DELETE FROM audience WHERE audience_id = %s", (audience_id,))
                    conn.commit()
                    st.success("Аудитория успешно удалена!")
                cur.close()
            else:
                st.write("Аудиторий нет в базе данных!")
        elif choice == 'Расписание(timetable)':
            cur = conn.cursor()
            cur.execute("SELECT * FROM direction ORDER BY direction_id ASC;")
            direction = cur.fetchall()
            direction.insert(0, (None, "..."))
            id_of_direction = st.selectbox('Выберите направление', options=direction, format_func=lambda x: f"{x[1]}")[
                0]
            if id_of_direction is not None:
                courses = list(range(1, 5))
                courses.insert(0, "...")
                number_of_course = st.selectbox('Номер курса', courses)
                if number_of_course != "...":
                    semesters = list(range((number_of_course - 1) * 2 + 1, number_of_course * 2 + 1))
                    semesters.insert(0, "...")
                    semester = st.selectbox('Выберите семестр', semesters)
                    if semester != "...":
                        options = ["...", "Удалить занятие", "Выбрать занятие и удалить из расписания"]
                        action = st.selectbox('Выберите действие', options)
                        if action == "Удалить занятие":
                            cur.execute(
                                "SELECT lesson.lesson_id, type_lesson.name_lesson, study_plan.subject_study_plan, job_position.name_job_position, employee.first_name, employee.second_name, employee.last_name FROM lesson INNER JOIN study_plan ON lesson.study_plan_id = study_plan.study_plan_id INNER JOIN type_lesson ON lesson.type_lesson_id = type_lesson.type_lesson_id INNER JOIN lecturer ON lesson.lecturer_id = lecturer.lecturer_id INNER JOIN job_position ON lecturer.job_position_id = job_position.job_position_id INNER JOIN employee ON lecturer.employee_id = employee.employee_id WHERE study_plan.direction_id = %s AND study_plan.semester_study_plan = %s ORDER BY lesson.lesson_id ASC;",
                                (id_of_direction, semester))
                            lessons = cur.fetchall()
                            lessons.insert(0, (None, "..."))
                            id_of_lesson = st.selectbox('Выберите занятие для удаления', options=lessons,
                                                        format_func=lambda
                                                            x: f"{x[1][:3]}: {x[2]} - ({x[3]}) {x[4]} {x[5]} {x[6]}" if
                                                        x[0] is not None else x[1])[0]
                            if id_of_lesson is not None and st.button('Удалить'):
                                cur.execute("DELETE FROM lesson WHERE lesson_id = %s", (id_of_lesson,))
                                conn.commit()
                                st.success("Дисциплина успешно удалена!")
                        if action == "Выбрать занятие и удалить из расписания":
                            cur.execute(
                                "SELECT timetable.timetable_id, lesson.lesson_id, type_lesson.name_lesson, study_plan.subject_study_plan, job_position.name_job_position, employee.first_name, employee.second_name, employee.last_name, weekday.name_weekday, course.time_course, audience.number_audience, timetable.type_week FROM timetable INNER JOIN lesson ON timetable.lesson_id = lesson.lesson_id INNER JOIN study_plan ON lesson.study_plan_id = study_plan.study_plan_id INNER JOIN type_lesson ON lesson.type_lesson_id = type_lesson.type_lesson_id INNER JOIN lecturer ON lesson.lecturer_id = lecturer.lecturer_id INNER JOIN job_position ON lecturer.job_position_id = job_position.job_position_id INNER JOIN employee ON lecturer.employee_id = employee.employee_id INNER JOIN weekday ON timetable.weekday_id = weekday.weekday_id INNER JOIN course ON timetable.course_id = course.course_id INNER JOIN audience ON timetable.audience_id = audience.audience_id WHERE study_plan.direction_id = %s AND study_plan.semester_study_plan = %s ORDER BY timetable.timetable_id ASC;",
                                (id_of_direction, semester))
                            timetables = cur.fetchall()
                            timetables.insert(0, (None, "..."))
                            id_of_timetable = st.selectbox('Выберите расписание для удаления', options=timetables,
                                                           format_func=lambda
                                                               x: f"{x[2][:3]}.{x[3]} - {x[4]} {x[5][:1]}.{x[6][:1]}.{x[7]} {x[8]} {x[9]} {x[10]} {x[11]}" if
                                                           x[0] is not None else x[1])[0]
                            if id_of_timetable is not None and st.button('Удалить'):
                                cur.execute("DELETE FROM timetable WHERE timetable_id = %s", (id_of_timetable,))
                                conn.commit()
                                st.success("Дисциплина успешно удалена из расписания!")
                            cur.close()
        elif choice == 'Группа(team)':
            cur = conn.cursor()
            cur.execute("SELECT * FROM team ORDER BY team_id ASC;")
            teams = cur.fetchall()
            teams.insert(0, (None, "..."))
            id_of_team = st.selectbox('Выберите группу для удаления', options=teams, format_func=lambda x: f"{x[1]}")[0]
            if id_of_team is not None and st.button('Удалить'):
                cur.execute("DELETE FROM team WHERE team_id = %s", (id_of_team,))
                conn.commit()
                st.success("Группа успешно удалена!")
            cur.close()
    elif admin_choice == 'Откат':
        st.header('Откат')
        choice = st.selectbox('Что откататить?',
                              ('Выбирай', 'Сотрудник(employee)', 'Преподаватель(lecturer)',
                               'Аудитория(audience)', 'Группа(team)', 'Занятие(lesson)', 'Расписание(timetable)',
                               'Направление(direction)', 'Учебный план(study_plan)'
                               ))
        if choice == 'Выбирай':
            pass
        elif choice == 'Сотрудник(employee)':
            cur = conn.cursor()
            cur.execute("SELECT op_time FROM employee_temp ORDER BY op_time DESC LIMIT 1")
            last_records = cur.fetchall()
            cur.close()
            for record in last_records:
                st.write("Последняя запись:", record[0].strftime('%Y-%m-%d %H:%M:%S'))

            rollback_date = st.date_input("Выберите дату").strftime('%Y-%m-%d')
            rollback_hour = st.slider("Выберите час", 0, 23)
            rollback_minute = st.slider("Выберите минуту", 0, 59)
            rollback_second = st.slider("Выберите секунду", 0, 59)
            rollback_time_str = f"{rollback_hour:02d}:{rollback_minute:02d}:{rollback_second:02d}"
            rollback_datetime_str = f"{rollback_date} {rollback_time_str}"
            rollback_datetime = datetime.datetime.strptime(rollback_datetime_str, '%Y-%m-%d %H:%M:%S')
            if st.button("Откатить до заданного времени"):
                cur = conn.cursor()
                cur.execute("SELECT rollback_employee(%s)", (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                conn.commit()
                cur.close()
                st.success("Откат выполнен успешно!")
        elif choice == 'Преподаватель(lecturer)':
            cur = conn.cursor()
            cur.execute("SELECT op_time FROM lecturer_temp ORDER BY op_time DESC LIMIT 1")
            last_records = cur.fetchall()
            cur.close()
            for record in last_records:
                st.write("Последняя запись:", record[0].strftime('%Y-%m-%d %H:%M:%S'))

            rollback_date = st.date_input("Выберите дату").strftime('%Y-%m-%d')
            rollback_hour = st.slider("Выберите час", 0, 23)
            rollback_minute = st.slider("Выберите минуту", 0, 59)
            rollback_second = st.slider("Выберите секунду", 0, 59)
            rollback_time_str = f"{rollback_hour:02d}:{rollback_minute:02d}:{rollback_second:02d}"
            rollback_datetime_str = f"{rollback_date} {rollback_time_str}"
            rollback_datetime = datetime.datetime.strptime(rollback_datetime_str, '%Y-%m-%d %H:%M:%S')
            if st.button("Откатить до заданного времени"):
                cur = conn.cursor()
                cur.execute("SELECT rollback_lecturer(%s)", (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                conn.commit()
                cur.close()
                st.success("Откат выполнен успешно!")
        elif choice == 'Аудитория(audience)':
            cur = conn.cursor()
            cur.execute("SELECT op_time FROM audience_temp ORDER BY op_time DESC LIMIT 1")
            last_records = cur.fetchall()
            cur.close()
            for record in last_records:
                st.write("Последняя запись:", record[0].strftime('%Y-%m-%d %H:%M:%S'))

            rollback_date = st.date_input("Выберите дату").strftime('%Y-%m-%d')
            rollback_hour = st.slider("Выберите час", 0, 23)
            rollback_minute = st.slider("Выберите минуту", 0, 59)
            rollback_second = st.slider("Выберите секунду", 0, 59)
            rollback_time_str = f"{rollback_hour:02d}:{rollback_minute:02d}:{rollback_second:02d}"
            rollback_datetime_str = f"{rollback_date} {rollback_time_str}"
            rollback_datetime = datetime.datetime.strptime(rollback_datetime_str, '%Y-%m-%d %H:%M:%S')
            if st.button("Откатить до заданного времени"):
                cur = conn.cursor()
                cur.execute("SELECT rollback_audience(%s)", (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                conn.commit()
                cur.close()
                st.success("Откат выполнен успешно!")
        elif choice == 'Группа(team)':
            cur = conn.cursor()
            cur.execute("SELECT op_time FROM team_temp ORDER BY op_time DESC LIMIT 1")
            last_records = cur.fetchall()
            cur.close()
            for record in last_records:
                st.write("Последняя запись:", record[0].strftime('%Y-%m-%d %H:%M:%S'))

            rollback_date = st.date_input("Выберите дату").strftime('%Y-%m-%d')
            rollback_hour = st.slider("Выберите час", 0, 23)
            rollback_minute = st.slider("Выберите минуту", 0, 59)
            rollback_second = st.slider("Выберите секунду", 0, 59)
            rollback_time_str = f"{rollback_hour:02d}:{rollback_minute:02d}:{rollback_second:02d}"
            rollback_datetime_str = f"{rollback_date} {rollback_time_str}"
            rollback_datetime = datetime.datetime.strptime(rollback_datetime_str, '%Y-%m-%d %H:%M:%S')
            if st.button("Откатить до заданного времени"):
                cur = conn.cursor()
                cur.execute("SELECT rollback_team(%s)", (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                conn.commit()
                cur.close()
                st.success("Откат выполнен успешно!")
        elif choice == 'Расписание(timetable)':
            cur = conn.cursor()
            cur.execute("SELECT op_time FROM timetable_temp ORDER BY op_time DESC LIMIT 1")
            last_records = cur.fetchall()
            cur.close()
            for record in last_records:
                st.write("Последняя запись:",
                         record[0].strftime('%Y-%m-%d %H:%M:%S'))  # Вывод времени в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС

            rollback_date = st.date_input("Выберите дату").strftime('%Y-%m-%d')
            rollback_hour = st.slider("Выберите час", 0, 23)
            rollback_minute = st.slider("Выберите минуту", 0, 59)
            rollback_second = st.slider("Выберите секунду", 0, 59)
            rollback_time_str = f"{rollback_hour:02d}:{rollback_minute:02d}:{rollback_second:02d}"
            rollback_datetime_str = f"{rollback_date} {rollback_time_str}"
            rollback_datetime = datetime.datetime.strptime(rollback_datetime_str, '%Y-%m-%d %H:%M:%S')
            if st.button("Откатить до заданного времени"):
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT rollback_timetable(%s)", (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                    conn.commit()
                    cur.execute("SELECT rollback_timetable_team(%s)",
                                (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                    conn.commit()
                    cur.close()
                    st.success("Откат выполнен успешно!")
                except Exception as e:
                    st.success("Откат выполнен успешно!")
        elif choice == 'Занятие(lesson)':
            cur = conn.cursor()
            cur.execute("SELECT op_time FROM lesson_temp ORDER BY op_time DESC LIMIT 1")
            last_records = cur.fetchall()
            cur.close()
            for record in last_records:
                st.write("Последняя запись:", record[0].strftime('%Y-%m-%d %H:%M:%S'))

            rollback_date = st.date_input("Выберите дату").strftime('%Y-%m-%d')
            rollback_hour = st.slider("Выберите час", 0, 23)
            rollback_minute = st.slider("Выберите минуту", 0, 59)
            rollback_second = st.slider("Выберите секунду", 0, 59)
            rollback_time_str = f"{rollback_hour:02d}:{rollback_minute:02d}:{rollback_second:02d}"
            rollback_datetime_str = f"{rollback_date} {rollback_time_str}"
            rollback_datetime = datetime.datetime.strptime(rollback_datetime_str, '%Y-%m-%d %H:%M:%S')
            if st.button("Откатить до заданного времени"):
                cur = conn.cursor()
                cur.execute("SELECT rollback_lesson(%s)", (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                conn.commit()
                cur.close()
                st.success("Откат выполнен успешно!")
        elif choice == 'Учебный план(study_plan)':
            cur = conn.cursor()
            cur.execute("SELECT op_time FROM study_plan_temp ORDER BY op_time DESC LIMIT 1")
            last_records = cur.fetchall()
            cur.close()
            for record in last_records:
                st.write("Последняя запись:", record[0].strftime('%Y-%m-%d %H:%M:%S'))

            rollback_date = st.date_input("Выберите дату").strftime('%Y-%m-%d')
            rollback_hour = st.slider("Выберите час", 0, 23)
            rollback_minute = st.slider("Выберите минуту", 0, 59)
            rollback_second = st.slider("Выберите секунду", 0, 59)
            rollback_time_str = f"{rollback_hour:02d}:{rollback_minute:02d}:{rollback_second:02d}"
            rollback_datetime_str = f"{rollback_date} {rollback_time_str}"
            rollback_datetime = datetime.datetime.strptime(rollback_datetime_str, '%Y-%m-%d %H:%M:%S')
            if st.button("Откатить до заданного времени"):
                cur = conn.cursor()
                cur.execute("SELECT rollback_study_plan(%s)", (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                conn.commit()
                cur.close()
                st.success("Откат выполнен успешно!")
        elif choice == 'Направление(direction)':
            cur = conn.cursor()
            cur.execute("SELECT op_time FROM direction_temp ORDER BY op_time DESC LIMIT 1")
            last_records = cur.fetchall()
            cur.close()
            for record in last_records:
                st.write("Последняя запись:", record[0].strftime('%Y-%m-%d %H:%M:%S'))

            rollback_date = st.date_input("Выберите дату").strftime('%Y-%m-%d')
            rollback_hour = st.slider("Выберите час", 0, 23)
            rollback_minute = st.slider("Выберите минуту", 0, 59)
            rollback_second = st.slider("Выберите секунду", 0, 59)
            rollback_time_str = f"{rollback_hour:02d}:{rollback_minute:02d}:{rollback_second:02d}"
            rollback_datetime_str = f"{rollback_date} {rollback_time_str}"
            rollback_datetime = datetime.datetime.strptime(rollback_datetime_str, '%Y-%m-%d %H:%M:%S')
            if st.button("Откатить до заданного времени"):
                cur = conn.cursor()
                cur.execute("SELECT rollback_direction(%s)", (rollback_datetime.strftime('%Y-%m-%d %H:%M:%S'),))
                conn.commit()
                cur.close()
                st.success("Откат выполнен успешно!")
    elif admin_choice == 'Направление':
        action_choice = st.selectbox("Выберите действие",
                                     ["Добавить направление", "Обновить направление", "Удалить направление"])
        cur = conn.cursor()

        if action_choice == "Добавить направление":
            new_direction = st.text_input("Введите название направления")
            if st.button("Добавить"):
                cur.execute("INSERT INTO direction (name_direction) VALUES (%s)", (new_direction,))
                conn.commit()
                st.success("Направление успешно добавлено!")
        elif action_choice == "Обновить направление":
            cur.execute("SELECT name_direction FROM direction")
            directions = [row[0] for row in cur.fetchall()]
            selected_direction = st.selectbox("Выберите направление", directions)
            updated_direction = st.text_input("Обновите название направления", selected_direction)
            if st.button("Обновить"):
                cur.execute("UPDATE direction SET name_direction = %s WHERE name_direction = %s",
                            (updated_direction, selected_direction))
                conn.commit()
                st.success("Направление успешно обновлено!")
        elif action_choice == "Удалить направление":
            cur.execute("SELECT name_direction FROM direction")
            directions = [row[0] for row in cur.fetchall()]
            selected_direction = st.selectbox("Выберите направление", directions)
            if st.button("Удалить"):
                cur.execute("DELETE FROM direction WHERE name_direction = %s", (selected_direction,))
                conn.commit()
                st.success("Направление успешно удалено!")
        cur.close()
    elif admin_choice == 'Учебный план':
        cur = conn.cursor()
        cur.execute("SELECT name_direction FROM direction")
        directions = [row[0] for row in cur.fetchall()]
        selected_direction = st.selectbox("Выберите направление", directions)
        cur.execute(
            "SELECT name_study_plan FROM study_plan WHERE direction_id = (SELECT direction_id FROM direction WHERE name_direction = %s)",
            (selected_direction,))
        study_plans = [row[0] for row in cur.fetchall()]
        if len(study_plans) == 0:
            view_choice = st.selectbox("Выберите действие", ["Добавление учебного плана"])
        else:
            view_choice = st.selectbox("Выберите действие",
                                       ["Просмотр групп", "Добавление учебного плана", "Просмотр учебного плана"])
        if view_choice == "Добавление учебного плана":
            new_study_plan = st.text_input("Введите название учебного плана")
            if new_study_plan:
                last_digit = int(new_study_plan[-1])
                available_semesters = [last_digit * 2 - 1, last_digit * 2]
                selected_semester = st.selectbox("Выберите семестр", available_semesters)
                new_subject = st.text_input("Добавить предмет")
                if st.button("Добавить"):
                    cur.execute(
                        "INSERT INTO study_plan (name_study_plan, semester_study_plan, subject_study_plan, direction_id) VALUES (%s, %s, %s, (SELECT direction_id FROM direction WHERE name_direction = %s))",
                        (new_study_plan, selected_semester, new_subject, selected_direction))
                    conn.commit()
                    st.success("Учебный план успешно добавлен!")
        if view_choice == "Просмотр групп":
            cur.execute(
                "SELECT name_team FROM team WHERE direction_id = (SELECT direction_id FROM direction WHERE name_direction = %s) ORDER BY name_team",
                (selected_direction,))
            groups = [row[0] for row in cur.fetchall()]
            df = pd.DataFrame(groups, columns=["Группы"])
            st.table(df)
        elif view_choice == "Просмотр учебного плана":
            cur.execute(
                "SELECT DISTINCT name_study_plan FROM study_plan WHERE direction_id = (SELECT direction_id FROM direction WHERE name_direction = %s)",
                (selected_direction,))
            study_plans = [row[0] for row in cur.fetchall()]
            selected_study_plan = st.selectbox("Выберите учебный план", study_plans)
            cur.execute("SELECT subject_study_plan, semester_study_plan FROM study_plan WHERE name_study_plan = %s",
                        (selected_study_plan,))
            study_plan = cur.fetchall()
            df = pd.DataFrame(study_plan, columns=["Предмет", "Семестр"])
            st.table(df)

            action_choice = st.selectbox("Выберите действие", ["Дополнить", "Обновить", "Удалить"])

            if action_choice == "Дополнить":
                cur.execute("SELECT DISTINCT semester_study_plan FROM study_plan WHERE name_study_plan = %s",
                            (selected_study_plan,))
                available_semesters = [row[0] for row in cur.fetchall()]
                selected_semester = st.selectbox("Выберите семестр", available_semesters)
                new_subject = st.text_input("Введите название предмета")
                if st.button("Добавить"):
                    cur.execute("SELECT direction_id FROM direction WHERE name_direction = %s",
                                (selected_direction,))
                    direction_id = cur.fetchone()[0]
                    cur.execute(
                        "INSERT INTO study_plan (name_study_plan, semester_study_plan, subject_study_plan, direction_id) VALUES (%s, %s, %s, %s)",
                        (selected_study_plan, selected_semester, new_subject, direction_id))
                    conn.commit()
                    st.success("Предмет успешно добавлен!")
            elif action_choice == "Обновить":
                cur.execute(
                    "SELECT subject_study_plan, semester_study_plan FROM study_plan WHERE name_study_plan = %s",
                    (selected_study_plan,))
                subjects = cur.fetchall()
                selected_subject = st.selectbox("Выберите предмет", subjects)
                updated_subject = st.text_input("Обновите название предмета", selected_subject[0])
                cur.execute("SELECT DISTINCT semester_study_plan FROM study_plan WHERE name_study_plan = %s",
                            (selected_study_plan,))
                available_semesters = [row[0] for row in cur.fetchall()]
                updated_semester = st.selectbox("Обновите семестр", available_semesters,
                                                index=available_semesters.index(selected_subject[1]) if
                                                selected_subject[1] in available_semesters else 0)
                if st.button("Обновить"):
                    cur.execute(
                        "UPDATE study_plan SET subject_study_plan = %s, semester_study_plan = %s WHERE name_study_plan = %s AND subject_study_plan = %s AND semester_study_plan = %s",
                        (updated_subject, updated_semester, selected_study_plan, selected_subject[0],
                         selected_subject[1]))
                    conn.commit()
                    st.success("Предмет успешно обновлен!")
            elif action_choice == "Удалить":
                cur.execute(
                    "SELECT subject_study_plan, semester_study_plan FROM study_plan WHERE name_study_plan = %s",
                    (selected_study_plan,))
                subjects = cur.fetchall()
                selected_subject = st.selectbox("Выберите предмет", subjects)
                if st.button("Удалить"):
                    cur.execute(
                        "DELETE FROM study_plan WHERE name_study_plan = %s AND subject_study_plan = %s AND semester_study_plan = %s",
                        (selected_study_plan, selected_subject[0], selected_subject[1]))
                    conn.commit()
                    st.success("Предмет успешно удален!")
        cur.close()
    elif admin_choice == "Выйти":
        st.session_state['user'] = None

elif st.session_state['user'][5] == 't':

    with st.sidebar:
        teacher_choice = option_menu("Навигация",
                                     ["Расписание групп", "Мое расписание", "Выйти"],
                                     icons=['list-task', 'list-task', 'door-open'],
                                     menu_icon="cast",
                                     default_index=1)

    if teacher_choice == "Расписание групп":
        group_timetable()
    elif teacher_choice == "Мое расписание":
        teacher_timetable()

    elif teacher_choice == "Выйти":
        st.session_state['user'] = None
