import dash
from dash import dcc, html, Input, Output, callback, State, dash_table, Dash
import dash_bootstrap_components as dbc

import base64
import io

from pm import plate
from hscm import half
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Create a Dash web application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Define the layout of the app
app.layout = html.Div(style={'margin':'15px'},
    children=[
       
        html.H2("Lithosphere Cooling Models", style={"text-align":"center"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(
                    [
                        html.H4("Parameters", style={"text-align":"center"}),
                        html.P(
                            "Select the cooling model for visualization.",
                            className="card-text",
                        ),
                        dcc.Dropdown(["Half Space Cooling Model","Plate Model","Both"],
                                     "Half Space Cooling Model",id="model",
                                     style={'width': '100%','background-color':'#a2b4c6','color':'#222222'},clearable=False),
                        html.Hr(),
                        html.P("Surface Temperature °C"),
                        dcc.Slider(min=0, max=100, step=1, value=0, id='T0',marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True}),
                        html.P("Bottom Temperature °C"),
                        dcc.Slider(min=1000, max=1600, step=1, value=1400, id='T1',marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True}),
                        html.P("Thermal Diffusivity"),
                        dcc.Slider(min=0.1, max=10, step=0.1, value=1, id='kappa',marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True}),
                        html.P("Lithosphere thickness"),
                        dcc.Slider(min=10, max=200, step=1, value=120, id='h',marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True}),
                        html.P("Number of iterations for plate model"),
                        dcc.Slider(min=1, max=300, step=1, value=50, id='iter',marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True}),
                        html.P("Age for geoterm profile in My"),
                        dcc.Slider(min=1, max=300, step=1, value=50, id='profile',marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True}),
                        
            ])
        ]),
                
            ],width=3),
            dbc.Col([
                dcc.Graph(figure={},id='main-plot'),
                html.Div([dcc.Checklist(
                        ['Fill', 'Sqrt','Light','Points'],
                        ['Fill'],
                        inline=True,
                        id="checklist"
                    ),
                    dcc.Slider(min=0,max=1,value=0.9,id='grid_alpha',marks=None,className='slider')],style={'display':'flex'}
                    ),
                              
                
                
            ],width=9),
           
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H4("3D Visualization (Click on surface for projections)"),
                    dcc.Graph(figure={},id='3d'),
                    
                ])
                
            ]),
            dbc.Col([
                dbc.Card([
                    html.H4("2D Projection Depth vs Temp"),
                    dcc.Graph(figure={},id='2da'),
                    
                ])
                
            ]),
            dbc.Col([
                dbc.Card([
                    html.H4("2D Projection Age vs Temperature"),
                    dcc.Graph(figure={},id='2db'),
                    
                ])
                
            ]),
        ]),
        dbc.Row([
            dbc.Card([
                html.Div([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select File'),
                            
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=False
                    ),
                    html.Div(id='output-data-upload'),
                
                ])
            ],className="w-50")
        
             
        ])
    ])

# Define callback to update the second plot based on hover data from the first plot
@callback(
    Output(component_id='main-plot', component_property='figure'),
    Input(component_id='model', component_property='value'),
    Input(component_id='T0', component_property='value'),
    Input(component_id='T1', component_property='value'),
    Input(component_id='kappa', component_property='value'),
    Input(component_id='h', component_property='value'),
    Input(component_id='iter', component_property='value'),
    Input(component_id='checklist', component_property='value'),
    Input(component_id='profile', component_property='value'),
    Input(component_id='grid_alpha', component_property='value'),        
    
   
)
def update_main(model,T0,Ttop,kappa,h,iter,values,profile,ga):
    X1,Y1,T1 = half(T0,Ttop,h,kappa)
    X2,Y2,T2 = plate(T0,Ttop,h,kappa,iter)
    if model=="Half Space Cooling Model":
        X,Y,T = X1,Y1,T1
    elif model=="Plate Model":
        X,Y,T = X2,Y2,T2
    else:
        X,Y,T = X2,Y2,T2
        
    if "Fill" in values:
        coloring = 'heatmap'
    else:
        coloring = 'lines'
        
    if "Sqrt" in values:
        pow = 0.5
    else:
        pow = 1
        
    if "Light" in values:
        temp = 'plotly'
    else:
        temp='plotly_dark'
    
        
    abb = ''.join([x[0] for x in model.split()])
    
    fig = make_subplots(rows=1, cols=2, column_widths=[0.75, 0.25],
                        subplot_titles=(f"Temperature (°C) vs depth and age", f"Temperature profile at {profile} My"))    
    fig.add_trace(go.Contour(name=abb,z=T,x=X**pow,y=Y,transpose=True, line_width=2, opacity=0.85,
        contours=dict(
            coloring =coloring,
            
            showlabels = True, # show labels on contours
            start=100,
            end=1500,
            size=200,
            labelfont = dict( # label font properties
                size = 12,
                color = 'white',
        )),colorbar=dict(
                    x=0.68,                        
        )
        ),row=1,col=1)
    fig.update_xaxes(title_text="age in My", row=1, col=1,gridcolor=f"rgba(92,92,92,{ga})")
    fig.update_xaxes(title_text="Temperature °C", row=1, col=2,)
    fig.update_yaxes(title_text="depth in km", row=1, col=1,gridcolor=f"rgba(92,92,92,{ga})")
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(template=temp,
                      height=640,
                      margin=dict(t=50, b=20, l=5, r=20)
                                           
                    )
    fig.add_trace(go.Scatter(x=T[profile,:],y=Y,name='PM'),row=1,col=2)
    
    if "Points" in values:
        fig.add_trace(go.Scatter(data=df,x=df['age'],y=df['depth']))
    
    if model=="Both":
        fig.add_trace(go.Contour(z=T1,x=X1**pow,y=Y1,transpose=True, line_width=2,line_dash='dash', opacity=0.85,
        contours=dict(
            coloring =coloring,
            
            showlabels = True, # show labels on contours
            start=100,
            end=1500,
            size=200,
            labelfont = dict( # label font properties
                size = 12,
                color = 'green',
        )),colorbar=dict(
                    x=0.68,                        
        )),row=1,col=1)
        fig.add_trace(go.Scatter(x=T1[profile,:],y=Y1,name='HSCM'),row=1,col=2)
        
        
            
    return fig

