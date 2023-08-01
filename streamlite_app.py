import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
import pandas as pd


# st.title("Epidemic Surveillance System")
# Translate the text to Chinese
st.title("民 航 疫 情 监 测 系 统")
# st.write("This is a demo of the Epidemic Surveillance System. Notice that the data is not real. the data is shown as below:")



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["实时航班","历史航班"])

with tab2:
    routes = pd.read_csv('flights edited v3.3.3.csv')
    # st.header("A cat")
    col1, col2, col3 = st.columns(3)

    with col1:
        # select infectious disease
        choice = st.selectbox("选择传染病：", 
                              [ "出发地猴痘确诊病例", 
                                "出发地新冠确诊病例"])
        routes["病例"] = routes[choice]

    with col2:
        # select destination city
        city = st.multiselect("选择航班目的地：", routes["目的地城市"].unique(),
                            default=["Beijing", "Shenzhen","Dalian"])
        routes = routes[routes["目的地城市"].map(lambda x: x in city)]
        # st.write(routes)
    with col3:
        # select airlines
        airlines = st.multiselect("选择航班：", routes["航空公司名称"].unique(), 
                                  default=routes["航空公司名称"].unique()[:1])

        routes = routes[routes["航空公司名称"].isin(airlines)]
    cases_max = routes["病例"].max()
    cases_min = routes["病例"].min()
    values = st.slider(
    '病例数范围',
    0.0, float(cases_max),
    (0.1, float(cases_max))
    )
    
    routes = routes[routes["病例"].between(values[0], values[1])]
    # st.write("Distribution of cases across the world, and the flights arriving to China")

    import json
    # load config
    with open("config2.json", "r") as f:
        config = json.loads(f.read())


    map_1 = KeplerGl(height=600, width=800, config=config)
    map_1.add_data(data=routes.copy(), name="航班")
    keplergl_static(map_1)


    # 
    st.write("航班数: ", len(routes))
    
    # st.dataframe(routes.head())

with tab1:
    import time
    import requests
    import pandas as pd
    import pydeck as pdk
    data = pd.read_parquet("data.parquet")
    # st.write(data.head())
    data["datetime"] =  pd.to_datetime(data["unix_time"], unit="s")
    real_time_cases = pd.read_csv("realtime-cases.csv")
    
    real_time_cases['病例'] = real_time_cases['出发地猴痘确诊病例']
    real_time_cases = real_time_cases[real_time_cases["病例"] > 0]
    # Use pandas to calculate additional data
    # real_time_cases["exits_radius"] = real_time_cases["病例"]
    # scale 病例 to 1-100
    max = real_time_cases["病例"].max()
    min = real_time_cases["病例"].min()
    real_time_cases["exits_radius"] = real_time_cases["病例"].map(lambda x: (x - min) / (max - min) * 100 + 1)

    cases_layer = pdk.Layer(
        "ScatterplotLayer",
        real_time_cases,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=1500,
        radius_min_pixels=1,
        radius_max_pixels=300,
        line_width_min_pixels=1,
        get_position=["src_lng", "src_lat"],
        get_radius="exits_radius",
        get_fill_color=[255, 0, 0],
        get_line_color=[0, 0, 0],
    )

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
            color_map_by_country = {
                "Guatemala": (0, 255, 0, 255) ,
                "Slovenia":(255, 128, 0, 255),
                "Norway": (255, 0, 255, 255),
                "United States": (255, 0, 0, 255),
            }

            states["color"] = states["origin_country"].map(lambda country: color_map_by_country.get(country, (255, 255, 255, 255)))
            # random make some of them yellow
            # import numpy as np
            # states["color"] = states["color"].map(lambda color: (255, 255, 0, 255) if np.random.random() > 0.8 else color)


            from pydeck import Layer, Deck
            from pydeck.data_utils import compute_view
            from pydeck.types import String
            import pydeck as pdk


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
                size_scale=550,
                # _animations={"*": {"speed": 5}},
                # _lighting=String("pbr"),
            )

            # Render
            # put china in the center of the map

            view  = {"latitude": 31, "longitude": 114, "zoom": 3.5, "pitch": 0, "bearing": 0}

            with placeholder.container():

                import datetime
                # get Beijing time

                beijing_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
                st.write("北京时间：", beijing_time)

                r = Deck(
                    
                     [cases_layer, layer],
         
                    #  put China in the center
                    
                    # api_keys={"mapbox": "pk.eyJ1Ijoid3liZXJ0IiwiYSI6ImNrYjk0bnpkdjBhczAycm84OWczMGFseDcifQ.icmgMlugfJ8erQ-JKmovWQ"},
                        initial_view_state=view,
            
                    # use chinese map style
                    # map_style="road",
                    map_provider="mapbox", 
                    map_style= pdk.map_styles.SATELLITE,
                    # "mapbox://styles/wybert/ciy3x71yu000l2st2r4t0f6nw",
                        #  initial_view_state=view
                        # show country name and icao24 as tooltip
                    tooltip= {"text": "航班来自: {origin_country} \n ICAO代码: {icao24}"}
                        )

                st.pydeck_chart(r)

            time.sleep(0.1)
        time.sleep(0.5)

    # r.to_html("scenegraph_layer1.html")
# st.write("这是一个疫情监测系统的演示。请注意，数据不是真实的。")

