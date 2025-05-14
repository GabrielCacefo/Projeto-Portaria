# region imports e ETC's
#!!!!!!!!!!!!!!#


import sqlite3
from datetime import datetime
import re
import os
import platform
import time

system = platform.system()

# Pega a pasta onde o script está salvo
pasta_script = os.path.dirname(os.path.abspath(__file__))

# Caminho da pasta "bancos_de_dados" dentro de "scripts-exemplos"
pasta_banco = os.path.join(pasta_script, "bancos_teste")
caminho_banco = os.path.join(pasta_banco, "portaria.db")

# Criar a pasta se não existir
if not os.path.exists(pasta_banco):
    os.makedirs(pasta_banco)

# conecta ao banco de dados no local correto
conn = sqlite3.connect(caminho_banco)
c = conn.cursor()


#!!!!!!!!!!!!!!#
# endregion


# region Tabelas(BD)
#!!!!!!!!!!!!!!!#


c.execute(
    """CREATE TABLE IF NOT EXISTS "moradores" (
    "id_morador" INTEGER,
    "mor_nome" TEXT NOT NULL,
    "mor_cpf" TEXT NOT NULL UNIQUE,
    "mor_rg" TEXT NOT NULL UNIQUE,
    "mor_telefone" TEXT NOT NULL,
    "mor_n_apartamento" TEXT NOT NULL,
    "mor_bl_apartamento" TEXT NOT NULL,
    "mor_proprietario" TEXT NOT NULL CHECK("mor_proprietario" IN ('S', 'N')),
    "mor_n_garagem" TEXT,
    PRIMARY KEY("id_morador" AUTOINCREMENT))"""
)

c.execute(
    """CREATE TABLE IF NOT EXISTS visitantes (
    id_visitantes INTEGER PRIMARY KEY AUTOINCREMENT,
    vis_nome TEXT NOT NULL,
    vis_cpf TEXT NOT NULL UNIQUE,
    vis_telefone TEXT)"""
)

c.execute(
    """CREATE TABLE IF NOT EXISTS funcionarios (
    id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
    fun_nome TEXT NOT NULL,
    fun_cpf TEXT NOT NULL UNIQUE,
    fun_rg TEXT NOT NULL UNIQUE,
    fun_telefone TEXT NOT NULL)"""
)

c.execute(
    """CREATE TABLE IF NOT EXISTS "prestadores_servicos" (
    "id_prestador_servicos" INTEGER,
    "pre_nome" TEXT NOT NULL,
    "pre_cpf" TEXT NOT NULL UNIQUE,
    "pre_rg" TEXT NOT NULL UNIQUE,
    "pre_telefone" TEXT NOT NULL,
    PRIMARY KEY("id_prestador_servicos" AUTOINCREMENT))"""
)

c.execute(
    """CREATE TABLE IF NOT EXISTS "entregadores" (
    "id_entregador" INTEGER,
    "ent_nome" TEXT NOT NULL,
    "ent_cpf" TEXT NOT NULL UNIQUE,
    "ent_telefone" TEXT NOT NULL,
    PRIMARY KEY("id_entregador" AUTOINCREMENT))"""
)

