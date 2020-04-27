"""
Example of application of SimplePFD for building an absorption plant PFD from MEL..
"""
import simplepfd as pfd

components = pfd.components_from_mel('components.csv')
pfd. write_pfd('components.xml', components)