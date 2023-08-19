import dash
from dash import html, dcc, Dash
import dash_bootstrap_components as dbc
import base64


location = '/Users/ali/Desktop/Projects/Dashboard/Website/src'
#Users/ali/ for personal, Users/aconway/ for work

app = Dash(__name__, use_pages = True, external_stylesheets=[dbc.themes.LUX])
server = app.server

#elements
NED_logo = f'{location}/assets/Oikos2.png'
NED_logo_base64 = base64.b64encode(open(NED_logo, 'rb').read()).decode('ascii')

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='data:image/png;base64,{}'.format(NED_logo_base64), height="20px"), width='auto'),
                        dbc.Col(dbc.NavbarBrand("OIKOS – New Economic Development", class_name="ms-2"), width='auto'),
                    ],
                    align="center",
                    class_name="g-0",
                ),
                href='/',
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.NavItem(dbc.NavLink("About the author", href="https://alessandroconway.netlify.app",
                        external_link= 'True', target='_blank')
                        ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("NED Tool", href = '/'),
                    dbc.DropdownMenuItem("Methodology", href='/methodology'),
                ],
                nav=True,
                in_navbar=True,
                label="Menu",
            ),
        ]
    ),
    fixed = 'top',
    color="dark",
    dark=True,
)
footerbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavItem(dbc.NavLink("Copyright © 2023 Alessandro Conway. All rights reserved.", disabled=True)),
            dbc.NavItem(dbc.NavLink("Return to top", href="#")),
        ]
    ),
    color = "tertiary",
    #dark = True
)


app.layout = dbc.Container(
    [
        navbar,
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),

        dash.page_container,

        html.Br(),
        footerbar,
    ],
    fluid=True
)

#Run the app
if __name__ == '__main__':
#   app.run_server(debug=False)
   app.run(debug=False, host='127.0.0.1', port=8061)