c.execute(
    """CREATE TABLE IF NOT EXISTS veiculos (
    id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
    vei_id_usuario INTEGER NOT NULL,
    vei_tipo_usuario TEXT NOT NULL CHECK(vei_tipo_usuario IN ('morador', 'funcionario', 'prestador_servicos', 'entregador')),
    vei_tipo TEXT NOT NULL,
    vei_fabricante TEXT NOT NULL,
    vei_modelo TEXT NOT NULL,
    vei_cor TEXT NOT NULL,
    vei_placa TEXT NOT NULL UNIQUE,
    vei_ano INTEGER)"""
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS registros_entrada_saida (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        reg_tipo TEXT NOT NULL CHECK(reg_tipo IN ('entrada', 'saida')),
        reg_id_usuario INTEGER NOT NULL,
        reg_tipo_usuario TEXT NOT NULL CHECK(reg_tipo_usuario IN ('morador', 'funcionario', 'prestador_servicos', 'entregador', 'visitante')),
        reg_id_morador_responsavel INTEGER,
        reg_n_apartamento TEXT,
        reg_bl_apartamento TEXT,
        reg_data DATE NOT NULL,
        reg_hora TIME NOT NULL,
        reg_id_veiculo INTEGER,
        FOREIGN KEY (reg_id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE CASCADE,
        FOREIGN KEY (reg_id_usuario) REFERENCES moradores(id_morador) ON DELETE CASCADE,
        FOREIGN KEY (reg_id_usuario) REFERENCES funcionarios(id_funcionario) ON DELETE CASCADE,
        FOREIGN KEY (reg_id_usuario) REFERENCES prestadores_servicos(id_prestador_servicos) ON DELETE CASCADE,
        FOREIGN KEY (reg_id_usuario) REFERENCES entregadores(id_entregador) ON DELETE CASCADE,
        FOREIGN KEY (reg_id_usuario) REFERENCES visitantes(id_visitantes) ON DELETE CASCADE,
        FOREIGN KEY (reg_id_morador_responsavel) REFERENCES moradores(id_morador) ON DELETE CASCADE
    )
    """
)

conn.commit()


#!!!!!!!!!!!!!!!#
# endregion


# region Formatações
#!!!!!!!!!!!!!!!!!#


# Função para formatar a placa do veículo


def animacao():
    limpar_terminal()
    print(" - Carregando")
    time.sleep(0.25)
    limpar_terminal()
    print(" - Carregando.")
    time.sleep(0.25)
    limpar_terminal()
    print(" - Carregando..")
    time.sleep(0.25)
    limpar_terminal()
    print(" - Carregando...")
    time.sleep(0.25)
    limpar_terminal()


def formatar_placa(placa):
    """
    Remove pontuação, espaços e transforma a placa para letras maiúsculas.
    Ex: ' abc-1d23 ' -> 'ABC1D23'
    """
    placa_formatada = re.sub(
        r"[^A-Za-z0-9]", "", placa
    )  # Remove tudo que não for letra ou número
    return placa_formatada.upper()


# Função para limpar terminal
def limpar_terminal():
    if system == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# Função para formatar RG
def formatar_rg(rg):
    rg = re.sub(r"\D", "", rg)
    return f"{rg[:2]}.{rg[2:5]}.{rg[5:8]}-{rg[8:]}" if len(rg) == 9 else rg


# Função para formatar Telefone
def formatar_telefone(telefone):
    telefone = re.sub(r"\D", "", telefone)
    if len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    elif len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:3]}{telefone[3:7]}-{telefone[7:]}"
    return telefone


# Função para formatar CPF
def formatar_cpf(cpf):
    cpf_numeros = re.sub(r"\D", "", cpf)
    if len(cpf_numeros) == 11:
        return (
            f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
        )
    return cpf


# Função para limpar documento
def limpar_formatacao(formatacao):
    return re.sub(r"\D", "", formatacao)


#!!!!!!!!!!!!!!!!!#
# endregion


# region Validar(CPF)
#!!!!!!!!!!!!!!!!!#


# Função para validar CPF
def validar_cpf(cpf):
    cpf_numeros = re.sub(r"\D", "", cpf)
    if len(cpf_numeros) != 11 or cpf_numeros == cpf_numeros[0] * 11:
        return False
    soma = sum(int(cpf_numeros[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf_numeros[9]):
        return False
    soma = sum(int(cpf_numeros[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf_numeros[10]):
        return False
    return True


# Função para validar RG
def validar_rg(rg):
    rg_numeros = re.sub(r"\D", "", rg)
    if len(rg_numeros) != 9:
        return False
    return True


# Função para validar Placa de veículo
def validar_placa(placa):
    placa = placa.strip().upper()

    padrao_antigo = r"^[A-Z]{3}[0-9]{4}$"
    padrao_mercosul = r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$"

    if re.match(padrao_antigo, placa) or re.match(padrao_mercosul, placa):
        return True
    return False


#!!!!!!!!!!!!!!!!!#
# endregion


# region Menus
#!!!!!!!!!!!!!!#


def em_desenvolvimento():
    limpar_terminal()
    print("Em Desenvolvimento.")
    time.sleep(0.4)
    limpar_terminal()
    print("Em Desenvolvimento..")
    time.sleep(0.4)
    limpar_terminal()
    print("Em Desenvolvimento...")
    time.sleep(0.4)


###################################################################################################################################
def menu_principal():
    limpar_terminal()

    print("####################################")
    print("# Controle de Portaria (Alpha 0.6) #")
    print("####################################")

    opcao = input(
        "\nEscolha uma opção: \n1 - Registrar Entrada/Saída \n2 - Registrar Entrega (Em Desenvolvimento) \n3 - Consultar Registros \n4 - Cadastrar pesssoa \n5 - Menu de Veículos \n6 - Sair \nOpção: "
    )
    if opcao == "1":
        menu_registrar_entrada_saida()
    elif opcao == "2":
        em_desenvolvimento()
        menu_principal()
    elif opcao == "3":
        consultar_registros()
    elif opcao == "4":
        menu_cadastro()
    elif opcao == "5":
        menu_de_veiculos()
    elif opcao == "6":
        limpar_terminal()
        print("Saindo do sistema...")
        exit()
    else:
        opcao_invalida()
        menu_principal()


###################################################################################################################################
def menu_cadastro():
    limpar_terminal()
    print("=== Menu de Cadastro ===")
    cadastro_opcao = input(
        "1 - Cadastrar Morador \n2 - Cadastrar Visitante \n3 - Cadastrar Funcionário \n4 - Cadastrar Prestador de serviços \n5 - Cadastrar Entregador \n6 <-- Voltar \nOpção: "
    )
    if cadastro_opcao == "1":
        cadastrar_morador()
    elif cadastro_opcao == "2":
        print("Cadastro Visitantes")
        cadastrar_visitante()
    elif cadastro_opcao == "3":
        print("Cadastro Funcionários")
        cadastrar_funcionario()
    elif cadastro_opcao == "4":
        print("Cadastro Prestador de Serviços")
        cadastrar_prestador()
    elif cadastro_opcao == "5":
        print("Cadastro Entregador")
        cadastrar_entregador()
    elif cadastro_opcao == "6":
        limpar_terminal()
        menu_principal()
    else:
        opcao_invalida()
        menu_cadastro()


###################################################################################################################################
def menu_registrar_entrada_saida():
    while True:
        limpar_terminal()
        print("=== Menu de Registro de Entrada/Saída ===")
        print("Por favor selecione o critério de busca:")
        escolha = input(
            "1 - Buscar por nome/CPF \n2 - Buscar por número e bloco do apartamento (apenas moradores) \n3 - <-- Voltar \nOpção: "
        )

        if escolha == "1":
            registrar_a_entrada_e_saida()

        elif escolha == "2":
            n_apartamento = inserir_apartamento()
            bl_apartamento = inserir_bloco()

            c.execute(
                "SELECT mor_nome, mor_n_apartamento, mor_bl_apartamento, id_morador FROM moradores WHERE mor_n_apartamento = ? AND mor_bl_apartamento = ?",
                (n_apartamento, bl_apartamento),
            )
            moradores = c.fetchall()

            if not moradores:
                print(
                    "Nenhum morador encontrado com esse número e bloco de apartamento. Gostaria de cadastrar um novo morador? (S/N)"
                )
                opcao = input("Opção: ").strip().upper()
                if opcao == "S":
                    cadastrar_morador()
                else:
                    menu_principal()

            for i, morador in enumerate(moradores, start=1):
                mor_nome, mor_n_apartamento, mor_bl_apartamento, mor_id = morador
                print(
                    f"{i}. {mor_nome} Apto: {mor_n_apartamento} Bloco: {mor_bl_apartamento}"
                )

            while True:
                try:
                    escolha = (
                        int(
                            input(
                                "\nDigite o número do morador que deseja registrar a entrada/saída (ou digite 0 e aperte Enter para cancelar): "
                            )
                        )
                        - 1
                    )
                    if escolha == -1:
                        print("Cadastro cancelado.")
                        time.sleep(2)
                        menu_principal()

                    if 0 <= escolha < len(moradores):
                        limpar_terminal()
                        mor_nome, mor_n_apartamento, mor_bl_apartamento, mor_id = (
                            moradores[escolha]
                        )
                        print(
                            f"\nVocê escolheu: {mor_nome} Apto: {mor_n_apartamento} Bloco: {mor_bl_apartamento}"
                        )
                        while True:
                            print("Gostaria de registrar a entrada ou saída? (E/S)")
                            registro = input("Opção: ").strip().upper()
                            if registro == "E":
                                tipo_registro = "entrada"
                                hora_atual = datetime.now().strftime(
                                    "%H:%M"
                                )  # Formata apenas hora e minuto
                                c.execute(
                                    "INSERT INTO registros_entrada_saida (reg_tipo, reg_id_usuario, reg_tipo_usuario, reg_n_apartamento, reg_bl_apartamento, reg_data, reg_hora) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (
                                        tipo_registro,
                                        mor_id,
                                        "morador",
                                        mor_n_apartamento,
                                        mor_bl_apartamento,
                                        str(datetime.now().date()),
                                        hora_atual,
                                    ),
                                )
                                conn.commit()
                                print("Entrada registrada com sucesso!")
                                time.sleep(2)
                                menu_principal()

                            elif registro == "S":
                                tipo_registro = "saida"
                                hora_atual = datetime.now().strftime(
                                    "%H:%M"
                                )  # Formata apenas hora e minuto
                                c.execute(
                                    "INSERT INTO registros_entrada_saida (reg_tipo, reg_id_usuario, reg_tipo_usuario, reg_n_apartamento, reg_bl_apartamento, reg_data, reg_hora) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (
                                        tipo_registro,
                                        mor_id,
                                        "morador",
                                        mor_n_apartamento,
                                        mor_bl_apartamento,
                                        str(datetime.now().date()),
                                        hora_atual,
                                    ),
                                )
                                conn.commit()
                                print("Saída registrada com sucesso!")
                                time.sleep(2)
                                menu_principal()

                            elif registro == "":
                                print("Registro Cancelado.")
                                time.sleep(2)
                                menu_principal()

                            else:
                                print(
                                    f"Nome: {mor_nome} Apto: {mor_n_apartamento} Bloco: {mor_bl_apartamento}"
                                )
                                opcao_invalida()
                                continue

                    else:
                        print(
                            "Opção inválida! Por favor, escolha um número válido da lista de moradores."
                        )
                        time.sleep(2)
                        limpar_terminal()
                        for i, morador in enumerate(moradores, start=1):
                            mor_nome, mor_n_apartamento, mor_bl_apartamento, mor_id = (
                                morador
                            )
                            print(
                                f"{i}. {mor_nome} Apto: {mor_n_apartamento} Bloco: {mor_bl_apartamento}"
                            )

                except ValueError:
                    print("Entrada inválida! Digite apenas números.")
                    time.sleep(2)
                    continue  # Continua o loop se o usuário inserir algo não numérico

        elif escolha == "3":
            menu_principal()

        else:
            opcao_invalida()
            continue


#!!!!!!!!!!!!!!#
# endregion


# region erros
#!!!!!!!!!!!!!!!!!#


###################################################################################################################################
def opcao_invalida():
    limpar_terminal()
    print("Opção inválida, por favor tente novamente #=--#")
    time.sleep(0.5)
    limpar_terminal()
    print("Opção inválida, por favor tente novamente #==-#")
    time.sleep(0.5)
    limpar_terminal()
    print("Opção inválida, por favor tente novamente #===#")
    time.sleep(0.5)
    limpar_terminal()


###################################################################################################################################
def erro_de_integridade():
    limpar_terminal()
    print("Erro: CPF ou RG já cadastrado. #---#")
    time.sleep(0.4)
    limpar_terminal()
    print("Erro: CPF ou RG já cadastrado. #=--#")
    time.sleep(0.4)
    limpar_terminal()
    print("Erro: CPF ou RG já cadastrado. #==-#")
    time.sleep(0.4)
    limpar_terminal()
    print("Erro: CPF ou RG já cadastrado. #===#")
    time.sleep(0.4)
    limpar_terminal()


#!!!!!!!!!!!!!!!!!#
# endregion


# region Inserções
####################################################################################################################################
def inserir_nome_ou_cpf():
    termo = input("Digite o nome ou CPF: ").strip()
    termo_like = f"%{termo}%"

    query = """
        SELECT 'morador' AS tipo, id_morador AS id, mor_nome AS nome, mor_cpf AS cpf
        FROM moradores
        WHERE mor_nome LIKE ? OR mor_cpf = ?

        UNION ALL

        SELECT 'funcionario', id_funcionario, fun_nome, fun_cpf
        FROM funcionarios
        WHERE fun_nome LIKE ? OR fun_cpf = ?

        UNION ALL

        SELECT 'visitante', id_visitantes, vis_nome, vis_cpf
        FROM visitantes
        WHERE vis_nome LIKE ? OR vis_cpf = ?

        UNION ALL

        SELECT 'prestador_servicos', id_prestador_servicos, pre_nome, pre_cpf
        FROM prestadores_servicos
        WHERE pre_nome LIKE ? OR pre_cpf = ?

        UNION ALL

        SELECT 'entregador', id_entregador, ent_nome, ent_cpf
        FROM entregadores
        WHERE ent_nome LIKE ? OR ent_cpf = ?
    """

    params = [termo_like, termo] * 5
    c.execute(query, params)
    usuarios = c.fetchall()

    if not usuarios:
        print("Nenhum usuário encontrado.")
        opcao = input("Deseja cadastrar um novo morador? (S/N): ").strip().upper()
        if opcao == "S":
            cadastrar_morador()
        else:
            menu_principal()
        return

    limpar_terminal()
    while True:
        try:
            print("\nLista de usuários encontrados:")
            for i, (tipo, id_usuario, nome, cpf) in enumerate(usuarios, start=1):
                print(f"{i}. [{tipo}] {nome} (CPF: {cpf})")
            return
        except ValueError:
            print("Por favor, digite um número válido.")
        except Exception as e:
            print(f"\nOcorreu um erro inesperado: {e}")


####################################################################################################
def registrar_a_entrada_e_saida():
    termo = input("Digite o nome ou CPF: ").strip()
    termo_like = f"%{termo}%"

    query = """
        SELECT 'morador' AS tipo, id_morador AS id, mor_nome AS nome, mor_cpf AS cpf
        FROM moradores
        WHERE mor_nome LIKE ? OR mor_cpf = ?

        UNION ALL

        SELECT 'funcionario', id_funcionario, fun_nome, fun_cpf
        FROM funcionarios
        WHERE fun_nome LIKE ? OR fun_cpf = ?

        UNION ALL

        SELECT 'visitante', id_visitantes, vis_nome, vis_cpf
        FROM visitantes
        WHERE vis_nome LIKE ? OR vis_cpf = ?

        UNION ALL

        SELECT 'prestador_servicos', id_prestador_servicos, pre_nome, pre_cpf
        FROM prestadores_servicos
        WHERE pre_nome LIKE ? OR pre_cpf = ?

        UNION ALL

        SELECT 'entregador', id_entregador, ent_nome, ent_cpf
        FROM entregadores
        WHERE ent_nome LIKE ? OR ent_cpf = ?
    """

    params = [termo_like, termo] * 5
    c.execute(query, params)
    usuarios = c.fetchall()

    if not usuarios:
        print("Nenhum usuário encontrado.")
        opcao = input("Deseja cadastrar um novo morador? (S/N): ").strip().upper()
        if opcao == "S":
            cadastrar_morador()
        else:
            menu_principal()
        return

    limpar_terminal()
    while True:
        try:
            print("\nLista de usuários encontrados:")
            for i, (tipo, id_usuario, nome, cpf) in enumerate(usuarios, start=1):
                print(f"{i}. [{tipo}] {nome} (CPF: {cpf})")
            escolha = int(
                input(
                    "\nDigite o número do usuário que deseja selecionar (ou 0 para voltar): "
                )
            )

            if escolha == 0:
                print("Saindo do menu.")
                return

            if 1 <= escolha <= len(usuarios):
                tipo, id_usuario, nome, cpf = usuarios[escolha - 1]

                while True:
                    limpar_terminal()
                    print(f"\nVocê escolheu: [{tipo}] {nome} (ID: {id_usuario})")
                    registro = (
                        input("Gostaria de registrar a entrada ou saída? (E/S): ")
                        .strip()
                        .upper()
                    )

                    if registro not in ["E", "S"]:
                        print(
                            "Opção inválida! Digite 'E' para entrada ou 'S' para saída."
                        )
                        continue

                    data = datetime.now().strftime("%d/%m/%Y")
                    hora_atual = datetime.now().strftime("%H:%M")
                    reg_morador_responsavel = None
                    reg_n_apartamento = None
                    reg_bl_apartamento = None

                    if tipo == "morador":
                        # Se for morador, buscamos o apartamento e bloco dele
                        c.execute(
                            "SELECT mor_n_apartamento, mor_bl_apartamento FROM moradores WHERE id_morador = ?",
                            (id_usuario,),
                        )
                        reg_n_apartamento, reg_bl_apartamento = c.fetchone()

                    elif registro == "E":
                        # Se não for morador e for registro de entrada,
                        # perguntamos qual o morador responsável
                        while True:
                            c.execute(
                                "SELECT id_morador, mor_nome, mor_n_apartamento, mor_bl_apartamento FROM moradores"
                            )
                            moradores = c.fetchall()
                            limpar_terminal()
                            print("\nLista de moradores disponíveis:")
                            print("0. Condomínio (Caso seja para o condomínio)")
                            for i, (
                                id_morador,
                                nome_morador,
                                n_apartamento,
                                bl_apartamento,
                            ) in enumerate(moradores, start=1):
                                print(
                                    f"{i}. {nome_morador} (Apartamento: {n_apartamento}, Bloco: {bl_apartamento}, ID: {id_morador})"
                                )

                            try:
                                escolha_morador = int(
                                    input("\nSelecione o Morador Responsável: ")
                                )
                                if escolha_morador == 0:
                                    reg_morador_responsavel = "condomínio"
                                    reg_n_apartamento = None
                                    reg_bl_apartamento = None
                                    break
                                elif 1 <= escolha_morador <= len(moradores):
                                    # Correção: os índices 2 e 3 correspondem ao número do apartamento e bloco, respectivamente.
                                    reg_morador_responsavel = moradores[
                                        escolha_morador - 1
                                    ][0]
                                    reg_n_apartamento = moradores[escolha_morador - 1][
                                        2
                                    ]
                                    reg_bl_apartamento = moradores[escolha_morador - 1][
                                        3
                                    ]
                                    break
                                else:
                                    print("Opção inválida. Tente novamente.")
                            except ValueError:
                                print("Por favor, digite um número válido.")

                    c.execute(
                        """INSERT INTO registros_entrada_saida 
                        (reg_tipo, reg_id_usuario, reg_tipo_usuario, reg_id_morador_responsavel, reg_n_apartamento, reg_bl_apartamento, reg_data, reg_hora)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            "entrada" if registro == "E" else "saida",
                            id_usuario,
                            tipo,
                            reg_morador_responsavel,  # Aqui usamos o ID correto do morador responsável
                            reg_n_apartamento,
                            reg_bl_apartamento,
                            str(datetime.now().date()),
                            hora_atual,
                        ),
                    )

                    conn.commit()
                    print(
                        f"{'Entrada' if registro == 'E' else 'Saída'} registrada para {nome} ({tipo}) em {data} às {hora_atual}."
                    )
                    time.sleep(2)
                    menu_principal()
                    break
            else:
                print("Opção inválida! Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")
        except Exception as e:
            print(f"\nOcorreu um erro inesperado: {e}")


