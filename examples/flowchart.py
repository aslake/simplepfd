"""
CO2LOS WP7 Feasibility study.
"""
import simplepfd as pfd

components = pfd.components_from_mel('flowchart.csv')
pfd. write_pfd('flowchart.xml', components)