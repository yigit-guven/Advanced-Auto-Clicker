import urllib.parse

THEME_TEMPLATE = """
QMainWindow {{
    background-color: {bg_main};
}}

QWidget {{
    color: {text_main};
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}}

QLabel#Title {{
    font-size: 24px;
    font-weight: bold;
    color: {primary};
    margin-bottom: 10px;
}}

QLabel#ActionHeader {{
    font-weight: 800;
    color: {primary};
    font-size: 16px;
}}

QFrame#Card {{
    background-color: {bg_card};
    border-radius: 12px;
    border: 1px solid {border};
    padding: 10px;
}}

QPushButton {{
    background-color: {btn_bg};
    color: {text_main};
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {btn_hover};
}}

QPushButton:disabled {{
    color: {border};
    background-color: {bg_main};
    border: 1px solid {border};
}}

QPushButton#Primary {{
    background-color: {primary};
    color: {btn_primary_text};
    border: none;
    border-radius: 8px;
}}

QPushButton#Primary:hover {{
    background-color: {primary_hover};
}}

QPushButton#Danger {{
    background-color: #f43f5e;
    color: #ffffff;
    border: none;
    border-radius: 8px;
}}

QPushButton#Danger:hover {{
    background-color: #fb7185;
}}

QPushButton#GhostDanger {{
    background-color: {btn_bg};
    color: {text_main};
    border: 1px solid {border};
    border-radius: 4px;
    font-size: 14px;
    font-weight: bold;
}}

QPushButton#GhostDanger:hover {{
    color: white;
    background-color: #f43f5e;
    border: 1px solid #f43f5e;
}}

QLineEdit {{
    background-color: {bg_main};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 5px;
    color: {text_light};
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {bg_main};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 5px;
    padding-right: 20px;
    color: {text_light};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid {border};
    border-bottom: 0.5px solid {border};
    border-top-right-radius: 5px;
    background-color: {bg_card};
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: {btn_bg};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid {border};
    border-top: 0.5px solid {border};
    border-bottom-right-radius: 5px;
    background-color: {bg_card};
}}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {btn_bg};
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url("{up_arrow_svg}");
    width: 10px;
    height: 10px;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url("{down_arrow_svg}");
    width: 10px;
    height: 10px;
}}

QComboBox {{
    background-color: {bg_main};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 5px;
    padding-right: 25px;
    color: {text_light};
}}

QComboBox::drop-down {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid {border};
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    background-color: {bg_card};
}}

QComboBox::drop-down:hover {{
    background-color: {btn_bg};
}}

QComboBox::down-arrow {{
    image: url("{down_arrow_svg}");
    width: 10px;
    height: 10px;
}}

QCheckBox {{
    spacing: 8px;
    color: {text_main};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {border};
    border-radius: 4px;
    background-color: {bg_main};
}}

QCheckBox::indicator:hover {{
    border-color: {primary};
    background-color: {bg_card};
}}

QCheckBox::indicator:checked {{
    background-color: {primary};
    border-color: {primary};
    image: url("{checkmark_svg}");
}}

QCheckBox::indicator:checked:hover {{
    background-color: {primary_hover};
    border-color: {primary_hover};
}}

QScrollArea {{
    border: none;
    background-color: {bg_main};
}}

QWidget#ListWidget {{
    background-color: {bg_main};
}}

QComboBox QAbstractItemView {{
    background-color: {bg_main};
    border: 1px solid {border};
    selection-background-color: {primary};
    selection-color: {btn_primary_text};
    color: {text_light};
}}

QScrollBar:vertical {{
    border: none;
    background: {bg_main};
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {btn_bg};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {btn_hover};
}}

QFrame#UpdateBanner {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #b45309);
    border-radius: 8px;
    border: 1px solid #f59e0b;
}}

QPushButton#UpdateBtn {{
    background-color: {bg_main};
    color: #fbbf24;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    font-size: 12px;
    border: 1px solid #fbbf24;
}}

QPushButton#UpdateBtn:hover {{
    background-color: {bg_card};
    color: #ffffff;
}}

QPushButton#OrderBtn {{
    background-color: {btn_bg};
    color: {text_main};
    border: 1px solid {border};
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
    padding: 0px;
}}

QPushButton#OrderBtn:hover {{
    background-color: {btn_hover};
    color: {primary};
}}

QPushButton#OrderBtn:disabled {{
    color: {border};
    background-color: {bg_main};
    border: 1px solid {border};
}}

QPushButton#SettingsBtn {{
    background-color: transparent;
    color: {text_main};
    border: 1px solid {border};
    font-size: 13px;
    padding: 6px 12px;
    font-weight: 600;
    border-radius: 6px;
}}

QPushButton#SettingsBtn:hover {{
    background-color: {bg_card};
    border-color: {primary};
}}
"""

