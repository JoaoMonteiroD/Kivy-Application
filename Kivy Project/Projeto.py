from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import mysql.connector
import smtplib
from email.message import EmailMessage
from datetime import datetime, date


Window.maximize()

# Cor de fundo da aplicação
Window.clearcolor = ( "#c7d0d8" )

# Conectar à base de dados
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="base_dos_ids_3_teste"
    )

# Criar um cursor para executar comandos SQL
cursor = mydb.cursor()

#Criar base de dados:
#cursor.execute("CREATE DATABASE base_dos_ids_3_teste")

# Criação da tabela de utilizadores
criar_tabela_utilizadores = '''
    CREATE TABLE IF NOT EXISTS Utilizadores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(255),
        email VARCHAR(255),
        senha VARCHAR(255)
    )
'''

cursor.execute(criar_tabela_utilizadores)

criar_tabela_tipo_desp_sub = '''
    CREATE TABLE IF NOT EXISTS tipo_desp_sub (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tipo_desp_sub VARCHAR(100)
    )
'''

cursor.execute(criar_tabela_tipo_desp_sub)

# Criação da tabela de dados específicos do utilizador
criar_tabela_dados_utilizadores = '''
    CREATE TABLE IF NOT EXISTS dados_utilizadores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_utilizador INT,
        Subscrição VARCHAR(100),
        Tipo_Subscrição INT,
        Valor VARCHAR(100),
        Fidelização VARCHAR(100),
        Data_Início_Subscrição VARCHAR(100),
        Data_Término_Subscrição VARCHAR(100),
        FOREIGN KEY (id_utilizador) REFERENCES Utilizadores(id),
        FOREIGN KEY (Tipo_Subscrição) REFERENCES tipo_desp_sub(id)
    )
'''
cursor.execute(criar_tabela_dados_utilizadores)


# Criação da tabela de dados específicos do utilizador
criar_tabela_dados_utilizadores_despesas = '''
    CREATE TABLE IF NOT EXISTS dados_utilizadores_despesas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_utilizador INT,
        Despesa VARCHAR(100),
        Tipo_Despesa INT,
        Valor VARCHAR(100),
        Data_Início_Despesa VARCHAR(100),
        Data_Limite_Despesa VARCHAR(100),
        FOREIGN KEY (id_utilizador) REFERENCES Utilizadores(id),
        FOREIGN KEY (Tipo_Despesa) REFERENCES tipo_desp_sub(id)
    )
'''
cursor.execute(criar_tabela_dados_utilizadores_despesas)

def enviar_email(destinatario, assunto, mensagem):

    remetente = "testeprojeto10@hotmail.com"
    senha = "12345_PT"

    msg = EmailMessage()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto

    # Define o conjunto de caracteres UTF-8 para a mensagem
    msg.set_content(mensagem, subtype = 'plain', charset = 'utf-8')

    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)

        print("Email enviado com sucesso!")

    except Exception as e:

        print("Ocorreu um erro ao enviar o email:", str(e))


# Função para verificar as subscrições e enviar email quando a data de término for atingida
def verificar_subscricoes(email_logado):

    cursor.execute("""
        SELECT Subscrição, Data_Término_Subscrição 
        FROM dados_utilizadores 
        WHERE id_utilizador = (SELECT id FROM Utilizadores WHERE email = %s)
    """, (email_logado,))

    resultados = cursor.fetchall()

    if resultados:
        subscricoes_agrupadas = {}  # Dicionário para agrupar as subscrições por data de término

        for subscricao, data_termino in resultados:
            data_termino = data_termino.strftime("%Y-%m-%d")  # Converter para formato de data
            if data_termino == str(datetime.today().date()):
                if data_termino in subscricoes_agrupadas:
                    # Se a data já existir no dicionário, adiciona a subscrição à lista existente
                    subscricoes_agrupadas[data_termino].append(subscricao)
                else:
                    # Se a data não existir no dicionário, cria uma nova lista com a subscrição
                    subscricoes_agrupadas[data_termino] = [subscricao]

        if subscricoes_agrupadas:
            destinatario = email_logado
            assunto = "Pagamento das subscrições"
            mensagem = "Olá, é hora de renovar as seguintes subscrições:\n"

            for data, subscricoes in subscricoes_agrupadas.items():
                mensagem += f"\nData de término: {data}\n"
                mensagem += "\nSubscrições:\n"
                for subscricao in subscricoes:
                    mensagem += f"- {subscricao}\n"

            enviar_email(destinatario, assunto, mensagem)
        else:
            print("Utilizador não possui subscrições.")

    else:
        print("Utilizador não possui subscrições.")        

    
