import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


problem_1txt="""

# Gender Pay

The gender pay gap is the difference in earnings between women and men. According to Pew Research Center, in 2024 women earned about 85% of what men earned, compared to 81% in 2003. The gap is smaller for younger workers aged 25 to 34, where women earned about 95 cents for every dollar men earned. Over time, the gap has narrowed from 35 cents in 1982 to 15 cents in 2024 for all workers. Factors like education, work experience, and job type explain some of the gap, but discrimination may also play a role. Women remain overrepresented in lower-paying jobs, and opinions differ on the main causes. About half of U.S. adults say unequal treatment by employers is a major reason, while others point to family-work balance choices or women working in lower-paying jobs.

The Darden School of Business explains that the gap is often larger in higher-paying jobs that require long hours, known as “greedy jobs.” Parenthood impacts women’s earnings more than men’s, with women facing a “motherhood penalty” and men sometimes earning more after becoming fathers. In team-based work, women may get less credit for contributions, especially in male-dominated fields. Occupational segregation also contributes, with women concentrated in lower-paying jobs.


# GCC

The General Social Survey (GSS) is a big survey of adults in the United States that has been happening since 1972. It was started by James A. Davis, who worked on it until 2009 and helped run the research center called NORC. He wanted to create a way to track changes in important social topics like gender roles, race relations, and people's opinions every year, and share that info with everyone who’s interested. The GSS asks questions about things like behavior, attitudes, crime, and social life. Because it asks some of the same questions over many years, researchers can see how things change over time. It’s one of the best sources for understanding how American society changes, and it also works with a global survey project called ISSP to compare data from other countries.


###  References

* https://www.pewresearch.org/short-reads/2025/03/04/gender-pay-gap-in-us-has-narrowed-slightly-over-2-decades/

* https://news.darden.virginia.edu/2024/04/04/why-the-gender-pay-gap-persists-in-american-businesses/

* https://gss.norc.org/us/en/gss/about-the-gss.html
"""


gss = pd.read_csv(
    "https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
    encoding='cp1252',
    na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE','DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"]
)

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk']

gss_clean = gss[mycols].rename(columns={
    'wtss':'weight',
    'educ':'education',
    'coninc':'income',
    'prestg10':'job_prestige',
    'mapres10':'mother_job_prestige',
    'papres10':'father_job_prestige',
    'sei10':'socioeconomic_index',
    'fechld':'relationship',
    'fefam':'male_breadwinner',
    'fepol':'men_bettersuited',
    'fepresch':'child_suffer',
    'meovrwrk':'men_overwork'
})

gss_clean.age = gss_clean.age.replace({'89 or older':'89'}).astype('float')

region_name_map = {
    'e. nor. central': 'East North Central',
    'e. sou. central': 'East South Central',
    'middle atlantic': 'Middle Atlantic',
    'mountain': 'Mountain',
    'new england': 'New England',
    'pacific': 'Pacific',
    'south atlantic': 'South Atlantic',
    'w. nor. central': 'West North Central',
    'w. sou. central': 'West South Central'
}

region_options = [{'label': region_name_map.get(r, r.title()), 'value': r}
                  for r in sorted(gss_clean['region'].dropna().unique())]

def categorize_education(years):
    if pd.isna(years):
        return 'Missing'
    elif years <= 8:
        return 'Less than High School'
    elif years <= 12:
        return 'High School Graduate'
    elif years <= 15:
        return 'Some College'
    elif years <= 18:
        return "Bachelor's Degree"
    else:
        return 'Graduate Degree'

gss_clean['education_cat'] = gss_clean['education'].apply(categorize_education)

bar_feature_map = {
    'satjob': 'Satisfaction with Job',
    'relationship': 'Relationship Satisfaction',
    'male_breadwinner': 'Male Breadwinner Statement',
    'men_bettersuited': 'Men Better Suited for Politics',
    'child_suffer': 'Children Suffer if Mother Works',
    'men_overwork': 'Men Overwork'
}

bar_feature_options = [{'label': v, 'value': k} for k, v in bar_feature_map.items()]

