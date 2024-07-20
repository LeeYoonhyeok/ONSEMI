from celery import shared_task

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
import requests
import json
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense
from statsmodels.tsa.statespace.sarimax import SARIMAX

# TensorFlow에서 GPU를 사용하지 않도록 설정
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

@shared_task
def my_task():
 
  def crop_name(column_name):
    if '_' in column_name:
      return column_name.split('_')[0]
    return column_name
 
  def url_data(itemcategorycode, itemcode, kindcode, rankcode):
      url = f"https://www.kamis.or.kr/service/price/xml.do?action=periodProductList&" \
            f"p_productclscode=01&" \
            f"p_startday=2024-01-01&" \
            f"p_itemcategorycode={itemcategorycode}&" \
            f"p_itemcode={itemcode}&" \
            f"p_kindcode={kindcode}&" \
            f"p_productrankcode={rankcode}&" \
            f"p_convert_kg_yn=Y&" \
            f"p_cert_key=381ef533-54ca-4418-bac6-40ff8a94b775&" \
            f"p_cert_id=4536&" \
            f"p_returntype=json&"\
            f"p_countrycode=1101"
      response = requests.get(url)
      data = response.json()
      return data
 
  def preprocessing(itemcategorycode, itemcode, kindcode, rankcode):
      data = url_data(itemcategorycode, itemcode, kindcode, rankcode)
 
      # 작물 이름 가져오기
      df_data = pd.DataFrame(data['data']['item'])
      name = df_data[df_data['countyname'] == '서울']['itemname'].unique()
      kindname = df_data[df_data['countyname'] == '서울']['kindname'].unique()
 
      # 전국 평균가격 추출
      df_data = df_data.loc[df_data['countyname'] == '평균']
 
      # 컬럼가져오기
      df_data = df_data[['itemname', 'yyyy', 'regday', 'price']]
      df_data['itemname'] = name[0]
 
      # 시계열로 변경
      df_data['datetime'] = pd.to_datetime(df_data['yyyy'].astype(str) + '-' + df_data['regday'])
 
      df_data = df_data[['datetime', 'price']]
      df_data.columns = ['datetime', name[0]+'_'+kindname[0]]
 
      # 가격을 숫자로 변환
      df_data[name[0]+'_'+kindname[0]] = df_data[name[0]+'_'+kindname[0]].str.replace(',', '').astype(float)
 
      return df_data
 
  # 작물 코드 목록
  items = [
      {"itemcategorycode": "200", "itemcode": "212", "kindcode": "00", "rankcode": "04"},#양상추 #상시판매
      {"itemcategorycode": "200", "itemcode": "213", "kindcode": "00", "rankcode": "04"},#시금치 #상시판매
      {"itemcategorycode": "100", "itemcode": "111", "kindcode": "01", "rankcode": "04"},#쌀 #상시판매
      {"itemcategorycode": "100", "itemcode": "141", "kindcode": "01", "rankcode": "04"},#흰콩 #상시판매
      {"itemcategorycode": "100", "itemcode": "143", "kindcode": "00", "rankcode": "04"},#녹두 #상시판매
      {"itemcategorycode": "100", "itemcode": "151", "kindcode": "00", "rankcode": "04"},#고구마 #상시판매
      {"itemcategorycode": "100", "itemcode": "152", "kindcode": "01", "rankcode": "04"},#감자 #상시판매
      {"itemcategorycode": "200", "itemcode": "215", "kindcode": "00", "rankcode": "04"},#배추 봄 여름 가을 월동?
      {"itemcategorycode": "200", "itemcode": "214", "kindcode": "01", "rankcode": "04"},#적상추 #상시판매
      {"itemcategorycode": "200", "itemcode": "221", "kindcode": "00", "rankcode": "04"},#수박 #상시판매
 
      {"itemcategorycode": "200", "itemcode": "223", "kindcode": "01", "rankcode": "04"},#오이 #상시판매
      {"itemcategorycode": "200", "itemcode": "224", "kindcode": "01", "rankcode": "04"},#애호박 #상시판매
      {"itemcategorycode": "200", "itemcode": "225", "kindcode": "00", "rankcode": "04"},#토마토  #상시판매
      {"itemcategorycode": "200", "itemcode": "232", "kindcode": "01", "rankcode": "04"},#당근 #상시판매
      {"itemcategorycode": "200", "itemcode": "233", "kindcode": "00", "rankcode": "04"},#열무 # 상시판매
      {"itemcategorycode": "200", "itemcode": "242", "kindcode": "02", "rankcode": "04"},#꽈리고추 # 상시판매
      {"itemcategorycode": "200", "itemcode": "245", "kindcode": "00", "rankcode": "04"},#양파 # 상시판매
      {"itemcategorycode": "200", "itemcode": "246", "kindcode": "00", "rankcode": "04"},#대파 # 상시판매
      {"itemcategorycode": "200", "itemcode": "248", "kindcode": "00", "rankcode": "04"},#고춧가루 # 상시판매
      {"itemcategorycode": "200", "itemcode": "253", "kindcode": "00", "rankcode": "04"},#깻잎 # 상시판매
      {"itemcategorycode": "200", "itemcode": "255", "kindcode": "00", "rankcode": "04"},#피망 # 상시판매
      {"itemcategorycode": "200", "itemcode": "257", "kindcode": "00", "rankcode": "04"},#멜론 # 상시판매
      {"itemcategorycode": "200", "itemcode": "258", "kindcode": "01", "rankcode": "04"},#깐마늘 # 상시판매
      {"itemcategorycode": "300", "itemcode": "315", "kindcode": "00", "rankcode": "04"},#느타리버섯 # 상시판매
      {"itemcategorycode": "300", "itemcode": "317", "kindcode": "00", "rankcode": "04"},#새송이버섯 # 상시판매
      {"itemcategorycode": "400", "itemcode": "412", "kindcode": "01", "rankcode": "04"},#배 # 상시판매
      {"itemcategorycode": "400", "itemcode": "418", "kindcode": "02", "rankcode": "04"},#바나나 # 상시판매
      {"itemcategorycode": "400", "itemcode": "420", "kindcode": "02", "rankcode": "04"},#파인애플 # 상시판매
      {"itemcategorycode": "400", "itemcode": "422", "kindcode": "01", "rankcode": "04"},#방울토마토 # 상시판매
  ]
 
  non_season_list = [preprocessing(**item) for item in items]
 
  df_non_season = non_season_list[0]
  for df in non_season_list[1:]:
      df_non_season = pd.merge(df_non_season, df, on='datetime', how='outer')
 
  #일정구간 거래가격 변 없어서 스무딩 처리
  df_non_season['콩_흰 콩(국산)(1kg)'] = df_non_season['콩_흰 콩(국산)(1kg)'].rolling(window=5).mean()
  df_non_season['녹두_국산(1kg)'] = df_non_season['녹두_국산(1kg)'].rolling(window=5).mean()
  df_non_season['오이_가시계통(10개)'] = df_non_season['오이_가시계통(10개)'].rolling(window=5).mean()
  df_non_season['고춧가루_국산(1kg)'] = df_non_season['고춧가루_국산(1kg)'].rolling(window=5).mean()
  df_non_season['파인애플_수입(1개)'] = df_non_season['파인애플_수입(1개)'].rolling(window=5).mean()
 
  #(비계절성)주말데이터를 채우는 작업
  df_non_season['datetime'] = pd.to_datetime(df_non_season['datetime'])
 
  date_range = pd.date_range(start=df_non_season['datetime'].min(), end=df_non_season['datetime'].max())
 
  df_range = pd.DataFrame({'datetime': date_range})
 
  df_non_season = pd.merge(df_range, df_non_season, on='datetime', how='left')
 
  df_non_season = df_non_season.interpolate(method='linear')
 
  #계절성 과일
  def preprocessing2(itemcategorycode, itemcode, kindcode, rankcode):
      data = url_data(itemcategorycode, itemcode, kindcode, rankcode)
 
      # 작물 이름 가져오기
      df_data = pd.DataFrame(data['data']['item'])
      name = df_data[df_data['countyname'] == '서울']['itemname'].unique()
      kindname = df_data[df_data['countyname'] == '서울']['kindname'].unique()
 
      # 전국 평균가격 추출
      df_data = df_data.loc[df_data['countyname'] == '평균']
 
      # 컬럼가져오기
      df_data = df_data[['itemname', 'yyyy', 'regday', 'price']]
      df_data['itemname'] = name[0]
 
      # 시계열로 변경
      df_data['datetime'] = pd.to_datetime(df_data['yyyy'].astype(str) + '-' + df_data['regday'])
 
      df_data = df_data[['datetime', 'price']]
      df_data.columns = ['datetime', name[0]+'_'+kindname[0]]
 
      # 가격을 숫자로 변환
      df_data[name[0]+'_'+kindname[0]] = df_data[name[0]+'_'+kindname[0]].str.replace(',', '').astype(float)
 
      return df_data
 
      # 작물 코드 목록
  items = [
    {"itemcategorycode": "200", "itemcode": "222", "kindcode": "00", "rankcode": "04"},#참외
    {"itemcategorycode": "400", "itemcode": "413", "kindcode": "01", "rankcode": "04"},#복숭아 # 판매 너무짧음
    {"itemcategorycode": "400", "itemcode": "415", "kindcode": "01", "rankcode": "13"},#귤 # 판매 너무 짧음
    {"itemcategorycode": "400", "itemcode": "411", "kindcode": "05", "rankcode": "04"},#사과 # 잠시 보류
    {"itemcategorycode": "200", "itemcode": "226", "kindcode": "00", "rankcode": "04"},#딸기 #오랜기간 판매를 안하는 품목에 대한 처리 고민
  ]
 
  season_list = [preprocessing2(**item) for item in items]
 
  df_season= season_list[0]
  for df in season_list[1:]:
      df_season = pd.merge(df_season, df, on='datetime', how='outer')
 
  #(계절성)전처리 및 주말데이터 처리
  df_season['datetime'] = pd.to_datetime(df_season['datetime'])
 
  df_season = df_season.sort_values(by='datetime')
 
  df_season = df_season.fillna(0)
 
  date_range = pd.date_range(start=df_season['datetime'].min(), end=df_season['datetime'].max())
 
  df_range2 = pd.DataFrame({'datetime': date_range})
 
  df_season = pd.merge(df_range2, df_season, on='datetime', how='left')
 
  df_season = df_season.interpolate(method='linear')
 
  df_season = df_season.iloc[12:]
 
  #계절성 비계절성 작물 병합
  df_crop= pd.merge(df_non_season, df_season, on = 'datetime')
  #이름만 추출
  crop_columns = [crop_name(col) for col in df_crop.columns]
 
  total = df_crop.copy()
  total.columns = crop_columns
 
  # 문자열을 datetime으로 변환
  total['datetime'] = pd.to_datetime(total['datetime'])
 
  # 날짜만 추출
  total['datetime'] = total['datetime'].dt.date
  # 과거 2022-2023 데이터
  df_past = pd.read_csv('2022-2023_data.csv')
  # 2022 ~ 현재
  df_total = pd.concat([df_past,total ], axis = 0)
  df_total = df_total.round(0)
  df_total.rename(columns = {'호박':'애호박'}, inplace = True)
 
  scale_down = ["시금치", "콩", "녹두", "감자", "상추", "오이", "당근", "풋고추", "파", "깻잎", "피망", "느타리버섯", "새송이버섯", "배", "방울토마토", "참외", "복숭아", "사과"]
  scale_up = ["쌀"]
 
  #scale처리
  df_total[scale_down] = df_total[scale_down] / 10
  df_total[scale_up] = df_total[scale_up] * 5
 
  df_total.to_csv('total.csv',index = False)
  ##모델링 코드
 
  # 데이터 전처리
  def preprocess(data, time_step=7):
      scalers = {}
      data_scaled = np.zeros_like(data)
      for i in range(data.shape[1]):
          scalers[i] = MinMaxScaler()
          data_scaled[:, i] = scalers[i].fit_transform(data[:, i].reshape(-1, 1)).flatten()
 
      X, y = [], []
      for i in range(len(data_scaled) - time_step):
          X.append(data_scaled[i:i + time_step])
          y.append(data_scaled[i + time_step, 0])  # 가격 데이터만 예측 대상
 
      X = np.array(X)
      y = np.array(y)
      return X, y, scalers
 
  # 시계열 전처리
  def preprocess_time(data, crop_index, time_step=7):
      crop_data = data.iloc[:, crop_index].values.reshape(-1, 1)
 
      data['weekday'] = data['datetime'].dt.weekday
      data['month'] = data['datetime'].dt.month
 
      additional_data = data[['weekday', 'month']].values
      crop_data = np.concatenate([crop_data, additional_data], axis=1)
 
      X, y, scalers = preprocess(crop_data, time_step)
      return X, y, scalers
 
  # GRU 모델 생성
  def create_gru(input_shape):
      model = Sequential()
      model.add(GRU(units=32, return_sequences=True, input_shape=input_shape, activation = 'relu'))
      model.add(GRU(units=64, return_sequences=True, activation = 'relu'))
      model.add(GRU(units=128, activation = 'relu'))
      model.add(Dense(50, activation='relu'))
      model.add(Dense(1, activation='linear'))
      model.compile(optimizer='adam', loss='mean_squared_error')
      return model
 
  # GRU 예측
  def predict_gru(model, last_data, time_step, scalers, days=7):
      predictions = []
      for _ in range(days):
          last_data_scaled = np.zeros_like(last_data[-time_step:])
          for i in range(last_data.shape[1]):
              last_data_scaled[:, i] = scalers[i].transform(last_data[-time_step:, i].reshape(-1, 1)).flatten()
 
          input_data = last_data_scaled.reshape(1, time_step, -1)
          predict = model.predict(input_data)
          predict_price = scalers[0].inverse_transform(predict).flatten()[0]
          predictions.append(predict_price)
 
          new_row = np.array([[predict_price, (last_data[-1][1] + 1) % 7, (last_data[-1][2] % 12) + 1]])
          last_data = np.append(last_data, new_row, axis=0)
      return predictions
 
  # SARIMA 예측
  def predict_sarima(data, steps=7):
      model = SARIMAX(data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 30))
      model_fit = model.fit(disp=False)
      predict = model_fit.get_forecast(steps=steps)
      predict_mean = predict.predicted_mean
      return predict_mean
 
  # 데이터 로드
