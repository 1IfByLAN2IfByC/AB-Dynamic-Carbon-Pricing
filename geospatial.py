plotData = savedGrid[:,:,0] +1 


# for i in range(0,15):
# 	for j in range(0:15):
# 		CRD =[i,j]


column_labels = ['{num}'.format(num=Xgrid) for Xgrid in range(0,15)]

fig, ax = plt.subplots()
heatmap = ax.pcolor(plotData, cmap=plt.cm.Blues)

# put the major ticks at the middle of each cell
ax.set_xticks(arange(plotData.shape[0])+0.5, minor=False)
ax.set_yticks(arange(plotData.shape[1])+0.5, minor=False)

# want a more natural, table-like display
ax.invert_yaxis()
ax.xaxis.tick_top()

ax.set_xticklabels(column_labels, minor=False)
ax.set_yticklabels(column_labels, minor=False)
# py.plotly.iplot_mpl(fig)

plt.show()