group_by_options = [
    {'label': 'Sex', 'value': 'sex'},
    {'label': 'Region', 'value': 'region'},
    {'label': 'Education Category', 'value': 'education_cat'}
]

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Gender Pay Gap & General Social Survey Data Dashboard",
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px', 'fontFamily': 'Arial'}),
        dcc.Tabs([
        dcc.Tab(label='Summary', children=[
            html.Div([
                dcc.Markdown(problem_1txt,
                             style={'padding': '20px', 'fontFamily': 'Arial', 'fontSize': '16px'})
            ])
        ]),
        dcc.Tab(label='Distributions', children=[
            html.Div([
                dcc.Dropdown(
                    id='region-dropdown',
                    options=region_options,
                    multi=True,
                    placeholder='Select one or more regions',
                    style={'width': '50%', 'margin': '20px auto'}
                ),
                html.H3("Agreement Levels on Male Breadwinner Statement by Sex",
                        style={'textAlign': 'center', 'color': '#34495e'}),
                dcc.Graph(id='barplot'),
                html.H3("Distribution of Income and Job Prestige by Sex",
                        style={'textAlign': 'center', 'color': '#34495e', 'marginTop': '40px'}),
                html.Div([
                    dcc.Graph(id='income-boxplot', style={'flex': '1', 'marginRight': '10px'}),
                    dcc.Graph(id='jobprestige-boxplot', style={'flex': '1'})
                ], style={'display': 'flex', 'padding': '0 20px'})
            ])
        ]),
        dcc.Tab(label='Scatter Plot', children=[
            html.Div([
                dcc.Dropdown(
                    id='region-dropdown-scatter',
                    options=region_options,
                    multi=True,
                    placeholder='Select one or more regions',
                    style={'width': '50%', 'margin': '20px auto'}
                ),
                html.H3("Job Prestige vs. Income by Sex",
                        style={'textAlign': 'center', 'color': '#34495e'}),
                dcc.Graph(id='scatterplot')
            ])
        ]),
        dcc.Tab(label='Customizable Barplot', children=[
            html.Div([
                html.Label("Select Bar Feature:", style={'fontWeight': 'bold', 'marginTop': '20px'}),
                dcc.Dropdown(
                    id='custom-bar-feature',
                    options=bar_feature_options,
                    value='male_breadwinner',
                    clearable=False,
                    style={'width': '50%', 'marginBottom': '20px'}
                ),
                html.Label("Group Bars By:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='custom-groupby',
                    options=group_by_options,
                    value='sex',
                    clearable=False,
                    style={'width': '50%', 'marginBottom': '20px'}
                ),
                dcc.Graph(id='custom-barplot')
            ], style={'padding': '20px'})
        ])
    ])
])

@app.callback(
    Output('barplot', 'figure'),
    Output('income-boxplot', 'figure'),
    Output('jobprestige-boxplot', 'figure'),
    Input('region-dropdown', 'value')
)
def update_distribution_plots(selected_regions):
    if not selected_regions:
        filtered = gss_clean
    else:
        filtered = gss_clean[gss_clean['region'].isin(selected_regions)]

    df_bar = filtered[['sex', 'male_breadwinner']].dropna()
    df_box = filtered.dropna(subset=['income', 'job_prestige', 'sex'])

    bar_fig = px.histogram(
        df_bar,
        x='male_breadwinner',
        color='sex',
        barmode='group',
        category_orders={'male_breadwinner': ['strongly disagree', 'disagree', 'agree', 'strongly agree']},
        labels={
            'male_breadwinner': 'Level of Agreement with "Male Breadwinner" Statement',
            'count': 'Number of Respondents',
            'sex': 'Sex'
        },
        color_discrete_map={'male': 'red', 'female': 'blue'}
    )
    bar_fig.update_layout(xaxis_title='Level of Agreement', yaxis_title='Number of Respondents', legend_title_text='Sex')

    income_box = px.box(
        df_box,
        x='sex',
        y='income',
        labels={'sex': '', 'income': 'Personal Annual Income'},
        color='sex',
        color_discrete_map={'male': 'red', 'female': 'blue'}
    )
    income_box.update_layout(showlegend=False)

    jobprestige_box = px.box(
        df_box,
        x='sex',
        y='job_prestige',
        labels={'sex': '', 'job_prestige': 'Job Prestige Score'},
        color='sex',
        color_discrete_map={'male': 'red', 'female': 'blue'}
    )
    jobprestige_box.update_layout(showlegend=False)

    return bar_fig, income_box, jobprestige_box

@app.callback(
    Output('scatterplot', 'figure'),
    Input('region-dropdown-scatter', 'value')
)
def update_scatterplot(selected_regions):
    if not selected_regions:
        filtered = gss_clean.dropna(subset=['job_prestige', 'income', 'sex', 'education', 'socioeconomic_index'])
    else:
        filtered = gss_clean[gss_clean['region'].isin(selected_regions)].dropna(subset=['job_prestige', 'income', 'sex', 'education', 'socioeconomic_index'])

    scatter_fig = px.scatter(
        filtered,
        x='job_prestige',
        y='income',
        color='sex',
        labels={
            'job_prestige': 'Job Prestige Score',
            'income': 'Personal Annual Income',
            'sex': 'Sex'
        },
        hover_data=['education', 'socioeconomic_index'],
        color_discrete_map={'male': 'red', 'female': 'blue'},
        trendline='ols'
    )
    scatter_fig.update_layout(xaxis_title='Job Prestige', yaxis_title='Income', legend_title_text='Sex')
    return scatter_fig

@app.callback(
    Output('custom-barplot', 'figure'),
    Input('custom-bar-feature', 'value'),
    Input('custom-groupby', 'value')
)
def update_custom_barplot(bar_feature, groupby_col):
    df = gss_clean.dropna(subset=[bar_feature, groupby_col])
    if groupby_col == 'region':
        df['region_friendly'] = df['region'].map(region_name_map).fillna(df['region'])
        groupby = 'region_friendly'
    elif groupby_col == 'education_cat':
        groupby = 'education_cat'
    else:
        groupby = groupby_col

    color_map = {'male': 'red', 'female': 'blue'} if groupby == 'sex' else None

    fig = px.histogram(
        df,
        x=bar_feature,
        color=groupby,
        barmode='group',
        labels={bar_feature: bar_feature_map.get(bar_feature, bar_feature),
                'count': 'Count',
                groupby: groupby.replace('_', ' ').title()},
        color_discrete_map=color_map
    )
    fig.update_layout(
        xaxis_title=bar_feature_map.get(bar_feature, bar_feature),
        yaxis_title='Count',
        legend_title=groupby.replace('_', ' ').title()
    )
    return fig