@callback(
    Output(component_id='3d', component_property='figure'),
    
    Input(component_id='T0', component_property='value'),
    Input(component_id='T1', component_property='value'),
    Input(component_id='kappa', component_property='value'),
    Input(component_id='h', component_property='value'),
    Input(component_id='iter', component_property='value'),
       
)

def update_3d(T0,Ttop,kappa,h,iter):
    
    X,Y,T = plate(T0,Ttop,h,kappa,iter)   
    fig = go.Figure()
    fig.add_trace(go.Surface(z=np.transpose(T),x=X,y=Y, opacity=0.9))
    fig.update_layout(template='plotly_dark',
                      scene_camera=dict(eye=dict(x=1.25,y=-1.25,z=1.25)))
    fig.layout.xaxis.title.text='Age in My'
    fig.layout.yaxis.title.text='Depth in km'
    fig.layout.title.text = "3D surface Temperature vs depth vs Age"
    fig.layout.margin.b=40    
    return fig


@callback(
    Output(component_id='2da', component_property='figure'),
    Output(component_id='2db', component_property='figure'),    
    Input(component_id='T0', component_property='value'),
    Input(component_id='T1', component_property='value'),
    Input(component_id='kappa', component_property='value'),
    Input(component_id='h', component_property='value'),
    Input(component_id='iter', component_property='value'),
    Input(component_id='3d', component_property='clickData')    
)

def update_2da(T0,Ttop,kappa,h,iter,hoverData):
    
    X,Y,T = plate(T0,Ttop,h,kappa,iter)
    
    a = hoverData['points'][0]['x'] if hoverData else 0
    b = hoverData['points'][0]['y'] if hoverData else 0
    
    
    
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=X,x=T[a,:]))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(template='plotly_dark')
    fig.layout.xaxis.title.text='Temperature °C'
    fig.layout.yaxis.title.text='Depth in km'
    fig.layout.title.text = f"Temperature vs depth for age of {a}My (Vertical profile)"
    fig.layout.margin.b=40
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=X,y=T[:,b]))
    fig2.update_layout(template='plotly_dark')
    fig2.layout.xaxis.title.text='Age in My'
    fig2.layout.yaxis.title.text='Temperature °C'
    fig2.layout.title.text = f"Temperature vs age for depth of {b}km (horizontal profile)"
    fig2.layout.margin.b=40
    
    return fig, fig2


@callback(Output('output-data-upload', 'children'),         
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              Input('main-plot','figure'),prevent_initial_call=True)
def parse_contents(contents, filename,fig):
    if contents is not None:
        content_type, content_string = contents.split(',')      

        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file                
                
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
                
            elif 'xls' in filename:
                 
                
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
                
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.', 
            ])
            
        
        return html.Div([
            html.H5(filename),        
            dash_table.DataTable(
                df.to_dict('records'),
                [{'name': i, 'id': i} for i in df.columns],
            page_size=20,
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
                
            },
            style_data={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            
            },),        
            
        ]), 




# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
    
    
    
    
    
    
    
    
    


