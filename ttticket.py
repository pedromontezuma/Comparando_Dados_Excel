# coding=utf8
import numpy as np
import pandas as pd
desired_width=1000
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',100)

cg = pd.read_csv('compras-ga.csv', delimiter = ';')
cg.dropna(inplace=True)
#for i in range(len(cg)):
#    if cg['Status'][i] == 'Reprovado':
#        cg.drop(i, inplace = True)
#    elif cg['Status'][i] == 'Falha':
#        cg.drop(i, inplace = True)

cg.reset_index(inplace = True)
cg.drop('index', axis = 1, inplace=True)
print(cg)

ga_ticket = pd.read_csv('ga_ticket.csv', delimiter=',')
ga_ticket.dropna(inplace=True)
print(ga_ticket)

a = pd.merge(ga_ticket,cg, left_on='Código da transação', right_on='File')
a.dropna(inplace=True)
a.index.name = 'index'
a.drop('File', axis = 1, inplace=True)
a.drop('Quantidade', axis = 1, inplace=True)
a.drop('Imposto', axis=1,inplace=True)
a.drop('Frete', axis = 1, inplace=True)
#a.drop('Valor do reembolso', axis = 1, inplace=True)
a['Div. Valor'] = 'X'
a['Div. Origem'] = 'X'
a['Não Encontrado'] = 'X'
a['Código da transação'] = a['Código da transação'].astype(np.int64)

print(a)
with open('log_ttticket.txt', 'w') as l:
    for b in range(len(a)):
        elo = 'elo.com.br'
        elo2 = 'cartaoelo.com.br'
        elo3 = a['Afiliado'][1]
        origem = str(a['Origem'][b])
        if origem == elo or origem == elo2:
            a['Origem'][b] = elo3

    for b in range(len(a)):
        codigo = a['Código da transação'][b]
        receita = str(a['Receita'][b]).replace('R$ ', '')
        valor = str(a['Valor'][b])
        if receita != valor:
            a['Div. Valor'][b] = "Valor no Extranet: " + str(valor) + " / Valor no GA: " + str(receita)
            #l.write("Divergência de valor em: %s\n" % codigo + " ---- Valor no Extranet: " + str(valor) + " / Valor no GA: " + str(receita) + "\n\n")
    #l.write("\n\n Fim das Divergências de valor")
    #l.write("\n ____________________________________________________________________\n")


    for b in range(len(a)):
        codigo = a['Código da transação'][b]
        origem = str(a['Origem'][b])
        afiliado = str(a['Afiliado'][b])

        if origem != afiliado:
            a['Div. Origem'][b] = "Origem no Extranet: " + afiliado + " / Origem no GA: " + origem
            #l.write("Divergência de origem em: %s\n" % codigo + " ---- Origem no Extranet: " + afiliado + " / Origem no GA: " + origem + "\n\n")
    #l.write("\n\n Fim das Divergências de origem")
    #l.write("\n ____________________________________________________________________\n")

    r = set(cg['File'])
    g = set(ga_ticket['Código da transação'])

    my_set = set(r | g)
    # put every value in a set, so that you don't check each column twice

    for i in my_set:
        print(i)
        try:
            #index_teste = a[a['Código da transação'] == i].index[0]
            if i in cg['File'].values:
                if i in ga_ticket['Código da transação'].values:
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


a.drop('Valor', axis = 1, inplace= True)
a.to_csv('ttticket_analisado_ga_ticket_Extranet.csv', encoding='utf-8-sig', sep = ';')
