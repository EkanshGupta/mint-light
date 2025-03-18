import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
from os import listdir
from os.path import isfile, join
import os
import re

################################################################
#Transaction format as per banks
#Amex - date range
#BOFA - statement month wise
#Chase - year to date
#Citi - year to date or statement month-wise
#USB - date range
#WF - date range
#
#
#
#
#################################################################

def func(pct, allvals):
    absolute = int(pct/100.*(allvals.sum()))
    return "{:.1f}%\n(${:d})".format(pct, absolute)

def loadLabeledTransactions(folder):
    labeled = processCSVFile(folder+"labeledTransactions.csv")
    labeled = cleanData(labeled)
    return labeled

def findMatch(name1, name2):
    M = len(name1)
    N = len(name2)
    arr = np.zeros((M+1,N+1))
    for j in range(N,0,-1):
        for i in range(M,0,-1):
            if name1[i-1]==name2[j-1]:
                arr[i-1,j-1] = max(1 + (arr[i,j]), max(arr[i-1,j],arr[i,j-1]))
            else:
                arr[i-1,j-1] = max(arr[i,j],max(arr[i-1,j],arr[i,j-1]))
    score = arr[0,0]
    return score*1.0/M   

def processName(name1):
    exclusionList = ['atlanta','ga','roswell','sandy','springs']
    name1 = str(name1)
    name1 = name1.replace("*"," ")
    name1 = name1.replace("."," ")
    name1 = [elem for elem in name1.split(" ") if elem.strip()!='']
    name1 = [re.sub("[^A-Z]", "", elem,0,re.IGNORECASE).lower() for elem in name1]
    name1 = [elem for elem in name1 if elem!='']
    name1 = [elem for elem in name1 if elem not in exclusionList]
    return name1

def returnMatch(name1, name2):
    name2=processName(name2)
    score = findMatch(name1, name2)
    if score>0.5:
        return True
    else:
        return False

def getTypeFromName(name, trainData):
    name=processName(name)
    #The algorithm is as follows
    #p = #name matches name and type matches type / #name
    #get a list of rows from trainData with name matches and choose the most common type
    #df.loc[df.index[index_list]] indexes a df
    idx = trainData.index.tolist() 
    idxList = []
    for i in idx:
        name2 = trainData.loc[i,'name']
        if returnMatch(name, name2):
            idxList.append(i) 
    if idxList==[]:
        return '',''
    trainSubset = trainData.loc[idxList]
#     print("the name is: ",name)
    trainSubset = trainSubset.mode()
    
#     print("The returned mode is ",trainSubset)
    return trainSubset.at[0,'type'], trainSubset.at[0,'subtype']

def labelTranUsingTrain(aggregateDf, trainData):
    idx = aggregateDf.index.tolist() 
#     print(aggregateDf)
    for i in idx:
        name = aggregateDf.loc[i,'name']
        typeCat, subtypeCat = getTypeFromName(name, trainData)
        aggregateDf.at[i,'type'] = typeCat
        aggregateDf.at[i,'subtype'] = subtypeCat
#         print(name) 
#         print(typeCat) 
#         print(subtypeCat)
    return aggregateDf

def cleanData(df):
    #this function removes unlabeled columns, negative transactions
    df = df.dropna(axis=0, subset=['type','subtype'])
    df = df[df['value']>0]
#     with pd.option_context('display.max_colwidth', None,'display.max_rows', None):
#         display(df)
    return df

def labelTransactions(folder):
    csvFiles = getCSVFileList(folder)
    aggregateDf = pd.DataFrame()
    
    #get unlabeled transaction files first
    for file in csvFiles:
        if "train" not in file and "labeled" not in file:
            data = processCSVFile(file)
            data = data[data['value']>0]
            if aggregateDf.empty:
                aggregateDf = data
            else:
                aggregateDf = pd.concat([aggregateDf, data], axis=0, ignore_index=True)
    aggregateDf = aggregateDf[aggregateDf['value']>0]
    #get train transactions
    trainData = processCSVFile(folder+"labeledTransactions.csv")
    trainData = cleanData(trainData)
    
    aggregateDf = labelTranUsingTrain(aggregateDf, trainData)
    with pd.option_context('display.max_colwidth', None,'display.max_rows', None):
        display(aggregateDf)
        
    #Uncomment this line only if you are sure of the correctness of the new labeled transactions
    aggregateDf.to_csv(folder+'labeledTransactions.csv', index=False)  

    return aggregateDf
    

