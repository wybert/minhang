import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
import pandas as pd


# st.title("Epidemic Surveillance System")
# Translate the text to Chinese
st.title("民航疫情监测系统")
# st.write("This is a demo of the Epidemic Surveillance System. Notice that the data is not real. the data is shown as below:")

routes = pd.read_csv('flights edited.csv')

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["实时航班","历史航班"])

with tab2:
    # st.header("A cat")
    col1, col2, col3 = st.columns(3)

    with col1:
        # select infectious disease
        choice = st.selectbox("选择传染病：", 
                              ["Covid confirmed cases_src",
                                "Monkeypox confirmed cases_src", 
                              "Covid confirmed cases_dst", 
                              "Monkeypox confirmed cases_dst"])
        routes["cases"] = routes[choice]

    with col2:
        # select destination city
        city = st.multiselect("选择航班目的地：", routes["city_dst"].unique(),
                            default=["Beijing", "Shenzhen","Dalian"])
        routes = routes[routes["city_dst"].isin(city)]

    with col3:
        # select airlines
        airlines = st.multiselect("选择航班：", routes["airline_name"].unique(), 
                                  default=["Air China"])

        routes = routes[routes["airline_name"].isin(airlines)]


    
    # st.write("Distribution of cases across the world, and the flights arriving to China")

    import json
    # load config
    with open("config.json", "r") as f:
        config = json.loads(f.read())


    map_1 = KeplerGl(height=600, width=800, config=config)
    map_1.add_data(data=routes.copy(), name="flights")
    keplergl_static(map_1)


    # 
    st.write("航班数: ", len(routes))
    



    # st.dataframe(routes.head())

with tab1:
    import time
    import requests
    import pandas as pd
    data = pd.read_parquet("data.parquet")
    # st.write(data.head())
    data["datetime"] =  pd.to_datetime(data["unix_time"], unit="s")

    t = data.datetime.drop_duplicates().sort_values()

    # url = "https://opensky-network.org/api/states/all"

    # from dotenv import load_dotenv
    # import os
    # from dotenv import load_dotenv, find_dotenv
    # load_dotenv(find_dotenv())

    # user = os.environ.get("user")
    # password = os.environ.get("password")
    # creating a single-element container
    placeholder = st.empty()
    while True:
        # r = requests.get(url, auth=(user, password))

        # json_data = r.json()

        # unix_time = json_data["time"]

        # states = pd.DataFrame(json_data['states'], columns=['icao24', 'callsign', 'origin_country', 'time_position', 
        #                                                     'last_contact', 'longitude', 'latitude', 'baro_altitude', 'on_ground', 'velocity', 
        #                                                     'true_track', 'vertical_rate', 'sensors', 'geo_altitude', 'squawk', 'spi', 'position_source'])
        
        # make a loop to show the data
        for i in range(0, len(t)):
            # unix_time = t.iloc[i].timestamp()
            # get the data at the time
            states = data[data["datetime"] == t.iloc[i]]

            # fill null values
            states =   states.fillna(0)
            states["roll"] = 0
            states["yaw"] = -states["true_track"]
            states["pitch"] = 90

            # import matplotlib.cm as cm
            # cmap = cm.get_cmap('viridis') 
            # states['color'] = states['origin_country'].map(lambda country: tuple(int(c * 255) for c in cmap(hash(country))[:3]) + (255,))  # RGBA values with alpha=255

            # make the color column random as yello, red, green, make sure most of them are green
            states["color"] = states["origin_country"].map(lambda country: (0, 255, 0, 255)  if country == "China" else (255, 0, 0, 255))
            # random make some of them yellow
            # import numpy as np
            # states["color"] = states["color"].map(lambda color: (255, 255, 0, 255) if np.random.random() > 0.8 else color)


            from pydeck import Layer, Deck
            from pydeck.data_utils import compute_view
            from pydeck.types import String


            SCENEGRAPH_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/scenegraph-layer/airplane.glb"

            # Automatically fit viewport location based on data
            # df = pd.read_json(DATA_URL)
            # testjson = [
            #             {"name": "test",
            #              "coordinates" : [-83.7582848, 42.2739968],
            #             },
            #         ],
            layer = Layer(
                type="ScenegraphLayer",
                id="scenegraph-layer",
                data=states,
                pickable=True,
                scenegraph=SCENEGRAPH_URL,
                get_position=["longitude", "latitude", "geo_altitude"],
                sizeMinPixels=0.1,
                  sizeMaxPixels=1.5,
                get_orientation= ["roll","yaw" , "pitch"],
                # set color
                get_color= "color",
                size_scale=500,
                # _animations={"*": {"speed": 5}},
                # _lighting=String("pbr"),
            )

            # Render
            # put china in the center of the map

            view  = {"latitude": 22, "longitude": 114, "zoom": 5, "pitch": 0, "bearing": 0}

            with placeholder.container():

                import datetime
                # get Beijing time

                beijing_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
                st.write("北京时间：", beijing_time)

                r = Deck(layer, 
                        #  put China in the center
                            initial_view_state=view,
                        #  initial_view_state=view
                        # show country name and icao24 as tooltip
                            tooltip= {"text": "航班来自: {origin_country} \n ICAO代码: {icao24}"}
                        )

                st.pydeck_chart(r)

            time.sleep(0.5)
        time.sleep(0.5)

    # r.to_html("scenegraph_layer1.html")
# st.write("这是一个疫情监测系统的演示。请注意，数据不是真实的。")

