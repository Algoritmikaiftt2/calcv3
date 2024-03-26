import streamlit as st
import pandas as pd
import openpyxl

# Загрузка данных
xlsx = pd.ExcelFile('Калькулятор 1 млн.xlsx')
df = pd.read_excel(xlsx, 'Данные')
df = df[df['Кол-во детей в проекте'] >= 300]
main_cols = [col for col in df.columns if col.startswith('Добавить') or col.startswith('Добрать')]
main_cols.extend(['Кол-во классов в проекте', 'Кол-во детей в проекте', 'Нужно кабинетов на проект', 'UTIS'])
df_ = df[main_cols].set_index('UTIS').sort_values(by='Кол-во детей в проекте', ascending=False)

# Функция получения данных по технике для указанного количества школ
def get_n_technic(data, n_school):
    data.sort_values(by='Кол-во детей в проекте', ascending=False, inplace=True)
    return data.head(n_school)[['Кол-во детей в проекте', 'Нужно кабинетов на проект', 'Добрать компьютеров на проект']].sum()

# Функция определения школ по количеству компьютеров
def schools_by_computers(data, target_comp):
    data.sort_values(by='Кол-во детей в проекте', ascending=False, inplace=True)
    n = 0
    schools_id = []
    for utis, n_comp in zip(data.index, data['Добрать компьютеров на проект']):
        if target_comp >= n_comp:
            target_comp -= n_comp
            n += 1
            schools_id.append(utis)
    return n, target_comp, schools_id

# Функция определения необходимой техники по количеству детей
def technics_by_children(data, n_children):
    data.sort_values(by='Кол-во детей в проекте', ascending=False, inplace=True)
    n_school = n_technics = 0
    schools_id = []
    for utis, n_ch, n_comp in zip(data.index, data['Кол-во детей в проекте'], data['Добрать компьютеров на проект']):
        if n_children >= n_ch:
            n_school += 1
            n_technics += n_comp
            n_children -= n_ch
            schools_id.append(utis)
    return n_school, n_technics, n_children, schools_id

# Функция определения школ по доступным деньгам
def get_schools_by_money(data, target_money):
    data['money'] = (data['Добрать компьютеров на проект'] * COMP_PRICE +
                     data['Добрать проекторов на проект'] * PROJ_PRICE +
                     data['Добавить стульев на проект'] * FURN_PRICE +
                     data['Нужно кабинетов на проект'] * CLASS_PRICE)
    data.sort_values(by='Кол-во детей в проекте', inplace=True, ascending=False)
    n_school = n_ch = n_class = 0
    schools_id = []
    for utis, ch_in_sch, cl_in_sch, money_sch in zip(data.index, data['Кол-во детей в проекте'], data['Нужно кабинетов на проект'], data['money']):
        if target_money >= money_sch:
            target_money -= money_sch
            n_school += 1
            n_ch += ch_in_sch
            n_class += cl_in_sch
            schools_id.append(utis)
    return n_school, n_ch, n_class, target_money, schools_id

# Определение констант
COMP_PRICE = 950
PROJ_PRICE = 1300
FURN_PRICE = 151
CLASS_PRICE = 2700

# Создание интерфейса с помощью Streamlit
def main():
    st.title('Калькулятор')
    
    # Вывод результатов по количеству школ
    st.subheader('Получить данные по количеству школ')
    n_school = st.number_input('Введите кол-во школ:', min_value=1, value=1)
    if st.button('Посчитать школы', key='button_schools'):
        st.write(get_n_technic(df_, n_school=n_school))
    
    # Вывод результатов по количеству компьютеров
    st.subheader('Определить школы по количеству компьютеров')
    n_computers = st.number_input('Введите кол-во компьютеров:', min_value=1, value=1)
    if st.button('Посчитать компьютеры', key='button_computers'):
        res = schools_by_computers(df_, n_computers)
        st.write(f'Кол-во школ покрыто: {res[0]}')
        st.write(f'Кол-во компьютеров осталось: {res[1]}')
        st.write(f'UTIS: {res[2]}')
    
    # Вывод результатов по количеству детей
    st.subheader('Определить технику по количеству детей')
    n_child = st.number_input('Введите кол-во детей:', min_value=1, value=1)
    if st.button('Посчитать детей', key='button_children'):
        res = technics_by_children(df_, n_child)
        st.write(f'Кол-во школ покрыто: {res[0]}')
        st.write(f'Кол-во компьютеров осталось: {res[1]}')
        st.write(f'Кол-во детей не покрыто: {res[2]}')
        st.write(f'UTIS: {res[3]}')

    # Вывод результатов по доступным деньгам
    st.subheader('Определить школы по доступным деньгам')
    n_money = st.number_input('Введите кол-во денег:', min_value=0.0, value=0.0)
    if st.button('Посчитать деньги', key='button_money'):
        res = get_schools_by_money(df_, n_money)
        st.write(f'Кол-во школ покрыто: {res[0]}')
        st.write(f'Кол-во детей покрыто: {res[1]}')
        st.write(f'Кол-во классов покрыто: {res[2]}')
        st.write(f'Кол-во денег осталось: {res[3]}')
        st.write(f'UTIS: {res[4]}')

if __name__ == '__main__':
    main()