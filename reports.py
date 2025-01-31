from flask import Flask, render_template, request, session, redirect, url_for, Response
from flask_session import Session # Utilizado para armazenamento de sessão, algumas consultas requerem mais espaço
import pandas as pd

app = Flask(__name__)
# Configurando Flask para armazenar sessões em arquivos
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './sessions'  # Diretório para armazenar arquivos de sessão
app.config['SESSION_USE_SIGNER'] = True # Criptografar dados

app.secret_key = "secret_key"

Session(app)

# Carregar o CSV
vendas_df = pd.read_csv('./reports/vendas-10_01_25.csv', encoding='utf-16', sep='\t')
ordem_servico_df = pd.read_csv('./reports/consulta-ordem-servico.csv', encoding='utf-16', sep='\t')
compras_10_01_2025_df = pd.read_csv('./reports/compras_10-01-2025.csv', encoding='utf-16', sep='\t')
compras_16_01_2025_df = pd.read_csv('./reports/relatorio_de_compras_16-01-2025.csv', encoding='utf-16', sep='\t')
num_serie_27_01_2025_df = pd.read_csv('./reports/num_de_serie_27_01_2025.csv', encoding='utf-16', sep='\t')

# Definindo as colunas de tipos específicos do vendas_df
campos_int_vendas = ['#', "Nº do documento", "ID interno do documento"]
campos_data_vendas = ['Data de lançamento', 'Data de vencimento', 'Linha da data de entrega']
campos_float_vendas = ['Preço após desconto', '% de desconto por linha', 'Total da linha', 'Total da linha (ME)']

# Definindo as colunas de tipos específicos do ordem_servico_df
campos_int_ordem_servico = ['#', 'Nº de série do fabricante', 'Nº do contrato', 'Nº do documento', 'Série']
campos_data_ordem_servico = ['Data final do contrato', 'Data de criação', 'Data de encerramento', 'Data de resolução', 'Data da resposta']

# Definindo as colunas de tipos específicos do compras_10_01_2025_df
campos_int_compras_10_01_2025 = ['#', 'Nº do documento', 'Nº do documento.1']
campos_float_compras_10_01_2025 = ['Quantidade', 'Preço']
campos_data_compras_10_01_2025 = ['Data de lançamento']

# Definindo as colunas de tipos específicos do compras_16_01_2025_df
campos_int_compras_16_01_2025 = ['Nº do documento']
campos_float_compras_16_01_2025 = ['Quantidade', 'Preço', 'Total da linha']
campos_data_compras_16_01_2025 = ['Data de lançamento', 'Data de vencimento', 'Linha da data de entrega']

# Definindo as colunas de tipos específicos do num_serie_27_01_2025_df
campos_int_num_serie_27_01_2025 = ['#', 'Nº da entrega', 'Nº da nota fiscal', 'Município']
campos_data_num_serie_27_01_2025 = ['Data de entrega']

# Converter os tipos das colunas no DataFrame vendas_df
def converter_tipos(df, campos_int=[], campos_data=[], campos_float=[]):
    # Converter campos inteiros
    for campo in campos_int:
        # Usar pd.to_numeric para converter e forçar valores inválidos a NaN, depois preenchemos com 0
        df[campo] = pd.to_numeric(df[campo], errors='coerce').fillna(0).astype(int)

    # Converter campos de data
    for campo in campos_data:
        df[campo] = pd.to_datetime(df[campo], format='%d/%m/%Y', errors='coerce')

    # Converter campos de float
    for campo in campos_float:
        # Substituir vírgulas por ponto e forçar a conversão para float
        df[campo] = df[campo].str.replace(',', '.').apply(pd.to_numeric, errors='coerce').fillna(0.0)

    return df

vendas_df = converter_tipos(df=vendas_df, campos_int=campos_int_vendas, campos_data=campos_data_vendas, campos_float=campos_float_vendas)
ordem_servico_df = converter_tipos(df=ordem_servico_df, campos_int=campos_int_ordem_servico, campos_data=campos_data_ordem_servico)
compras_10_01_2025_df = converter_tipos(df=compras_10_01_2025_df, campos_int=campos_int_compras_10_01_2025, campos_data=campos_data_compras_10_01_2025, campos_float=campos_float_compras_10_01_2025)
compras_16_01_2025_df = converter_tipos(df=compras_16_01_2025_df, campos_int=campos_int_compras_16_01_2025, campos_data=campos_data_compras_16_01_2025, campos_float=campos_float_compras_16_01_2025)
num_serie_27_01_2025_df = converter_tipos(df=num_serie_27_01_2025_df, campos_int=campos_int_num_serie_27_01_2025, campos_data=campos_data_num_serie_27_01_2025)

