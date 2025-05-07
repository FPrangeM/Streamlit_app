import streamlit as st
import pandas as pd
import re  # Para usar expressões regulares

# Nome do arquivo CSV para armazenar os dados
DATA_FILE = "cadastros.csv"

def carregar_dados():
    """Carrega os dados do arquivo CSV se ele existir, senão retorna um DataFrame vazio."""
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=['nome', 'matricula', 'gestor'])

def salvar_dados(df):
    """Salva o DataFrame no arquivo CSV."""
    df.to_csv(DATA_FILE, index=False)

def validar_nome(nome):
    """Valida se o nome contém apenas letras e espaços."""
    return bool(re.match(r'^[a-zA-Z\s]+$', nome))

def validar_matricula(matricula):
    """Valida se a matrícula segue o formato: 3 letras maiúsculas seguidas de 4 números."""
    return bool(re.match(r'^[A-Z]{3}\d{4}$', matricula))

def main():
    st.sidebar.title("Navegação")
    pagina = st.sidebar.radio("Selecione a página:", ["Formulário", "Base de Dados"])

    if pagina == "Formulário":
        pagina_formulario()
    elif pagina == "Base de Dados":
        pagina_base_de_dados()

def pagina_formulario():
    st.title("Formulário de Cadastro")
    df = carregar_dados()  # Carrega os dados existentes

    campos_validos = True

    with st.form(key="cadastro"):

        # Campo Nome
        with st.container():
            nome = st.text_input("Nome:", key="nome_form_input")
            invalido_nome = nome and not validar_nome(nome)
            if invalido_nome:
                campos_validos = False

            # Estilização e mensagem
            st.markdown(
                f"""
                <style>
                    div[data-baseweb="input"] > input#nome_form_input {{
                        border: {'1px solid red' if invalido_nome else '1px solid #ccc'};
                        margin-bottom: 0px;
                    }}
                    .msg-erro-nome {{
                        font-size: 0.8em;
                        color: #888;
                        margin: 0;
                        padding: 0;
                        line-height: 1.2;
                    }}
                </style>
                """,
                unsafe_allow_html=True,
            )

            if invalido_nome:
                st.markdown('<div class="msg-erro-nome">Apenas letras e espaços são permitidos.</div>', unsafe_allow_html=True)

        # Campo Matrícula
        with st.container():
            matricula = st.text_input("Matrícula:", key="matricula_form_input")
            invalido_matricula = matricula and not validar_matricula(matricula)
            if invalido_matricula:
                campos_validos = False

            st.markdown(
                f"""
                <style>
                    div[data-baseweb="input"] > input#matricula_form_input {{
                        border: {'1px solid red' if invalido_matricula else '1px solid #ccc'};
                        margin-bottom: 0px;
                    }}
                    .msg-erro-matricula {{
                        font-size: 0.8em;
                        color: #888;
                        margin: 0;
                        padding: 0;
                        line-height: 1.2;
                    }}
                </style>
                """,
                unsafe_allow_html=True,
            )

            if invalido_matricula:
                st.markdown(
                    '<div class="msg-erro-matricula">Formato inválido. Use 3 letras MAIÚSCULAS seguidas de 4 números (ex: ABC1234).</div>',
                    unsafe_allow_html=True
                )

        # Campo Gestor
        gestor = st.text_input("Gestor:", key="gestor_form_input")

        # Botão de envio
        enviar = st.form_submit_button("Enviar")

        if enviar:
            if campos_validos:
                novo_registro = pd.DataFrame([{'nome': nome, 'matricula': matricula, 'gestor': gestor}])
                df = pd.concat([df, novo_registro], ignore_index=True)
                salvar_dados(df)
                st.success("Cadastro realizado com sucesso!")
            else:
                st.error("Por favor, corrija os campos com erro antes de enviar.")




def pagina_base_de_dados():
    st.title("Base de Dados de Cadastros")
    df = carregar_dados()

    st.header("Filtros")
    col1, col2, col3 = st.columns(3)
    with col1:
        nome_filtro = st.multiselect("Filtrar por Nome:", df['nome'].unique())
    with col2:
        matricula_filtro = st.multiselect("Filtrar por Matrícula:", df['matricula'].unique())
    with col3:
        gestor_filtro = st.multiselect("Filtrar por Gestor:", df['gestor'].unique())

    # Aplicando filtros
    df_filtrado = df.copy()
    if nome_filtro:
        df_filtrado = df_filtrado[df_filtrado['nome'].isin(nome_filtro)]
    if matricula_filtro:
        df_filtrado = df_filtrado[df_filtrado['matricula'].isin(matricula_filtro)]
    if gestor_filtro:
        df_filtrado = df_filtrado[df_filtrado['gestor'].isin(gestor_filtro)]

    st.dataframe(df_filtrado)

    # Adiciona a opção de baixar os dados
    st.download_button(
        label="Baixar dados como CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='cadastros.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()