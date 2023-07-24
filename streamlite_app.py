import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
import pandas as pd


# st.title("Epidemic Surveillance System")
# Translate the text to Chinese
st.title("疫情监测系统")
# st.write("This is a demo of the Epidemic Surveillance System. Notice that the data is not real. the data is shown as below:")

routes = pd.read_csv('flights edited.csv')

tab1, tab2 = st.tabs(["历史航班", "实时航班"])

with tab1:
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

    st.write("这是一个疫情监测系统的演示。请注意，数据不是真实的。数据如下：")

    st.dataframe(routes.head())

with tab2:
    st.write("实时航班数据")

    import requests
    import pandas as pd

    url = "https://opensky-network.org/api/states/all"

    from dotenv import load_dotenv

    import os
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())

    user = os.environ.get("user")
    password = os.environ.get("password")

    r = requests.get(url, auth=(user, password))

    json_data = r.json()
    states = pd.DataFrame(json_data['states'], columns=['icao24', 'callsign', 'origin_country', 'time_position', 
                                                        'last_contact', 'longitude', 'latitude', 'baro_altitude', 'on_ground', 'velocity', 
                                                        'true_track', 'vertical_rate', 'sensors', 'geo_altitude', 'squawk', 'spi', 'position_source'])
    # fill null values
    states =   states.fillna(0)
    states["roll"] = 0
    states["yaw"] = -states["true_track"]
    states["pitch"] = 90

    import matplotlib.cm as cm
    cmap = cm.get_cmap('viridis') 
    states['color'] = states['origin_country'].map(lambda country: tuple(int(c * 255) for c in cmap(hash(country))[:3]) + (255,))  # RGBA values with alpha=255


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
        # pickable=True,
        scenegraph=SCENEGRAPH_URL,
        get_position=["longitude", "latitude", "geo_altitude"],
        sizeMinPixels=0.1,
          sizeMaxPixels=1.5,
        get_orientation= ["roll","yaw" , "pitch"],
        # set color
        get_color= "color",
        size_scale=500,
        # _animations={"*": {"speed": 5}},
        _lighting=String("pbr"),
    )

    # Render
    # put china in the center of the map

    view  = {"latitude": 35.8617, "longitude": 104.1954, "zoom": 3.5, "pitch": 0, "bearing": 0}
    r = Deck(layer, 
            #  put China in the center
                initial_view_state=view,
            #  initial_view_state=view
            )

    st.pydeck_chart(r)

    # r.to_html("scenegraph_layer1.html")