####################################################################################################################################
def inserir_nome():
    while True:
        nome = input("Nome e Sobrenome: ").strip()
        if nome == "":  # Se o usuário pressionar Enter sem digitar nada
            print("Cadastro cancelado.")
            time.sleep(2)
            menu_principal()
            return None
        partes_nome = nome.split()  # Divide o nome em partes
        if len(partes_nome) < 2:  # Verifica se há pelo menos duas palavras
            print("Nome inválido! Digite o nome e o sobrenome.")
            time.sleep(2)
        else:
            return nome  # Retorna o nome válido


###################################################################################################################################
def inserir_cpf():
    while True:
        cpf = input("CPF: ")
        if cpf == "":
            print("Cadastro cancelado.")
            time.sleep(2)
            menu_principal()
            return None
        elif not validar_cpf(cpf):
            print("CPF inválido. Tente novamente.")
            time.sleep(2)
        else:
            return cpf


###################################################################################################################################
def inserir_rg():
    while True:
        rg = input("RG: ")
        if rg == "":
            print("Cadastro cancelado.")
            time.sleep(2)
            menu_principal()
            return None
        elif not validar_rg(rg):
            print("RG inválido. Tente novamente.")
            time.sleep(2)
        else:
            return rg


###################################################################################################################################
def inserir_telefone():
    while True:
        telefone = input("Telefone (com DDD): ").strip()
        if telefone == "":  # Se estiver em branco, cancela
            print("Cadastro cancelado.")
            time.sleep(2)
            menu_principal()
            return None
        # Remove caracteres não numéricos (ex: espaços, parênteses, traços)
        telefone_limpo = limpar_formatacao(telefone)
        # Valida se tem 10 ou 11 dígitos (fixo ou celular)
        if not re.match(r"^\d{10,11}$", telefone_limpo):
            print("Telefone inválido. Tente novamente.")
            time.sleep(2)
        else:
            return telefone_limpo  # Retorna o número sem formatação


