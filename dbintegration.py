import pyodbc
import re


class DbCommands:

    def __init__(self):

        self.conn = pyodbc.connect('Driver={SQL Server};'
                                   'Server=NT-03366;'
                                   'Database=Carlito_Teste;'
                                   'Trusted_Connection=yes;')

    def clear_string(self, text):

        text = str(text)
        text = text.replace('\'', '')
        text = text.replace('(', '')
        text = text.replace(', )', '')

        return text

    def generate_new_conversation(self, contact_name):

        #self.contact = contact_name

        cursor = self.conn.cursor()

        cursor.execute(
            '''
                       INSERT INTO Carlito_Teste.dbo.t_conversation(start_date, end_date, contact_name) 
                       VALUES (getdate(), null, ?); 
                       ''',
            contact_name
        )
        cursor.commit()

        cursor = self.conn.cursor()

        query = 'SELECT TOP 1 id FROM Carlito_Teste.dbo.t_conversation ' \
                'WHERE contact_name = ? order by start_date desc '
        cursor.execute(query, [contact_name])
        conversation_id = cursor.fetchone()

        conversation_id = self.clear_string(conversation_id)

        return conversation_id

    def find_response_dialogs(self, status):
        cursor = self.conn.cursor()

        query = 'SELECT text_response, is_final FROM Carlito_Teste.dbo.t_dialogs WHERE status = ? '
        cursor.execute(query, [status])
        row = cursor.fetchone()

        if not row:
            return 'notfound', 0

        response = row[0]
        is_final = row[1]

        response = self.clear_string(response)
        is_final = self.clear_string(is_final)

        return response, is_final

    def find_response_subjects(self, status):

        subject = status[0:4]
        cursor1 = self.conn.cursor()

        query1 = 'SELECT target_table FROM Carlito_Teste.dbo.t_subjects WHERE status = ?'
        cursor1.execute(query1, [subject])
        trgt_table = self.clear_string(cursor1.fetchone())

        print('indice da tabela: '+ str(subject))
        print('tabela procurada: '+ str(trgt_table))
        cursor2 = self.conn.cursor()

        query2 = 'SELECT response, is_final FROM Carlito_Teste.dbo.' + trgt_table + ' WHERE status = ? '
        cursor2.execute(query2, [status])
        row = cursor2.fetchone()

        if not row:
            return 'notfound', 0

        response = row[0]
        is_final = row[1]

        response = self.clear_string(response)
        is_final = self.clear_string(is_final)

        return response, is_final

    def get_indicator(self, indicator):
        cursor = self.conn.cursor()

        query = 'SELECT value FROM Carlito_Teste.dbo.t_indicators WHERE id = ? '
        cursor.execute(query, [indicator])
        indicator_value = cursor.fetchone()

        indicator_value = self.clear_string(indicator_value)

        return indicator_value

    def write_log_conversation(self, log_type, conv_id, cnt_name, cnt_status, cnt_is_final, cnt_last_text, cnt_add_inf):

        cursor = self.conn.cursor()

        cursor.execute(
            '''
                       INSERT INTO Carlito_Teste.dbo.t_log_holding(log_holding_type, conversation_id, log_holding_date, contact_name_ contact_status, contact_final, contact_last_text, contact_add_information) 
                       VALUES (?, ?, getdate(), ?, ?, ?, ?, ?); 
                       ''',
            log_type, conv_id, cnt_name, cnt_status, cnt_is_final, cnt_last_text, cnt_add_inf
        )
        cursor.commit()
