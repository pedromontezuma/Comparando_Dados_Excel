import numpy as np
import pandas as pd
desired_width=1000
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',100)

rs = pd.read_csv('reservas-ga.csv', delimiter=';')
#for i in range(len(rs)):
#    if rs['Status'][i] == 'Reprovado':
#        rs.drop(i, inplace = True)
#    elif rs['Status'][i] == 'Falha':
#        rs.drop(i, inplace = True)
#rs.dropna(inplace=True)

rs.reset_index(inplace = True)
rs.drop('index', axis = 1, inplace=True)
rs.dropna(inplace=True)
for b in range(len(rs['File'])):
    l = str(rs['File'][b]).replace(".0", "")
    #print("Códigos de transação: " + l)
    rs['File'][b] = int(l)
    #print(a)
#print(rs)

ga_car = pd.read_csv('ga_car.csv', delimiter=',')
ga_car.dropna(inplace=True)
for b in range(len(ga_car['Código da transação'])):
    l = str(ga_car['Código da transação'][b]).replace(".0", "")
    #print("Códigos de transação: " + l)
    ga_car['Código da transação'][b] = int(l)
    #print(a)
#print(ga_car)

a = pd.merge(ga_car,rs, left_on='Código da transação', right_on='File')
a.dropna(inplace=True)
a.index.name = 'index'
a.drop('File', axis = 1, inplace=True)
a.drop('Quantidade', axis = 1, inplace=True)
a.drop('Imposto', axis=1,inplace=True)
a.drop('Frete', axis = 1, inplace=True)
a.drop('Valor do reembolso', axis = 1, inplace=True)
a['Div. Valor'] = 'X'
a['Div. Origem'] = 'X'
a['Não Encontrado'] = 'X'
a['Código da transação'] = a['Código da transação'].astype(np.int64)
#print("TAMANHO: " + str(len(a['Código da transação'])))


for b in range(len(a['Código da transação'])):
    l = str(a['Código da transação'][b]).replace(".0", "")
    #print("Códigos de transação: " + l)
    a['Código da transação'][b] = int(l)
    #print(a)

with open('log_ttcar.txt', 'w') as l:
    for b in range(len(a)):
        avianca = 'intranet.avianca.com.br'
        avianca2 = a['Afiliado'][1]
        origem = str(a['Origem'][b])
        if origem == avianca:
            a['Origem'][b] = avianca2

    for b in range(len(a)):
        codigo = a['Código da transação'][b]
        #print("Este é um código: " + str(codigo))
        receita = str(a['Receita'][b]).replace('R$ ', '')
        valor = str(a['Valor'][b])
        if receita != valor:
            a['Div. Valor'][b] = "Valor no Extranet: " + str(valor) + " / Valor no GA: " + str(receita)
    l.write("Fim das Divergências de valor")
    l.write("\n ____________________________________________________________________\n")


    for b in range(len(a)):
        codigo = a['Código da transação'][b]
        origem = str(a['Origem'][b])
        afiliado = str(a['Afiliado'][b])

        if origem != afiliado:
            a['Div. Origem'][b] = "Origem no Extranet: " + afiliado + " / Origem no GA: " + origem
    l.write("\n\n Fim das Divergências de origem")
    l.write("\n ____________________________________________________________________\n")

    r = set(rs['File'])
    g = set(ga_car['Código da transação'])

    my_set = set(r | g)
    # put every value in a set, so that you don't check each column twice

    for i in my_set:
        print(i)
        try:
            #index_teste = a[a['Código da transação'] == i].index[0]
            if i in rs['File'].values:
                if i in ga_car['Código da transação'].values:
                    #a['Não Encontrado'][index_teste] = "X"
                    print("Tem em ambas")
                else:
                    #a['Não Encontrado'][index_teste] = "Falta no GA"
                    l.write("Divergência de Código em : %s\n" % i + " ---- Código não apareceu no Google Analytics\n\n")
                    print("Não tem no GA")
            else:  # if the value is not in A, it is obviously in B
                #a['Não Encontrado'][index_teste] = "Incompatibilidade no status"
                print("Não tem na Extranet")
                l.write("Divergência de Código em : %s\n" % i + " ---- Transação sem Status na Extranet\n\n")
        except Exception as Erro:
            print(Erro)


    l.write("\n\nFim das Divergências de códigos nas plataformas")
    l.write("\n ____________________________________________________________________\n")

a.to_csv('ttcar_analisado_ga_car_Extranet.csv', encoding='utf-8-sig', sep = ';')
