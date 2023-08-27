import streamlit as st
import asana
from asana.rest import ApiException
import pandas as pd
import plotly.express as px
import datetime
import os
from dotenv import load_dotenv
from streamlit_echarts import st_echarts

load_dotenv()

configuration = asana.Configuration()
configuration.access_token = os.getenv('ASANA_TOKEN')
api_client = asana.ApiClient(configuration)
tasks_api_instance = asana.TasksApi(api_client)

project_id = os.getenv('ASANA_PROJECT')
opt_fields = ["completed", "name", "custom_fields", "assignee", "projects"]

@st.cache_data(ttl=60, show_spinner=False)  # Cache for one hour
def fetch_data_from_asana():
    try:
        tasks = tasks_api_instance.get_tasks(project=project_id, opt_fields=opt_fields)
        return tasks.to_dict().get('data', [])
    except ApiException as e:
        st.error(f"Exception when calling TasksApi->get_tasks: {e}")
        return []

def prepare_dataframe(data):
    df = pd.DataFrame(data)
    if 'custom_fields' in df.columns:
        df['department'] = df['custom_fields'].apply(lambda x: x[0].get("display_value", "Other") if x else "Other")
    else:
        df['department'] = "Other"
    df['department'] = df.department.fillna('Other')
    df['completed_status'] = df['completed'].apply(lambda x: 'Complete' if x else 'Incomplete')
    return df[['gid', 'name', 'completed_status', 'department']]

def main():
    st.title("DSRS Tasks Dashboard")

    # Displaying timestamp for the last fetched data
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = fetch_data_from_asana()

    if data:
        df = prepare_dataframe(data)

        #fig1 = px.pie(df, names='completed_status', title="Task Completion Status", hole=0.3, color_discrete_sequence=px.colors.qualitative.D3)
        #st.plotly_chart(fig1)

        #fig2 = px.pie(df, names='department', title="Task by Department", hole=0.3, color_discrete_sequence=px.colors.qualitative.D3)
        #st.plotly_chart(fig2)
    else:
        st.error("No data fetched from Asana.")
    values = []
    total = len(df)
    total_tasks = f"Total Tasks: {total}"
    names = ["ACCY", "BA", "FIN", "DSRS", "EXTERNAL", "Other"]
    for n in names:
        if n == "EXTERNAL":
            name = "External"
        else:
            name = n
        values.append({'name':name , 'value':len(df[df.department==n])})
    values_completed = []
    for n in list(df.completed_status.unique()):
        values_completed.append({'name':n , 'value':len(df[df.completed_status==n])})
    options = {
        "title": {"text": "Task by Department", "left": "center"},
        "title": {"text": "Task by Department", "subtext": total_tasks, "left": "center", "top": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"top": "center", "left": "left", "orient": "vertical"},
        "series": [
            {
                
                "type": "pie",
                "radius": ["55%", "90%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 1,
                },
                "label": {"show": True, "position": "inside", "formatter": "{c}", "fontSize": "18", "fontWeight": "bold"},
                "emphasis": {
                    "label": {"show": True, "fontSize": "20", "fontWeight": "bold"}
                },
                "labelLine": {"show": False},
                "data": values,
            }
        ],
    }
    st_echarts(options=options, height="400px")

    options2 = {
        "title": {"text": "Task by Department", "left": "center"},
        "title": {"text": "Task Completion status", "subtext": total_tasks, "left": "center", "top": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"top": "center", "left": "left", "orient": "vertical"},
        "series": [
            {
                
                "type": "pie",
                "radius": ["55%", "90%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 1,
                },
                "label": {"show": True, "position": "inside", "formatter": "{c}", "fontSize": "18", "fontWeight": "bold"},
                "emphasis": {
                    "label": {"show": True, "fontSize": "20", "fontWeight": "bold"}
                },
                "labelLine": {"show": False},
                "data": values_completed,
            }
        ],
    }
    st_echarts(options=options2, height="400px")
    st.write(f"Data last fetched at: {current_time}")

if __name__ == "__main__":
    main()
