
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Pesquisa Eleitoral - Caxias/MA",
    layout="wide"
)

# ==================================================
# LOGO CENTRALIZADO
# ==================================================

col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])

with col_logo2:
    st.image(
        "CONSULTARE-Imagem.png",
        width=320
    )
# ==============================
# LEITURA DA BASE
# ==============================

BD = pd.read_excel("Caxias-Dash.xlsx")

BD.columns = (
    BD.columns
    .str.strip()
    .str.replace("\n", " ", regex=False)
    .str.replace("  ", " ", regex=False)
)

# ==============================
# VARIÁVEIS
# ==============================

Sexo = "Sexo"
FE = "Faixa etária"
Zona = "Zona"

Q4 = "Como você o(a) sr.(a) avalia a administração do presidente Lula"
Q5 = "Como você o(a) sr.(a) avalia a administração do Governador Brandão"

Q7 = "Qual dessas características mais combina com um bom Deputado Estadual?"
Q8 = "O(a) sr.(a) já ouviu falar ou conhece alguma dessas ações? (Pode marcar mais de uma)"
Q9 = "Essas ações influenciam sua decisão de voto?"
Q10 = "O(a) sr.(a) sabe qual deputado estadual é responsável por essas ações? Se sim, pode me dizer quem é?"
Q11 = "Se a eleição fosse hoje em quem o(a) sr(a) votaria para Deputado Estadual? (Espontânea)."
Q12 = "Com relação ao cargo de deputado Estadual, o seu voto:"
Q13 = "Se a eleição fosse hoje, qual dos candidatos à seguir o senhor(a) votaria para Deputado Federal?"
Q14 = "Se a eleição fosse hoje, qual dos candidatos à seguir o senhor(a) votaria para Deputado Estadual?"
Q15 = "Em qual desses candidatos o(a) sr.(a) NÃO votaria de jeito nenhum para Deputado Estadual?"

F1 = "Foto 1"
F2 = "Foto 2"
F3 = "Foto 3"
F4 = "Foto 4"
# ==================================================
# ORDEM DAS IDADES
# ==================================================

ordem_idade = [
    "16 a 24 anos",
    "25 a 44 anos",
    "45 a 59 anos",
    "60 anos +"
]

# ==============================
# AJUSTE DE NOMES ALTERNATIVOS
# ==============================

mapa_colunas = {}

for col in BD.columns:
    col_limpa = col.strip().replace("\n", " ").replace("  ", " ")

    if "ações?" in col_limpa and "Pode marcar" in col_limpa:
        mapa_colunas[col] = Q8

    if "Se sim, pode me dizer quem é" in col_limpa or "Se sim pode me dizer quem é" in col_limpa:
        mapa_colunas[col] = Q10

    if "Com relação ao cargo de deputado Estadual" in col_limpa:
        mapa_colunas[col] = Q12

    if "Deputado Federal" in col_limpa:
        mapa_colunas[col] = Q13

    if "votaria para Deputado Estadual" in col_limpa and "Espontânea" not in col_limpa:
        mapa_colunas[col] = Q14

BD = BD.rename(columns=mapa_colunas)

# ==============================
# FUNÇÕES
# ==============================

