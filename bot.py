from _datetime import datetime, timedelta
import os
import re
import time
from dbintegration import DbCommands
from selenium import webdriver

class HBot:
    # Setamos o caminho de nossa aplicação.
    dir_path = os.getcwd()

    # Nosso contrutor terá a entrada do nome do nosso
    def __init__(self):
        # Setamos onde está nosso chromedriver.
        self.chrome = self.dir_path + '\chromedriver.exe'
        # Configuramos um profile no chrome para não precisar logar no whats toda vez que iniciar o bot.
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(r"user-data-dir=" + self.dir_path + "\profile\wpp")

        self.database = DbCommands()

    def start_application(self):
        # Iniciamos o driver.
        self.driver = webdriver.Chrome(self.chrome, chrome_options=self.options)

        # Selenium irá entrar no whats e aguardar 10 segundos até o dom estiver pronto.
        self.driver.get('https://web.whatsapp.com')
        self.driver.implicitly_wait(10)

    def close_browser(self):
        self.driver.close()

    def find_unread_conversation(self):

        # Tenta abrir conversa que esteja com tag de nao lida _15G96
        try:

            self.contato = self.driver.find_element_by_xpath('//*[@id="pane-side"]/div[1]/div/div/div[1]/div/div/div/div[2]/div[2]/div[2]/span[1]/div')
            self.contato.click() # _1ZMSM    ---- OUeyt //div/div/div/span/div/span[@class = "_1ZMSM"]
            self.contato.click()
            self.contato.click()
            time.sleep(1)

            has_open = '1'
        except:
            has_open = '0'

        return has_open

    def return_contact(self):
    #_3XrHh  _1wjf
        try:
            contact_name = self.driver.find_element_by_xpath('//div[@class = "_3XrHh"]').text
        #nome_contato = 'contato'
        except:
            contact_name = 'exception'

        return contact_name

    def print_response(self, text):

        try:
            self.caixa_de_mensagem = self.driver.find_element_by_class_name('_3u328') #_2S1VP
            self.caixa_de_mensagem.send_keys(text)
            time.sleep(1)
            self.botao_enviar = self.driver.find_element_by_class_name('_35EW6')
            self.botao_enviar.click()

            self.clica_fora = self.driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/input') #_3_7SH _3qMSo message-out
            self.clica_fora.click()
            self.clica_fora = self.driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/input')  # _3_7SH _3qMSo message-out
            self.clica_fora.click()
        except:
            print('erro print response')

    def listen(self):
        # Vamos setar todos as mensagens no grupo.
        post = self.driver.find_elements_by_class_name('_12pGw EopGb') #_3_7SH
        # Vamos pegar o índice da última conversa.
        last = len(post) - 1
        # Vamos pegar o  texto da última conversa e retornar.

        try:
            text_read = post[last].find_element_by_css_selector('span.selectable-text').text
        except Exception:
            text_read = 'exception'

        return text_read

    def respond(self, text_read, current_status, is_final):

        # iniciamos a variavel de informacoes add: nota e/ou chamado
        add_information = 'x'

        # validamos se input eh valido
        is_valid = self.validate_input(text_read, current_status, is_final)

        # se for valido
        if is_valid:

            # a qualquer momento, se digitar 0 volta ao menu inicial
            if text_read == '0':
                current_status = '0'

            # verifica se estado nao é zero, em caso positivo procura resposta de estado+input
            if current_status != '0':

                # se o usuario escrever VOLTAR, volta para estado anterior desempilhando o status
                if text_read.lower() == 'voltar':

                    search_status = current_status[0:len(current_status)-1]

                    if search_status == '01':
                        search_status = '0'

                else:
                    # se o status não for final, empilha o texto no status
                    if is_final == '0':
                        search_status = self.generate_search_index(text_read, current_status) # str(estado_atual) + str(texto)
                    else:
                        # se esta num status final, irá buscar a mensagem referente a este status
                        if is_final == '1':
                            search_status = '991'
                        elif is_final == '2':
                            search_status = '992'
                        else:
                            search_status = '999'

            # caso estado atual seja 0, busca resposta pra 0
            else:
                #
                search_status = str(current_status)

            # armazena resposta trazida pelo estado procurado
            print('estado a ser procurado: '+ str(search_status))
            response, is_final = self.find_response(search_status)
            response = str(response)

            # atualiza qual estado deve ir
            if current_status != '0':
                if response != 'notfound':

                    # Se recebeu avaliacao valida, chamado ou ok
                    # respondera ao usuario agradecendo e adicionara a informacao necessaria para tira-lo da lista
                    if search_status in ('991', '992'):
                        add_information = text_read

                    self.print_response(response)
                    new_status = search_status

                else:
                    # caso uma opcao sem resposta correspondente tenha sido informada logo depois da saudacao,
                    # volta status pra imprimir saudacao
                    if current_status == '01':
                        new_status = '0'
                    # para os outros status, mantém o mesmo status
                    else:
                        new_status = current_status

                    # neste ponto nao eh necessario validar status final ou nao,
                    # pois em status final a resposta encontrada nao dependera da entrada do usuario
                    self.print_response(
                        'Resposta não encontrada para a opção informada, favor conferir novamente as opções')
                    response, is_final = self.find_response(new_status)
                    self.print_response(response)

                # caso tenha sido necessario voltar pro 0 pra imprimir saudacao,
                # setamos novamente para 01 para empilhar depois
                if new_status == '0':
                    new_status = '01'

            else:  # No caso do estado 0 (estado inicial), será impressa a saudação
                # posteriormente, altera-se o status para 01 para iniciar a pilha a partir da próxima iteração
                self.print_response(response)
                new_status = '01'

            ######
        else:

            new_status = current_status
            ###VALIDA STATUS FINAL PARA RESPONDER ###########
            ###
            # Quando é informada uma entrada invalida, o usuário deve ser advertido
            # o status se mantém o mesmo, assim a mesma mensagem é informada ao usuário
            if is_final == '1':

                response = 'O valor informado diferente do esperado, favor avaliar dentre as seguites opções: ' \
                           '*1* - Ruim  | *2* - Bom  | *3* - Excelente'
                #response, is_final = self.find_response(current_status)


            elif is_final == '2':

                response = 'Informação inválida, favor digitar o número do chamado referente à situação ' \
                    'caso tenha sido aberto um, ou digite apenas *ok* caso não queira abrir chamado para esta situação'
                #response, is_final = self.find_response(current_status)

            else:

                self.print_response('Resposta invalida, favor conferir novamente as opções')
                response, is_final = self.find_response(new_status)


            self.print_response(response)

        # retorna para gravar em arquivo
        new_list = [response, new_status, is_final, add_information]

        return new_list

    def find_response(self, status):

        if len(status) < 4:
        #if status in ('0', '01', '011', '012'):
            # find response by topics like T1, T2, saudation and others
            response, is_final = self.database.find_response_dialogs(status)
        else:
            # find response by subject in its own table
            response, is_final = self.database.find_response_subjects(status)


        #response = 'teste find response' + status
        #is_final = '0'

        return response, is_final

    def validate_input(self, text_read, current_status, is_final):

        possible = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                     'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                     'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                     'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        allowed = ['voltar']

        #verifica se a entrada para o status é válida
        if is_final == '0':
            if current_status != '0':
                if len(text_read) == 1 and text_read not in allowed:
                    if text_read in possible:
                        return 1
                    else:
                        return 0
                else:
                    if len(text_read) == 2 and text_read not in allowed:
                        if text_read in possible:
                            return 1
                        else:
                            return 0

                    if text_read.lower() in allowed:
                        return 1
                    else:
                        return 0
        elif is_final == '1':
            if text_read in ('1', '2', '3'):
                return 1

        elif is_final == '2':

            if 5 < len(text_read) < 10:
                return 1
            elif text_read.lower() == 'ok':
                return 1
            else:
                return 0
        else:
            return 0

        return 1

    def generate_search_index(self, text_read, current_status):

        # concatena status com o texto
        new_index = str(current_status) + str(text_read)

        return new_index

    def two_digit_conversion (self, text_read):
        if text_read == '10':
            return 'A'
        if text_read == '11':
            return 'B'
        if text_read == '12':
            return 'C'
        if text_read == '13':
            return 'D'
        if text_read == '14':
            return 'E'
        if text_read == '15':
            return 'F'
        if text_read == '16':
            return 'G'
        if text_read == '17':
            return 'H'
        if text_read == '18':
            return 'I'
        if text_read == '19':
            return 'J'
        if text_read == '20':
            return 'K'
        if text_read == '21':
            return 'L'
        if text_read == '22':
            return 'M'
        if text_read == '23':
            return 'N'
        if text_read == '24':
            return 'O'
        if text_read == '25':
            return 'P'
        if text_read == '26':
            return 'Q'
        if text_read == '27':
            return 'R'
        if text_read == '28':
            return 'S'
        if text_read == '29':
            return 'T'
        if text_read == '30':
            return 'U'
        if text_read == '31':
            return 'V'
        if text_read == '32':
            return 'W'
        if text_read == '33':
            return 'X'
        if text_read == '34':
            return 'Y'
        if text_read == '35':
            return 'Z'

        return 'invalido'

    def remove_from_list(self, contacts_list):

        run_list = 0

        while run_list < len(contacts_list):

            if contacts_list[run_list][2] < datetime.now() - timedelta(minutes=30):

                # REMOVE CONTACT BY TIMEOUT
                old_contact = contacts_list[run_list]
                print('contato retirado da lista  por timeout' + str(old_contact))
                contacts_list.remove(old_contact)

                # WRITE LOG log type (log_type, conv_id, cnt_name, cnt_status, cnt_is_final, cnt_last_text, cnt_add_inf)
                self.database.write_log_conversation('111', old_contact[6], old_contact[0], old_contact[1], old_contact[5], old_contact[3], old_contact[4])

            if contacts_list[run_list][4] != 'x':

                # REMOVE CONTACT BY FINAL STATE
                old_contact = contacts_list[run_list]
                print('contato retirado da lista por estado final:  ' + str(old_contact))
                contacts_list.remove(old_contact)

                # WRITE LOG log type (log_type, conv_id, cnt_name, cnt_status, cnt_is_final, cnt_last_text, cnt_add_inf)
                if contacts_list[run_list][4] in ('1', '2', '3'): # RATING
                    self.database.write_log_conversation('121', old_contact[6], old_contact[0], old_contact[1], old_contact[5], old_contact[3], old_contact[4])
                elif 5 < len(contacts_list[run_list][4]) < 10: # NO HELP WITH OPEN TICKET
                    self.database.write_log_conversation('122', old_contact[6], old_contact[0], old_contact[1], old_contact[5], old_contact[3], old_contact[4])
                elif contacts_list[run_list][4].lower() == 'ok': # NO HELP AND NO OPEN TICKET
                    self.database.write_log_conversation('123', old_contact[6], old_contact[0], old_contact[1], old_contact[5], old_contact[3], old_contact[4])

            run_list = run_list + 1

        return contacts_list

    def generate_new_conversation(self, contact_name):
        # generate_new_conversation(contact_name, '0', datetime.now(), '', 'x','0')
        # generate new conversation with contacts name,
        new_conv_id = self.database.generate_new_conversation(contact_name)
        #new_conv_id = '0'
        print(contact_name + ' ' + str(new_conv_id))
        new_conv_id = str(new_conv_id)

        return new_conv_id

    def write_log_conversation(self, log_type, conv_id, cnt_name, cnt_status, cnt_is_final, cnt_last_text, cnt_add_inf):

        print(log_type + ' ' + conv_id + ' ' + cnt_name + ' ' + cnt_status +
              ' ' + cnt_is_final + ' ' + cnt_last_text + ' ' + cnt_add_inf)
        self.database.write_log_conversation(log_type, conv_id, cnt_name, cnt_status, cnt_is_final, cnt_last_text, cnt_add_inf)


'''
- log_holding_id ///gerado no banco
- log_holding_type
- conversation_id
- log_holding_date ///gerado no banco
- contact_name
- contact_status 
- contact_final 
- contact_last_text 
- contact_add_information //nota ou chamado etc..'''