from _datetime import datetime, timedelta
import threading
from tkinter import *

from bot import HBot

cbot = HBot('Carlito')

def main_flow():

    cbot.start_application()
    print('iniciou')

    # trabalhando com lista  de contatos atual
    # cada linha se refere a um contato
    # cada coluna se refere a uma determinada informação deste contato
    # [0 = nome_contato, 1 = status, 2 = ultima_interacao data, 3 = ultimo_texto, 4= ultima entrada valida]
    contacts_list = []

    # controle de conversa aberta ou não
    # 0 = não , 1 = sim
    # estado inicial sempre será 0 pois nenhuma conversa será aberta logo ao iniciar
    conv_has_open = '0'

    while True:
        # procura conversa com msg nao lida (se há "bolinha verde" no canto)
        conv_has_open = cbot.find_unread_conversation()
        print(conv_has_open)

        if conv_has_open == '1':
            # Vamos procurar o contato/grupo que está em um span
            # e possui o título igual que buscamos e vamos clicar.
            contact_name = cbot.return_contact()
            print('nome encontrado na barra superior: ' + contact_name)

            if contact_name != 'exception':

                # Procura se o contato está na lista de contatos atuais
                i = 0
                current_index = -1
                # procura indice atual
                while i < len(contacts_list):
                    if contact_name == contacts_list[i][0]:
                        current_index = i
                    i = i + 1

                if current_index < 0:
                    # se nao encontra o contato, cria uma nova instancia para a lista
                    contacts_list.append([contact_name, '0', datetime.now(), '','x'])
                    # indice_atual = len(lista_contatos) - 1
                    current_index = i
                    print('contato add a lista')

                print('indice que encontrou o contato: ' + str(current_index))
                print('contato: ' + str(contacts_list[current_index]))
                print('lista contatos: ' + str(contacts_list))
                #irá ler a última mensagem da conversa
                text_read = str(cbot.listen())

                # se o texto for diferente do último texto da lista de informações do contato
                # o bot deve interpretar o que foi dito e responder
                print('entrada: ' + text_read + ' / ultimo texto da conversa: ' + str(contacts_list[current_index][3]))


def btn_activate():
    #close first window
    first_window.destroy()

    #initializing main thread
    main_thread = threading.Thread(target=main_flow)
    main_thread.daemon = True  # Daemonize thread
    main_thread.start()

    start_date = datetime.now()

    ###SECOND WINDOW - second_window
    second_window = Tk()
    second_window.title('Carlito')
    second_window.configure(background='white')

    def btn_close_second_window():
        second_window.destroy()
        cbot.close_browser()
        #os._exit(1)

    lbl2_nome = Label(second_window, text="Ativo desde: " + str(start_date.strftime('%d/%m/%Y %H:%M:%S')), bg="white",font="Calibri 12")
    lbl2_conv_iniciadas = Label(second_window, text="Conversas iniciadas até o momento: " , bg="white", font="Calibri 12")
    lbl2_conv_ativas = Label(second_window, text="Conversas ativas: " , bg="white", font="Calibri 12")
    lbl2_conv_resolvidas = Label(second_window, text="Orientações resolvidas: ", bg="white", font="Calibri 12")
    lbl2_conv_direcionadas = Label(second_window, text="Chamados direcionados: " , bg="white", font="Calibri 12")
    lbl2_conv_timeout = Label(second_window, text="Conversas abandonadas: " , bg="white", font="Calibri 12")
    btn_close_2w = Button(second_window, text="Parar", command=btn_close_second_window, bg="white", font="Calibri 11")

    lbl2_nome.place(x=50, y=50)
    lbl2_conv_iniciadas.place(x=50, y=90)
    lbl2_conv_ativas.place(x=50, y=130)
    lbl2_conv_resolvidas.place(x=50, y=170)
    lbl2_conv_direcionadas.place(x=50, y=210)
    lbl2_conv_timeout.place(x=50, y=250)
    btn_close_2w.place(x=700, y=350)

    second_window.wm_iconbitmap('CarlitoApp.ico')
    second_window.geometry("800x420+100+100")
    second_window.resizable(False, False)
    second_window.mainloop()

def btn_close_first_window():
    first_window.destroy()


########FIRST WINDOW - first_window
first_window = Tk()


lbl_name = Label(first_window, text="Carlito", bg="white", font="Calibri 18")
lbl_version_label = Label(first_window, text="Versão Beta", bg="white", font="Arial 8")

btn_activate_mf = Button(first_window, text="Ativar", command=btn_activate, bg="white", font="Calibri 13")
btn_close_1w = Button(first_window, text="Fechar", command=btn_close_first_window, bg="white", font="Calibri 13")

photo = PhotoImage(file="carlitoImage.png")
lbl_photo = Label(first_window, image=photo, bg="white")

lbl_photo.pack(side=TOP, fill=BOTH, expand=1)
lbl_name.pack(side=TOP, fill=BOTH, expand=1)
btn_activate_mf.pack(side=TOP, fill=BOTH, expand=1)
btn_close_1w.pack(side=TOP, fill=BOTH, expand=1)
lbl_version_label.pack(side=TOP, fill=BOTH, expand=1)

first_window.wm_iconbitmap('CarlitoApp.ico')
first_window.title('Carlito')
first_window.geometry("250x350+100+100")
first_window.resizable(False, False)
first_window.configure(background='white')
first_window.mainloop()
