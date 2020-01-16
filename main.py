from _datetime import datetime, timedelta
import threading
from tkinter import *

from indicators import Indicators
from bot import HBot

# INSTANCES OF BOT AND INDICATORS
cbot = HBot()
indicator = Indicators()

def main_flow():

    cbot.start_application()
    print('iniciou')

    # WORKING WITH CURRENT CONTACTS LIST
    # EACH LINE REFERS TO A DIFFERENT CONTACT
    # EACH COLUMN REFERS TO A SPECIFIC INFORMATION OF THIS CONTACT
    # [0 = CONTACT NAME (retrieved from top of whatsapp page),
    # 1 = STATUS,
    # 2 = LAST INTERACTION DATE,
    # 3 = LAST WRITTEN TEXT,
    # 4= ADDITIONAL INFORMATION (rating/ticket/ok/x),
    # 5= IS FINAL (0 = no, 1= final with rating, 2= final with no help),
    # 6= CONVERSATION ID (retrieved from database)]
    contacts_list = []

    # MAIN LOOP, ALWAYS LOOKING FOR UNREAD CONVERSATIONS
    while True:

        # FIND UNREAD CONVERSATION WHERE THERE IS A "GREEN BALL" IN OUR CONTACT
        conv_has_open = cbot.find_unread_conversation()
        print(conv_has_open)

        if conv_has_open == '1':

            # GET CONTACT NAME IN THE TOP OF WHATSAPP PAGE
            contact_name = cbot.return_contact()
            print('nome encontrado na barra superior: ' + contact_name)

            if contact_name != 'exception':

                # RUN THE CONTACTS LIST SEARCHING FOR THIS CONTACT INDEX (if exists)
                i = 0
                current_index = -1
                while i < len(contacts_list):
                    if contact_name == contacts_list[i][0]:
                        current_index = i
                    i = i + 1

                # IF THIS CONTACT IS NOT IN OUR CURRENT CONTACT LIST, THE CURRENT INDEX WILL NOT BE CHANGED
                # SO A NEW INSTANCE HAS TO BE CREATED WITH THIS CONTACT NAME
                if current_index < 0:

                    # FIRSTLY, CREATE A NEW CONVERSATION FOR THIS CONTACT IN OU DB AND GET A CONVERSATION ID
                    new_conv_id = cbot.generate_new_conversation(contact_name)

                    # APPEND THIS CONTACT WITH INITIAL INFORMATION
                    contacts_list.append([contact_name, '0', datetime.now(), '', 'x', '0', new_conv_id])

                    # IN THIS CASE, THE "i" VARIABLE HAS ACHIEVED THE VALUE OF LIST LENGTH
                    # SO AFTER WE APPEND THE CONTACT, IT WILL BE HIS POSITION IN THE LIST
                    current_index = i
                    print('contato add a lista')

                print('indice que encontrou o contato: ' + str(current_index))
                print('contato: ' + str(contacts_list[current_index]))
                print('lista contatos: ' + str(contacts_list))

                # READ THE LAST MESSAGE OF CURRENT OPENED CONVERSATION
                text_read = str(cbot.listen())

                # IF THIS TEXT IS DIFFERENT THAN THE LAST TEXT IN THE BOT MEMORY (contacts_list) FOR THIS CONVERSATION
                # THE BOT MUST PROCEED TO INTERPRETATION PHASE AND ANSWER ADEQUATELY
                print('entrada: ' + text_read + ' / ultimo texto da conversa: ' + str(contacts_list[current_index][3]))

                if text_read != contacts_list[current_index][3]:

                    # FOR LOG PURPOSE, THE READ TEXT IS SAVED IN setamos o texto lido como o último texto da conversa
                    contacts_list[current_index][3] = text_read

                    #  WRITE LOG log type (log_type, conv_id, cnt_name, cnt_status, cnt_is_final, cnt_last_text, cnt_add_inf)
                    #cbot.write_log_conversation('101', contacts_list[current_index][6], contacts_list[current_index][0], contacts_list[current_index][1], contacts_list[current_index][5], contacts_list[current_index][3], contacts_list[current_index][4])

                    # pegamos o estado atual do indice e procuramos a resposta
                    current_status = contacts_list[current_index][1]
                    is_final = contacts_list[current_index][5]
                    print('atual status: ' + str(current_status))

                    if len(text_read) == 2:
                        text_read = cbot.two_digit_conversion(text_read)

                    #create a list for return of RESPOND, will contain all information to update our contact
                    #0-response 1-status 2-is final 3-add information
                    return_list = cbot.respond(text_read, current_status, is_final)

                    # seta status trazido da resposta
                    contacts_list[current_index][1] = return_list[1]
                    print('novo status: ' + str(contacts_list[current_index][1]))

                    #current date
                    contacts_list[current_index][2] = datetime.now()
                    print('nova data: ' + str(contacts_list[current_index][2]))

                    #last msg
                    #contacts_list[current_index][3] = return_list[0]
                    contacts_list[current_index][3] = cbot.listen()
                    print('nova ult msg: ' + str(contacts_list[current_index][3]))

                    #last rating
                    contacts_list[current_index][4] = return_list[3]
                    print('nova nota/chamado: ' + str(contacts_list[current_index][4]))

                    #last is final
                    contacts_list[current_index][5] = return_list[2]
                    print('eh final: ' + str(contacts_list[current_index][5]))

                    # WRITE LOG robo carlito bot
                    #  WRITE LOG log type (log_type, conv_id, cnt_name, cnt_status, cnt_is_final, cnt_last_text, cnt_add_inf)
                    #cbot.write_log_conversation('101', contacts_list[current_index][6], 'Carlito', contacts_list[current_index][1], contacts_list[current_index][5], contacts_list[current_index][3], contacts_list[current_index][4])

                    print('contato pos interacao: ' + str(contacts_list[current_index]))
                    print('------------')


