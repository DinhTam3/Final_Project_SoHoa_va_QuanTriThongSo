import pandas as pd 
import dash
from dash.dependencies import Input,Output
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html, callback, ctx, State
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

'''------------------------------------------------------------------------------------'''
app = dash.Dash(__name__)
server = app.server
df = pd.read_csv("out.csv")

# đoạn code này dùng để tách tháng và năm ra thành các cột riêng lẻ
year = df['Invoice Date'].str.split('/')
get_year = []
get_month = []
for i in year:
    y = i[2]
    m = i[1]
    get_year.append(y)
    get_month.append(m)
df['Year'] = get_year
df['Month'] = get_month

'''------------------------------------Tạo Các Hàm Dùng Cho Vẽ Biểu Đồ------------------------------------------------'''

def create_bar_chart_retailer(year='2020'):
    if year == '2020':
        data_2020 = df[df['Year'] == '2020']
        filtered_data = data_2020.groupby('Retailer').sum().reset_index().sort_values(by='Total Sales')
        bar_fig = px.bar(filtered_data, x='Total Sales', y='Retailer', title='BIỂU ĐỒ CỘT THỂ HIỆN TỔNG DOANH THU THEO CÁC NHÀ BÁN LẺ')
        bar_fig.update_layout(height=600)
    elif year == '2021':
        data_2021 = df[df['Year'] == '2021']
        filtered_data = data_2021.groupby('Retailer').sum().reset_index().sort_values(by='Total Sales')
        bar_fig = px.bar(filtered_data, x='Total Sales', y='Retailer', title='BIỂU ĐỒ CỘT THỂ HIỆN TỔNG DOANH THU THEO CÁC NHÀ BÁN LẺ')
        bar_fig.update_layout(height=600)
    return bar_fig
    
def create_bar_chart_product(year='2020', method='In-store'):
    if year == '2020':
        data_2020 = df[df['Year'] == '2020']
        filtered_data = data_2020[data_2020['Sales Method'] == method].groupby('Product').sum().reset_index()

        bar_fig = px.bar(filtered_data, x='Total Sales', y='Product', title=f'BIỂU ĐỒ CỘT THỂ HIỆN DOANH THU THEO SẢN PHẨM - {method} - {year}')
        bar_fig.update_layout(height=600)
    if year == '2021':
        data_2021 = df[df['Year'] == '2021']
        filtered_data = data_2021[data_2021['Sales Method'] == method].groupby('Product').sum().reset_index()

        bar_fig = px.bar(filtered_data, x='Total Sales', y='Product', title=f'BIỂU ĐỒ CỘT THỂ HIỆN DOANH THU THEO SẢN PHẨM - {method} - {year}')
        bar_fig.update_layout(height=600)
    return bar_fig

def create_pie_chart(year='2020'):
    if year == '2020':
        data2020 = df[df['Year'] == '2020']
        methods_unique = data2020['Sales Method'].unique()
        count = data2020.groupby('Sales Method')['Sales Method'].count()
        count1 = data2020.groupby('Sales Method').count().reset_index()
        sum = data2020.groupby('Sales Method')['Sales Method'].count().sum()
        methods = []
        percent = []
        for m in methods_unique:
            methods.append(m)
        for i in methods:
            per = round((count[i] / sum) * 100, 2)
            percent.append(per)
        count1['Percentages'] = percent
        pie = px.pie(data_frame=count1, names='Sales Method', values='Percentages', labels='Sales Method', hole=.3, title='TỈ LỆ PHẦN TRĂM PHƯƠNG THỨC MUA HÀNG ĐƯỢC ƯA CHUỘNG')
        return pie
    elif year == '2021':
        data2021 = df[df['Year'] == '2021']
        methods_unique = data2021['Sales Method'].unique()
        count = data2021.groupby('Sales Method')['Sales Method'].count()
        count1 = data2021.groupby('Sales Method').count().reset_index()
        sum = data2021.groupby('Sales Method')['Sales Method'].count().sum()
        methods = []
        percent = []
        for m in methods_unique:
            methods.append(m)
        for i in methods:
            per = round((count[i] / sum) * 100, 2)
            percent.append(per)
        count1['Percentages'] = percent
        pie = px.pie(data_frame=count1, names='Sales Method', values='Percentages', labels='Sales Method', hole=.3, title='TỈ LỆ PHẦN TRĂM PHƯƠNG THỨC MUA HÀNG ĐƯỢC ƯA CHUỘNG')
        return pie