THEMES = {
    "Dark Blue": {
        "bg_main": "#0f172a",
        "text_main": "#e2e8f0",
        "text_light": "#f8fafc",
        "primary": "#22d3ee",
        "primary_hover": "#67e8f9",
        "bg_card": "#1e293b",
        "border": "#334155",
        "btn_bg": "#334155",
        "btn_hover": "#475569",
        "btn_primary_text": "#0f172a",
    },
    "Light": {
        "bg_main": "#f8fafc",
        "text_main": "#1e293b",
        "text_light": "#0f172a",
        "primary": "#0284c7",
        "primary_hover": "#0369a1",
        "bg_card": "#ffffff",
        "border": "#cbd5e1",
        "btn_bg": "#e2e8f0",
        "btn_hover": "#cbd5e1",
        "btn_primary_text": "#ffffff",
    },
    "Matrix Green": {
        "bg_main": "#030712",
        "text_main": "#10b981",
        "text_light": "#34d399",
        "primary": "#10b981",
        "primary_hover": "#34d399",
        "bg_card": "#06150f",
        "border": "#047857",
        "btn_bg": "#06251b",
        "btn_hover": "#047857",
        "btn_primary_text": "#030712",
    },
    "Sunset Purple": {
        "bg_main": "#1e1b4b",
        "text_main": "#e0e7ff",
        "text_light": "#f8fafc",
        "primary": "#ec4899",
        "primary_hover": "#f472b6",
        "bg_card": "#312e81",
        "border": "#4338ca",
        "btn_bg": "#4338ca",
        "btn_hover": "#4f46e5",
        "btn_primary_text": "#ffffff",
    }
}

def get_svg_url(svg_xml):
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg_xml)

def make_svgs(text_color, checkmark_color):
    up = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{text_color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>'
    down = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{text_color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>'
    check = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{checkmark_color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
    return get_svg_url(up), get_svg_url(down), get_svg_url(check)

def get_theme_stylesheet(theme_name):
    theme_data = THEMES.get(theme_name, THEMES["Dark Blue"]).copy()
    up, down, check = make_svgs(theme_data["text_main"], theme_data["btn_primary_text"])
    theme_data["up_arrow_svg"] = up
    theme_data["down_arrow_svg"] = down
    theme_data["checkmark_svg"] = check
    return THEME_TEMPLATE.format(**theme_data)

def get_overlay_stylesheet(theme_name):
    theme_data = THEMES.get(theme_name, THEMES["Dark Blue"])
    hex_color = theme_data["primary"].lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"""
QLabel {{
    background-color: rgba({r}, {g}, {b}, 0.25);
    border: 2px solid {theme_data["primary"]};
    border-radius: 25px;
    color: #ffffff;
    font-weight: bold;
    font-size: 18px;
    qproperty-alignment: 'AlignCenter';
}}
"""

# Default styles for initialization
MAIN_STYLE = get_theme_stylesheet("Dark Blue")
OVERLAY_STYLE = get_overlay_stylesheet("Dark Blue")