#   data = pd.read_csv('test_data.csv')
 
#   data['datetime'] = pd.to_datetime(data['datetime'])

  data = pd.read_csv('total.csv')
  print(data.head()) 
  # data = data[['datetime', '양배추']]
  data['datetime'] = pd.to_datetime(data['datetime'])
 
  time_step = 7
 
  results = []
  models = {}
 
  # 작물별 학습 및 예측
  for crop_index in range(1, data.shape[1] - 2):  # 컬럼 제외
  # for crop_index in range(1, data.shape[1]):  # 컬럼 제외
      crop_name = data.columns[crop_index]
      print(f"Preprocessing column: {crop_name}")
      X, y, scalers = preprocess_time(data, crop_index, time_step)
 
      # GRU 모델 학습
      gru_model = create_gru((X.shape[1], X.shape[2]))
      gru_model.fit(X, y, epochs=30, batch_size=128, validation_split=0.2, verbose=0)
      print(f"GRU model trained for {crop_name}")
 
      last_data = data.iloc[-time_step:, [crop_index]].values
      last_data = np.concatenate([last_data, data.iloc[-time_step:, -2:].values], axis=1)
      #GRU
      gru_price = predict_gru(gru_model, last_data, time_step, scalers)
      print(f"Predictions for {crop_name} (GRU): {gru_price}")
 
      # SARIMA
      sarima_price = predict_sarima(data.iloc[:, crop_index].values)
      print(f"Predictions for {crop_name} (SARIMA): {sarima_price}")
 
      # 앙상블
      future_prices = (np.array(gru_price) + np.array(sarima_price)) / 2
      print(f"Predictions for {crop_name} (Ensemble): {future_prices}")
 
      # 비율 계산
      start_price = last_data[-1][0]
      end_price = future_prices[-1]
    #   rise_ratio = ((end_price - start_price) / start_price)
      rise_ratio = ((end_price - start_price) / start_price) if start_price != 0 else 0
      
 
      if start_price == 0:
        rise_ratio = 0
 
      results.append((crop_name, start_price, end_price, rise_ratio))
      models[crop_name] = (gru_model, scalers, future_prices)
 
 
  # 상승 상위5개
  results_top = sorted(results, key=lambda x: x[3], reverse=True)[:5]
  results_bottom = sorted(results, key=lambda x: x[3], reverse=True)[-5:]

  results_top = pd.DataFrame(results_top, columns=["작물명", "시작 가격", "종료 가격", "상승 비율"])
  results_bottom = pd.DataFrame(results_bottom, columns=["작물명", "시작 가격", "종료 가격", "상승 비율"])

#   results_df = pd.concat([results_top, results_bottom], axis=0)
#   results_df.to_csv('result_total.csv', index=False, encoding='UTF-8')
#   results_df[["작물명", "상승 비율"]].to_csv('result.csv', index=False, encoding='UTF-8')
 
 
#   results_top = pd.DataFrame(results_top)
#   results_bottom = pd.DataFrame(results_bottom)
 
  results_df = pd.concat([results_top,results_bottom], axis = 0)
  print(results_df.head()) 
  results_df.to_csv('result_total.csv',index = False, encoding = 'UTF-8')
#   results_df[[0,3]].to_csv('result.csv',index = False, encoding = 'UTF-8')
  results_df.iloc[:, [0, 3]].to_csv('result.csv', index=False, encoding='UTF-8')
#   ans = pd.read_csv('total.csv')
#   print(ans.head())

  print("CSV 파일 저장 완료")

  return "작업 완료"


# @shared_task
# def my_task():
#     print('고생했다')
#     return 'Task completed'