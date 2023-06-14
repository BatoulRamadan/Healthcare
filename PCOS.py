import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.graph_objects as go
import streamlit as st
import holoviews as hv
from streamlit_agraph import agraph, TripleStore
import streamlit.components.v1 as components
import hydralit_components as hc
from streamlit_lottie import st_lottie
from plotly.subplots import make_subplots
from moviepy.editor import VideoFileClip
from io import BytesIO



st.set_page_config(
    page_title="Polycystic Ovarian Syndrome (PCOS)",
    page_icon="🌸",
    layout='wide'
)

# Add custom CSS style to change the background color
custom_css = """
    .fullScreenFrame > div:first-child {
        background-color: #f8f8f8;
    }
"""
st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)

        
    
menu_data = [
    {'label': "Home", 'icon': '🏠'},
    {'label': 'Diagnosis', 'icon': '🩺'},
    {'label': 'Effects', 'icon': '📝'},
    {'label':"Recommendations", 'icon':'👩‍⚕️'}]

over_theme = {'txc_inactive': 'black','menu_background':'pink', 'option_active':'white'}

menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    hide_streamlit_markers=True,
    sticky_nav=True, #at the top or not
    sticky_mode='sticky', #jumpy or not-jumpy, but sticky or pinned
)


t1, t2 = st.columns((2,2))
with t1:
    st.markdown('# PCOS')

with t2:
    st.write("")
    st.write("") 
    st.write("""
    **Health Care Analytics** | Made by Batoul Ramadan 
    """)
    

# In[3]:

#Load the data
d_1= pd.read_excel('PCOS_data_without_infertility.xlsx',sheet_name="Full_new")

# In[5]:
#Load the data
d_2= pd.read_csv('PCOS_infertility.csv')


# In[7]:
#Merge the files
data = pd.merge(d_1,d_2, on='Patient File No.',  suffixes=('', '_wo'), how='left')
#Drop repeated features
data =data.drop(['Unnamed: 44', 'Sl. No_wo', 'PCOS (Y/N)_wo', '  I   beta-HCG(mIU/mL)_wo',
       'II    beta-HCG(mIU/mL)_wo', 'AMH(ng/mL)_wo'], axis=1)
#Change the title of the properties
data = data.rename(columns = {"PCOS (Y/N)":"PCOS"})

# In[8]:
#Drop unnecessary features
data = data.drop(["Sl. No","Patient File No."],axis = 1)


# In[10]:


#Converting
data["AMH(ng/mL)"] = pd.to_numeric(data["AMH(ng/mL)"], errors='coerce')
data["II    beta-HCG(mIU/mL)"] = pd.to_numeric(data["II    beta-HCG(mIU/mL)"], errors='coerce')


# In[12]:


category = ["PCOS", "Pregnant(Y/N)", "Weight gain(Y/N)", "hair growth(Y/N)", "Skin darkening (Y/N)", "Hair loss(Y/N)", 
            "Pimples(Y/N)"]



# In[14]:


#Filling missing values with the median value of the features.

data['Marraige Status (Yrs)'].fillna(data['Marraige Status (Yrs)'].median(),inplace=True)
data['II    beta-HCG(mIU/mL)'].fillna(data['II    beta-HCG(mIU/mL)'].median(),inplace=True)
data['AMH(ng/mL)'].fillna(data['AMH(ng/mL)'].median(),inplace=True)
data['Fast food (Y/N)'].fillna(data['Fast food (Y/N)'].median(),inplace=True)


# In[ ]:


numeric = [" Age (yrs)", "Weight (Kg)","Marraige Status (Yrs)"]


# In[ ]:


def bar_plot():
    # User input for the variables
    variables = st.multiselect("Select up to three categories", [cat for cat in category if cat != "PCOS"], key="select_categories")

    # Check if at least one variable is selected
    if not variables:
        st.warning("Please select at least one variable!")
        return

    # Check if the variables are valid
    invalid_variables = [var for var in variables if var not in data.columns]
    if invalid_variables:
        st.error(f"Invalid variables: {', '.join(invalid_variables)}")
        return

    # Filter data for patients with PCOS
    pcos_data = data[data['PCOS'] == 1]

    # Create subplots for up to three variables per row
    num_plots = len(variables)
    num_rows = (num_plots + 2) // 3
    num_cols = min(num_plots, 3)
    fig = make_subplots(rows=num_rows, cols=num_cols)

    # Iterate over the selected variables
    for i, variable in enumerate(variables):
        # Get the data for the variable
        var = pcos_data[variable]
        var_value = var.value_counts()

        # Define custom colors
        colors = ['rgb(255, 192, 203)', 'rgb(211, 211, 211)']

        # Determine the subplot location
        row = i // 3 + 1
        col = i % 3+ 1

        # Create the bar plot for the variable
        fig.add_trace(
            go.Bar(x=var_value.index, y=var_value, marker_color=colors),
            row=row, col=col
        )

        # Update the layout for the subplot
        fig.update_xaxes(title_text=variable, row=row, col=col)
        fig.update_yaxes(title_text='Count', row=row, col=col)

    # Update the overall layout
    fig.update_layout(
        title=dict(text="Multiple Category Bar Plots", x=0.5),
        showlegend=False
    )

    # Render the plotly chart
    st.plotly_chart(fig)

    for variable in variables:
        var = pcos_data[variable]
        var_value = var.value_counts()
        st.write(f"{variable}:\n{var_value}")
 
