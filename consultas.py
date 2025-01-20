from flask import Flask, render_template, request, Response, session, redirect, url_for
import pdfkit # Lib para gerar o PDF
import pandas as pd

app = Flask(__name__)

app.secret_key = 'secret_key' # Armazenar sessão, para que o cliente_info seja passado na rota para_pdf

# Carregar o DataFrame
dados_df = pd.read_csv('./analise-vendas.csv')

# Casting dos campos
campos_casting = ['Total de Nota Fiscal de Saída', 'Lucro bruto', 'Total de NS em aberto']
for campo in campos_casting:
    dados_df[campo] = dados_df[campo].replace({r'R\$ ': '', r'\.': '', ',': '.'}, regex=True).astype(float)

def validar_valor(campo, valor):
    try:
        if campo in ["#", "Nota Fiscal de Saída"]:
            return int(valor)
        elif campo in ['% de lucro bruto', 'Total de Nota Fiscal de Saída', 'Lucro bruto', 'Total de NS em aberto']:
            return float(valor)
    except ValueError:
        if campo in ["#", "Nota Fiscal de Saída"]:
            return f"O valor do {campo} deve ser algum número inteiro."
        if campo in ['% de lucro bruto', 'Total de Nota Fiscal de Saída', 'Lucro bruto', 'Total de NS em aberto']:
            return f"O valor do {campo} deve ser algum número decimal."
    return valor

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    colunas = list(dados_df.columns) # Utilizado no consulta.html para mostrar dinamicamente quais os campos presentes no CSV
    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor']

        if campo in dados_df.columns:
            valor_validado = validar_valor(campo, valor)
            if isinstance(valor_validado, str):  # Retorna mensagem de erro, pois a função validar_campo retorna o erro caso seja Str
                return valor_validado

            valor = valor_validado
            cliente_info = dados_df[dados_df[campo] == valor]

            session['cliente_info'] = cliente_info.to_dict(orient='records')  # Armazenando em formato de dicionário

            if not cliente_info.empty:
                return redirect(url_for('resultado'))
            else:
                return f"Nenhum registro encontrado para o campo '{campo}' com o valor '{valor}'."
        else:
            return f"Campo '{campo}' não encontrado no arquivo."

    return render_template('consulta.html', colunas=colunas)

@app.route('/resultado')
def resultado():
    # Recuperando os dados da sessão
    cliente_info = session.get('cliente_info', None)
    cliente_info_df = pd.DataFrame(cliente_info)

    if cliente_info:
        return render_template('resultado.html', cliente_info=cliente_info_df)
    else:
        return "Nenhum dado encontrado para exibir."

@app.route('/para_pdf', methods=['POST'])
def route_pdf():
    cliente_info = session.get('cliente_info', None) # Recuperando os dados da consulta encontrada para gerar PDF

    if not cliente_info:
        return "Erro: Nenhuma consulta encontrada para gerar o PDF."

    out = render_template("tabela_pdf.html", cliente_info=cliente_info) # Gera a página HTML contendo a tabela com os dados reais de cliente_info

    options = {
        "orientation": "landscape",
        "page-size": "A4",
        "margin-top": "1.0cm",
        "margin-right": "1.0cm",
        "margin-bottom": "1.0cm",
        "margin-left": "1.0cm",
        "encoding": "UTF-8",
    }

    pdf = pdfkit.from_string(out, options=options) # Gerar PDF a partir do conteúdo HTML

    response = Response(pdf, mimetype="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=tabela.pdf" # Configura o cabeçalho para forçar o Download do PDF

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
