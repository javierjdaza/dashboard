import streamlit as st 
import pandas as pd
st.set_page_config(page_title='Report Dashboards',page_icon=":brain:",initial_sidebar_state="collapsed", layout = 'wide')
import plotly.graph_objects as go

def etl(df:pd.DataFrame):
    df_list = df.to_dict(orient='records')

    fecha = [ i for i in df['Unnamed: 14'].values if str(i).startswith('Fecha')][0]
    nombre_proyecto = [ i for i in df['Unnamed: 14'].values if str(i).startswith('Nombre')][0].split(':')[1].strip()
    categorias = [i for i in df['Unnamed: 4'].values if str(i) != 'nan' and not str(i).startswith('Opci') and str(i) != 'Obligatorio'and not str(i).startswith('Mé') and str(i) != 'Responsabilidad Social (RS)']
    estados = [i for i in df['Unnamed: 14'].values if str(i) in ['Estado','No Aplica','Cerrado','Pendiente','En proceso']]

    dict_ = {}
    contador = 0
    for i in estados:
        if i == 'Estado':
            contador +=1
            pass
        else:
            try:
                dict_[f'{contador}'].append(i)
            except:
                dict_.update({
                    f'{contador}':[i]
                })

    dict_catego_estado = {}
    for i,v in enumerate(categorias):
        dict_catego_estado.update({v:dict_[list(dict_.keys())[i]]})


    list_final = []
    for k,v in dict_catego_estado.items():
        cerrado = 0
        no_aplica = 0
        en_proceso = 0
        pendiente = 0
        for i in v:
            if i == 'Cerrado':
                cerrado +=1
            if i == 'No Aplica':
                no_aplica +=1
            if i == 'En proceso':
                en_proceso +=1
            if i == 'Pendiente':
                pendiente +=1
        dict_temp = {
            # 'nombre_proyecto' : nombre_proyecto,
            # 'fecha':fecha,
            'categoria':k,
            'cerrado' : cerrado,
            # 'no_aplica' : no_aplica,
            'en_proceso' : en_proceso,
            'pendiente' : pendiente,
            }
        list_final.append(dict_temp)

    df_2 = pd.DataFrame(list_final)
    rows_keep = [
    'Sostenibilidad en el Entorno (SE)',
    'Sostenibilidad en Obra (SO)',
    'Eficiencia de Recursos (ER)',
    'Eficiencia en Agua (EA)',
    'Eficiencia en Energía (EE)',
    'Eficiencia en Materiales (EM)',
    'Bienestar (B)']
    df_2 = df_2[df_2['categoria'].isin(rows_keep)]
    df_2 = df_2[~((df_2['cerrado'] == 0) & (df_2['en_proceso'] == 0) & (df_2['pendiente'] == 0))]

    return df_2

def plot_categories(df_2:pd.DataFrame):
    

    colors_cerrado = ['#AACB73','#AACB73','#AACB73','#AACB73','#AACB73','#AACB73','#AACB73',]
    colors_process = ['#F9D949','#F9D949','#F9D949','#F9D949','#F9D949','#F9D949','#F9D949',]
    colors_pending = ['#EB455F','#EB455F','#EB455F','#EB455F','#EB455F','#EB455F','#EB455F',]
    categorias_ = df_2['categoria']
    fig = go.Figure(data = [
        go.Bar(name = 'Cerrado', x=categorias_, y=df_2['cerrado'],text= df_2['cerrado'], textposition='auto', marker_color = colors_cerrado),
        go.Bar(name = 'En proceso', x=categorias_, y=df_2['en_proceso'],text= df_2['en_proceso'], textposition='auto', marker_color = colors_process),
        go.Bar(name = 'Pendiente', x=categorias_, y=df_2['pendiente'],text= df_2['pendiente'], textposition='auto',marker_color = colors_pending),

            ])
    fig.update_layout(barmode='group',title = 'Conteo Status por Categorias',
        xaxis_title="Categoria",
        yaxis_title="Count",)

    return fig

def plot_progress(df_2:pd.DataFrame):
    
    df_2['progress'] = df_2['cerrado']  / (df_2['cerrado'] + df_2['en_proceso'] + df_2['pendiente'])
    df_2['progress'] = df_2['progress'].apply(lambda x: round(x,2))
    df_2.sort_values(by = ['progress'], inplace = True, ascending = True)
    progress_ = df_2['progress']
    categoria_ = df_2['categoria']
    fig = go.Figure(data = [
        go.Bar(name = 'Cerrado', y=categoria_, orientation='h',x=df_2['progress'],text= df_2['progress'],marker=dict(
            color='rgb(123, 203, 164,0.6)',
            line=dict(color='rgb(123, 203, 164, 1.0)', width=3)))],layout_xaxis_range = [0,1])

    fig.update_layout(barmode='group',title = 'Progress Status por Categorias',
        xaxis_title="% Progress")

    return fig

def get_name_date_project(df):
    fecha = [ i for i in df['Unnamed: 14'].values if str(i).startswith('Fecha')][0]
    nombre_proyecto = [ i for i in df['Unnamed: 14'].values if str(i).startswith('Nombre')][0].split(':')[1].strip()

    return nombre_proyecto,fecha

c1,c2,c3 = st.columns((1,3,1))
with c2:
    st.title('Proyect Progress Dashboard 📊')
    st.caption('Cristian Daza')
    st.write('---')
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        try:
            df = pd.read_excel(uploaded_file)
            nombre_proyecto,fecha = get_name_date_project(df)
            fecha = fecha.replace('Fecha:','')
            df_2 = etl(df)
            fig = plot_categories(df_2)
            fig_2 = plot_progress(df_2)
            st.write('---')
            st.write(' ')
            st.header(f'🔧 Nombre del proyecto: {nombre_proyecto}')
            st.subheader(f'📅 Fecha: {fecha}')
            st.plotly_chart(fig, use_container_width=True)
            st.plotly_chart(fig_2,use_container_width=True)
        except:
            st.error('Por favor asegurate de subir el archivo con el formato correcto')
    
    

