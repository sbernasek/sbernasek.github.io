# resorts = ['Montgenèvre', 'Cervinia', 'Solitude', 'Brighton', 'Snowbird', 'Alta', 'Jackson Hole', 'Squaw', 'Alpine']

# import altair as alt

# width = 450
# height = 250


# line_kw = dict(color=color, strokeWidth=3, interpolate='natural')

# color_kw = dict(scale=alt.Scale(scheme='spectral'),
#             legend=alt.Legend(title="Resort", orient="top-left"),
#             sort=resorts)

# # create chart
# chart = alt.Chart(SKI_DAYS_GPX_RESAMPLED.reset_index(), width=width, height=height).mark_line(**line_kw).encode(
#         x=alt.X('time_elapsed_hours', axis=alt.Axis(title='Time Elapsed (hr)')),
#         y=alt.Y('elevation_gain_ft', axis=alt.Axis(title='Vertical Feet')),
#         color=alt.Color('location', **color_kw),
#         detail=alt.Detail('date')
#         ).configure_axis(
#             grid=False
#         ).configure_view(
#             strokeWidth=0
#         )

# chart