###################################################################################################################################
def inserir_apartamento():
    while True:
        try:
            n_apartamento = input("Número do apartamento: ").strip()
            if n_apartamento == "":
                print("Consulta cancelada.")
                time.sleep(2)
                menu_principal()
                return None
            n_apartamento = int(n_apartamento)
            if n_apartamento <= 0:
                print("Número do apartamento inválido. Tente novamente.")
                time.sleep(2)
            else:
                return n_apartamento
        except ValueError:
            print("Entrada inválida! Digite apenas números.")
            time.sleep(2)


###################################################################################################################################
def inserir_bloco():
    while True:
        bl_apartamento = input("Bloco do apartamento: ").upper()
        if bl_apartamento == "":
            print("Consulta cancelada.")
            time.sleep(2)
            menu_principal()
            return None
        elif not bl_apartamento.isalpha():
            print("Bloco inválido. Tente novamente.")
            time.sleep(2)
        elif len(bl_apartamento) > 1:
            print("Bloco inválido. Deve conter apenas uma letra.")
            time.sleep(2)
        else:
            return bl_apartamento


###################################################################################################################################
def inserir_proprietario():
    while True:
        proprietario = input("Proprietário (S/N): ").upper()
        if proprietario == "":
            print("Cadastro cancelado.")
            time.sleep(2)
            menu_principal()
            return None
        elif proprietario not in ["S", "N"]:
            print("Opção inválida. Tente novamente.")
            time.sleep(2)
        else:
            return proprietario


###################################################################################################################################
def inserir_garagem():
    while True:
        try:
            n_garagem = input("Número da garagem (ou 0 para deixar nulo): ").strip()
            if n_garagem == "":
                print("Cadastro cancelado.")
                time.sleep(2)
                menu_principal()
                return None
            n_garagem = int(n_garagem)
            if n_garagem == 0:
                return None
            elif n_garagem < 0:
                print("Número da garagem inválido. Tente novamente.")
                time.sleep(2)
            else:
                return n_garagem
        except ValueError:
            print("Entrada inválida! Digite apenas números.")
            time.sleep(2)


# endregion


# region Cadastros


