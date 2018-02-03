# encoding: utf-8

from bs4 import BeautifulSoup
import re
import requests
import filecmp
import time
import telebot
import sys

site = "https://g1.globo.com/economia/concursos-e-emprego/noticia/lista-de-programas-de-estagio-e-trainee.ghtml"
titulo = "Estagio"
tempo = int(sys.argv[1])


# COMUNICAÇÃO DO BOT COM O TELEGRAM
bot = telebot.TeleBot('KeyBotTelegram')

# FUNÇÕES

def sendToUser(message):
    bot.send_message('IdChat', message)

def getTable(data):
    soup = BeautifulSoup(data, 'html.parser')
    table = soup.select(".show-table__container")
    return str(table)

def getEstagio(table,dia,mes):
    table = list(table.split("<td>"))
    # Multiplo 6 => Empresa
    # Multiplo 7 => Data
    # Multiplo 8 => Salário
    # Multiplo 9 => Tipo
    # Multiplo 10 => Site

    empresas = []
    salarios = []
    vagas = []
    links = []

    # Procurar data
    for i in range(7,len(table),5):
        if re.match("\d",str(table[i][7:9])):
            if (int(dia) == int(table[i][7:9])) and (int(mes) == int(table[i][10:12])):
                empresas.append(str(table[i-1][:-6]))
                vagas.append(str(table[i+1][:-6]))
                salarios.append(str(table[i+2][:-6]))
                links.append(str(table[i+3][:-17]))

    return empresas, salarios, vagas, links


while True:
    currentTime = "[" + time.strftime("%d/%m/%Y %H:%M:%S") + "]"
    print(currentTime)
    # Criar arquivo de log
    try:
        log = open(titulo + ".log", 'r')  # Abre o arquivo caso ele já exista
        textLog = log.readlines() # Carregar logs antigos
        #textLog = []  # Sobrepor logs antigos
        log.close()
    except:
        print("ERRO: Não foi possível abrir arquivo de log")
        textLog = []
        log = open(titulo + ".log", 'w')
        log.close()

    # Baixar página
    try:
        r = requests.get(site)
        data = r.text
        data = getTable(data)
    except:
        print(currentTime + " Houve um erro ao efetuar o download da página.")
        textLog.append(currentTime + " Houve um erro ao efetuar o download da página.\n")

    # VERFICADOR DOS SITES
    try:
        old = open("old" + titulo + ".html", "r")
    except:
        old = open("old" + titulo + ".html", "w")
        old.write(data.encode('utf-8'))
        old.close()

    new = open("new" + titulo + ".html", "w")
    new.write(data.encode('utf-8'))
    new.close()

    oldName = 'old' + titulo + '.html'
    newName = 'new' + titulo + '.html'

    if not (filecmp.cmp(oldName, newName)):
        message = "• Nova oportunidade de emprego!\nLink: " + site + "\n"

        # Info p/ o log
        # print(currentTime + " -> Houve atualização.")
        textLog.append(currentTime + " -> Houve atualização.\n")

        # Enviar notificação para o Telegram
        try:
            sendToUser(message)
        except:
            # print(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram")
            textLog.append(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram\n")

        # Atualizar arquivo antigo
        old = open("old" + titulo + ".html", "w")
        old.write(data.encode('utf-8'))
        old.close()
    else:
        # Info p/ o log
        # print(currentTime + " -> Sem atualização.")
        textLog.append(currentTime + " -> Sem atualização.\n")
    # Notificar vagas todos os dias ao 12h e às 20h

    hour = time.strftime("%H")

    if hour == hour or hour == 20:
        day = int(time.strftime("%d"))
        month = int(time.strftime("%m"))

        # Verificar vagas que terminam "hoje"
        empresas, salarios, vagas, links = getEstagio(data, day, month)

        if len(empresas) == 0:
            msgm = "• NENHUMA VAGA TERMINA HOJE!"

        else:
            msgm = "• EMPRESAS COM VAGAS QUE TERMINAM HOJE:\n\n"
            for i in range(len(empresas)):
                msgm = msgm + "Empresa: " + empresas[i] + "\nSalário: " + salarios[i] + "\nVagas: " + vagas[i] + "\nSite: " + links[i] + "\n\n"

        print (msgm)
        # Enviar notificação para o Telegram
        try:
            sendToUser(msgm)
        except:
            # print(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram")
            textLog.append(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram\n")

        # Verificar vagas que terminam "amanhã"
        empresas, salarios, vagas, links = getEstagio(data, day+1, month)

        if len(empresas) == 0:
            msgm = "• NENHUMA VAGA TERMINARÁ AMANHÃ!"

        else:
            msgm = "• EMPRESAS COM VAGAS QUE TERMINARÃO AMANHÃ:\n\n"
            for i in range(len(empresas)):
                msgm = msgm + "Empresa: " + empresas[i] + "\nSalário: " + salarios[i] + "\nVagas: " + vagas[
                    i] + "\nSite: " + links[i] + "\n\n"
                aux = "Empresa: " + empresas[i]

        print (msgm)
        # Enviar notificação para o Telegram
        try:
            sendToUser(msgm)
        except:
            # print(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram")
            textLog.append(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram\n")

        # Verificar vagas que terminam daqui a dois dias
        empresas, salarios, vagas, links = getEstagio(data, day + 2, month)

        if len(empresas) == 0:
            msgm = "• NENHUMA VAGA TERMINARÁ DEPOIS DE AMANHÃ!"

        else:
            msgm = "• EMPRESAS COM VAGAS QUE TERMINARÃO DEPOIS DE AMANHÃ:\n\n"
            for i in range(len(empresas)):
                msgm = msgm + "Empresa: " + empresas[i] + "\nSalário: " + salarios[i] + "\nVagas: " + vagas[
                    i] + "\nSite: " + links[i] + "\n\n"

        print (msgm)
        # Enviar notificação para o Telegram
        try:
            sendToUser(msgm)
        except:
            # print(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram")
            textLog.append(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram\n")

    # Escreve no log, e fecha o arquivo.
    log = open(titulo + ".log", 'w')
    log.writelines(textLog)
    log.close()

    # Sleep
    time.sleep(int(tempo*3600))
