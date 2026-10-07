import streamlit as st
import folium
from streamlit_folium import st_folium
import hashlib

# Configuración de la página
st.set_page_config(page_title="eat-TESA", page_icon="🍴", layout="wide")

# CSS para ocultar la barra superior, marcas flotantes, código e interfaz de desarrollador
st.markdown("""
    <style>
    /* Ocultar menú principal, header y barra de herramientas de Streamlit Cloud */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .stAppToolbar {display: none !important;}
    
    /* Ocultar pie de página estándar */
    footer {visibility: hidden; display: none !important;}
    
    /* Ocultar la barra gris de Embed ("Built with Streamlit / Fullscreen / Edit with GitHub") */
    [data-testid="stEmbedFooter"] {display: none !important;}
    div[class*="embedFooter"] {display: none !important;}
    
    /* Ocultar insignias flotantes y botones de desarrollador */
    div[data-testid="stViewerBadge"] {display: none !important;}
    [class*="viewerBadge"] {display: none !important;}
    [class*="styles_viewerBadge"] {display: none !important;}
    .viewerBadge_container__1tA6D {display: none !important;}
    a[href*="streamlit.io"] {display: none !important;}
    
    /* Ocultar opciones de inspección contextual en Streamlit */
    button[title="View source"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# Función de seguridad para encriptar contraseñas (SHA-256)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Coordenadas de puntos de referencia
ITESA_LAT, ITESA_LNG = 19.728763, -98.467741
ESTACIONAMIENTO_LAT, ESTACIONAMIENTO_LNG = 19.727963, -98.467674

# Base de datos de establecimientos en Col. Las Peñitas
ESTABLECIMIENTOS = [
    {
        "id": 1,
        "nombre": "BILLAR",
        "categoria": "Comida",
        "lat": 19.727554,
        "lng": -98.467488,
        "direccion": "Calle Cierra alta, alado del estacionamiento",
        "pago": "Efectivo y Tarjeta",
        "menu": [("Tacos de pastor", "$15 c/u"), ("Gringas", "$35"),("Guajolotas","$37"),("Sopa instantanea","$37")]
    },
    {
        "id": 2,
        "nombre": "BILLAR",
        "categoria": "Entretenimiento",
        "lat": 19.727560,
        "lng": -98.467401,
        "direccion": "Calle Cierra alta, alado del estacionamiento",
        "pago": "Efectivo y Transferencia",
        "menu": [("Billar (1 hr)", "$25"), ("Maquinitas", "$1-10")]
    },
    {
        "id": 3,
        "nombre": "Carnitas y asados",
        "categoria": "Comida",
        "lat": 19.727710,
        "lng": -98.467814,
        "direccion": "Calle Principal #12, Las Peñitas",
        "pago": "Solo Efectivo",
        "menu": [("Gorditas", "$20"), ("Quesadillas", "$18")]
    },
    {
        "id": 4,
        "nombre": "Comida rapida",
        "categoria": "Comida",
        "lat": 19.727560,
        "lng": -98.467401,
        "direccion": "Frente a la entrada principal ITESA",
        "pago": "Efectivo y Transferencia",
        "menu": [("Gorditas", "$20"), ("Torta de jamon", "$30")]
    }
]

# Base de datos simulación (en producción conectar con Supabase o Firebase)
if "db_usuarios" not in st.session_state:
    st.session_state.db_usuarios = {}

# Inicializar estados de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""
if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"
if "local_seleccionado" not in st.session_state:
    st.session_state.local_seleccionado = None
if "categoria_filtro" not in st.session_state:
    st.session_state.categoria_filtro = "Todos"

# --- LOGIN Y REGISTRO ---
if not st.session_state.autenticado:
    st.title("🍴 eat-TESA")
    st.caption("Guía de comida y servicios en Col. Las Peñitas, Apan Hidalgo")
    st.divider()

    p_login, p_reg = st.tabs(["Iniciar Sesión", "Registrarse"])

    with p_login:
        email_login = st.text_input("Correo Institucional ITESA", placeholder="matricula@itesa.edu.mx")
        pass_login = st.text_input("Contraseña", type="password", key="l_pass")
        
        if st.button("Ingresar a eat-TESA", type="primary"):
            email_clean = email_login.strip().lower()
            if not email_clean.endswith("@itesa.edu.mx"):
                st.error("Acceso denegado. Debes usar tu correo institucional (@itesa.edu.mx).")
            elif not pass_login:
                st.error("Por favor ingresa tu contraseña.")
            else:
                pass_hash = hash_password(pass_login)
                # Validación de contraseña en base segura
                if email_clean in st.session_state.db_usuarios:
                    if st.session_state.db_usuarios[email_clean] == pass_hash:
                        st.session_state.autenticado = True
                        st.session_state.usuario_email = email_clean
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
                else:
                    # Permitir acceso directo por primera demostración si pasa la validación de correo
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
                # Guardar usuario con contraseña cifrada
                st.session_state.db_usuarios[email_clean] = hash_password(pass_reg)
                st.success("¡Cuenta creada con éxito!")
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
            st.session_state.categoria_filtro = "Todos"
            st.rerun()

    st.divider()

    # Menú de Navegación
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🏠 Inicio", use_container_width=True):
            st.session_state.pagina = "dashboard"
            st.rerun()
    with col_nav2:
        if st.button("🗺️ Ver Mapa Interactivo", use_container_width=True):
            st.session_state.categoria_filtro = "Todos"
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
            st.write("Establecimientos para comer cerca del ITESA.")
            if st.button("Explorar Comida ➔"):
                st.session_state.categoria_filtro = "Comida"
                st.session_state.pagina = "mapa"
                st.rerun()

        with col_c2:
            st.subheader("🎮 Entretenimiento")
            st.write("Cibercafés, videojuegos y áreas de descanso.")
            if st.button("Explorar Entretenimiento ➔"):
                st.session_state.categoria_filtro = "Entretenimiento"
                st.session_state.pagina = "mapa"
                st.rerun()

    # VISTA 2: MAPA INTERACTIVO CON RUTA DINÁMICA
    elif st.session_state.pagina == "mapa":
        st.header("🗺️ Mapa de Establecimientos y Rutas")
        
        opciones_categoria = ["Todos", "Comida", "Entretenimiento"]
        idx_filtro = opciones_categoria.index(st.session_state.categoria_filtro) if st.session_state.categoria_filtro in opciones_categoria else 0

        cat_filtro = st.selectbox(
            "Filtrar por categoría:", 
            opciones_categoria, 
            index=idx_filtro
        )
        st.session_state.categoria_filtro = cat_filtro
        
        col_lista, col_mapa = st.columns([1, 2])

        # Determinar centro del mapa
        centro_lat, centro_lng = ITESA_LAT, ITESA_LNG
        if st.session_state.local_seleccionado:
            centro_lat = st.session_state.local_seleccionado["lat"]
            centro_lng = st.session_state.local_seleccionado["lng"]

        # Crear mapa con capa Satelital ESRI y Zoom ampliado
        m = folium.Map(
            location=[centro_lat, centro_lng],
            zoom_start=17,
            max_zoom=18.7,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            max_native_zoom=19
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

        # Marcador de Referencia: Salida Estacionamiento
        html_estacionamiento = """
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(40, 40, 40, 0.85);
            color: #ffffff;
            padding: 2px 6px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.6);
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
            backdrop-filter: blur(3px);
        ">
            <span>🚗</span>
            <span>Salida</span>
        </div>
        """
        folium.Marker(
            [ESTACIONAMIENTO_LAT, ESTACIONAMIENTO_LNG],
            popup="<b>Salida Estacionamiento</b>",
            icon=folium.DivIcon(html=html_estacionamiento, icon_size=(150, 24), icon_anchor=(75, 12))
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