# Função de validação para garantir que o valor inserido seja do tipo correto
def validar_valor(campo, valor):
    tipos_de_campos = {
        "int": campos_int_vendas + campos_int_ordem_servico + campos_int_compras_10_01_2025 + campos_int_compras_16_01_2025 + campos_int_num_serie_27_01_2025,
        "float": campos_float_vendas + campos_float_compras_10_01_2025 + campos_float_compras_16_01_2025,
        "data": campos_data_vendas + campos_data_ordem_servico + campos_data_compras_10_01_2025 + campos_data_compras_16_01_2025 + campos_data_num_serie_27_01_2025,
    }

    try:
        if campo in tipos_de_campos["int"]:
            return int(valor)  # Tenta converter para inteiro
        elif campo in tipos_de_campos["float"]:
            return float(valor)  # Tenta converter para float
        elif campo in tipos_de_campos["data"]:
            return pd.to_datetime(valor, format='%d/%m/%Y', errors='coerce')  # Converte para datetime
    except (ValueError, TypeError):
        return None  # Retorna None se a conversão falhar

    return valor  # Caso seja um campo string ou não identificado, retorna o valor como está

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    filtrar_data_vendas = ['Data de lançamento', 'Data de vencimento']
    colunas_desejadas = ['#', 'Nº do documento', 'Código do cliente/fornecedor', 'Nome do cliente/fornecedor']
    colunas = [col for col in vendas_df.columns if col in colunas_desejadas] # Retornam apenas as colunas que não constam em colunas_indesejadas

    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor'].strip()  # Remover espaços extras
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        campo_data = request.form.get('campo_data', None)  # Campo de data escolhido pelo usuário

        cliente_info = vendas_df.copy()  # Criar uma cópia para não alterar o DataFrame original

        # Filtro por data (caso o usuário tenha preenchido data_inicio ou data_fim)
        if data_inicio or data_fim:
            data_inicio = pd.to_datetime(data_inicio) if data_inicio else None
            data_fim = pd.to_datetime(data_fim) if data_fim else None

            if campo_data in campos_data_vendas:  # Conforme as infos forem passadas vai alterando o DF cliente_info
                if data_inicio:
                    cliente_info = cliente_info[cliente_info[campo_data] >= data_inicio]

                if data_fim:
                    cliente_info = cliente_info[cliente_info[campo_data] <= data_fim]

        # Filtro por outros campos (campo e valor)
        if campo in vendas_df.columns:
            valor_validado = validar_valor(campo, valor)  # Valida o valor de acordo com o campo

            if valor_validado is None:
                return f"Valor '{valor}' para o campo '{campo}' é inválido."

            if campo == "Nome do cliente/fornecedor" and valor_validado:
                mask = cliente_info[campo].str.contains(valor_validado, case=False, na=False)  # Busca o valor dentro da string
                cliente_info = cliente_info[mask]  # Aplica o filtro ao DataFrame filtrado por data (se houver)
            # Para campos string, normalizamos os valores para uma consulta mais precisa
            elif cliente_info[campo].dtype == 'object':
                dados_normalizados = cliente_info[campo].fillna('').astype(str).str.strip().str.title() # Trata o dataframe
                valor_validado = valor_validado.title()  # Normaliza o valor consultado, trata os dados vindo do cliente, via input
                mask = dados_normalizados == valor_validado
                cliente_info = cliente_info[mask]  # Aplicando filtro ao DataFrame filtrado por data (se houver)
            else:
                # Para outros tipos de campo, realiza a consulta diretamente
                cliente_info = cliente_info[cliente_info[campo] == valor_validado]

        # Verifica se a consulta retornou resultados
        if not cliente_info.empty:
            for col in campos_data_vendas:
                cliente_info[col] = cliente_info[col].dt.strftime('%d/%m/%Y') # Formata para entregar no frontend
            cliente_info['Linha da data de entrega'] = cliente_info['Linha da data de entrega'].apply(lambda x: None if pd.isna(x) else x)
            session['cliente_info'] = cliente_info.to_dict(orient='records')
            session['origem'] = 'vendas'
            return redirect(url_for('resultado'))
        else:
            return "Nenhum dado encontrado para os critérios fornecidos."
    return render_template('vendas.html', colunas=colunas, campos_data_vendas=campos_data_vendas, filtrar_data_vendas=filtrar_data_vendas)

