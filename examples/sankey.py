"""
CO2LOS WP7 Feasibility study.
"""
import simplepfd as pfd

boxA = pfd.Unit('Box A', 'box')
boxB = pfd.Unit('Box B', 'box')
boxC = pfd.Unit('Box C', 'box')
boxD = pfd.Unit('Box D', 'box')

flow1 = pfd.Flow('F1', 'Box A', 'Box B',   width=30, dashed=False, color='green', nolabel=True)
flow2 = pfd.Flow('F2', 'Box B', 'Box C',   width=30, dashed=False, color='green', nolabel=True)
flow3 = pfd.Flow('F3', 'Box C', 'Box D',   width=15, dashed=False, color='green', nolabel=True)
flow4 = pfd.Connector('F4', 'Box C', 'Box D',   width=10, dashed=False, color='red', nolabel=True)
flow5 = pfd.Connector('F5', 'Box C', 'Box D',   width=7, dashed=False, color='blue', nolabel=True)
flow6 = pfd.Connector('F6', 'Box C', 'Box D',   width=5, dashed=False, color='orange', nolabel=True)
flow7 = pfd.Connector('F7', 'Box C', 'Box D',   width=2, dashed=False, color='grey', nolabel=True)
flow8 = pfd.Flow('F8', 'Box C', 'Box B',   width=10, dashed=False, color='red', nolabel=True)
flow9 = pfd.Connector('F9', 'Box C', 'Box B',   width=5, dashed=False, color='blue', nolabel=True)
flow10 = pfd.Connector('F10', 'Box C', 'Box B', width=2, dashed=False, color='orange', nolabel=True)



# Define units part of process flow diagram;
components = [boxA, boxB, boxC, boxD, flow1, flow2, flow3, flow4, flow5, flow6, flow7, flow8, flow9, flow10]

# Write XML-file for import in DrawIO:
pfd.write_pfd("sankey.xml", components)