def btn_activate():

    # CLOSE FIRST WINDOW
    first_window.destroy()

    # INITIALIZING MAIN THREAD
    main_thread = threading.Thread(target=main_flow)
    main_thread.daemon = True  # Daemonize thread
    main_thread.start()

    start_date = datetime.now()

    # SECOND WINDOW - second_window
    second_window = Tk()
    second_window.title('Carlito')
    second_window.configure(background='white')

    def btn_close_second_window():
        second_window.destroy()
        cbot.close_browser()
        #os._exit(1)

    lbl2_nome = Label(second_window, text="Ativo desde: " + str(start_date.strftime('%d/%m/%Y %H:%M:%S')), bg="white",font="Calibri 12")
    lbl2_conv_iniciadas = Label(second_window, text="Conversas iniciadas até o momento: " + indicator.get_indicator_value(1) , bg="white", font="Calibri 12")
    lbl2_conv_ativas = Label(second_window, text="Conversas ativas: " + indicator.get_indicator_value(2), bg="white", font="Calibri 12")
    lbl2_conv_resolvidas = Label(second_window, text="Orientações resolvidas: " + indicator.get_indicator_value(3), bg="white", font="Calibri 12")
    lbl2_conv_direcionadas = Label(second_window, text="Orientações com chamados direcionados: " + indicator.get_indicator_value(4), bg="white", font="Calibri 12")
    lbl2_conv_nao_direcionadas = Label(second_window, text="Orientações sem chamados direcionados: " + indicator.get_indicator_value(5), bg="white", font="Calibri 12")
    lbl2_conv_timeout = Label(second_window, text="Conversas abandonadas: " + indicator.get_indicator_value(6), bg="white", font="Calibri 12")
    btn_close_2w = Button(second_window, text="Parar", command=btn_close_second_window, bg="white", font="Calibri 11")

    lbl2_nome.place(x=50, y=50)
    lbl2_conv_iniciadas.place(x=50, y=90)
    lbl2_conv_ativas.place(x=50, y=130)
    lbl2_conv_resolvidas.place(x=50, y=170)
    lbl2_conv_direcionadas.place(x=50, y=210)
    lbl2_conv_nao_direcionadas.place(x=50, y=250)
    lbl2_conv_timeout.place(x=50, y=290)
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
