from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Carregar o DataFrame de exemplo (substitua com o seu arquivo CSV)
dados_df = pd.read_csv('./analise-vendas.csv')

# Criar página do site
# 1- Route 
# 2- Função
# 3- Template
@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor']
        
        if campo in dados_df.columns:
            # Verifique se o valor é numérico para campos específicos
            if campo in ["#", "Nota Fiscal de Saída"]:
                try:
                    valor = int(valor)
                except ValueError:
                    return f"O valor para '{campo}' deve ser numérico."
            
            # Filtrar os dados
            cliente_info = dados_df[dados_df[campo] == valor]
            if not cliente_info.empty:
                return render_template('resultado.html', cliente_info=cliente_info)
            else:
                return f"Nenhum registro encontrado para o campo '{campo}' com o valor '{valor}'."
        else:
            return f"Campo '{campo}' não encontrado no arquivo."

    return render_template('consulta.html')

if __name__ == '__main__':
    app.run(debug=True)