# Função para verificar as despesas e enviar email quando a data de término for atingida
def verificar_despesas(email_logado):
    cursor.execute("""
        SELECT Despesa, Data_Limite_Despesa 
        FROM dados_utilizadores_despesas 
        WHERE id_utilizador = (SELECT id FROM Utilizadores WHERE email = %s)
    """, (email_logado,))

    resultados = cursor.fetchall()

    if resultados:
        despesas_agrupadas = {}  # Dicionário para agrupar as despesas por data de término

        for despesa, data_limite in resultados:
            data_limite = data_limite.strftime("%Y-%m-%d")  # Converter para formato de data
            if data_limite == str(datetime.today().date()):
                if data_limite in despesas_agrupadas:
                    # Se a data já existir no dicionário, adiciona a despesa à lista existente
                    despesas_agrupadas[data_limite].append(despesa)
                else:
                    # Se a data não existir no dicionário, cria uma nova lista com a despesa
                    despesas_agrupadas[data_limite] = [despesa]

        if despesas_agrupadas:
            destinatario = email_logado
            assunto = "Pagamento das despesas"
            mensagem = "Olá, é hora de pagar as seguintes despesas:\n"

            for data, despesas in despesas_agrupadas.items():
                mensagem += f"\nData limite: {data}\n"
                mensagem += "\nDespesas:\n"
                for despesa in despesas:
                    mensagem += f"- {despesa}\n"

            enviar_email(destinatario, assunto, mensagem)
        else:
            print("Utilizador não possui despesas.")

    else:
        print("Utilizador não possui despesas.")         


#---------------------------------------------------------------------- JANELA GESTORA ---------------------------------------------------------------------

class Janela_Gestora(ScreenManager):
    pass

#---------------------------------------------------------------------- JANELA PRINCIPAL ---------------------------------------------------------------------

class Janela_Principal(Screen):
    pass

#------------------------------------------------------------------------- TELA LOGIN ------------------------------------------------------------------------

class Tela_Login(Screen):

    email_logado = ""  # Atributo para armazenar o email do usuário logado
    
    def login(self):
        nome_mail = self.ids.nome_mail.text
        palavra_p = self.ids.palavra_chave.text
        mail = self.ids.nome_mail.text

        # Verificar se o utilizador e a senha estão corretos
        sql = "SELECT * FROM Utilizadores WHERE (nome = %s OR email = %s) AND senha = %s"
        val = (nome_mail, mail, palavra_p)

        cursor.execute(sql, val)

        result = cursor.fetchone()

        if result:
            self.ids.msg_erro.text = 'Login realizado com sucesso.'

            # Armazena o ID da conta do utilizador autenticado na variável global
            global conta_atual
            conta_atual = result[0]  # Posição do ID da conta na base de dados

            # Obter o endereço de email do utilizador logado
            self.email_logado = result[2]

            # Verificar as subscrições quando o login for realizado
            verificar_subscricoes(self.email_logado)
            
            verificar_despesas(self.email_logado)

            # Redireciona para a tela seginte
            self.manager.current = 'Tela_Escolha'

        else:
            self.ids.msg_erro.text = 'Nome de utilizador/e-mail ou senha incorretos.'

#---------------------------------------------------------------------- TELA CRIAR CONTA ----------------------------------------------------------------------

class Tela_Criar_Conta(Screen):

    def criar_conta(self):
        nome = self.ids.nome.text
        mail = self.ids.mail.text
        palavra_p = self.ids.palavra_chave.text
        confirmar_palavra_p = self.ids.confirmar_palavra_chave.text

        # Verificar se o e-mail já foi utilizado
        sql = "SELECT * FROM Utilizadores WHERE email = %s"
        val = (mail, )

        cursor.execute(sql, val)

        result = cursor.fetchone()

        # Verificação de campos em falta
        if not nome or not mail or not palavra_p or not confirmar_palavra_p:
            self.ids.msg_erro.text = 'Campos em falta'

        elif result is not None:
            self.ids.msg_erro.text = 'Este e-mail já está a ser utilizado.'

        # Verificação se as passes inseridas são iguais    
        elif palavra_p != confirmar_palavra_p:
            self.ids.msg_erro.text = 'As senhas não correspondem.'

        else:
            # Inserir dados na tabela
            sql = "INSERT INTO Utilizadores (nome, email, senha) VALUES (%s, %s, %s)"
            val = (nome, mail, palavra_p)

            cursor.execute(sql, val)

            mydb.commit()

            self.ids.msg_erro.text = 'Conta criada com sucesso.'
            
            # Redireciona para a tela seginte
            self.manager.current = "Tela_Login"

#---------------------------------------------------------------------- TELA ESCOLHA ----------------------------------------------------------------------

class Tela_Escolha(Screen):
    pass

#----------------------------------------------------------------- TELA SERVIÇOS (POPUP'S) ----------------------------------------------------------------