def grafico_pizza(base, coluna, titulo):
    fig = px.pie(
        base,
        names=coluna,
        title=titulo,
        hole=0.4
    )

    fig.update_traces(
        textposition="inside",
        texttemplate="%{label}<br>%{percent:.2%}"
    )

    fig.update_layout(
        legend_title_text="",
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig


def grafico_barras(base, coluna, titulo, top_n=None, ordem=None):
    tabela = (
        base[coluna]
        .fillna("Não respondeu")
        .value_counts()
        .reset_index()
    )

    tabela.columns = ["Resposta", "Quantidade"]

    tabela["Percentual"] = tabela["Quantidade"] / tabela["Quantidade"].sum() * 100

    if top_n:
        tabela = tabela.head(top_n)

    fig = px.bar(
        tabela,
        x="Percentual",
        y="Resposta",
        orientation="h",
        text=tabela["Percentual"].map(lambda x: f"{x:.2f}%"),
        title=titulo
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Percentual",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
        xaxis=dict(ticksuffix="%"),
        height=max(400, len(tabela) * 45),
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig


def grafico_avaliacao(base, coluna, titulo):
    ordem = ["Péssimo", "Ruim", "Regular", "Bom", "Ótimo", "PNR"]

    cores = {
        "Péssimo": "#E51C23",
        "Ruim": "#F05A24",
        "Regular": "#FDB515",
        "Bom": "#D7DF23",
        "Ótimo": "#20C997",
        "PNR": "#00BFA5"
    }

    tabela = (
        base[coluna]
        .fillna("PNR")
        .value_counts()
        .reindex(ordem)
        .fillna(0)
        .reset_index()
    )

    tabela.columns = ["Avaliação", "Quantidade"]
    tabela["Percentual"] = tabela["Quantidade"] / tabela["Quantidade"].sum() * 100

    fig = go.Figure()

    for _, row in tabela.iterrows():
        fig.add_trace(go.Bar(
            y=[titulo],
            x=[row["Percentual"]],
            name=row["Avaliação"],
            orientation="h",
            marker=dict(
                color=cores[row["Avaliação"]],
                line=dict(color="white", width=2)
            ),
            text=f'{row["Avaliação"]}<br>{row["Percentual"]:.2f}%',
            textposition="inside",
            hovertemplate=(
                f"<b>{row['Avaliação']}</b><br>"
                f"Quantidade: {int(row['Quantidade'])}<br>"
                f"Percentual: {row['Percentual']:.2f}%"
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        barmode="stack",
        height=260,
        xaxis=dict(
            range=[0, 100],
            ticksuffix="%"
        ),
        yaxis=dict(showticklabels=False),
        legend_title="Avaliação",
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig


# ==============================
# FILTROS
# ==============================

st.sidebar.title("Filtros")

sexo_filtro = st.sidebar.multiselect(
    "Sexo",
    BD[Sexo].dropna().unique(),
    default=BD[Sexo].dropna().unique()
)

zona_filtro = st.sidebar.multiselect(
    "Zona",
    BD[Zona].dropna().unique(),
    default=BD[Zona].dropna().unique()
)

ordem_idade = [
    "16 a 24 anos",
    "25 a 44 anos",
    "45 a 59 anos",
    "60 anos +"
]

fe_filtro = st.sidebar.multiselect(
    "Faixa etária",
    options=ordem_idade,
    default=ordem_idade
)

dados = BD[
    (BD[Sexo].isin(sexo_filtro)) &
    (BD[Zona].isin(zona_filtro)) &
    (BD[FE].isin(fe_filtro))
]

# ==============================
# DASHBOARD
# ==============================

st.title("Dashboard - Pesquisa Eleitoral Caxias/MA")

st.markdown(f"**Total de entrevistas filtradas:** {len(dados)}")

# ==============================
# PERFIL DA AMOSTRA
# ==============================

st.header("Perfil da Amostra")

col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(
        grafico_pizza(dados, Sexo, "Distribuição por Sexo"),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        grafico_pizza(dados, Zona, "Distribuição por Zona"),
        use_container_width=True
    )

with col3:
    st.plotly_chart(
        grafico_barras(dados, FE, "Distribuição por Faixa Etária", ordem=ordem_idade),
        use_container_width=True
    )

# ==============================
# AVALIAÇÕES ADMINISTRATIVAS
# ==============================

st.header("Avaliação das Administrações")

st.plotly_chart(
    grafico_avaliacao(dados, Q4, "Avaliação Lula"),
    use_container_width=True
)

st.plotly_chart(
    grafico_avaliacao(dados, Q5, "Avaliação Brandão"),
    use_container_width=True
)

# ==============================
# PERCEPÇÕES POLÍTICAS
# ==============================

st.header("Percepções e Influência das Ações")

st.plotly_chart(
    grafico_barras(dados, Q7, "Característica mais associada a um bom Deputado Estadual"),
    use_container_width=True
)

st.plotly_chart(
    grafico_barras(dados, Q8, "Conhecimento sobre ações realizadas"),
    use_container_width=True
)

st.plotly_chart(
    grafico_barras(dados, Q9, "Influência das ações na decisão de voto"),
    use_container_width=True
)

st.plotly_chart(
    grafico_barras(dados, Q10, "Deputado associado às ações"),
    use_container_width=True
)

# ==============================
# INTENÇÃO DE VOTO
# ==============================

st.header("Intenção de Voto")

st.plotly_chart(
    grafico_barras(dados, Q11, "Deputado Estadual - Espontânea", top_n=20),
    use_container_width=True
)

st.plotly_chart(
    grafico_barras(dados, Q12, "Nível de decisão do voto para Deputado Estadual"),
    use_container_width=True
)

st.plotly_chart(
    grafico_barras(dados, Q13, "Intenção de voto para Deputado Federal", top_n=20),
    use_container_width=True
)

st.plotly_chart(
    grafico_barras(dados, Q14, "Intenção de voto para Deputado Estadual", top_n=20),
    use_container_width=True
)

st.plotly_chart(
    grafico_barras(dados, Q15, "Rejeição para Deputado Estadual", top_n=20),
    use_container_width=True
)

# ==============================
# FOTOS
# ==============================

st.header("Avaliação por Fotos")

col4, col5 = st.columns(2)

with col4:
    st.plotly_chart(
        grafico_barras(dados, F1, "Foto 1"),
        use_container_width=True
    )

with col5:
    st.plotly_chart(
        grafico_barras(dados, F2, "Foto 2"),
        use_container_width=True
    )

col6, col7 = st.columns(2)

with col6:
    st.plotly_chart(
        grafico_barras(dados, F3, "Foto 3"),
        use_container_width=True
    )

with col7:
    st.plotly_chart(
        grafico_barras(dados, F4, "Foto 4"),
        use_container_width=True
    )

# ==================================================
# IMAGEM FINAL
# ==================================================

st.header("Mapa Visual dos Candidatos")

col_img1, col_img2, col_img3 = st.columns([1, 2, 1])

with col_img2:
    st.image(
        "Disco_de_imagem-removebg-preview.png",
        width=700
    )
