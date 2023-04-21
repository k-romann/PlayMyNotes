import streamlit as st
import subprocess
from streamlit_lottie import st_lottie
import torch
import pandas as pd
from PIL import Image
from music21 import *
import requests
import numpy as np


st.set_page_config(
    page_title='Play My Notes',
    page_icon= ":melody:"
)

model = torch.hub.load('ultralytics/yolov5', 'custom', path='mdl_weights/YOLO_1280_new.pt', device='cpu')


note_dict = {'-5':'B2',
        '-4.5':'C3','-4':'D3','-3.5':'E3','-3':'F3','-2.5':'G3','-2':'A3','-1.5':'B3',
        '-1':'C4','-0.5':'D4', '0':'E4', '0.5': 'F4', '1':'G4', '1.5':'A4', '2':'B4', 
        '2.5':'C5','3':'D5','3.5':'E5','4':'F5','4.5':'G5','5':'A5','5.5':'B5',
        '6':'C6','6.5':'D6','7':'E6','7.5':'F6','8':'G6','8.5':'A6','9':'B6', 
        'rest':'rest', 'sharp':'#', 'flat':'b','bass':'bass','treble':'treble','key':'key',
        'natural':'natural'}

dur_dict ={'whole':'whole', 'half':'half', 'quarter':'quarter', 'eight':'eighth', 'sixteen':'16th', 'thirtytwo':'32nd',
        '1-1':'whole', '1-2':'half', '1-4':'quarter', '1-8': 'eighth', '1-16':'16th', '1-32':'32nd','':''}


def find_adjacent_diff(column):
    diff = column.diff()
    return diff


def clean(data):
    # data['center x'] = data.apply(lambda row: (row['x1'] + (row['x2']-row['x1'])/ 2) , axis=1)
    difff = find_adjacent_diff(data['xcenter'])
    poisk2 = pd.DataFrame(difff)
    poisk2['xcenter'] = poisk2['xcenter'].apply(lambda x: abs(x))
    poisk2 = poisk2.sort_values(by=['xcenter'])
    poisk2.reset_index(inplace= True)
    mass = []
    x=0
    if poisk2.iloc[x]['xcenter']/data['width'].mean() < 0.1:
        while poisk2.iloc[x]['xcenter']/data['width'].mean() < 0.1:
            mass.append(poisk2.iloc[x]['index'])
            x+=1
        mass = [int (x) for x in mass]
        to_drop = []
        for i in mass:
            if data.iloc[i]['confidence'] < data.iloc[i-1]['confidence']:
                to_drop.append(i)
            else:
                to_drop.append(i-1)
    
        df = data.drop(to_drop)
    else:
        df = data
    return df


def convert_names(lst, n_dict, dur_dict):
    for i in range(len(lst)):
        if lst[i] in ['sharp', 'flat', 'natural', 'bass', 'treble']:
            lst[i] = lst[i] + '_'
    lst = [i.split('_') for i in lst]
    conv_list = [[n_dict[i[0]], dur_dict[i[1]]] for i in lst]
    for i, symb in enumerate(conv_list):
        if symb[0] in ['#','b']:
            conv_list[i+1][0] = conv_list[i+1][0][0] + symb[0] + conv_list[i+1][0][1:]    
            conv_list.pop(i)
    return conv_list

def g_em(n):
    if 'F' in n:
        n = n + '#'
    return n

def d_bm(n):
    if 'F' in n or 'C' in n:
        n = n + '#'
    return n

def a_fm(n):
    if 'F' in n or 'C' in n or 'G' in n:
        n = n + '#'
    return n

def f_dm(n):
    if 'B' in n:
        n = n + 'b'
    return n

def eb_cm(n):
    if 'A' in n or 'B' in n or 'E' in n:
        n = n + 'b'
    return n


url = requests.get(
    "https://assets2.lottiefiles.com/private_files/lf30_LrduTx.json")
url_json = dict()
if url.status_code == 200:
    url_json = url.json()
else:
    print("Error in URL")
    
st_lottie(url_json,
          reverse=True,
          height=300,  
          width=300,
          speed=1,  
          loop=True,  
          quality='high',
          )

st.write("""
<style>
@import url('https://fonts.googleapis.com/css?family=Dancing+Script');
html, body, [class*="css"]  {
   font-family: 'Dancing Script', cursive; 
}
</style>
""", unsafe_allow_html=True)


st.title("Play My Notes")

st.markdown('Сервис для воспроизвеления простых мелодий по нотам фортепиано. Распознает ноты в скрипичном ключе длительностью от целой ноты до 1/16 в самых популярных тональностях.')

uploaded_file = st.file_uploader(
    "Загрузите фотографию нот", 
    type=["jpg", "jpeg", "png"]
    )
if uploaded_file != None:
    st.image(uploaded_file)

    #----results-processing----------------
    img = Image.open(uploaded_file)
    model.conf = 0.4
    results = model(img, size=1280)
    res1_df = results.pandas().xywh[0].sort_values(by=['xcenter', 'ycenter'])
    res1_df = res1_df.reset_index()
    res1_df = clean(res1_df)
    res1_list = res1_df['name'].to_list()

    tkey = ''
    if 'treble' in res1_list[0] and len(res1_list[0].split('_'))>1:
        tkey = res1_list[0].split('_')[1]
        res1_list.pop(0)

    for i, obj in enumerate(res1_list):
        if 'key' in obj:
            tkey = obj
            res1_list.pop(i)

    if 'treble' in res1_list[0]:
        res1_list = res1_list[1:]

    notes_list = convert_names(res1_list, note_dict, dur_dict)
    
    s = stream.Stream()
    note_arr = np.array(notes_list)
    if 'G-Em' in tkey:
        note_arr[:,0] = np.vectorize(g_em)(note_arr[:,0])
        s.append(key.KeySignature(1))
    if 'D-Bm' in tkey :
        note_arr[:,0] = np.vectorize(d_bm)(note_arr[:,0])
        s.append(key.KeySignature(2))
    if 'A-F-m' in tkey:
        note_arr[:,0] = np.vectorize(a_fm)(note_arr[:,0])
        s.append(key.KeySignature(3))
    if 'F-Dm' in tkey:
        note_arr[:,0] = np.vectorize(f_dm)(note_arr[:,0])
        s.append(key.KeySignature(-1))
    if 'Eb-Cm' in tkey:
        note_arr[:,0] = np.vectorize(eb_cm)(note_arr[:,0])
        s.append(key.KeySignature(-3))
   
   
    for n, dur in note_arr:
        if n == 'rest':
            s.append(note.Rest(type=dur))
        else:      
            s.append(note.Note(n, type=dur))
        
    s.insert(0, meter.TimeSignature('4/4'))
    
    s.insert(0, tempo.MetronomeMark(number=120))

    s.write('musicxml.png','pic')

    s.write('midi', 'out.mid')
    subprocess.run(['timidity', 'out.mid', '-Ow'])


    st.markdown('При распознавании нот возможна неточность. Мелодия будет воспроизведена по нотам, которые представленны ниже: ')
    st.image('pic-1.png')
    audio_file = open('out.wav', 'rb')
    audio_bytes = audio_file.read()

    st.audio(audio_bytes, format='audio/wav')