'''------------------------------------Tạo Các Hàm Dùng Cho Phân tích------------------------------------------------'''
def analysis_price(select_retailer, select_product, input_units_sold, select_sales_method, select_region):
    
    if (select_retailer != None) and (select_product != None) and (input_units_sold != None) and (select_sales_method != None) and (select_region != None):
        input_choose = transform_input(select_retailer, select_product, input_units_sold, select_sales_method, select_region)
        X = handle(df)
        Y = df['Price per Unit']
        X_train, x_test, Y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

        lm = LinearRegression()
        lm.fit(X_train, Y_train)

        Y_pred = lm.predict(X)
        Y_pred = pd.DataFrame(Y_pred, columns=['Price Predict'])
        result_compare = pd.concat([X, Y, Y_pred], axis=1)
        result_compare['Deviation'] = result_compare['Price Predict'] - result_compare['Price per Unit']

        x_new = [input_choose]
        x_new = pd.DataFrame(x_new, columns=['Retailer', 'Product', 'Units Sold', 'Sales Method', 'Region'])
        price = lm.predict(x_new)
        price = pd.DataFrame(price, columns=['Price predict'])
        df_n = pd.concat([x_new, price], axis=1)
        return '%.2f' % df_n['Price predict'][0] 

def transform_input(select_retailer, select_product, input_units_sold, select_sales_method, select_region):     
    input_choose = []
    retailer_dict = {'Foot Locker': 0, 
                     'Walmart': 1, 
                     'Sports Direct': 2, 
                     'West Gear': 3, 
                     "Kohl's": 4, 
                     'Amazon': 5}
    product_dict = {"Men's Street Footwear": 0, 
                    "Men's Athletic Footwear": 1, 
                    "Women's Street Footwear": 2, 
                    "Women's Athletic Footwear": 3,
                    "Men's Apparel": 4, 
                    "Women's Apparel": 5}
    sales_method_dict = {'In-store': 0, 
                         'Outlet': 1, 
                         'Online': 2}
    region_dict = {'Northeast': 0, 
                   'South': 1, 
                   'West': 2, 
                   'Midwest': 3, 
                   'Southeast': 4}
    for i in retailer_dict:
        if select_retailer == i:
            input_choose.append(retailer_dict[select_retailer])
    for i in product_dict:
        if select_product == i:
            input_choose.append(product_dict[select_product])
    for i in sales_method_dict:
        if select_sales_method == i:
            input_choose.append(sales_method_dict[select_sales_method])
    for i in region_dict:
        if select_region == i:
            input_choose.append(region_dict[select_region])
    input_choose.insert(2, input_units_sold)

    return input_choose

def handle(df):
    retailer_dict = {'Foot Locker': 0, 
                     'Walmart': 1, 
                     'Sports Direct': 2, 
                     'West Gear': 3, 
                     "Kohl's": 4, 
                     'Amazon': 5}
    product_dict = {"Men's Street Footwear": 0, 
                    "Men's Athletic Footwear": 1, 
                    "Women's Street Footwear": 2, 
                    "Women's Athletic Footwear": 3,
                    "Men's Apparel": 4, 
                    "Women's Apparel": 5}
    sales_method_dict = {'In-store': 0, 
                         'Outlet': 1, 
                         'Online': 2}
    region_dict = {'Northeast': 0, 
                   'South': 1, 
                   'West': 2, 
                   'Midwest': 3, 
                   'Southeast': 4}
    
    X = df[['Retailer', 'Product', 'Units Sold', 'Sales Method', 'Region']]

    X['Retailer'] = X['Retailer'].map(retailer_dict)
    X['Product'] = X['Product'].map(product_dict)
    X['Sales Method'] = X['Sales Method'].map(sales_method_dict)
    X['Region'] = X['Region'].map(region_dict)

    return X

    


'''------------------------------------Widgets------------------------------------------------'''
# vẽ doanh thu theo các nhà bán lẻ
year_values = df['Year'].unique()
select_year_bar_chart_re = dcc.RadioItems(id='select_year_bar_chart_re', options=year_values, value='2020')

# vẽ doanh thu theo loại sản phẩm
select_year_bar_chart_pr = dcc.RadioItems(id='select_year_bar_chart_pr', options=year_values, value='2020')
select_methods_bar_chart_pr = dcc.Dropdown(
    id='select_methods_bar_chart_pr', 
    options=df['Sales Method'].unique(),
    value='In-store')

# vẽ phần trăm số lượng phương thức mua hàng
select_year_pie_chart = dcc.RadioItems(id='select_year_pie_chart', options=year_values, value='2020')

