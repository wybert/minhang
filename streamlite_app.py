import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
import pandas as pd


st.title("Epidemic Surveillance System")
st.write("This is a demo of the Epidemic Surveillance System. Notice that the data is not real. the data is shown as below:")

routes = pd.read_csv('flights edited.csv')

st.dataframe(routes)


# select infectious disease
choice = st.selectbox("Select infectious disease", 
                      ["Covid confirmed cases_src",
                        "Monkeypox confirmed cases_src", 
                       "Covid confirmed cases_dst", 
                       "Monkeypox confirmed cases_dst"])
routes["cases"] = routes[choice]

# select airlines
airlines = st.multiselect("Select airlines", routes["airline_name"].unique(), 
                          default=routes["airline_name"].unique())

routes = routes[routes["airline_name"].isin(airlines)]

# 
st.write("Number of flights: ", len(routes))

st.write("Distribution of cases across the world, and the flights arriving to China")

import json
# load config
with open("config.json", "r") as f:
    config = json.loads(f.read())


map_1 = KeplerGl(height=600, width=800, config=config)
map_1.add_data(data=routes.copy(), name="flights")
keplergl_static(map_1)