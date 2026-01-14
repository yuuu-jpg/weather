import os
import requests
from flask import Flask, render_template
from dotenv import load_dotenv
from datetime import datetime

# .envファイルを読み込み
load_dotenv()

# 曜日の日本語
JP_WEEKDAYS = ['月', '火', '水', '木', '金', '土', '日']

def format_date_with_weekday(date_str):
    """YYYY-MM-DD形式の日付に曜日を付与（例：2026-01-13（火））"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekday = JP_WEEKDAYS[date_obj.weekday()]
    return f"{date_str}（{weekday}）"

app = Flask(__name__)

# OpenWeatherMap APIキー
API_KEY = os.getenv('OPENWEATHER_API_KEY')
CITY = 'Tokyo'
LAT = 35.6762
LON = 139.6503

@app.route('/')
def index():
    """東京の天気情報と5日間予報を取得して表示"""
    try:
        # APIキー事前チェック
        if not API_KEY:
            return render_template('index.html', error='OpenWeatherのAPIキーが設定されていません。.env に OPENWEATHER_API_KEY= を追加してください。')

        # 現在の天気情報を取得
        url = f'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'lat': LAT,
            'lon': LON,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'ja'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 必要なデータを抽出
        sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset_time = datetime.utcfromtimestamp(data['sys']['sunset']).strftime('%H:%M')
        
        weather_info = {
            'city': CITY,
            'temperature': round(data['main']['temp']),
            'humidity': data['main']['humidity'],
            'weather': data['weather'][0]['main'],
            'description': data['weather'][0]['description'],
            'feels_like': round(data['main']['feels_like']),
            'sunrise': sunrise_time,
            'sunset': sunset_time
        }
        
        # 紫外線指数を取得
        try:
            uv_url = 'https://api.openweathermap.org/data/2.5/uvi'
            uv_params = {
                'lat': LAT,
                'lon': LON,
                'appid': API_KEY
            }
            uv_response = requests.get(uv_url, params=uv_params)
            uv_response.raise_for_status()
            uv_data = uv_response.json()
            weather_info['uv_index'] = round(uv_data['value'], 1)
        except requests.exceptions.RequestException:
            weather_info['uv_index'] = None
        
        # 空気品質を取得
        try:
            air_url = 'https://api.openweathermap.org/data/2.5/air_pollution'
            air_params = {
                'lat': LAT,
                'lon': LON,
                'appid': API_KEY
            }
            air_response = requests.get(air_url, params=air_params)
            air_response.raise_for_status()
            air_data = air_response.json()
            
            # AQI (Air Quality Index) の解釈
            aqi = air_data['list'][0]['main']['aqi']
            aqi_levels = {
                1: {'label': '優', 'color': '#00ff00'},
                2: {'label': '良', 'color': '#ffff00'},
                3: {'label': '普通', 'color': '#ff9900'},
                4: {'label': '悪い', 'color': '#ff0000'},
                5: {'label': '非常に悪い', 'color': '#8b0000'}
            }
            weather_info['air_quality'] = aqi_levels.get(aqi, {'label': '不明', 'color': '#999999'})
            
            # 主な汚染物質の濃度も取得
            components = air_data['list'][0]['components']
            weather_info['pm25'] = round(components.get('pm2_5', 0), 1)
            weather_info['pm10'] = round(components.get('pm10', 0), 1)
        except requests.exceptions.RequestException:
            weather_info['air_quality'] = None
            weather_info['pm25'] = None
            weather_info['pm10'] = None
        
        # 7日間予報の取得（One Call API 3.0 を試行 → 失敗時に5日予報へフォールバック）
        forecast_list = []
        try:
            # One Call API 3.0: daily予報（最大7日）
            onecall_url = 'https://api.openweathermap.org/data/3.0/onecall'
            onecall_params = {
                'lat': LAT,
                'lon': LON,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'ja',
                'exclude': 'current,minutely,hourly,alerts'
            }
            oc_response = requests.get(onecall_url, params=onecall_params)
            oc_response.raise_for_status()
            oc_data = oc_response.json()

            for item in oc_data.get('daily', [])[:7]:
                date = datetime.utcfromtimestamp(item['dt']).strftime('%Y-%m-%d')
                date_with_weekday = format_date_with_weekday(date)
                forecast_list.append({
                    'date': date_with_weekday,
                    'temp_min': round(item['temp']['min']),
                    'temp_max': round(item['temp']['max']),
                    'description': item['weather'][0]['description'],
                    'humidity': item.get('humidity', 0)
                })

        except requests.exceptions.RequestException:
            # フォールバック: 5日予報（3時間刻み）から日ごとに抽出
            forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'
            forecast_params = {
                'lat': LAT,
                'lon': LON,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'ja'
            }
            fv_response = requests.get(forecast_url, params=forecast_params)
            fv_response.raise_for_status()
            fv_data = fv_response.json()

            processed_dates = set()
            for item in fv_data['list']:
                date = item['dt_txt'].split(' ')[0]
                if date not in processed_dates:
                    processed_dates.add(date)
                    date_with_weekday = format_date_with_weekday(date)
                    forecast_list.append({
                        'date': date_with_weekday,
                        'temp_min': round(item['main']['temp_min']),
                        'temp_max': round(item['main']['temp_max']),
                        'description': item['weather'][0]['description'],
                        'humidity': item['main']['humidity']
                    })
                if len(forecast_list) >= 5:
                    break
        
        # 現在の日付を取得
        current_date = datetime.now().strftime('%Y年%m月%d日')
        current_time = datetime.now().strftime('%H:%M:%S')
        
        return render_template('index.html', weather=weather_info, forecast=forecast_list, current_date=current_date, current_time=current_time)
    
    except requests.exceptions.RequestException as e:
        error_message = f'天気情報の取得に失敗しました: {str(e)}'
        return render_template('index.html', error=error_message)

@app.route('/health')
def health():
    """Renderのヘルスチェック用エンドポイント"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