@app.route('/ordem_servico', methods=['GET', 'POST'])
def ordem_servico():
    colunas_desejadas = ['#', 'Código do parceiro de negócios', 'Nome do parceiro de negócios']
    colunas = [col for col in ordem_servico_df.columns if col in colunas_desejadas]
    
    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor'].strip()
        cliente_info = ordem_servico_df.copy()
        # Filtra pelo campo e valor informado
        if campo in ordem_servico_df.columns:
            valor_validado = validar_valor(campo, valor)
            if valor_validado is None:
                return f"Valor {valor} para o campo {campo} é inválido"

            if campo == "Nome do parceiro de negócios" and valor_validado:
                mask = cliente_info[campo].str.contains(valor_validado, case=False, na=False)
                cliente_info = cliente_info[mask]          
            # Normaliza dados de campos de tipo 'object' (strings)
            elif cliente_info[campo].dtype == 'object':
                dados_normalizados = cliente_info[campo].fillna('').astype(str).str.strip().str.title()
                valor_validado = valor_validado.title()
                mask = dados_normalizados == valor_validado
                cliente_info = cliente_info[mask]
            else:
                cliente_info = cliente_info[cliente_info[campo] == valor_validado]

        # Garantir que as colunas de data estão no formato correto e formatá-las
        for col in campos_data_ordem_servico:
            if col in cliente_info.columns and cliente_info[col].dtype == 'datetime64[ns]':
                cliente_info[col] = cliente_info[col].dt.strftime('%d/%m/%Y')
            else:
                # Caso a coluna não seja datetime ou tenha valores vazios, converte para datetime
                cliente_info[col] = pd.to_datetime(cliente_info[col], errors='coerce').dt.strftime('%d/%m/%Y')

        # Verifica se há resultados para exibir
        if not cliente_info.empty:
            session['cliente_info'] = cliente_info.to_dict(orient='records')
            session['origem'] = 'ordem_servico' # Utilizado no template /resultado.html para renderizar os campos corretos
            return redirect(url_for('resultado'))
        else:
            return "Nenhum dado encontrado para os critérios fornecidos."
    
    return render_template('ordem_servico.html', colunas=colunas)        

@app.route('/compras_10_01_2025', methods=['GET', 'POST'])
def compras_10_01_2025():
    colunas_desejadas = ['#', 'Nº do documento', 'Nome do cliente/fornecedor', 'Código do cliente/fornecedor']
    colunas = [col for col in compras_10_01_2025_df.columns if col in colunas_desejadas]

    # Inicializar variáveis para evitar erros de acesso
    cliente_info = compras_10_01_2025_df.copy()

    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor'].strip()

        if campo in compras_10_01_2025_df.columns:
            valor_validado = validar_valor(campo, valor)

            if valor_validado is None:
                return f"Valor {valor} para o campo {campo} é inválido."
            
            if campo == "Nome do cliente/fornecedor" and valor_validado:
                mask = cliente_info[campo].str.contains(valor_validado, case=False, na=False)
                cliente_info = cliente_info[mask]
            elif cliente_info[campo].dtype == 'object':
                dados_normalizados = cliente_info[campo].fillna('').astype(str).str.strip().str.title()
                valor_validado = valor_validado.title()
                mask = dados_normalizados == valor_validado
                cliente_info = cliente_info[mask]
            else:
                cliente_info = cliente_info[cliente_info[campo] == valor_validado]

            # Formatar colunas de data
            for col in campos_data_compras_10_01_2025:
                if col in cliente_info.columns and cliente_info[col].dtype == 'datetime64[ns]':
                    cliente_info[col] = cliente_info[col].dt.strftime('%d/%m/%Y')
                else:
                    # Caso a coluna não seja datetime ou tenha valores vazios, converte para datetime
                    cliente_info[col] = pd.to_datetime(cliente_info[col], errors='coerce').dt.strftime('%d/%m/%Y')

            if not cliente_info.empty:
                session['cliente_info'] = cliente_info.to_dict(orient='records')
                session['origem'] = 'compras_10_01_2025'  # Utilizado no template /resultado.html para renderizar os campos corretos
                return redirect(url_for('resultado'))
            else:
                return "Nenhum dado encontrado para os critérios fornecidos."

    # Renderizar o template para requisições GET
    return render_template('compras_10_01_2025.html', colunas=colunas)

