import streamlit as st
import pandas as pd
import re
from io import BytesIO
import logging
from datetime import datetime

# Configurações iniciais
st.set_page_config(
    page_title="Sistema de Cadastro",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
        .main {padding: 2rem;}
        .stTextInput input {font-size: 16px;}
        .msg-erro {color: red; font-size: 0.8em; margin-top: -15px; margin-bottom: 10px;}
        .stDataFrame {width: 100%;}
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 4px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .footer {
            text-align: center;
            color: #555;
            padding: 10px;
            font-size: 0.8em;
        }
        @media (max-width: 768px) {
            .main {padding: 1rem;}
        }
    </style>
""", unsafe_allow_html=True)

# Constantes
DATA_FILE = "cadastros.csv"
# LOG_FILE = "app.log"



def carregar_dados():
    """Carrega os dados do arquivo CSV."""
    try:
        df = pd.read_csv(DATA_FILE)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['nome', 'matricula', 'gestor', 'data_cadastro'])

def salvar_dados(df):
    """Salva o DataFrame no arquivo CSV."""
    df.to_csv(DATA_FILE, index=False)

def validar_nome(nome):
    """Valida se o nome contém apenas letras e espaços."""
    return bool(re.match(r'^[a-zA-ZÀ-ÿ\s]+$', nome)) if nome else False

def validar_matricula(matricula):
    """Valida se a matrícula segue o formato: 3 letras maiúsculas seguidas de 4 números."""
    return bool(re.match(r'^[A-Z]{3}\d{4}$', matricula)) if matricula else False

def formatar_dados(nome, matricula, gestor):
    """Formata os dados antes de salvar."""
    return {
        'nome': nome.title().strip(),
        'matricula': matricula.upper().strip(),
        'gestor': gestor.title().strip() if gestor else '',
        'data_cadastro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Páginas do aplicativo
def pagina_formulario():
    """Página de cadastro de novos colaboradores."""
    st.title("📝 Formulário de Cadastro")
    df = carregar_dados()

    with st.form(key="cadastro_form"):
        st.subheader("Dados do Colaborador")
        
        # Campos do formulário
        nome = st.text_input("Nome completo*", 
                            placeholder="Digite o nome completo (apenas letras)",
                            help="Obrigatório")
        
        matricula = st.text_input("Matrícula*", 
                                placeholder="Formato: ABC1234 (3 letras + 4 números)",
                                help="Obrigatório - Exemplo: ABC1234")
        
        gestor = st.text_input("Gestor", 
                             placeholder="Nome do gestor responsável")
        
        # Validações
        campos_validos = True
        if nome and not validar_nome(nome):
            st.error("❌ Nome inválido: use apenas letras e espaços")
            campos_validos = False
        
        if matricula and not validar_matricula(matricula):
            st.error("❌ Matrícula inválida: formato deve ser 3 letras MAIÚSCULAS + 4 números (ex: ABC1234)")
            campos_validos = False
        
        # Botão de envio
        enviar = st.form_submit_button("✅ Salvar Cadastro", 
                                      help="Clique para salvar os dados")
        
        if enviar:
            if not nome or not matricula:
                st.error("⚠️ Campos obrigatórios não preenchidos!")
            elif campos_validos:
                novo_registro = pd.DataFrame([formatar_dados(nome, matricula, gestor)])
                df = pd.concat([df, novo_registro], ignore_index=True)
                salvar_dados(df)
                st.success("✔️ Cadastro realizado com sucesso!")
                st.balloons()

def pagina_base_de_dados():
    """Página de visualização e gerenciamento dos dados."""
    st.title("📊 Base de Dados de Cadastros")
    df = carregar_dados()

    # Estatísticas - com verificação de DataFrame vazio
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Cadastros", len(df))
        col2.metric("Matrículas Únicas", df['matricula'].nunique())
        col3.metric("Gestores Únicos", df['gestor'].nunique())
        
        # Verifica se há dados na coluna data_cadastro
        if 'data_cadastro' in df.columns and not pd.isnull(df['data_cadastro']).all():
            ultimo_cadastro = df['data_cadastro'].max()[:10]
        else:
            ultimo_cadastro = "N/A"
        col4.metric("Último Cadastro", ultimo_cadastro)
    else:
        st.warning("⚠️ Nenhum cadastro encontrado na base de dados.")

    # Filtros - só mostra se houver dados
    if not df.empty:
        with st.expander("🔍 Filtros Avançados", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                nome_filtro = st.multiselect("Filtrar por Nome:", 
                                            sorted(df['nome'].unique()))
            with col2:
                matricula_filtro = st.multiselect("Filtrar por Matrícula:", 
                                                sorted(df['matricula'].unique()))
            with col3:
                gestor_filtro = st.multiselect("Filtrar por Gestor:", 
                                            sorted(df['gestor'].unique()))

        # Aplicar filtros
        df_filtrado = df.copy()
        if nome_filtro:
            df_filtrado = df_filtrado[df_filtrado['nome'].isin(nome_filtro)]
        if matricula_filtro:
            df_filtrado = df_filtrado[df_filtrado['matricula'].isin(matricula_filtro)]
        if gestor_filtro:
            df_filtrado = df_filtrado[df_filtrado['gestor'].isin(gestor_filtro)]

        # Exibir dados
        st.dataframe(
            df_filtrado.style.highlight_null(color='#FFCCCB').format({
                'data_cadastro': lambda x: x[:16] if pd.notnull(x) else ''
            }),
            height=400,
            use_container_width=True,
            hide_index=True
        )

        # # Opções de exportação
        # st.subheader("📤 Exportar Dados")
        # col1, col2, col3 = st.columns(3)
        # with col1:
        #     st.download_button(
        #         label="Baixar como CSV",
        #         data=df.to_csv(index=False, sep=';').encode('utf-8'),
        #         file_name='cadastros.csv',
        #         mime='text/csv',
        #     )
        # with col2:
        #     st.download_button(
        #         label="Baixar como Excel",
        #         data=df.to_excel(excel_writer=BytesIO(), index=False),
        #         file_name='cadastros.xlsx',
        #         mime='application/vnd.ms-excel',
        #     )
        # with col3:
        #     if st.button("Limpar Base de Dados", type="secondary"):
        #         with st.expander("⚠️ Confirmação", expanded=True):
        #             st.warning("Tem certeza que deseja apagar todos os registros?")
        #             if st.button("Confirmar Exclusão Total"):
        #                 pd.DataFrame(columns=df.columns).to_csv(DATA_FILE, index=False)
        #                 st.success("Base de dados limpa com sucesso!")
        #                 st.rerun()
    else:
        st.info("Adicione cadastros através do formulário para começar.")


def pagina_sobre():
    """Página com informações sobre o aplicativo."""
    st.title("ℹ️ Sobre o Sistema")
    st.markdown("""
        ### Sistema de Cadastro de Colaboradores
        
        **Versão:** 1.0.0  
        **Última atualização:** 2023-11-20  
        **Desenvolvido por:** Sua Empresa
        
        ### Funcionalidades:
        - Cadastro de colaboradores com validação de dados
        - Armazenamento em banco de dados local (CSV)
        - Filtros avançados para consulta
        - Exportação para CSV e Excel
        
        ### Tecnologias utilizadas:
        - Python 3
        - Streamlit
        - Pandas
    """)

# Navegação principal
def main():
    """Função principal que controla a navegação."""
    st.sidebar.title("Navegação")
    # st.sidebar.image("https://via.placeholder.com/150x50?text=Logo", use_container_width=True)
    
    pagina = st.sidebar.radio(
        "Menu:",
        ["Formulário", "Base de Dados", "Sobre"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        <div class="footer">
            © 2023 Sua Empresa | v1.0.0
        </div>
    """, unsafe_allow_html=True)

    # Roteamento de páginas
    if pagina == "Formulário":
        pagina_formulario()
    elif pagina == "Base de Dados":
        pagina_base_de_dados()
    elif pagina == "Sobre":
        pagina_sobre()

if __name__ == "__main__":
    main()