def visualize_data(data):
    # Define the color palette
    color = ["grey", "plum"]

    # Define the available visualizations
    visualizations = {
        "Length of menstrual phase in PCOS vs normal": {
            "x": " Age (yrs)",
            "y": "Cycle length(days)",
            "hue": "PCOS",
            "palette": color
        },
        "Pattern of weight gain (BMI) over years in PCOS and Normal": {
            "x": " Age (yrs)",
            "y": "BMI",
            "hue": "PCOS",
            "palette": color
        },
        "Cycle IR wrt age": {
            "x": " Age (yrs)",
            "y": "Cycle(R/I)",
            "hue": "PCOS",
            "palette": color
        },
        "Distribution of follicles in both ovaries": {
            "x": "Follicle No. (R)",
            "y": "Follicle No. (L)",
            "hue": "PCOS",
            "palette": color
        }
    }

    # Add a selectbox for choosing the visualization
    selected_visualization = st.selectbox("Select Visualization", list(visualizations.keys()))

    # Generate and display the selected visualization
    if selected_visualization in visualizations:
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.lmplot(data=data, x=visualizations[selected_visualization]["x"],
                         y=visualizations[selected_visualization]["y"],
                         hue=visualizations[selected_visualization]["hue"],
                         palette=visualizations[selected_visualization]["palette"])

        # Save the figure to an image buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Display the image using st.image()
        st.image(buffer)

   
 
def plot_age_distribution(data, group):
    # Age Distribution (Histogram)
    fig, ax = plt.subplots(figsize=(10,8), dpi=100)
    
    for i, group in enumerate(group):
        if group == 'PCOS':
            ax.hist(data[data['PCOS'] == 1][' Age (yrs)'], bins=10, alpha=0.5, label=group, color='pink')
        elif group == 'Normal':
            ax.hist(data[data['PCOS'] == 0][' Age (yrs)'], bins=10, alpha=0.5, label=group, color='lightgrey')

    ax.set_xlabel('Age (years)', fontsize=8)
    ax.set_ylabel('Frequency', fontsize=8)
    ax.set_title('Age Distribution', fontsize=10)
    ax.legend(fontsize=8)
    
    return fig



    
# In[ ]:

if menu_id == 'Diagnosis':
 st.header("How to know if I have PCOS?")
 st.markdown("1. Long Menstrual Cycle")
 st.markdown("2. Weight Gain")
 st.markdown("3. High Insulin Resistance")
 st.markdown("4. High count of follicles in both ovaries ")
 st.header("Diagnosis")
 st.markdown("1. Pelvic exam")
 st.markdown("2. Blood tests")
 st.markdown("3. Ultrasound")
 st.header("Check the visuals")   
 visualize_data(data)


if menu_id == 'Effects':
 image_path = "https://images.ctfassets.net/285b4h6rshof/3k19hkgTOaG05qKiad6wKZ/e1c2651f89551fadc06068c9e4485df7/DT_PCOS_Symptoms_2x.jpg?w=1600"
 st.image(image_path, use_column_width=True)
 bar_plot()



if menu_id == 'Home':
    video_path = 'PCOS.mp4'
    clip = VideoFileClip(video_path)

    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            st.video(video_path)
        else:
            st.write("Unable to read video frame.")
    else:
        st.write("Unable to open video file.")

    option = st.multiselect('Select a group', ['PCOS', 'Normal'], default=['PCOS', 'Normal'])
    
    # # Call the function to plot the age distribution
    # age_plot = plot_age_distribution(data, option)
    
    # # Display the plot using Streamlit
    # st.pyplot(age_plot)

    # Create a container
    age_plot = plot_age_distribution(data, option)

    # Convert the figure to an image buffer
    buffer = BytesIO()
    age_plot.savefig(buffer, format='png')
    buffer.seek(0)

    # Display the image using st.image()
    st.image(buffer)

if menu_id == "Recommendations":
    col1, col2 = st.columns(2)
    with col1:
        image_path = "https://getgym.co.uk/wp-content/uploads/2022/05/PCOS_exercise.jpg"
        st.image(image_path, width=600)
    with col2:    
         image_path = "https://d16qt3wv6xm098.cloudfront.net/Q0UcoKNVSGiVGQzbJd8M2ztnSKqwovv9/_.png"
         st.image(image_path, width=600)


    st.header("Recommendations")
    st.markdown("1- Early Detection and Diagnosis")
    st.markdown(f"""
                </div> 
        

                2- Lifestyle Modifications:

                - Encouraging regular exercise, a balanced diet, and weight management can help improve insulin sensitivity, regulate hormone levels, and reduce the risk of associated complications.

                - Nutrition counseling and support groups can be valuable resources for individuals with PCOS.

                </div>""",unsafe_allow_html = True)
    
    st.markdown(f"""
                </div>
                3- Mental Health Support:

                 - PCOS can have a significant impact on mental health due to its physical manifestations and potential fertility-related concerns. 
                 
                 - Integrating mental health support services, such as counseling and support groups, can help individuals cope with the emotional challenges associated with PCOS.
                </div>""",unsafe_allow_html = True)