# phân tích dự báo
select_retailer = dcc.Dropdown(id='select_retailer', options=df['Retailer'].unique())
select_product = dcc.Dropdown(id='select_product', options=df['Product'].unique())
select_sales_method = dcc.Dropdown(id='select_sales_method', options=df['Sales Method'].unique())
select_region = dcc.Dropdown(id='select_region', options=df['Region'].unique())
input_units_sold = dcc.Input(id='input_units_sold', type="number", debounce=True)
button_analysis = html.Button('Phân tích', id='btn_nclicks', n_clicks=0)
output_analysis = html.Div(id='output_analysis', children='')
'''------------------------------------Layout------------------------------------------------'''
app.layout = html.Div(
    children=[
        html.H1('PHÂN TÍCH XU HƯỚNG CÁC NHÀ BÁN LẺ CỦA ADIDAS', style={"textAlign":"center"}),
        html.H3('Các thành viên: Đình Tam - Tinh Khôi - Minh Hiếu', style={"textAlign":"center"}),

        html.Br(),
        html.Br(),

        html.Div(
            children=[
                html.Div('Chọn năm mà bạn muốn'),
                html.Br(),
                select_year_bar_chart_re,
                html.Br(),
                dcc.Graph(id='bar_chart_re', figure=create_bar_chart_retailer())
            ],
            style={"textAlign":"center"},    
        ),

        html.Div('-'*248),
        html.Br(),
        html.Br(),

        html.Div(
            children=[
                html.Div('Chọn năm mà bạn muốn'),
                html.Br(),
                select_year_bar_chart_pr,
                html.Br(),
                html.Div('Chọn phương thức bán hàng mà bạn muốn'),
                html.Br(),
                select_methods_bar_chart_pr,
                html.Br(),
                dcc.Graph(id='bar_chart_pr', figure=create_bar_chart_product())  
            ],
            style={"textAlign":"center"}
        ),

        html.Div('-'*248),
        html.Br(),
        html.Br(),

        html.Div(
            children=[
                html.Div('Chọn năm mà bạn muốn'),
                html.Br(),
                select_year_pie_chart,
                html.Br(),
                dcc.Graph(id='pie_chart_percent', figure=create_pie_chart()) 
            ],
            style={"textAlign":"center"}
        ),

        html.Div('-'*248),
        html.Br(),
        html.Br(),
        html.Div(
            children=[
                html.H2('Phân tích dự đoán giá', style={"textAlign":"center"}),
                html.Br(),
                html.Div('Chọn nhà bán lẻ'),
                html.Br(),
                select_retailer,
                html.Br(),
                html.Br(),
                html.Div('Chọn nhà loại sản phẩm'),
                html.Br(),
                select_product,
                html.Br(),
                html.Br(),
                html.Div('Chọn phương thức bán hàng'),
                html.Br(),
                select_sales_method,
                html.Br(),
                html.Br(),
                html.Div('Chọn khu vực'),
                html.Br(),
                select_region,
                html.Br(),
                html.Br(),
                html.Div('Chọn số lượng sản phẩm đã bán ra'),
                html.Br(),
                input_units_sold,
                html.Br(),
                html.Br(),
                button_analysis,
                html.Br(),
                html.H3(output_analysis, style={"textAlign":"center"}),
            ]
        )
    ]
    
)

'''------------------------------------Callback------------------------------------------------'''

@callback(Output('bar_chart_re', 'figure'), [Input('select_year_bar_chart_re', 'value')])
def update_bar_chart_retailer(year):
    return create_bar_chart_retailer(year)

@callback(Output('bar_chart_pr', 'figure'), [Input('select_year_bar_chart_pr', 'value'), Input('select_methods_bar_chart_pr', 'value')])
def update_bar_chart_product(year, method):
    return create_bar_chart_product(year, method)

@callback(Output('pie_chart_percent', 'figure'), [Input('select_year_pie_chart', 'value')])
def update_pie_chart_percent(year):
    return create_pie_chart(year)

@callback(
    Output(output_analysis, 'children'),
    
    Input('select_retailer', 'value'),
    Input('select_product', 'value'),

    Input('btn_nclicks', 'n_clicks'),
    State('input_units_sold', 'value'),

    Input('select_sales_method', 'value'),
    Input('select_region', 'value'),

    prevent_initial_call=True
)
def update_output_analysis(re, pro, n_clicks, value, me, reg):
    result = analysis_price(re, pro, value, me, reg)
    value = result
    return 'Giá dự đoán là $ {}'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)