@app.route('/compras_16_01_2025', methods=['GET', 'POST'])
def compras_16_01_2025():
    colunas_desejadas = ['Nº do item', 'Nº do documento', 'Código do cliente/fornecedor', 'Nome do cliente/fornecedor', 'CNPJ']
    colunas = [col for col in compras_16_01_2025_df.columns if col in colunas_desejadas]

    # Inicializar variáveis para evitar erros de acesso
    cliente_info = compras_16_01_2025_df.copy()

    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor'].strip()

        if campo in compras_16_01_2025_df.columns:
            valor_validado = validar_valor(campo, valor)

            if valor_validado is None:
                return f"Valor {valor} para o campo {campo} é inválido."
            
            if campo == "Nome do cliente/fornecedor" and valor_validado:
                mask = cliente_info[campo].str.contains(valor_validado, case=False, na=False)
                cliente_info = cliente_info[mask]         
            # Normaliza dados de campos de tipo 'object' (strings)
            elif cliente_info[campo].dtype == 'object':
                dados_normalizados = cliente_info[campo].fillna('').astype(str).str.strip().str.title()
                valor_validado = valor_validado.title()
                mask = dados_normalizados == valor_validado
                cliente_info = cliente_info[mask]
            else:
                cliente_info = cliente_info[cliente_info[campo] == valor_validado]

            # Formatar colunas de data
            for col in campos_data_compras_16_01_2025:
                if col in cliente_info.columns and cliente_info[col].dtype == 'datetime64[ns]':
                    cliente_info[col] = cliente_info[col].dt.strftime('%d/%m/%Y')
                else:
                    # Caso a coluna não seja datetime ou tenha valores vazios, converte para datetime
                    cliente_info[col] = pd.to_datetime(cliente_info[col], errors='coerce').dt.strftime('%d/%m/%Y')

            if not cliente_info.empty:
                session['cliente_info'] = cliente_info.to_dict(orient='records')
                session['origem'] = 'compras_16_01_2025'  # Utilizado no template /resultado.html para renderizar os campos corretos
                return redirect(url_for('resultado'))
            else:
                return "Nenhum dado encontrado para os critérios fornecidos."

    # Renderizar o template para requisições GET
    return render_template('compras_16_01_2025.html', colunas=colunas)

@app.route('/num_serie', methods=['GET', 'POST'])
def num_serie():
    colunas_desejadas = ['#', 'Código do parceiro de negócios', 'Nome do parceiro de negócios']
    colunas = [col for col in num_serie_27_01_2025_df.columns if col in colunas_desejadas]

    if request.method == "POST":
        campo = request.form['campo']
        valor = request.form['valor'].strip()
        cliente_info = num_serie_27_01_2025_df.copy()
        

        if campo in num_serie_27_01_2025_df.columns:
            valor_validado = validar_valor(campo, valor)

            if valor_validado is None:
                return f"Valor {valor} para o campo {campo} é inválido."
            
            if campo == "Nome do parceiro de negócios" and valor_validado:
                mask = cliente_info[campo].str.contains(valor_validado, case=False, na=False)
                cliente_info = cliente_info[mask] 
                       
            # Normaliza dados de campos de tipo 'object' (strings)
            elif cliente_info[campo].dtype == 'object':
                dados_normalizados = cliente_info[campo].fillna('').astype(str).str.strip().str.title()
                valor_validado = valor_validado.title()
                mask = dados_normalizados == valor_validado
                cliente_info = cliente_info[mask]
            else:
                cliente_info = cliente_info[cliente_info[campo] == valor_validado]

        for col in campos_data_num_serie_27_01_2025:
            if col in cliente_info.columns and cliente_info[col].dtype == 'datetime64[ns]':
                cliente_info[col] = cliente_info[col].dt.strftime('%d/%m/%Y')
            else:
                cliente_info[col] = pd.to_datetime(cliente_info[col], errors='coerce').dt.strftime('%d/%m/%Y')
            
            if not cliente_info.empty:
                session['cliente_info'] = cliente_info.to_dict(orient='records')
                session['origem'] = 'numero_serie'
                return redirect(url_for('resultado'))            
            else:
                return "Nenhum dado encontrado para os critérios fornecidos."
            
    return render_template('num_serie.html', colunas=colunas)
    
@app.route('/resultado')
def resultado():

    # Verificando se temos dados na sessão
    cliente_info = session.get('cliente_info', None) # A session vinda está com as colunas DESORDENADAS
                                                    # Ajuste feito no html: {% set colunas_ordem ...
    if cliente_info:
        return render_template('resultado.html', cliente_info=cliente_info)
    else:
        return "Nenhum dado encontrado para exibir."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