# Popup para inserir as subscrições
class MeuPopup(Popup):

    def receber_tipo_subscricoes(self):

        # Consultar subscrições disponíveis
        cursor.execute("SELECT * FROM tipo_desp_sub")

        subscricoes = [row[1] for row in cursor.fetchall()]

        return subscricoes
        
    def inserir_dados_subscricoes(self):

        global conta_atual

        subscricao = self.ids.subscricao.text
        tipo_subscricao = self.ids.tipo_subscricao.text
        valor = self.ids.valor.text
        fidelizacao = self.ids.fidelizacao.text
        dt_inicio_subscricao = self.ids.dt_inicio_subscricao.text
        dt_termino_subscricao = self.ids.dt_termino_subscricao.text

        # Obter o ID do tipo de subscrição
        cursor.execute("SELECT id FROM tipo_desp_sub WHERE tipo_desp_sub = %s", (tipo_subscricao,))
        result = cursor.fetchone()
        if result is None:
            self.ids.msg_erro.text = 'Tipo de subscrição inválido.'
            return

        tipo_subscricao_id = result[0]

        # Verificar se o nº da subscrição já existe
        sql = "SELECT * FROM dados_utilizadores WHERE Subscrição = %s"
        val = (subscricao, )

        cursor.execute(sql, val)

        result = cursor.fetchone()

        if result is not None:
            self.ids.msg_erro.text = 'Esta subscrição já existe.'

        # Verificação de campos em falta
        if not subscricao or not tipo_subscricao or not valor or not fidelizacao or not dt_inicio_subscricao or not dt_termino_subscricao:
            self.ids.msg_erro.text = 'Campos em falta'  

        # Verifica se o valor recebe só numeros
        elif not self.ids.valor.text.replace('.', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira um valor numérico válido.'

        elif not self.ids.dt_inicio_subscricao.text.replace('-', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira datas válidas no formato aaaa-mm-dd.'

        elif not self.ids.dt_termino_subscricao.text.replace('-', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira datas válidas no formato aaaa-mm-dd.'

        else:
            # Verificar o intervalo do ano
            dt_parts = self.ids.dt_inicio_subscricao.text.split('-')
            dt_parts_1 = self.ids.dt_termino_subscricao.text.split('-')

            ano = int(dt_parts[0] and dt_parts_1[0])
            mes = int(dt_parts[1] and dt_parts_1[1])
            dia = int(dt_parts[2] and dt_parts_1[2])

            if mes < 1 or mes > 12:
                self.ids.msg_erro.text = 'Por favor, insira um mês válido entre 1 e 12.'
            
            elif dia < 1 or dia > 31:
                self.ids.msg_erro.text = 'Por favor, insira um dia válido entre 1 e 31.'

            elif mes == 2 and (dia < 1 or dia > 29):
                self.ids.msg_erro.text = 'Por favor, insira um dia válido entre 1 e 29 para o mês de fevereiro.'

            elif ano < 2023 or ano > 5000:
                self.ids.msg_erro.text = 'Por favor, insira um ano válido entre 2023 e 5000.'
             
            else:
                # Inserir dados específicos para um utilizador
                inserir_dados = '''INSERT INTO dados_utilizadores (id_utilizador, Subscrição, Tipo_Subscrição, Valor, Fidelização, Data_Início_Subscrição, Data_Término_Subscrição ) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
                id_utilizador = conta_atual
                val = (id_utilizador, subscricao, tipo_subscricao_id, valor, fidelizacao, dt_inicio_subscricao, dt_termino_subscricao)

                cursor.execute(inserir_dados, val)

                mydb.commit()

                self.ids.msg_erro.text = 'Subscrição criada com sucesso!'

                if result is not None:
                    conta_atual = result[0]  # Atribuição à variável global         

# Popup para remover as subscrições
class MeuPopup_1(Popup):

    def receber_subscricoes(self):

        # Consultar subscrições disponíveis
        cursor.execute("SELECT Subscrição FROM dados_utilizadores WHERE id_utilizador = %s", (conta_atual,))

        subscricoes = [row[0] for row in cursor.fetchall()]

        return subscricoes

    def remover_dados_subscricoes(self):

        subscricao_selecionada = self.ids.spinner_subscricao.text

        if not subscricao_selecionada or subscricao_selecionada == "Selecione uma subscrição":
            self.ids.msg_erro_sub.text = "Selecione uma subscrição antes de remover."
        else:
             # Remover a subscrição selecionada
            remover_dados = "DELETE FROM dados_utilizadores WHERE Subscrição = %s"
            val = (subscricao_selecionada,)

            cursor.execute(remover_dados, val)
            mydb.commit()

            self.ids.msg_erro_sub.text = "Subscrição removida com sucesso!"


class MeuPopup_2(Popup):

    def receber_subscricoes(self):

        # Consultar subscrições disponíveis
        cursor.execute("SELECT Subscrição FROM dados_utilizadores WHERE id_utilizador = %s", (conta_atual,))

        subscricoes = [row[0] for row in cursor.fetchall()]

        return subscricoes
    
    def abrir_popup_2_5(self, subscricao):

        # Consultar os dados da subscrição selecionada
        cursor.execute("""SELECT tipo_desp_sub, Valor, Fidelização, Data_Início_Subscrição, Data_Término_Subscrição 
                       FROM dados_utilizadores INNER JOIN tipo_desp_sub on dados_utilizadores.Tipo_Subscrição = tipo_desp_sub.id WHERE Subscrição = %s""", (subscricao,))
        resultado = cursor.fetchone()

        cursor.fetchall()

        # Abrir o segundo popup para edição da subscrição selecionada
        popup_2_5 = MeuPopup_2_5(subscricao_selecionada = subscricao, dados_subscricao = resultado)
        popup_2_5.open()

    def verificar_sub(self):

        subscricao_selecionada = self.ids.spinner_subscricao.text

        if not subscricao_selecionada or subscricao_selecionada == "Selecione uma subscrição":
            self.ids.msg_erro_sub.text = "Selecione uma subscrição antes de editar."
        else:
            self.abrir_popup_2_5(subscricao_selecionada)    


class MeuPopup_2_5(Popup):

    def __init__(self, subscricao_selecionada = None, dados_subscricao = None, **kwargs):
        super().__init__(**kwargs)
        
        # Armazeno o valor de subscricao_selecionada como um atributo da classe self.subscricao_selecionada, para que possa acessá-lo depois.
        self.subscricao_selecionada = subscricao_selecionada

        # Verificar se dados_subscricao retornou algo da consulta e atribuí os valores correspondentes
        if dados_subscricao:
            self.ids.subscricao.text = self.subscricao_selecionada
            self.ids.tipo_subscricao.text = str(dados_subscricao[0])
            self.ids.valor.text = str(dados_subscricao[1])
            self.ids.fidelizacao.text = str(dados_subscricao[2])
            self.ids.dt_inicio_subscricao.text = str(dados_subscricao[3])
            self.ids.dt_termino_subscricao.text = str(dados_subscricao[4])

    def atualizar_subscricoes(self):

        subscricao = self.ids.subscricao.text
        tipo_subscricao = self.ids.tipo_subscricao.text
        valor = self.ids.valor.text
        fidelizacao = self.ids.fidelizacao.text
        dt_inicio_subscricao = self.ids.dt_inicio_subscricao.text
        dt_termino_subscricao = self.ids.dt_termino_subscricao.text

        # Obter o ID do tipo de subscrição
        cursor.execute("SELECT id FROM tipo_desp_sub WHERE tipo_desp_sub = %s", (tipo_subscricao,))
        result = cursor.fetchone()
        if result is None:
            self.ids.msg_erro.text = 'Tipo de subscrição inválido.'
            return

        tipo_subscricao_id = result[0]

        # Verificação de campos em falta
        if not subscricao or not tipo_subscricao or not valor or not fidelizacao or not dt_inicio_subscricao or not dt_termino_subscricao:
            self.ids.msg_erro.text = 'Campos em falta'  

        # Verifica se o valor recebe só numeros
        elif not self.ids.valor.text.replace('.', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira um valor numérico válido.'

        elif not self.ids.dt_inicio_subscricao.text.replace('-', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira datas válidas no formato aaaa-mm-dd.'

        elif not self.ids.dt_inicio_subscricao.text.replace('-', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira datas válidas no formato aaaa-mm-dd.'

        else:
            if subscricao == '' or subscricao == self.subscricao_selecionada:

                # Verificar o intervalo do ano
                dt_parts = self.ids.dt_inicio_subscricao.text.split('-')
                dt_parts_1 = self.ids.dt_termino_subscricao.text.split('-')

                ano = int(dt_parts[0] and dt_parts_1[0])
                mes = int(dt_parts[1] and dt_parts_1[1])
                dia = int(dt_parts[2] and dt_parts_1[2])

                if mes < 1 or mes > 12:
                    self.ids.msg_erro.text = 'Por favor, insira um mês válido entre 1 e 12.'
                
                elif dia < 1 or dia > 31:
                    self.ids.msg_erro.text = 'Por favor, insira um dia válido entre 1 e 31.'

                elif mes == 2 and (dia < 1 or dia > 29):
                    self.ids.msg_erro.text = 'Por favor, insira um dia válido entre 1 e 29 para o mês de fevereiro.'

                elif ano < 2023 or ano > 5000:
                    self.ids.msg_erro.text = 'Por favor, insira um ano válido entre 2023 e 5000.'    

                # Executar a consulta SQL para atualizar os dados na base de dados
                else:
                    sql = "UPDATE dados_utilizadores SET Tipo_Subscrição = %s, Valor = %s, Fidelização = %s, Data_Início_Subscrição = %s, Data_Término_Subscrição = %s WHERE Subscrição = %s"
                    val = (tipo_subscricao_id, valor, fidelizacao, dt_inicio_subscricao, dt_termino_subscricao, self.subscricao_selecionada)

                    cursor.execute(sql, val)

                    mydb.commit()

                    self.ids.msg_erro.text = "Subscrição editada com sucesso!"

            else:
                self.ids.msg_erro.text = "Não é permitido alterar o nome da subscrição."      

#---------------------------------------------------------------------- TELA SERVIÇOS ----------------------------------------------------------------------

# Função auxiliar para consultar as subscrições

def consultar_subscricoes():
        
    # Consulta as subscrições relacionadas à conta atualmente logada
    cursor.execute("""SELECT Subscrição, tipo_desp_sub, Valor, Fidelização, Data_Início_Subscrição, Data_Término_Subscrição 
                   FROM dados_utilizadores INNER JOIN tipo_desp_sub on dados_utilizadores.Tipo_Subscrição = tipo_desp_sub.id WHERE id_utilizador = %s""", (conta_atual,))

    # Obter os resultados da consulta
    resultados = cursor.fetchall()

    return resultados

class Tela_Servicos(Screen):

    def on_enter(self):
        # Obter o endereço de email do usuário logado
        email_logado = self.manager.get_screen('Tela_Login').email_logado

        # Chamar a função verificar_subscricoes_popup
        self.verificar_subscricoes_popup(email_logado)

    # Função para verificar as subscrições e mostrar o popup quando a data de término estiver a dois dias de expirar
    def verificar_subscricoes_popup(self, email_logado):

        cursor.execute("""SELECT Subscrição, Data_Término_Subscrição 
                       FROM dados_utilizadores WHERE id_utilizador = (SELECT id FROM Utilizadores WHERE email = %s)""", (email_logado,))
        resultados = cursor.fetchall()

        subscricoes_agrupadas = {}  # Dicionário para agrupar as subscrições por data de término

        if resultados:
            
            for subscricao, data_termino in resultados:
                # Converter a data de término para o formato de data
                data_termino = datetime.strptime(str(data_termino), "%Y-%m-%d").date() 

                # Obter a data atual
                data_atual = datetime.now().date()

                # Calcular a diferença entre a data de término e a data atual
                diff = data_termino - data_atual

                if diff.days == 2:  # Verifica se faltam exatamente dois dias para a data de término
                    if data_termino in subscricoes_agrupadas:
                        # Se a data já existir no dicionário, adiciona a subscrição à lista existente
                        subscricoes_agrupadas[data_termino].append(subscricao)
                    else:
                        # Se a data não existir no dicionário, cria uma nova lista com a subscrição
                        subscricoes_agrupadas[data_termino] = [subscricao]

        if subscricoes_agrupadas:
            # Criação do conteúdo do popup
            popup_content = BoxLayout(orientation = 'vertical', spacing=10)
            popup_content.add_widget(Label(text = "Olá, suas subscrições estão próximas de expirar:"))

            for data, subscricoes in subscricoes_agrupadas.items():
                popup_content.add_widget(Label(text = f"Data de término: {data}"))
                for subscricao in subscricoes:
                    popup_content.add_widget(Label(text = f"- {subscricao}"))

            # Criação do popup
            popup = Popup(title = "Subscrições", content=popup_content, size_hint = (None, None), size = (400, 400))
            popup.open()
        else:
            print("Utilizador não possui subscrições.")    

    def consultar_e_exibir_subscricoes(self):

        # Consultar as subscrições
        resultados = consultar_subscricoes()

        # Obter a referência à tabela no KV
        tabela = self.ids.tabela

        # Limpar o conteúdo anterior
        tabela.clear_widgets()

        # Criação dos cabeçalhos da tabela
        cabecalhos = ['Subscrição', 'Tipo de Subscrição', 'Valor', 'Fidelização', 'Data de Início', 'Data de Término']
        for cabecalho in cabecalhos:
            tabela.add_widget(Label(text=cabecalho, color = ("#000000")))

        # Adicionar os dados da tabela
        for subscricao in resultados:
            tabela.add_widget(Label(text = str(subscricao[0]), color = ("#000000")))  # Subscrição
            tabela.add_widget(Label(text = str(subscricao[1]), color = ("#000000")))  # Tipo de Subscrição
            tabela.add_widget(Label(text = str(subscricao[2]), color = ("#000000")))  # Valor
            tabela.add_widget(Label(text = str(subscricao[3]), color = ("#000000")))  # Fidelização
            tabela.add_widget(Label(text = str(subscricao[4]), color = ("#000000")))  # Data de Início
            tabela.add_widget(Label(text = str(subscricao[5]), color = ("#000000")))  # Data de Término

        # Ajustar a altura do GridLayout
        num_linhas = len(resultados) + 1  # +1 para a linha de cabeçalhos
        altura_linha = 30  # Ajuste a altura conforme necessário
        altura_tabela = num_linhas * altura_linha
        tabela.height = altura_tabela
        tabela.minimum_height = altura_tabela    


#---------------------------------------------------------------------- TELA DESPESAS (POPUP'S) ----------------------------------------------------------------------

# Popup para inserir as subscrições
class MeuPopup_Despesas(Popup):

    def receber_tipo_despesas(self):

        # Consultar subscrições disponíveis
        cursor.execute("SELECT * FROM tipo_desp_sub")

        despesas = [row[1] for row in cursor.fetchall()]

        return despesas
        
    def inserir_dados_despesas(self):

        global conta_atual

        despesa = self.ids.despesa.text
        tipo_despesa = self.ids.tipo_despesa.text
        valor = self.ids.valor.text
        dt_inicio_despesa = self.ids.dt_inicio_despesa.text
        dt_limite_despesa = self.ids.dt_limite_despesa.text

        # Obter o ID do tipo de despesa
        cursor.execute("SELECT id FROM tipo_desp_sub WHERE tipo_desp_sub = %s", (tipo_despesa,))
        result = cursor.fetchone()
        if result is None:
            self.ids.msg_erro.text = 'Tipo de despesa inválido.'
            return

        tipo_despesa_id = result[0]

        # Verificar se o nº da subscrição já existe
        sql = "SELECT * FROM dados_utilizadores_despesas WHERE Despesa = %s"
        val = (despesa, )

        cursor.execute(sql, val)

        result = cursor.fetchone()

        if result is not None:
            self.ids.msg_erro.text = 'Esta subscrição já existe.'

        # Verificação de campos em falta
        if not despesa or not tipo_despesa or not valor or not dt_inicio_despesa or not dt_limite_despesa:
            self.ids.msg_erro.text = 'Campos em falta'  

        # Verifica se o valor recebe só numeros
        elif not self.ids.valor.text.replace('.', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira um valor numérico válido.'

        elif not self.ids.dt_inicio_despesa.text.replace('-', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira datas válidas no formato aaaa-mm-dd.'

        elif not self.ids.dt_limite_despesa.text.replace('-', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira datas válidas no formato aaaa-mm-dd.'

        else:
            # Verificar o intervalo do ano
            dt_parts = self.ids.dt_inicio_despesa.text.split('-')
            dt_parts_1 = self.ids.dt_limite_despesa.text.split('-')

            ano = int(dt_parts[0] and dt_parts_1[0])
            mes = int(dt_parts[1] and dt_parts_1[1])
            dia = int(dt_parts[2] and dt_parts_1[2])

            if mes < 1 or mes > 12:
                self.ids.msg_erro.text = 'Por favor, insira um mês válido entre 1 e 12.'
            
            elif dia < 1 or dia > 31:
                self.ids.msg_erro.text = 'Por favor, insira um dia válido entre 1 e 31.'

            elif mes == 2 and (dia < 1 or dia > 29):
                self.ids.msg_erro.text = 'Por favor, insira um dia válido entre 1 e 29 para o mês de fevereiro.'

            elif ano < 2023 or ano > 5000:
                self.ids.msg_erro.text = 'Por favor, insira um ano válido entre 2023 e 5000.'
             
            else:
                # Inserir dados específicos para um utilizador
                inserir_dados = '''INSERT INTO dados_utilizadores_despesas (id_utilizador, Despesa, Tipo_Despesa, Valor, Data_Início_Despesa, Data_Limite_Despesa ) VALUES (%s, %s, %s, %s, %s, %s)'''
                id_utilizador = conta_atual
                val = (id_utilizador, despesa, tipo_despesa_id, valor, dt_inicio_despesa, dt_limite_despesa)

                cursor.execute(inserir_dados, val)

                mydb.commit()

                self.ids.msg_erro.text = 'Subscrição criada com sucesso!'

                if result is not None:
                    conta_atual = result[0]  # Atribuição à variável global


# Popup para remover as despesas
class MeuPopup_1_Despesas(Popup):

    def receber_despesas(self):

        # Consultar despesas disponíveis
        cursor.execute("SELECT Despesa FROM dados_utilizadores_despesas WHERE id_utilizador = %s", (conta_atual,))

        despesas = [row[0] for row in cursor.fetchall()]

        return despesas

    def remover_dados_despesas(self):

        despesa_selecionada = self.ids.spinner_despesa.text

        if not despesa_selecionada or despesa_selecionada == "Selecione uma despesa":
            self.ids.msg_erro_sub.text = "Selecione uma despesa antes de remover."
        else:
             # Remover a despesa selecionada
            remover_dados = "DELETE FROM dados_utilizadores_despesas WHERE Despesa = %s"
            val = (despesa_selecionada,)

            cursor.execute(remover_dados, val)
            mydb.commit()

            self.ids.msg_erro_sub.text = "Despesa removida com sucesso!"


class MeuPopup_2_Despesas(Popup):

    def receber_despesas(self):

        # Consultar despesas disponíveis
        cursor.execute("SELECT Despesa FROM dados_utilizadores_despesas WHERE id_utilizador = %s", (conta_atual,))

        despesas = [row[0] for row in cursor.fetchall()]

        return despesas
    
    def abrir_popup_2_5_despesas(self, despesa):

        # Consultar os dados da despesa selecionada
        cursor.execute("SELECT tipo_desp_sub, Valor, Data_Início_Despesa, Data_Limite_Despesa FROM dados_utilizadores_despesas INNER JOIN tipo_desp_sub on dados_utilizadores_despesas.Tipo_Despesa = tipo_desp_sub.id WHERE Despesa = %s", (despesa,))
        resultado = cursor.fetchone()

        cursor.fetchall()

        # Abrir o segundo popup para edição da despesa selecionada
        popup_2_5 = MeuPopup_2_5_Despesas(despesa_selecionada = despesa, dados_despesa = resultado)
        popup_2_5.open()

    def verificar_despesa(self):

        despesa_selecionada = self.ids.spinner_despesa.text

        if not despesa_selecionada or despesa_selecionada == "Selecione uma despesa":
            self.ids.msg_erro_despesa.text = "Selecione uma despesa antes de editar."
        else:
            self.abrir_popup_2_5_despesas(despesa_selecionada)    


class MeuPopup_2_5_Despesas(Popup):

    def __init__(self, despesa_selecionada = None, dados_despesa = None, **kwargs):
        super().__init__(**kwargs)
        
        # Armazeno o valor de subscricao_selecionada como um atributo da classe self.subscricao_selecionada, para que possa acessá-lo depois.
        self.despesa_selecionada = despesa_selecionada

        # Verificar se dados_subscricao retornou algo da consulta e atribuí os valores correspondentes
        if dados_despesa:
            self.ids.despesa.text = self.despesa_selecionada
            self.ids.tipo_despesa.text = str(dados_despesa[0])
            self.ids.valor.text = str(dados_despesa[1])
            self.ids.dt_inicio_despesa.text = str(dados_despesa[2])
            self.ids.dt_limite_despesa.text = str(dados_despesa[3])

    def atualizar_despesas(self):

        despesa = self.ids.despesa.text
        tipo_despesa = self.ids.tipo_despesa.text
        valor = self.ids.valor.text
        dt_inicio_despesa = self.ids.dt_inicio_despesa.text
        dt_limite_despesa = self.ids.dt_limite_despesa.text

        # Obter o ID do tipo de subscrição
        cursor.execute("SELECT id FROM tipo_desp_sub WHERE tipo_desp_sub = %s", (tipo_despesa,))
        result = cursor.fetchone()
        if result is None:
            self.ids.msg_erro.text = 'Tipo de subscrição inválido.'
            return

        tipo_despesa_id = result[0]

        # Verificação de campos em falta
        if not despesa or not tipo_despesa or not valor or not dt_inicio_despesa or not dt_limite_despesa:
            self.ids.msg_erro.text = 'Campos em falta'  

        # Verifica se o valor recebe só numeros
        elif not self.ids.valor.text.replace('.', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira um valor numérico válido.'

        elif not self.ids.dt_inicio_despesa.text.replace('-', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira datas válidas no formato aaaa-mm-dd.'

        elif not self.ids.dt_limite_despesa.text.replace('-', '').isdigit():
            self.ids.msg_erro.text = 'Por favor, insira datas válidas no formato aaaa-mm-dd.'

        else:
            if despesa == '' or despesa == self.despesa_selecionada:

                # Verificar o intervalo do ano
                dt_parts = self.ids.dt_inicio_despesa.text.split('-')
                dt_parts_1 = self.ids.dt_limite_despesa.text.split('-')

                ano = int(dt_parts[0] and dt_parts_1[0])
                mes = int(dt_parts[1] and dt_parts_1[1])
                dia = int(dt_parts[2] and dt_parts_1[2])

                if mes < 1 or mes > 12:
                    self.ids.msg_erro.text = 'Por favor, insira um mês válido entre 1 e 12.'
                
                elif dia < 1 or dia > 31:
                    self.ids.msg_erro.text = 'Por favor, insira um dia válido entre 1 e 31.'

                elif mes == 2 and (dia < 1 or dia > 29):
                    self.ids.msg_erro.text = 'Por favor, insira um dia válido entre 1 e 29 para o mês de fevereiro.'

                elif ano < 2023 or ano > 5000:
                    self.ids.msg_erro.text = 'Por favor, insira um ano válido entre 2023 e 5000.'    

                # Executar a consulta SQL para atualizar os dados na base de dados
                else:
                    sql = "UPDATE dados_utilizadores_despesas SET Tipo_Despesa = %s, Valor = %s, Data_Início_Despesa = %s, Data_Limite_Despesa = %s WHERE Despesa = %s"
                    val = (tipo_despesa_id, valor, dt_inicio_despesa, dt_limite_despesa, self.despesa_selecionada)

                    cursor.execute(sql, val)

                    mydb.commit()

                    self.ids.msg_erro.text = "Despesa editada com sucesso!"

            else:
                self.ids.msg_erro.text = "Não é permitido alterar o nome da despesa."


#---------------------------------------------------------------------- TELA DESPESAS ----------------------------------------------------------------------

# Função auxiliar para consultar as subscrições

def consultar_despesas():
        
    # Consulta as subscrições relacionadas à conta atualmente logada
    cursor.execute("SELECT Despesa, tipo_desp_sub, Valor, Data_Início_Despesa, Data_Limite_Despesa FROM dados_utilizadores_despesas INNER JOIN tipo_desp_sub on dados_utilizadores_despesas.Tipo_Despesa = tipo_desp_sub.id WHERE id_utilizador = %s", (conta_atual,))

    # Obter os resultados da consulta
    resultados = cursor.fetchall()

    return resultados

class Tela_Despesas(Screen):

    def on_enter(self):
        # Obter o endereço de email do usuário logado
        email_logado = self.manager.get_screen('Tela_Login').email_logado

        # Chamar a função verificar_subscricoes_popup
        self.verificar_despesas_popup(email_logado)

    # Função para verificar as despesas e exibir popup quando a data limite estiver próxima
    def verificar_despesas_popup(self, email_logado):
        cursor.execute("""SELECT Despesa, Data_Limite_Despesa 
                       FROM dados_utilizadores_despesas WHERE id_utilizador = (SELECT id FROM Utilizadores WHERE email = %s)""", (email_logado,))
        resultados = cursor.fetchall()

        despesas_agrupadas = {}  # Dicionário para agrupar as despesas por data limite

        if resultados:
            for despesa, data_termino in resultados:
                # Converter a data limite para o formato de data
                data_termino = datetime.strptime(str(data_termino), "%Y-%m-%d").date()

                # Obter a data atual
                data_atual = datetime.now().date()

                # Calcular a diferença entre a data limite e a data atual
                diff = data_termino - data_atual

                if diff.days == 2:  # Verifica se faltam exatamente dois dias para a data limite
                    if data_termino in despesas_agrupadas:
                        # Se a data já existir no dicionário, adiciona a despesa à lista existente
                        despesas_agrupadas[data_termino].append(despesa)
                    else:
                        # Se a data não existir no dicionário, cria uma nova lista com a despesa
                        despesas_agrupadas[data_termino] = [despesa]

        if despesas_agrupadas:
            # Criação do conteúdo do popup
            popup_content = BoxLayout(orientation = 'vertical', spacing=10)
            popup_content.add_widget(Label(text = "Olá, suas despesas estão próximas de vencer:"))

            for data, despesas in despesas_agrupadas.items():
                popup_content.add_widget(Label(text = f"Data limite: {data}"))
                for despesa in despesas:
                    popup_content.add_widget(Label(text = f"- {despesa}"))

            # Criação do popup
            popup = Popup(title = "Despesas", content=popup_content, size_hint = (None, None), size = (400, 400))
            popup.open()
        else:
            print("Utilizador não possui despesas.")    

    def consultar_e_exibir_despesas(self):

        # Consultar as subscrições
        resultados = consultar_despesas()

        # Obter a referência à tabela no KV
        tabela = self.ids.tabela

        # Limpar o conteúdo anterior
        tabela.clear_widgets()

        # Criação dos cabeçalhos da tabela
        cabecalhos = ['Despesa', 'Tipo de Despesa', 'Valor', 'Data de Início', 'Data Limite']
        for cabecalho in cabecalhos:
            tabela.add_widget(Label(text=cabecalho, color = ("#000000")))

        # Adicionar os dados da tabela
        for despesa in resultados:
            tabela.add_widget(Label(text = str(despesa[0]), color = ("#000000")))  # Despesa
            tabela.add_widget(Label(text = str(despesa[1]), color = ("#000000")))  # Tipo de Despesa
            tabela.add_widget(Label(text = str(despesa[2]), color = ("#000000")))  # Valor
            tabela.add_widget(Label(text = str(despesa[3]), color = ("#000000")))  # Data de Início
            tabela.add_widget(Label(text = str(despesa[4]), color = ("#000000")))  # Data Limite

        # Ajustar a altura do GridLayout
        num_linhas = len(resultados) + 1  # +1 para a linha de cabeçalhos
        altura_linha = 30  # Ajuste a altura conforme necessário
        altura_tabela = num_linhas * altura_linha
        tabela.height = altura_tabela
        tabela.minimum_height = altura_tabela

#---------------------------------------------------------- ARRANQUE DA APLICAÇÃO E DO FICHEIRO KIVY ------------------------------------------------------

#Classe e função necessárias para o arranque do programa com o Kivy   
class MinhaApp(App):
    def build(self):
        self.title = "Save" 

        # Retorna o ficheiro responsável pela parte gráfica do programa
        return Builder.load_file("menu.kv")

    # Função para sair do programa    
    def sair(self):
        self.stop()
    
# Função de arranque
MinhaApp().run()

