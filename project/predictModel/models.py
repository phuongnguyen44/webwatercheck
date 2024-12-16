import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB


from sklearn.model_selection import cross_val_score

water_data=pd.read_csv('project/predictModel/water_potability.csv')
std_scaler=StandardScaler()
def water_Quality_Prediction(input_data,model):
  scaled_data=std_scaler.transform(input_data)
  model_prediction=model.predict(scaled_data)
  if model_prediction[0]==0:
    return 'Water NotSafe'
  else:
    return 'Water Safe'

def predicted(ph,Hardness,Solids,Chloramines,Sulfate,Conductivity,Organic_carbon,Trihalomethanes,Turbidity):
    dic={}
    X=water_data.drop('Potability',axis=1)
    y=water_data['Potability']
    # Kiểm tra NaN hoặc Inf
    if np.any(np.isnan(X)) or np.any(np.isinf(X)):
        print("Dữ liệu có chứa NaN hoặc Inf, cần xử lý trước khi chuẩn hóa.")
        # Xử lý NaN, ví dụ: thay thế NaN bằng giá trị trung bình hoặc giá trị gần nhất
        X = np.nan_to_num(X, nan=np.nanmean(X))
    X_scaled=std_scaler.fit_transform(X)
    x_train,x_test,y_train,y_test=train_test_split(X_scaled,y,test_size=0.2,random_state=42,stratify=y)

    LR =LogisticRegression()
    DT=DecisionTreeClassifier()
    RF=RandomForestClassifier()
    ETC=ExtraTreesClassifier()
    SVM=SVC()
    KNN=KNeighborsClassifier()
    ABC=AdaBoostClassifier()
    GBC=GradientBoostingClassifier()
    NB=GaussianNB()

    models=[LR,DT,RF,ETC,SVM,KNN,ABC,GBC,NB]
    features=X_scaled
    labels =y
    CV=5
    accu_list=[]
    ModelName=[]

    for model in models:
        model_name=model.__class__.__name__
        accuracies=cross_val_score(model,features,labels,scoring='accuracy',cv=CV)
        accu_list.append(accuracies.mean()*100)
        ModelName.append(model_name)

    model_acc_df=pd.DataFrame({'ModelName':ModelName,'Accuracy':accu_list})
    html_table = model_acc_df.to_html(index=False)

    SVM.fit(x_train,y_train)
    ETC.fit(x_train,y_train)
    RF.fit(x_train,y_train)
    LR.fit(x_train,y_train)
    KNN.fit(x_train,y_train)
    GBC.fit(x_train,y_train)
    ABC.fit(x_train,y_train)
    DT.fit(x_train,y_train)
    NB.fit(x_train,y_train)
    input_data=np.array([[ph,Hardness,Solids,Chloramines,Sulfate,Conductivity,Organic_carbon,Trihalomethanes,Turbidity]])
    dic['LR']=water_Quality_Prediction(input_data,LR)
    dic['DT']=water_Quality_Prediction(input_data,DT)
    dic['RF']=water_Quality_Prediction(input_data,RF)
    dic['ETC']=water_Quality_Prediction(input_data,ETC)
    dic['SVM']=water_Quality_Prediction(input_data,SVM)
    dic['KNN']=water_Quality_Prediction(input_data,KNN)
    dic['ABC']=water_Quality_Prediction(input_data,ABC)
    dic['GBC']=water_Quality_Prediction(input_data,GBC)
    dic['NB']=water_Quality_Prediction(input_data,NB)
    return [dic,html_table]