def processAmexCsv(file):
    df = pd.read_csv(file)
    df = df.rename(columns={"Date": "date", "Description": "name", "Amount":"value"})
    df['type']=''
    df['subtype']=''
    df['ownership']=''
    df['comments']=''
    df = df[['date','name','value','type','subtype','ownership','comments']]
    return df
    
def processWFCsv(file):
    with open(file, 'r') as f:
        data = f.read()
    if 'date,value,type' not in data:
        data = 'date,value,type,subtype,name\n'+data
        with open(file, 'w') as f:
            f.write(data)    
    df = pd.read_csv(file)
    df['value'] = df['value']*-1
    df['type']=''
    df['subtype']=''
    df['ownership']=''
    df['comments']=''
    df = df[['date','name','value','type','subtype','ownership','comments']]
    return df
    
def processCitiCsv(file):
    df = pd.read_csv(file)
    df=df.rename(columns={"Date": "date", "Description": "name", "Debit":"value"})
    df = df.drop(columns=['Status','Credit'])
    df['type']=''
    df['subtype']=''
    df['ownership']=''
    df['comments']=''
    return df
    
def processBofaCsv(file):
    df = pd.read_csv(file)
    df=df.rename(columns={"Posted Date": "date", "Payee": "name", "Amount":"value"})
    df = df.drop(columns=['Reference Number','Address'])
    df['value'] = df['value']*-1
    df['type']=''
    df['subtype']=''
    df['ownership']=''
    df['comments']=''
    return df
    
def processChaseCsv(file):
    df = pd.read_csv(file)
    df=df.rename(columns={"Transaction Date": "date", "Description": "name", "Amount":"value"})
    df = df.drop(columns=['Post Date','Category','Type','Memo'])
    df['value'] = df['value']*-1
    df['type']=''
    df['subtype']=''
    df['ownership']=''
    df['comments']=''
    return df
    
def processUSBCsv(file):
    df = pd.read_csv(file)
    df=df.rename(columns={"Date": "date", "Name": "name", "Amount":"value"})
    df = df.drop(columns=['Transaction','Memo'])
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['date'] = df['date'].dt.strftime('%m/%d/%Y')
    df['value'] = df['value']*-1
    df['type']=''
    df['subtype']=''
    df['ownership']=''
    df['comments']=''
    return df
    
def getCSVFileList(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles = [os.path.join(dirpath,f) for (dirpath, dirnames, filenames) in os.walk(mypath) for f in filenames]
    onlyCSV = [f for f in onlyfiles if 'csv' in f]
    return onlyCSV

def processCSVFile(file):
    if 'Amex' in file:
        return processAmexCsv(file)
    elif 'WF' in file:
        return processWFCsv(file)
    elif 'Citi' in file:
        return processCitiCsv(file)
    elif 'BOFA' in file:
        return processBofaCsv(file)
    elif 'Chase' in file:
        return processChaseCsv(file)
    elif 'USB' in file:
        return processUSBCsv(file)
    else:
        return pd.read_csv(file)

def getBudget(month):
    return 1400

def getTotalSpendFromDf(df):
    return np.around(df['value'].sum(),1)

def getSpendFromType(typeVal, df):
    df = df[df['type']==typeVal]
    return getTotalSpendFromDf(df)
    
def getSpendFromSubType(subTypeVal, df):
    df = df[df['subtype']==subTypeVal]
    return getTotalSpendFromDf(df)

def callSpendFunc(arg, df):
    if arg=='total':
        return getTotalSpendFromDf(df)
    elif arg == 'dineout':
        return getSpendFromSubType('dine-in',df) + getSpendFromSubType('takeout',df)
    elif 'groceries' in arg:
        arg,owner = arg.split('-')
        df = df[df['ownership']==owner]
        return getSpendFromSubType(arg,df)
    elif arg in typeList:
        return getSpendFromType(arg,df)
    elif arg in subTypeList:
        return getSpendFromSubType(arg,df)
