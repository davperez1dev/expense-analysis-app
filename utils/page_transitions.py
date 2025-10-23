"""
Utilidad para agregar transiciones y efectos visuales entre páginas
"""
import streamlit as st
import time


def add_page_transition():
    """Agrega un efecto de transición suave al cargar la página"""
    st.markdown("""
    <style>
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main .block-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Efectos para elementos individuales */
    .stMetric {
        animation: fadeIn 0.6s ease-out;
    }
    
    .stPlotlyChart {
        animation: fadeIn 0.7s ease-out;
    }
    
    /* Efecto hover en cards */
    .stMetric:hover {
        transform: scale(1.02);
        transition: transform 0.2s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Sidebar con transición */
    [data-testid="stSidebar"] {
        animation: slideInLeft 0.4s ease-out;
    }
    
    @keyframes slideInLeft {
        from {
            transform: translateX(-100%);
        }
        to {
            transform: translateX(0);
        }
    }
    
    /* Botones con efecto hover mejorado */
    .stButton>button {
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Expanders con animación */
    .streamlit-expanderHeader {
        transition: background-color 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(103, 126, 234, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)


def add_loading_animation(text="Cargando datos..."):
    """Muestra una animación de carga temporal"""
    loading_placeholder = st.empty()
    
    loading_placeholder.markdown(f"""
    <div style="display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 200px;
                flex-direction: column;">
        <div style="border: 4px solid #f3f3f3;
                    border-top: 4px solid #667eea;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 1s linear infinite;"></div>
        <p style="margin-top: 20px; color: #667eea; font-weight: 600;">{text}</p>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    return loading_placeholder


def show_success_message(message, duration=2):
    """Muestra un mensaje de éxito temporal con animación"""
    success_placeholder = st.empty()
    
    success_placeholder.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px;
                border-radius: 10px;
                color: white;
                text-align: center;
                animation: slideDown 0.5s ease-out;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
        <h3 style="margin: 0;">✓ {message}</h3>
    </div>
    
    <style>
    @keyframes slideDown {{
        from {{
            transform: translateY(-100%);
            opacity: 0;
        }}
        to {{
            transform: translateY(0);
            opacity: 1;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    time.sleep(duration)
    success_placeholder.empty()


def add_custom_css():
    """Agrega estilos CSS personalizados para mejorar la UI global"""
    st.markdown("""
    <style>
    /* Mejorar el aspecto general */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Headers con gradiente */
    h1, h2, h3 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Cards con shadow */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Tabs mejorados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f5f5f5;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    /* Dataframes con mejor estilo */
    .dataframe {
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-radius: 8px;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    </style>
    """, unsafe_allow_html=True)
