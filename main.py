import streamlit as st
import asana
from asana.rest import ApiException
import pandas as pd
import plotly.express as px
import datetime

configuration = asana.Configuration()
configuration.access_token = 'ENTER_ACCESS_TOKEN'
api_client = asana.ApiClient(configuration)
tasks_api_instance = asana.TasksApi(api_client)

project_id = 'ENTER_PROJECT_ID'
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
    df['completed_status'] = df['completed'].apply(lambda x: 'Complete' if x else 'Incomplete')
    return df[['gid', 'name', 'completed_status', 'department']]

def main():
    st.title("Asana Task Analytics")

    # Displaying timestamp for the last fetched data
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.write(f"Data last fetched at: {current_time}")

    data = fetch_data_from_asana()

    if data:
        df = prepare_dataframe(data)

        fig1 = px.pie(df, names='completed_status', title="Task Completion Status", hole=0.3,
                      color_discrete_sequence=px.colors.qualitative.D3)
        st.plotly_chart(fig1)

        fig2 = px.pie(df, names='department', title="Task by Department", hole=0.3,
                      color_discrete_sequence=px.colors.qualitative.D3)
        st.plotly_chart(fig2)
    else:
        st.error("No data fetched from Asana.")

if __name__ == "__main__":
    main()
