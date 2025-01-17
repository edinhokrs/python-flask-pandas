from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

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
        return f"O valor para '{campo}' deve ser do tipo correto."
    return valor

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    colunas = list(dados_df.columns)
    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor']

        if campo in dados_df.columns:
            valor_validado = validar_valor(campo, valor)
            if isinstance(valor_validado, str):  # Retorna mensagem de erro
                return valor_validado

            valor = valor_validado
            cliente_info = dados_df[dados_df[campo] == valor]
            if not cliente_info.empty:
                return render_template('resultado.html', cliente_info=cliente_info)
            else:
                return f"Nenhum registro encontrado para o campo '{campo}' com o valor '{valor}'."
        else:
            return f"Campo '{campo}' não encontrado no arquivo."

    return render_template('consulta.html', colunas=colunas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
