import plotly.graph_objects as go

fig = go.Figure(data=
    go.Scatterpolar(
        r = [0.5,1,2,2.5,3,4],
        theta = [35,70,120,155,205,240],
        mode = 'markers',
    ))

fig.update_layout(showlegend=False)
fig.show()