def cadastrar_morador():

    limpar_terminal()
    print("== Cadastro Morador ==")
    print(
        "Por Favor, preencha os dados a seguir (ou deixe em branco para cancelar, e pressione a tecla Enter):"
    )
    nome = inserir_nome()
    cpf = inserir_cpf()
    rg = inserir_rg()
    telefone = inserir_telefone()
    n_apartamento = inserir_apartamento()
    bl_apartamento = inserir_bloco()
    proprietario = inserir_proprietario()
    n_garagem = inserir_garagem()
    limpar_terminal()

    print(
        f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nRG: {formatar_rg(rg)} \nTelefone: {formatar_telefone(telefone)}  \nNúmero do apartamento: {n_apartamento} \nBloco do apartamento: {bl_apartamento} \nProprietário (S/N): {proprietario} \nNúmero da garagem: {n_garagem}"
    )
    try:
        while True:
            confirmar = input("Confirma os dados? (S/N): ").upper()
            if confirmar.lower() == "s":
                c.execute(
                    """INSERT INTO moradores (mor_nome, mor_cpf, mor_rg, mor_telefone, mor_n_apartamento, mor_bl_apartamento, mor_proprietario, mor_n_garagem) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        nome,
                        limpar_formatacao(cpf),
                        limpar_formatacao(rg),
                        telefone,
                        n_apartamento,
                        bl_apartamento,
                        proprietario,
                        n_garagem,
                    ),
                )
                conn.commit()
                print("Morador cadastrado com sucesso!")
                time.sleep(2)
                menu_principal()

            elif confirmar.lower() == "n":
                print("Cadastro cancelado.")
                time.sleep(2)
                menu_cadastro()

            else:
                opcao_invalida()
                limpar_terminal()
                print(
                    f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nRG: {formatar_rg(rg)} \nTelefone: {formatar_telefone(telefone)}  \nNúmero do apartamento: {n_apartamento} \nBloco do apartamento: {bl_apartamento} \nProprietário (S/N): {proprietario} \nNúmero da garagem: {n_garagem}"
                )

    except ValueError:
        opcao_invalida()
        menu_cadastro()

    except sqlite3.IntegrityError:
        erro_de_integridade()
        menu_cadastro()

    except sqlite3.OperationalError as e:
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #---#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #=--#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #==-#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #===#")
        time.sleep(0.4)
        limpar_terminal()
        menu_cadastro()


###################################################################################################################################
def cadastrar_visitante():
    limpar_terminal()
    print("== Cadastro Visitante ==")
    print(
        "Por Favor, preencha os dados a seguir (ou deixe em branco para cancelar, e pressione a tecla Enter):"
    )
    nome = inserir_nome()
    cpf = inserir_cpf()
    telefone = inserir_telefone()
    limpar_terminal()

    print(
        f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nTelefone: {formatar_telefone(telefone)}"
    )
    try:
        while True:
            confirmar = input("Confirma os dados? (S/N): ").upper()
            if confirmar.lower() == "s":
                c.execute(
                    """INSERT INTO visitantes (vis_nome, vis_cpf, vis_telefone) VALUES (?, ?, ?)""",
                    (nome, limpar_formatacao(cpf), telefone),
                )
                conn.commit()
                print("Visitante cadastrado com sucesso!")
                time.sleep(2)
                menu_principal()

            elif confirmar.lower() == "n":
                print("Cadastro cancelado.")
                time.sleep(2)
                menu_cadastro()

            else:
                opcao_invalida()
                limpar_terminal()
                print(
                    f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nTelefone: {formatar_telefone(telefone)}"
                )

    except ValueError:
        opcao_invalida()
        menu_cadastro()

    except sqlite3.IntegrityError:
        erro_de_integridade()
        menu_cadastro()

    except sqlite3.OperationalError as e:
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #---#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #=--#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #==-#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #===#")
        time.sleep(0.4)
        limpar_terminal()
        menu_cadastro()


###################################################################################################################################
def cadastrar_funcionario():

    limpar_terminal()
    print("== Cadastro Funcionário ==")
    print(
        "Por Favor, preencha os dados a seguir (ou deixe em branco para cancelar, e pressione a tecla Enter):"
    )
    nome = inserir_nome()
    cpf = inserir_cpf()
    rg = inserir_rg()
    telefone = inserir_telefone()
    limpar_terminal()

    print(
        f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nRG: {formatar_rg(rg)} \nTelefone: {formatar_telefone(telefone)}"
    )
    try:
        while True:
            confirmar = input("Confirma os dados? (S/N): ").upper()
            if confirmar.lower() == "s":
                c.execute(
                    """INSERT INTO funcionarios (fun_nome, fun_cpf, fun_rg, fun_telefone) VALUES (?, ?, ?, ?)""",
                    (nome, limpar_formatacao(cpf), limpar_formatacao(rg), telefone),
                )
                conn.commit()
                print("Funcionário cadastrado com sucesso!")
                time.sleep(2)
                menu_principal()

            elif confirmar.lower() == "n":
                print("Cadastro cancelado.")
                time.sleep(2)
                menu_cadastro()

            else:
                opcao_invalida()
                limpar_terminal()
                print(
                    f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nRG: {formatar_rg(rg)} \nTelefone: {formatar_telefone(telefone)}"
                )

    except ValueError:
        opcao_invalida()
        menu_cadastro()

    except sqlite3.IntegrityError:
        erro_de_integridade()
        menu_cadastro()

    except sqlite3.OperationalError as e:
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #---#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #=--#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #==-#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #===#")
        time.sleep(0.4)
        limpar_terminal()
        menu_cadastro()


###################################################################################################################################
def cadastrar_prestador():

    limpar_terminal()
    print("==Cadastro Prestador de Serviços==")
    print(
        "Por Favor, preencha os dados a seguir (ou deixe em branco para cancelar, e pressione a tecla Enter):"
    )
    nome = inserir_nome()
    cpf = inserir_cpf()
    rg = inserir_rg()
    telefone = inserir_telefone()
    limpar_terminal()

    print(
        f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nRG: {formatar_rg(rg)} \nTelefone: {formatar_telefone(telefone)}"
    )
    try:
        while True:
            confirmar = input("Confirma os dados? (S/N): ").upper()
            if confirmar.lower() == "s":
                c.execute(
                    """INSERT INTO prestadores_servicos (pre_nome, pre_cpf, pre_rg, pre_telefone) VALUES (?, ?, ?, ?)""",
                    (
                        nome,
                        limpar_formatacao(cpf),
                        limpar_formatacao(rg),
                        telefone,
                    ),
                )
                conn.commit()
                print("Prestador de serviços cadastrado com sucesso!")
                time.sleep(2)
                menu_principal()

            elif confirmar.lower() == "n":
                print("Cadastro cancelado.")
                time.sleep(2)
                menu_cadastro()

            else:
                opcao_invalida()
                limpar_terminal()
                print(
                    f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nRG: {formatar_rg(rg)} \nTelefone: {formatar_telefone(telefone)}"
                )

    except ValueError:
        opcao_invalida()
        menu_cadastro()

    except sqlite3.IntegrityError:
        erro_de_integridade()
        menu_cadastro()

    except sqlite3.OperationalError as e:
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #---#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #=--#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #==-#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #===#")
        time.sleep(0.4)
        limpar_terminal()
        menu_cadastro()


####################################################################################################################################
def cadastrar_entregador():

    limpar_terminal()
    print("== Cadastro Entregador ==")
    print(
        "Por Favor, preencha os dados a seguir (ou deixe em branco para cancelar, e pressione a tecla Enter):"
    )
    nome = inserir_nome()
    cpf = inserir_cpf()
    telefone = inserir_telefone()
    limpar_terminal()

    print(
        f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)} \nTelefone: {formatar_telefone(telefone)}"
    )
    try:
        while True:
            confirmar = input("Confirma os dados? (S/N): ").upper()
            if confirmar.lower() == "s":
                c.execute(
                    """INSERT INTO entregadores (ent_nome, ent_cpf, ent_telefone) VALUES (?, ?, ?)""",
                    (nome, limpar_formatacao(cpf), telefone),
                )
                conn.commit()
                print("Entregador cadastrado com sucesso!")
                time.sleep(2)
                menu_principal()

            elif confirmar.lower() == "n":
                print("Cadastro cancelado.")
                time.sleep(2)
                menu_cadastro()

            else:
                opcao_invalida()
                limpar_terminal()
                print(
                    f"=== Confirmando os dados === \nNome: {nome} \nCPF: {formatar_cpf(cpf)}\nTelefone: {formatar_telefone(telefone)}"
                )

    except ValueError:
        opcao_invalida()
        menu_cadastro()

    except sqlite3.IntegrityError:
        erro_de_integridade()
        menu_cadastro()

    except sqlite3.OperationalError as e:
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #---#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #=--#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #==-#")
        time.sleep(0.4)
        limpar_terminal()
        print(f"Erro no banco de dados: {e} #===#")
        time.sleep(0.4)
        limpar_terminal()
        menu_cadastro()


#!!!!!!!!!!!!!!!#
# endregion


# region Consultas


###################################################################################################################################
def consul_mor():
    limpar_terminal()
    print("=== Consultar Moradores ===")
    print(
        "\n --- Gostaria de buscar um morador em especifico ou varios moradores? \n 1 - Buscar uma pessoa em especifico \n 2 - Buscar por Bloco e Apartamento \n 3 - Sair"
    )

    escolha_consul_mor = int(input(f"\n Qual voce escolhe?: "))
    try:

        if escolha_consul_mor == 1:
            consul_mor = input("Digite o nome ou CPF: ").strip()
            consul_like = f"%{consul_mor}%"

            query = """
                SELECT id_morador, mor_nome, mor_telefone, mor_n_apartamento, mor_bl_apartamento, mor_proprietario, mor_n_garagem 
                FROM moradores
                WHERE mor_nome LIKE ? OR mor_cpf = ?
            """

            params = [consul_like, consul_mor]  # Passa apenas dois parâmetros
            c.execute(query, params)
            usuarios = c.fetchall()

            if not usuarios:
                print("Nenhum usuário encontrado.")
                time.sleep(2)
                menu_principal()

            # Adicione lógica de exibição dos resultados se necessário
            for usuario in usuarios:
                print(
                    f"Nome: {usuario[1]} | Telefone: {usuario[2]} | Apartamento: {usuario[3]} | Bloco: {usuario[4]} | Proprietário: {usuario[5]} | Garagem: {usuario[6]} | (ID: {usuario[0]})"
                )
            print()

            escolha_consul_mor = input("deseja voltar para o menu de consultas? s/n\n")
            if escolha_consul_mor == "s":
                animacao()
                consultar_registros()
            elif escolha_consul_mor == "n":
                animacao()
                menu_principal()
            else:
                opcao_invalida()

        elif escolha_consul_mor == 2:
            bloco_mor = input("Digite o Bloco : ").strip()
            apartamento_mor = input("Digite o Apartamento: ").strip()

            query = """
                SELECT id_morador, mor_nome, mor_telefone, mor_n_apartamento, mor_bl_apartamento, mor_proprietario, mor_n_garagem
                FROM moradores 
                WHERE mor_n_apartamento = ? AND mor_bl_apartamento = ?
                """

            params = [apartamento_mor, bloco_mor]
            c.execute(query, params)
            usuarios = c.fetchall()

            if not usuarios:
                print("Nenhum morador encontrado.")
                time.sleep(2)
                menu_principal()

            for usuario in usuarios:
                print(
                    f"Nome: {usuario[1]} | Telefone: {usuario[2]} | Apartamento: {usuario[3]} | Bloco: {usuario[4]} | Proprietário: {usuario[5]} | Garagem: {usuario[6]} | (ID: {usuario[0]})"
                )

            print()
            escolha_consul_mor = input("deseja voltar para o menu de consultas? s/n\n")
            if escolha_consul_mor == "s":
                animacao()
                consultar_registros()
            elif escolha_consul_mor == "n":
                animacao()
                menu_principal()
            else:
                opcao_invalida()

        elif escolha_consul_mor == 3:
            animacao()
            menu_principal()
        else:
            opcao_invalida()
            consul_mor()
    except ValueError:
        opcao_invalida()


###################################################################################################################################


###################################################################################################################################
def consul_por_nome():
    limpar_terminal()
    print("=== Consulta de Entradas e Saídas por Nome ===")
    nome = input("Digite o nome da pessoa: ").strip()
    nome_like = f"%{nome}%"

    query = """
    SELECT * FROM (
        SELECT 
            r.reg_tipo,
            r.reg_tipo_usuario,
            r.reg_data,
            r.reg_hora,
            r.reg_n_apartamento,
            r.reg_bl_apartamento,
            r.reg_id_usuario,
            r.reg_id_morador_responsavel,
            CASE 
                WHEN r.reg_tipo_usuario = 'morador' THEN 
                    (SELECT mor_nome FROM moradores WHERE id_morador = r.reg_id_usuario AND mor_nome LIKE ?)
                WHEN r.reg_tipo_usuario = 'funcionario' THEN 
                    (SELECT fun_nome FROM funcionarios WHERE id_funcionario = r.reg_id_usuario AND fun_nome LIKE ?)
                WHEN r.reg_tipo_usuario = 'visitante' THEN 
                    (SELECT vis_nome FROM visitantes WHERE id_visitantes = r.reg_id_usuario AND vis_nome LIKE ?)
                WHEN r.reg_tipo_usuario = 'prestador_servicos' THEN 
                    (SELECT pre_nome FROM prestadores_servicos WHERE id_prestador_servicos = r.reg_id_usuario AND pre_nome LIKE ?)
                WHEN r.reg_tipo_usuario = 'entregador' THEN 
                    (SELECT ent_nome FROM entregadores WHERE id_entregador = r.reg_id_usuario AND ent_nome LIKE ?)
                ELSE NULL
            END AS nome_usuario,
            (SELECT mor_nome FROM moradores WHERE id_morador = r.reg_id_morador_responsavel) AS nome_responsavel
        FROM registros_entrada_saida r
    ) sub
    WHERE nome_usuario IS NOT NULL
    ORDER BY reg_data DESC, reg_hora DESC
    """

    params = [nome_like] * 5
    c.execute(query, params)
    registros = c.fetchall()

    if registros:
        limpar_terminal()
        print("\n=== Registros Encontrados ===\n")
        for (
            reg_tipo,
            tipo_usuario,
            data,
            hora,
            apto,
            bloco,
            id_usuario,
            id_responsavel,
            nome_usuario,
            nome_responsavel,
        ) in registros:
            print(f"{reg_tipo.upper()} | {tipo_usuario.capitalize()}: {nome_usuario}")
            print(f"Data: {data} | Hora: {hora}")
            if apto or bloco:
                print(f"Apartamento: {apto or '---'} | Bloco: {bloco or '---'}")
            if nome_responsavel:
                print(f"Responsável: {nome_responsavel}")
            print("-" * 50)
    else:
        limpar_terminal()
        print("Nenhum registro encontrado para esse nome.")

    input("\nPressione Enter para voltar ao menu de consulta...")
    consul_entrada_saida()


###################################################################################################################################
def consul_por_data():
    limpar_terminal()
    print("=== Consulta de Entradas e Saídas por Data ===")
    data_input = input("Digite a data (DDMMAAAA): ").strip()

    try:
        data_convertida = datetime.strptime(data_input, "%d%m%Y").date()
    except ValueError:
        print("Data inválida. Por favor, use o formato DDMMAAAA.")
        time.sleep(2)
        return consul_por_data()

    query = """
        SELECT 
            r.reg_tipo,
            r.reg_tipo_usuario,
            r.reg_data,
            r.reg_hora,
            r.reg_n_apartamento,
            r.reg_bl_apartamento,
            r.reg_id_usuario,
            r.reg_id_morador_responsavel,
            CASE 
                WHEN r.reg_tipo_usuario = 'morador' THEN (SELECT mor_nome FROM moradores WHERE id_morador = r.reg_id_usuario)
                WHEN r.reg_tipo_usuario = 'funcionario' THEN (SELECT fun_nome FROM funcionarios WHERE id_funcionario = r.reg_id_usuario)
                WHEN r.reg_tipo_usuario = 'visitante' THEN (SELECT vis_nome FROM visitantes WHERE id_visitantes = r.reg_id_usuario)
                WHEN r.reg_tipo_usuario = 'prestador_servicos' THEN (SELECT pre_nome FROM prestadores_servicos WHERE id_prestador_servicos = r.reg_id_usuario)
                WHEN r.reg_tipo_usuario = 'entregador' THEN (SELECT ent_nome FROM entregadores WHERE id_entregador = r.reg_id_usuario)
                ELSE NULL
            END AS nome_usuario,
            (SELECT mor_nome FROM moradores WHERE id_morador = r.reg_id_morador_responsavel) AS nome_responsavel
        FROM registros_entrada_saida r
        WHERE r.reg_data = ?
        ORDER BY r.reg_data DESC, r.reg_hora DESC
    """

    c.execute(query, (str(data_convertida),))
    registros = c.fetchall()

    if registros:
        limpar_terminal()
        print("\n=== Registros Encontrados ===\n")
        for (
            tipo,
            tipo_usuario,
            data,
            hora,
            apto,
            bloco,
            id_usuario,
            id_responsavel,
            nome_usuario,
            nome_responsavel,
        ) in registros:
            print(f"{tipo.upper()} | {tipo_usuario.capitalize()}: {nome_usuario}")
            print(f"Data: {data} | Hora: {hora}")
            if apto or bloco:
                print(f"Apartamento: {apto or '---'} | Bloco: {bloco or '---'}")
            if nome_responsavel:
                print(f"Morador responsável: {nome_responsavel}")
            print("-" * 50)
    else:
        limpar_terminal()
        print("Nenhum registro encontrado para essa data.")

    input("\nPressione Enter para voltar ao menu de consulta...")
    consul_entrada_saida()


###################################################################################################################################
def consul_entrada_saida():
    limpar_terminal()
    print("=== Consulta de Entradas e Saídas ===")
    print("Por favor, selecione o critério de consulta:")
    print("1 - Data \n2 - Pessoa\n3 <-- Voltar")
    try:
        escolha = int(input("Opção: "))
        if escolha == 1:
            consul_por_data()
        elif escolha == 2:
            consul_por_nome()
        elif escolha == 3:
            consultar_registros()
    except ValueError:
        opcao_invalida()


###################################################################################################################################
def consultar_registros():
    limpar_terminal()
    print("=== Menu de Consulta de Registros ===")
    print(
        " --- olá que tipo de registro você gostaria de consultar? \n 1 - Moradores \n 2 - Visitantes (Em Desenvolvimento) \n 3 - Funcionários (Em Desenvolvimento) \n 4 - Prestadores de Serviços (Em Desenvolvimento) \n 5 - Entregadores (Em Desenvolvimento) \n 6 - Entradas e Saídas \n 7 - Sair"
    )
    try:
        escolhaCR = int(input("Opção (Apenas Números): "))
        if escolhaCR == 1:
            consul_mor()
        elif escolhaCR == 2:
            em_desenvolvimento()
            consultar_registros()
        elif escolhaCR == 3:
            em_desenvolvimento()
            consultar_registros()
        elif escolhaCR == 4:
            em_desenvolvimento()
            consultar_registros()
        elif escolhaCR == 5:
            em_desenvolvimento()
            consultar_registros()
        elif escolhaCR == 6:
            consul_entrada_saida()
        elif escolhaCR == 7:
            menu_principal()
        else:
            opcao_invalida()
    except ValueError:
        opcao_invalida()


###################################################################################################################################
def consul_placa_veiculo():
    limpar_terminal()
    print("=== Consulta de Veículo por Placa ===")
    placa = (
        input("Digite a placa do veículo (apenas letras e números): ").strip().upper()
    )

    if not validar_placa(placa):
        print("Placa inválida, por favor tente novamente.")
        time.sleep(2)
        return

    query = """
        SELECT 
            v.vei_placa,
            v.vei_tipo,
            v.vei_fabricante,
            v.vei_modelo,
            v.vei_cor,
            v.vei_ano,
            v.vei_tipo_usuario,
            COALESCE(m.mor_nome, f.fun_nome, p.pre_nome, e.ent_nome) AS nome_condutor,
            COALESCE(m.mor_cpf, f.fun_cpf, p.pre_cpf, e.ent_cpf) AS cpf_condutor,
            COALESCE(m.mor_telefone, f.fun_telefone, p.pre_telefone, e.ent_telefone) AS telefone_condutor
        FROM veiculos v
        LEFT JOIN moradores m ON v.vei_tipo_usuario = 'morador' AND v.vei_id_usuario = m.id_morador
        LEFT JOIN funcionarios f ON v.vei_tipo_usuario = 'funcionario' AND v.vei_id_usuario = f.id_funcionario
        LEFT JOIN prestadores_servicos p ON v.vei_tipo_usuario = 'prestador_servicos' AND v.vei_id_usuario = p.id_prestador_servicos
        LEFT JOIN entregadores e ON v.vei_tipo_usuario = 'entregador' AND v.vei_id_usuario = e.id_entregador
        WHERE v.vei_placa = ?
    """

    c.execute(query, (formatar_placa(placa),))
    veiculo = c.fetchone()

    if veiculo:
        limpar_terminal()
        print("=== Veículo Encontrado ===\n")
        print(f"Placa: {veiculo[0]}")
        print(f"Tipo: {veiculo[1]}")
        print(f"Fabricante: {veiculo[2]}")
        print(f"Modelo: {veiculo[3]}")
        print(f"Cor: {veiculo[4]}")
        print(f"Ano: {veiculo[5]}")
        print(f"Tipo de Condutor: {veiculo[6]}")
        print(f"Nome do Condutor: {veiculo[7]}")
        print(f"CPF do Condutor: {formatar_cpf(veiculo[8])}")
        print(f"Telefone do Condutor: {formatar_telefone(veiculo[9])}")
        input("Pressione Enter para voltar ao menu de consulta: ")
        consul_veiculo()
    else:
        print("Nenhum veículo encontrado com essa placa.")

    time.sleep(3)
    consul_veiculo()


###################################################################################################################################
def consul_proprietario_veiculo():
    limpar_terminal()
    print("=== Consulta de Veículo por Proprietário ===")
    termo = input("Digite o nome ou CPF do proprietário: ").strip()
    termo_like = f"%{termo}%"

    query = """
        SELECT v.vei_placa, v.vei_tipo, v.vei_fabricante, v.vei_modelo, v.vei_cor, v.vei_ano,
               u.tipo, u.nome, u.cpf, u.telefone
        FROM veiculos v
        JOIN (
            SELECT 'morador' AS tipo, id_morador AS id, mor_nome AS nome, mor_cpf AS cpf, mor_telefone AS telefone
            FROM moradores
            WHERE mor_nome LIKE ? OR mor_cpf = ?

            UNION ALL

            SELECT 'funcionario', id_funcionario, fun_nome, fun_cpf, fun_telefone
            FROM funcionarios
            WHERE fun_nome LIKE ? OR fun_cpf = ?

            UNION ALL

            SELECT 'visitante', id_visitantes, vis_nome, vis_cpf, vis_telefone
            FROM visitantes
            WHERE vis_nome LIKE ? OR vis_cpf = ?

            UNION ALL

            SELECT 'prestador_servicos', id_prestador_servicos, pre_nome, pre_cpf, pre_telefone
            FROM prestadores_servicos
            WHERE pre_nome LIKE ? OR pre_cpf = ?

            UNION ALL

            SELECT 'entregador', id_entregador, ent_nome, ent_cpf, ent_telefone
            FROM entregadores
            WHERE ent_nome LIKE ? OR ent_cpf = ?
        ) u ON u.id = v.vei_id_usuario AND u.tipo = v.vei_tipo_usuario
    """

    params = [termo_like, termo] * 5
    c.execute(query, params)
    veiculos = c.fetchall()

    if not veiculos:
        print("Nenhum veículo encontrado para esse proprietário.")
        time.sleep(3)
        return consul_veiculo()

    index = 0
    while True:
        limpar_terminal()
        veiculo = veiculos[index]
        print("=== Veículo Encontrado ===\n")
        print(f"Placa: {veiculo[0]}")
        print(f"Tipo: {veiculo[1]}")
        print(f"Fabricante: {veiculo[2]}")
        print(f"Modelo: {veiculo[3]}")
        print(f"Cor: {veiculo[4]}")
        print(f"Ano: {veiculo[5] if veiculo[5] else 'Não informado'}")
        print(f"Tipo de Condutor: {veiculo[6]}")
        print(f"Nome do Condutor: {veiculo[7]}")
        print(f"CPF do Condutor: {formatar_cpf(veiculo[8])}")
        print(f"Telefone do Condutor: {formatar_telefone(veiculo[9])}")

        print("\n[N] Próximo | [A] Anterior | [S] Sair para o menu de consulta")
        opcao = input("Escolha uma opção: ").strip().lower()

        if opcao == "n":
            if index < len(veiculos) - 1:
                index += 1
            else:
                limpar_terminal()
                print("\nVocê já está no último veículo.")
                time.sleep(1.5)
        elif opcao == "a":
            if index > 0:
                index -= 1
            else:
                limpar_terminal()
                print("\nVocê já está no primeiro veículo.")
                time.sleep(1.5)
        elif opcao == "s":
            break
        else:
            opcao_invalida()

    consul_veiculo()


###################################################################################################################################
def consul_veiculo():
    limpar_terminal()
    print("=== Consultar Veículos ===")
    print("Selecione o Critério de Busca")
    print("1 - Placa \n2 - Proprietário \n3 - Sair \n")
    try:
        opcao = int(input("Opção: "))
        if opcao == 1:
            consul_placa_veiculo()
        elif opcao == 2:
            consul_proprietario_veiculo()
        elif opcao == 3:
            menu_principal()
        else:
            opcao_invalida()
            consul_veiculo()
    except ValueError:
        opcao_invalida()
        consul_veiculo()


# endregion


###################################################################################################################################
def registrar_veiculo():
    limpar_terminal()
    print("Por favor Selecione o Condutor para cadastro")
    termo = input("Digite o nome ou CPF: ").strip()
    termo_like = f"%{termo}%"

    query = """
        SELECT 'morador' AS tipo, id_morador AS id, mor_nome AS nome, mor_cpf AS cpf
        FROM moradores
        WHERE mor_nome LIKE ? OR mor_cpf = ?

        UNION ALL

        SELECT 'funcionario', id_funcionario, fun_nome, fun_cpf
        FROM funcionarios
        WHERE fun_nome LIKE ? OR fun_cpf = ?

        UNION ALL

        SELECT 'visitante', id_visitantes, vis_nome, vis_cpf
        FROM visitantes
        WHERE vis_nome LIKE ? OR vis_cpf = ?

        UNION ALL

        SELECT 'prestador_servicos', id_prestador_servicos, pre_nome, pre_cpf
        FROM prestadores_servicos
        WHERE pre_nome LIKE ? OR pre_cpf = ?

        UNION ALL

        SELECT 'entregador', id_entregador, ent_nome, ent_cpf
        FROM entregadores
        WHERE ent_nome LIKE ? OR ent_cpf = ?
    """

    params = [termo_like, termo] * 5
    c.execute(query, params)
    usuarios = c.fetchall()

    if not usuarios:
        print("Nenhum usuário encontrado, por favor tente novamente.")
        time.sleep(2)
        return

    while True:
        try:
            print("\nLista de usuários encontrados:")
            for i, (tipo, id_usuario, nome, cpf) in enumerate(usuarios, start=1):
                print(f"{i}. [{tipo}] {nome} (CPF: {cpf})")
            escolha = int(
                input(
                    "\nDigite o número do usuário que deseja selecionar (ou 0 para voltar): "
                )
            )

            if escolha == 0:
                print("Saindo do menu.")
                return

            if 1 <= escolha <= len(usuarios):
                tipo, id_usuario, nome, cpf = usuarios[escolha - 1]

                while True:
                    limpar_terminal()
                    print(f"\nVocê escolheu: [{tipo}] {nome} (ID: {id_usuario})")
                    print("Por favor, preencha os dados do veículo:")
                    1
                    print(
                        "Selecione o Tipo do Veiculo? \n1 - Carro \n2 - Moto \n3 - Caminhão"
                    )
                    tipo_veiculo = int(input("Tipo do veículo: "))
                    if tipo_veiculo == 1:
                        tipo_veiculo = "carro"
                    elif tipo_veiculo == 2:
                        tipo_veiculo = "moto"
                    elif tipo_veiculo == 3:
                        tipo_veiculo = "caminhao"
                    else:
                        opcao_invalida()
                        continue

                    fabricante = input("Fabricante do veículo: ").strip().lower()
                    if fabricante == "":
                        print("Cadastro cancelado.")
                        time.sleep(2)
                        menu_de_veiculos()
                    modelo = input("Modelo do veículo: ").strip().lower()
                    if modelo == "":
                        print("Cadastro cancelado.")
                        time.sleep(2)
                        menu_de_veiculos()
                    cor = input("Cor do veículo: ").strip().lower()
                    if cor == "":
                        print("Cadastro cancelado.")
                        time.sleep(2)
                        menu_de_veiculos()
                    ano = int(
                        input("Ano do veículo (ou 0 e enter para não informar): ")
                    )
                    if ano < 0:
                        print("Cadastro cancelado.")
                        time.sleep(2)
                        menu_de_veiculos()
                    placa = input("Digite a placa do veículo: ")
                    if placa == "":
                        print("Cadastro cancelado.")
                        time.sleep(2)
                        menu_de_veiculos()
                    elif not validar_placa(placa):
                        print("Placa inválida, por favor tente novamente.")

                    while True:
                        print("== Conirmando os Dados ==")
                        print(f"Condutor: \n[{tipo}] {nome} (ID: {id_usuario})")
                        print(
                            f"Tipo do veículo: {tipo_veiculo} \nFabricante: {fabricante} \nModelo: {modelo} \nCor: {cor} \nAno: {ano} \nPlaca: {placa}"
                        )
                        confirmar = input("Confirma os dados? (S/N): ").upper()
                        if confirmar.lower() == "s":
                            c.execute(
                                """INSERT INTO veiculos (vei_id_usuario, vei_tipo_usuario, vei_tipo, vei_fabricante, vei_modelo, vei_cor, vei_placa, vei_ano) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (
                                    id_usuario,
                                    tipo,
                                    tipo_veiculo,
                                    fabricante,
                                    modelo,
                                    cor,
                                    formatar_placa(placa),
                                    ano if ano != 0 else None,
                                ),
                            )
                            conn.commit()
                            print("Veículo cadastrado com sucesso!")
                            time.sleep(2)
                            menu_principal()
                            break

                        elif confirmar.lower() == "n":
                            print("Cadastro cancelado.")
                            time.sleep(2)
                            menu_principal()
                            break

                        else:
                            opcao_invalida()

        except ValueError:
            opcao_invalida()
        else:
            opcao_invalida()


###################################################################################################################################
def menu_de_veiculos():
    limpar_terminal()
    print("=== Menu de Veículos===")
    print("1 - Registrar Veículo \n2 - Consultar Veículo \n3 - Sair")
    while True:
        try:
            opcao = int(input("Escolha uma opção: "))
            if opcao == 1:
                registrar_veiculo()
                pass
            elif opcao == 2:
                consul_veiculo()
                pass
            elif opcao == 3:
                menu_principal()
            else:
                opcao_invalida()
        except ValueError:
            opcao_invalida()


###################################################################################################################################


def main():
    menu_principal()


if __name__ == "__main__":
    main()
