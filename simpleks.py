#Simpleks Artur Czepiec
import fileinput
import sys
import re

MAX_ITER = 10

def readMinMax(default="max"):
    question="Wybierz max/min"
    valid = {"max": False, "MAX": False,
             "min": True, "MIN": True}
    if default is None:
        prompt = " [max]: "
    elif default == "max":
        prompt = " [max]: "
    elif default == "min":
        prompt = " [max]: "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Spróbuj ponownie\n")
         
def readInputRows(question, objF=False):
    inputData = dict();
    counter=0
    while True:
        sys.stdout.write(question)
        try:
            row = input().lower()
            (left,right) = parseInputRow(row)
            if objF:
                if objFunParsedCorrectly(row,left):
                    return left
                else:
                    sys.stdout.write("Coś poszło nie tak. Spróbuj podać wyrażenie w najprostszje postaci \n")
                    continue
            if rowParsedCorrectly(row,(left,right)):
                inputData[counter] = (left,right)
                counter = counter+1
            else:
                sys.stdout.write("Coś poszło nie tak. Spróbuj podać wyrażenie w najprostszje postaci \n")     
        except EOFError:
            return inputData

def objFunParsedCorrectly(row, parseResult):
    if not parseResult:
        return False
    row = ''.join(row.split())
    expr=""
    for e in parseResult:
        expr+=''.join(str(i) for i in e)
    if row == expr:
        return True
    return False
  
def parseInputRow(row):
    row = ''.join(row.split())
    left = re.findall(r'([+|-]?)(\d*\.?\d*)([a-z]+)', row)
    right = re.findall('(<=|>=|<|>|=)(-?)(\d+\.?\d*)', row)
    return (left,right)

def rowParsedCorrectly(row, parseResult):
    if not parseResult[0] or not parseResult[1]:
        return False
    tmp=parseResult[0]
    tmp.extend(parseResult[1])
    row = ''.join(row.split())
    left=""
    for e in tmp:
        left+=''.join(str(i) for i in e)
    if row == left:
        return True
    return False

def setupInputTables(objFunc, aRowsDict):
    recVariables = []
    f = []
    objFunc.sort(key=lambda tup: tup[2])
    for tup in objFunc:
        sigBefMult=1
        if tup[0] == '-':
            sigBefMult = -1
        val = tup[1]
        if val == '':
            val = 1
        f.append(float(val)*sigBefMult)
        recVariables.append(tup[2])
    A = [[0] * len(recVariables) for key in aRowsDict]
    for i,recVar in enumerate(recVariables):
        for j,key in enumerate(aRowsDict):
            sigBefMult=1
            if '>' in aRowsDict[key][1][0][0]:
                sigBefMult=sigBefMult*-1
            tup=getVarTuple(aRowsDict[key][0],recVar)
            if tup:
                if tup[0] == '-':
                    sigBefMult=sigBefMult*-1
                val = tup[1]
                if val == '':
                    val = 1
                else:
                    val = float(val)
                A[j][i] = val*sigBefMult
    b = []
    for key in aRowsDict:
        tup=aRowsDict[key][1][0]
        sigBefMult=1
        if tup[0] == '-':
            sigBefMult = -1
        b.append(float(tup[2])*sigBefMult)
    c = [0] * len(aRowsDict)
    return (A,f,b,c,recVariables)

  
def getVarTuple(tupList, var):
    for tup in tupList:
        if tup[2] == var:
            return tup
    return ()

def addSlackVariables(A):
    numOfVars = len(A)
    for i,row in enumerate(A):
        for j in range(numOfVars):
            row.append(int(i==j))

def isSolutionOptimal(resList, mini=False):
    for i in resList:
        if mini:
            if i < 0:
                return False
        elif i>0:
            return False
    return True

def computeZ(A,c):
    z = [0] * len(A[0])
    for i, row in enumerate(A):
        for j, col in enumerate(row):
            z[j]=z[j] + c[i] * col
    return z
          
def computeC_Z(f,z):
    c_z = [0] * len(z)
    for i, val in enumerate(f):
        c_z[i] = val - z[i]
    return c_z

def getPivotColumnIndex(c_z,mini):
    pivot_index = 0
    for i, val in enumerate(c_z):
        if mini:
            if val<c_z[pivot_index]:
                pivot_index=i
        elif(val>c_z[pivot_index]):
            pivot_index=i
    return pivot_index
  
def getPivotRowIndex(b,pivotCol):
    smallest = b[0]/pivotCol[0]
    pivot_row = 0
    for i, val in enumerate(b):
        tmp = val/pivotCol[i]
        if(tmp < smallest and tmp >=0):
            smallest = tmp;
            pivot_row = i
    return pivot_row

def getPivotRowIndexArr(b,pivotCol):
    indexDict = {}
    for i, val in enumerate(b):
        if pivotCol[i] == 0 or pivotCol[i]<0:
            continue
        tmp = val/pivotCol[i]
        indexDict[tmp] = i
    return indexDict

