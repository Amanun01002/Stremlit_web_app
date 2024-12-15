import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# API キー
API_key = st.secrets["general"]

# 関数: エリアデータを取得する
def fetch_area_data(url, params, area_key):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {item['name']: item['code'] for item in data['results'][area_key]}
    else:
        st.error("データの取得に失敗しました")
        return {}

# 初期化: session_state
if "shop_data" not in st.session_state:
    st.session_state.shop_data = None  # 店舗データの初期化

# Streamlit アプリ
st.title('Help みぃ〜!')  # タイトル
st.write("検索条件を指定してください")  # サブタイトル

# Large Area の選択肢を取得
url_large_area = "http://webservice.recruit.co.jp/hotpepper/large_area/v1/"
large_area_params = {"key": API_key, "format": "json"}
large_area_data = fetch_area_data(url_large_area, large_area_params, "large_area")

# Large Area を選択
large_area_name = st.selectbox("大エリアを選んでください", large_area_data.keys())
large_area_code = large_area_data[large_area_name]

# Middle Area の選択肢を取得
url_middle_area = "http://webservice.recruit.co.jp/hotpepper/middle_area/v1/"
middle_area_params = {"key": API_key, "large_area": large_area_code, "format": "json"}
middle_area_data = fetch_area_data(url_middle_area, middle_area_params, "middle_area")

# Middle Area を選択
if middle_area_data:
    middle_area_name = st.selectbox("中エリアを選んでください", middle_area_data.keys())
    middle_area_code = middle_area_data[middle_area_name]

    # Small Area の選択肢を取得
    url_small_area = "http://webservice.recruit.co.jp/hotpepper/small_area/v1/"
    small_area_params = {"key": API_key, "middle_area": middle_area_code, "format": "json"}
    small_area_data = fetch_area_data(url_small_area, small_area_params, "small_area")

    # Small Area を選択
    if small_area_data:
        small_area_name = st.selectbox("小エリアを選んでください", small_area_data.keys())
        small_area_code = small_area_data[small_area_name]

# 諸条件
Private_room = st.checkbox("個室あり")
free_drink = st.checkbox("飲み放題あり")
free_food = st.checkbox("食べ放題あり")

# 店の最大パーティ人数で絞る
party_capacity = st.slider('最大宴会収容人数', 1, 1000, 10)

# 表示データ数
count = st.slider('最大表示データ数', 1, 100, 30)



url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
params = {
    "key": API_key,
    "format": "json",
    "large_area": large_area_code,
    "middle_area": middle_area_code,
    "small_area": small_area_code,
    "Private_room":Private_room,
    "free_drink":free_drink,
    "free_food":free_food,
    "party_capacity": party_capacity,
    "count": count
}

# 店情報を取得
if st.button("検索開始"):
    data = requests.get(url, params=params).json()
    if "shop" in data["results"]:
        st.session_state.shop_data = data['results']['shop']  # データを session_state に保存
    else:
        st.session_state.shop_data = None
        st.warning("店舗情報が見つかりませんでした。")

# 検索結果の表示
if st.session_state.shop_data:
    st.write('お店の数', len(st.session_state.shop_data))

    # 地図作成
    m = folium.Map(location=[35.6895, 139.6917], zoom_start=12)  # 初期位置は東京に設定

    for shop in st.session_state.shop_data:
        lat = shop["lat"]
        lng = shop["lng"]
        name = shop["name"]

        # 店舗の情報を地図に追加
        folium.Marker(
            location=[lat, lng],
            popup=f"{name}",
        ).add_to(m)

        # 店舗情報の表示
        st.write(shop["name"])
        st.write(shop["access"])
        st.write(shop["budget"]["average"])
        st.write(shop["urls"]["pc"])
        st.write(shop["catch"])
        st.write('-------------------------------------------------')

    # Streamlitで地図を表示
    st_folium(m, width=700, height=500)
