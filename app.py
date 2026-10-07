import streamlit as st
import folium
from streamlit_folium import st_folium

# Configuración de la página
st.set_page_config(page_title="eat-TESA", page_icon="🍴", layout="wide")

# CSS para ocultar la barra superior, marcas flotantes y la barra gris de embed ("Built with Streamlit")
st.markdown("""
    <style>
    /* Ocultar menú principal y header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .stAppToolbar {display: none !important;}
    
    /* Ocultar pie de página estándar */
    footer {visibility: hidden; display: none !important;}
    
    /* Ocultar la barra gris de Embed ("Built with Streamlit / Fullscreen") */
    [data-testid="stEmbedFooter"] {display: none !important;}
    div[class*="embedFooter"] {display: none !important;}
    
    /* Ocultar insignias flotantes de la esquina inferior derecha */
    div[data-testid="stViewerBadge"] {display: none !important;}
    [class*="viewerBadge"] {display: none !important;}
    [class*="styles_viewerBadge"] {display: none !important;}
    .viewerBadge_container__1tA6D {display: none !important;}
    a[href*="streamlit.io"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# Coordenadas exactas del ITESA
ITESA_LAT, ITESA_LNG = 19.728763, -98.467741

# Base de datos de establecimientos en Col. Las Peñitas
ESTABLECIMIENTOS = [
    {
        "id": 1,
        "nombre": "Tacos El Güero",
        "categoria": "Comida",
        "lat": 19.729500,
        "lng": -98.466500,
        "direccion": "Av. Universidad, Col. Las Peñitas",
        "pago": "Efectivo y Tarjeta",
        "menu": [("Tacos de pastor", "$15 c/u"), ("Gringas", "$35")]
    },
    {
        "id": 2,
        "nombre": "Antojitos Doña Rosa",
        "categoria": "Comida",
        "lat": 19.727800,
        "lng": -98.468900,
        "direccion": "Calle Principal #12, Las Peñitas",
        "pago": "Solo Efectivo",
        "menu": [("Gorditas", "$20"), ("Quesadillas", "$18")]
    },
    {
        "id": 3,
        "nombre": "Ciber & Arcade ITESA",
        "categoria": "Entretenimiento",
        "lat": 19.730100,
        "lng": -98.467000,
        "direccion": "Frente a la entrada principal ITESA",
        "pago": "Efectivo y Transferencia",
        "menu": [("Renta Xbox (1 hr)", "$25"), ("Impresiones", "$2")]
    }
]

# Inicializar estados de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""
if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"
if "local_seleccionado" not in st.session_state:
    st.session_state.local_seleccionado = None

# --- LOGIN Y REGISTRO ---
if not st.session_state.autenticado:
    st.title("🍴 eat-TESA")
    st.caption("Guía de comida y servicios en Col. Las Peñitas, Apan Hidalgo")
    st.divider()

    p_login, p_reg = st.tabs(["Iniciar Sesión", "Registrarse"])

    with p_login:
        email_login = st.text_input("Correo Institucional ITESA", placeholder="tu_matricula@itesa.edu.mx")
        pass_login = st.text_input("Contraseña", type="password", key="l_pass")
        if st.button("Ingresar a eat-TESA", type="primary"):
            email_clean = email_login.strip().lower()
            if not email_clean.endswith("@itesa.edu.mx"):
                st.error("Acceso denegado. Debes usar tu correo institucional (@itesa.edu.mx).")
            elif not pass_login:
                st.error("Por favor ingresa tu contraseña.")
            else:
                st.session_state.autenticado = True
                st.session_state.usuario_email = email_clean
                st.rerun()

    with p_reg:
        nombre_reg = st.text_input("Nombre Completo")
        email_reg = st.text_input("Correo ITESA (@itesa.edu.mx)", placeholder="matricula@itesa.edu.mx")
        pass_reg = st.text_input("Contraseña", type="password", key="r_pass")
        if st.button("Crear mi Cuenta"):
            email_clean = email_reg.strip().lower()
            if not email_clean.endswith("@itesa.edu.mx"):
                st.error("Solo se permiten correos @itesa.edu.mx.")
            elif len(pass_reg) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            else:
                st.success("¡Cuenta creada!")
                st.session_state.autenticado = True
                st.session_state.usuario_email = email_clean
                st.rerun()

# --- APLICACIÓN PRINCIPAL ---
else:
    # Encabezado Superior
    c1, c2, c3 = st.columns([3, 4, 1])
    with c1:
        st.markdown("### 🍴 eat-**TESA**")
    with c2:
        st.info(f"👨‍🎓 {st.session_state.usuario_email}")
    with c3:
        if st.button("Salir 🚪"):
            st.session_state.autenticado = False
            st.session_state.usuario_email = ""
            st.session_state.pagina = "dashboard"
            st.session_state.local_seleccionado = None
            st.rerun()

    st.divider()

    # Menú de Navegación
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🏠 Inicio / Dashboard", use_container_width=True):
            st.session_state.pagina = "dashboard"
            st.rerun()
    with col_nav2:
        if st.button("🗺️ Ver Mapa Interactivo", use_container_width=True):
            st.session_state.pagina = "mapa"
            st.rerun()

    st.write("")

    # VISTA 1: DASHBOARD
    if st.session_state.pagina == "dashboard":
        st.header("¿Qué vas a comer hoy?")
        st.caption("📍 Las Peñitas, Apan Hidalgo")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("🍕 Comida")
            st.write("Establecimientos para comer cerca del campus.")
            if st.button("Explorar Comida ➔"):
                st.session_state.pagina = "mapa"
                st.rerun()

        with col_c2:
            st.subheader("🎮 Entretenimiento")
            st.write("Cibercafés, videojuegos y áreas de descanso.")
            if st.button("Explorar Entretenimiento ➔"):
                st.session_state.pagina = "mapa"
                st.rerun()

    # VISTA 2: MAPA INTERACTIVO CON RUTA DINÁMICA
    elif st.session_state.pagina == "mapa":
        st.header("🗺️ Mapa de Establecimientos y Rutas")
        
        cat_filtro = st.selectbox("Filtrar por categoría:", ["Todos", "Comida", "Entretenimiento"])
        
        col_lista, col_mapa = st.columns([1, 2])

        # Determinar centro del mapa
        centro_lat, centro_lng = ITESA_LAT, ITESA_LNG
        if st.session_state.local_seleccionado:
            centro_lat = st.session_state.local_seleccionado["lat"]
            centro_lng = st.session_state.local_seleccionado["lng"]

        # Crear mapa con capa Satelital ESRI
        m = folium.Map(
            location=[centro_lat, centro_lng],
            zoom_start=17,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery"
        )

        # Marcador de Entrada ITESA
        html_itesa = """
        <div style="background-color:#003049; color:white; padding:4px 8px; border-radius:10px; font-weight:bold; font-size:11px; border:2px solid white; box-shadow:0 2px 6px rgba(0,0,0,0.4);">
            🏫 ITESA
        </div>
        """
        folium.Marker(
            [ITESA_LAT, ITESA_LNG],
            popup="<b>Entrada Principal ITESA</b>",
            icon=folium.DivIcon(html=html_itesa)
        ).add_to(m)

        # Filtrar locales por categoría
        locales_visibles = [
            l for l in ESTABLECIMIENTOS 
            if cat_filtro == "Todos" or l["categoria"] == cat_filtro
        ]

        with col_lista:
            st.subheader("Establecimientos")
            st.caption("Selecciona uno para trazar la ruta desde ITESA:")

            for local in locales_visibles:
                es_seleccionado = (
                    st.session_state.local_seleccionado is not None and 
                    st.session_state.local_seleccionado["id"] == local["id"]
                )

                # Tarjeta del establecimiento con botón de trazado
                with st.container():
                    st.markdown(f"### 📍 {local['nombre']}")
                    st.write(f"**Ubicación:** {local['direccion']}")
                    st.write(f"**Pago:** {local['pago']}")

                    # Botón para trazar o quitar ruta
                    if es_seleccionado:
                        if st.button(f"❌ Ocultar Ruta", key=f"btn_{local['id']}"):
                            st.session_state.local_seleccionado = None
                            st.rerun()
                    else:
                        if st.button(f"🗺️ Trazar Ruta desde ITESA", key=f"btn_{local['id']}", type="primary"):
                            st.session_state.local_seleccionado = local
                            st.rerun()

                    with st.expander("Ver Menú / Servicios"):
                        for prod, precio in local["menu"]:
                            st.write(f"- {prod}: **{precio}**")
                    st.divider()

                # Marcador individual del local
                folium.Marker(
                    [local["lat"], local["lng"]],
                    popup=f"<b>{local['nombre']}</b><br>{local['direccion']}<br><b>Pago:</b> {local['pago']}",
                    icon=folium.Icon(color="red" if local["categoria"] == "Comida" else "purple", icon="info-sign")
                ).add_to(m)

        # TRAZAR RUTA ÚNICA SI HAY UN LOCAL SELECCIONADO
        if st.session_state.local_seleccionado:
            dest = st.session_state.local_seleccionado
            folium.PolyLine(
                locations=[[ITESA_LAT, ITESA_LNG], [dest["lat"], dest["lng"]]],
                color="#FF3333",
                weight=5,
                opacity=0.9,
                dash_array='8, 8'
            ).add_to(m)

        with col_mapa:
            st_folium(m, width=800, height=550)