def getUpdateedPivotRow(row, simpleksVal):
    for i,x in enumerate(row):
        row[i] = x/simpleksVal
    return row

def getUpdatedRow(pivotRow, currentRow, simpleksVal):
    for i,x in enumerate(currentRow):
        currentRow[i] = x-(simpleksVal*pivotRow[i])
    return currentRow

def updateTable(A,pivColI,pivRowI):
    simpleksVal = A[pivRowI][pivColI]
    A[pivRowI] = getUpdateedPivotRow(A[pivRowI],simpleksVal)
    Atmp = list(A)
    for i, row in enumerate(Atmp):
        if(i==pivRowI):
            next
        else:
            A[i] = getUpdatedRow(Atmp[pivRowI],row,row[pivColI])

def mergeAToB(A,b):
    for i,val in enumerate(A):
        A[i].append(b[i])
    return A

def printSimpleksTable(A,f,c,c_z,resVars,recVars):
    print("%9s"%"",end='')
    print("%8s"%"",end='')
    for elem in f:
        print("%8.2f"%elem,end='')
    print("")
    for i,row in enumerate(A):
        print("%8.2f "%c[i],end='')
        if resVars[i] < len(c):
            print("%8s"%recVars[resVars[i]],end='')
        else:
            print("%7s"%"Zm"+str(resVars[i]),end='')
        for elem in row:
            print("%8.2f"%elem,end='')
        print("")
    for elem in range(len(row)+2):
        print("-"*8,end='')
    print("")
    print("%9s"%"",end='')
    print("%8s"%"",end='')
    for elem in c_z:
        print("%8.2f"%elem,end='')
    print("\n\n")
       
def simpleks(A,f,b,c,mini):
    numOfVars = int(len(A));
    pivotRowArr = {}
    addSlackVariables(A)
    f.extend([0]*numOfVars)
    A_b = mergeAToB(A,b)
    resVars = list(range(numOfVars,numOfVars*2))
    for i in range(MAX_ITER):
        b=[x[-1] for x in A_b]
        c_z = computeC_Z(f,computeZ(A_b,c))
        print("----------Tabela po iteracji: " + str(i) + "----------")
        printSimpleksTable(A_b,f,c,c_z,resVars, recVariables)
        if isSolutionOptimal(c_z, mini):
            print("Znaleziono rozwiązanie optymalne!")
            b = [row[-1] for row in A_b]
            return(resVars ,b)
        elif i == MAX_ITER:
            print("Nie udało się znaleźć optymalnego rozwiązania w następującej liczbie iteracji: " + MAX_ITER)
            return(resVars ,b)
        pivotColIndex = getPivotColumnIndex(c_z,mini)
        pivCol = [row[pivotColIndex] for row in A_b ]
        pivotRowArr = getPivotRowIndexArr(b,pivCol)
        pivotRowIndex=pivotRowArr[min(list(pivotRowArr.keys()))]
        resVars[pivotRowIndex] = pivotColIndex
        updateTable(A_b, pivotColIndex, pivotRowIndex)
        c[pivotRowIndex] = f[pivotColIndex]
  
def printResult(recVars,resVars,b,f):
    print("\n\n")
    bound = len(recVars)
    res = 0
    for i,val in enumerate(resVars):
        if val>=bound:
            continue
        print(recVars[val],"=",b[i])
    for i,val in enumerate(resVars):
        if val>=bound:
            continue
        res = res + f[val] * b[i]
    print("Wynik",res)
      
usage = """
****USAGE***********************************************************

Program nie jest w pełni odporny na złosliwe/nieprawidłowe dane.
Zakłada, że użytkownik wie co wpisuje :).
Testowane tylko na prostych przypadkach nierówności. 
Zmienne reprezentowane są przez ciągi liter np.: x,y,z,zmiennA
->Przykład użycia:
    Wybierz max/min [max]: max
    Podaj funkcje celu (np. x+2y+z): 2z+3y+x
    Podaj nierówność.Ctrl+d żeby zakończyć. (np. x+2y<=5): x+y+z<4
    Podaj nierówność.Ctrl+d żeby zakończyć. (np. x+2y<=5): y+2z>=1
    Podaj nierówność.Ctrl+d żeby zakończyć. (np. x+2y<=5): z+x+2y<5
    Podaj nierówność.Ctrl+d żeby zakończyć. (np. x+2y<=5): ctrl+d
    ...
  
->Realizacja: Artur Czepiec 256769

********************************************************************

"""

print(usage)

obj = readMinMax()
q1="Podaj funkcje celu (np. x+2y+z): "
objFunc = readInputRows(q1,True)
q2="Podaj nierówność.Ctrl+d żeby zakończyć. (np. x+2y<=5): "
aRows = readInputRows(q2)
(A,f,b,c,recVariables) = setupInputTables(objFunc,aRows)
print("A:",A)
print("f:",f)
print("b:",b)
print("c:",c)
print("Zmienne:",recVariables)
(resVars ,b)=simpleks(A,f,b,c,obj)
printResult(recVariables,resVars,b,f)
