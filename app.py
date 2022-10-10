from PIL import Image, ImageDraw
# import requests
import streamlit as st
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import cv2
import pydicom as dicom
import math
import os
import pandas as pd



st.set_page_config(page_title="Profile, Projection, and Sinogram", page_icon="✋🏻", layout="wide")

remove_top_padding = """
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """
st.markdown(remove_top_padding, unsafe_allow_html=True)

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# ---- HEADER SECTION ----
with st.container():
    st.title("Profile, Projection, and Sinogram")
    st.write("---")
# ---- LOAD IMAGE ----
BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / 'images' 
imageNames = [f.name for f in IMAGE_DIR.iterdir() if f.suffix=='.dcm' or f.suffix==".DCM"]



with st.expander("CHANGE PROJECTION DATA"):
    sample_image = st.selectbox('Choose sample projection', imageNames, index=0)
    img_path = IMAGE_DIR / sample_image


ds = dicom.dcmread(img_path)
img = ds.pixel_array.astype(float)

scaled_image = (np.maximum(img, 0) / img.max()) * 255.0
disp_img = np.uint8(scaled_image)
t,m,n = np.shape(img)
arc = 360
step_angle = int(arc/t)
proj_angles = np.array(range(0,arc,int(arc/t)))

x = np.linspace(0,1,int(m/2))


with st.container():
    left_top_col, right_top_col = st.columns((1,1))
    with left_top_col:
        angle = st.slider("Projection angle (ϴ):", min_value=0, max_value=int(arc-step_angle), step=step_angle, value=0)
    with right_top_col:
        slice_loc = st.slider("Slice (y):", min_value=1, max_value=m, step=1, value=int(m/2))
    
    
    left_col, mid_col, right_col  = st.columns((1,1,1))
    
    with left_col:
        # st.subheader("PROJECTION DATA")
        angle_loc = int(angle/3)
        proj_img = disp_img[angle_loc,:,:].copy()
        proj_img[slice_loc,:] = 255.0
        # st.image(proj_img, width=256)

        fig, ax = plt.subplots()
        ax.imshow(proj_img, cmap="gray")
        ax.set_xlabel('Bin (x)')
        ax.set_ylabel('Slice (y)')
        st.caption('Projection at ϴ = ' + str(angle))
        st.pyplot(fig)

    with mid_col:
        sino = disp_img[:,slice_loc,:].copy()
        # sino = np.swapaxes(sino,0,1)
        profile = sino[angle_loc,:].copy()
        sino[angle_loc,:] = 255.0
        
        # st.image(sino, width=256)

        fig, ax = plt.subplots()
        
        ax.imshow(sino, cmap="gray")
        y_label_list = np.array(range(0,arc,30))
        ax.set_yticks(np.array(range(0,t,10)))
        ax.set_yticklabels(y_label_list)
        ax.set_xlabel('Bin (x)')
        ax.set_ylabel('Angle (ϴ)')
        st.caption('Sinogram at slice = ' + str(slice_loc))
        st.pyplot(fig)

    with right_col:
        st.caption('Profile at ϴ = '+ str(angle) + ', slice = '+ str(slice_loc))

        st.line_chart(profile)