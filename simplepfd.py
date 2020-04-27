"""
SimplePFD - Simple Python wrapper for app.diagrams.net process flow diagrams (PFDs).

Define units, flows, sensors and connectors -> render and edit PFDs in https://app.diagrams.net
Flow diagram definition can also be done from MEL (Main Equipment List) .csv :)

ver. 1.65

Author: Aslak Einbu 2020
"""

from os import path
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re

component = {
             'box': 'style="whiteSpace=wrap;html=1;movableLabel=1;aspect=fixed;" parent="1" vertex="1"><mxGeometry x="290" y="190" width="80" height="80" as="geometry" /></mxCell>',
             'text': 'style="whiteSpace=wrap;html=1;movableLabel=1;aspect=fixed;strokeColor=none;fillColor=none;" parent="1" vertex="1"><mxGeometry x="290" y="190" width="80" height="80" as="geometry" /></mxCell>',
             'vessel': 'style="rounded=1;whiteSpace=wrap;html=1;movableLabel=1;aspect=fixed;arcSize=50;" vertex="1" parent="1"> <mxGeometry x="160" y="420" width="40" height="130" as="geometry" /></mxCell>',
             'pump': 'style="shape=mxgraph.pid.pumps.gas_blower;html=1;movableLabel=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;flipH=1;" vertex="1" parent="1"><mxGeometry x="680" y="233" width="50" height="47" as="geometry" /></mxCell>',
             'blower': 'style="shape=mxgraph.pid.pumps.gas_blower;html=1;movableLabel=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="530" y="340" width="72" height="67" as="geometry" /></mxCell>',
             'compressor': 'style="shape=mxgraph.pid.compressors_-_iso.compressor,_vacuum_pump;html=1;movableLabel=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="130" y="130" width="40" height="40" as="geometry" /></mxCell>',
             'packedcolumn': 'style="verticalLabelPosition=top;outlineConnect=0;align=right;dashed=0;html=1;movableLabel=1;verticalAlign=bottom;shape=mxgraph.pid2misc.column;columnType=fixed;labelPosition=left;" vertex="1" parent="1"><mxGeometry x="-50" y="370" width="50" height="300" as="geometry" /></mxCell>',
             'heatexchanger': 'style="shape=mxgraph.pid.heat_exchangers.shell_and_tube_heat_exchanger_1;html=1;movableLabel=1;pointerEvents=1;align=right;verticalLabelPosition=top;verticalAlign=bottom;dashed=0;labelPosition=left;" vertex="1" parent="1"> <mxGeometry x="130" y="60" width="40" height="40" as="geometry" /></mxCell>',
             'valve': 'style="verticalLabelPosition=bottom;align=center;html=1;movableLabel=1;verticalAlign=top;pointerEvents=1;dashed=0;shape=mxgraph.pid2valves.valve;valveType=gate;fillColor=#FFFFFF;" vertex="1" parent="1"><mxGeometry x="240" y="110" width="20" height="10" as="geometry" /></mxCell>',
             'ballvalve': 'style="verticalLabelPosition=bottom;align=center;html=1;verticalAlign=top;pointerEvents=1;dashed=0;shape=mxgraph.pid2valves.valve;valveType=ball" vertex="1" parent="1"><mxGeometry x="480" y="250" width="20" height="14" as="geometry" /></mxCell>',
             'checkvalve': 'style="verticalLabelPosition=bottom;align=center;html=1;verticalAlign=top;pointerEvents=1;dashed=0;shape=mxgraph.pid2valves.valve;valveType=check;" vertex="1" parent="1"><mxGeometry x="670" y="230" width="20" height="9" as="geometry" /></mxCell>',
             'valve_nc': 'style="verticalLabelPosition=bottom;align=center;html=1;verticalAlign=top;pointerEvents=1;dashed=0;shape=mxgraph.pid2valves.valve;valveType=gate;defState=closed" vertex="1" parent="1"><mxGeometry x="670" y="256.75" width="20" height="9" as="geometry" /></mxCell>',
             'needlevalve': 'style="verticalLabelPosition=bottom;align=center;html=1;verticalAlign=top;pointerEvents=1;dashed=0;shape=mxgraph.pid2valves.valve;valveType=needle" vertex="1" parent="1"><mxGeometry x="740" y="305" width="20" height="10" as="geometry" /></mxCell>',
             '3w_valve': 'style="verticalLabelPosition=bottom;align=center;html=1;verticalAlign=top;pointerEvents=1;dashed=0;shape=mxgraph.pid2valves.valve;valveType=threeWay;actuator=none" vertex="1" parent="1"><mxGeometry x="740" y="360" width="20" height="14" as="geometry" /></mxCell>',
             'gatevalve': 'style="verticalLabelPosition=bottom;align=center;html=1;verticalAlign=top;pointerEvents=1;dashed=0;shape=mxgraph.pid2valves.valve;valveType=gate;actuator=man" vertex="1" parent="1"><mxGeometry x="670" y="300" width="20" height="20" as="geometry" /></mxCell>',
             'controlvalve': 'style="verticalLabelPosition=bottom;align=center;html=1;verticalAlign=top;pointerEvents=1;dashed=0;shape=mxgraph.pid2valves.valve;valveType=gate;actuator=powered" vertex="1" parent="1"><mxGeometry x="740" y="250" width="20" height="22.5" as="geometry" /></mxCell>',
             'filter':  'style="verticalLabelPosition=bottom;outlineConnect=0;align=center;dashed=0;html=1;verticalAlign=top;shape=mxgraph.pid.misc.air_filter;movableLabel=1;" vertex="1" parent="1"><mxGeometry x="130" y="900" width="40" height="40" as="geometry" /></mxCell>',
             'reboiler': 'style="shape=mxgraph.pid.heat_exchangers.reboiler;html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="279" y="610" width="161" height="60" as="geometry" /></mxCell>',
             'fan': 'style="verticalLabelPosition=bottom;outlineConnect=0;align=center;dashed=0;html=1;verticalAlign=top;shape=mxgraph.pid2misc.fan;fanType=common" vertex="1" parent="1"><mxGeometry x="140" y="260" width="50" height="50" as="geometry" /></mxCell>',
             'knockoutdrum':  'style="shape=mxgraph.pid.vessels.knock-out_drum;html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="540" y="360" width="51" height="95" as="geometry" /></mxCell>',
             'tank': 'style="shape=mxgraph.pid.vessels.tank;html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="670" y="430" width="40" height="95" as="geometry" /></mxCell>',
             'mixingreactor': 'style="shape=mxgraph.pid.vessels.mixing_reactor;html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="530" y="265.75" width="50" height="96" as="geometry" /></mxCell>',
             'gearpump': 'style="shape=mxgraph.pid.pumps_-_iso.pump_(gear);html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="480" y="55" width="40" height="40" as="geometry" /></mxCell>',
             'diaphragmpump': 'style="shape=mxgraph.pid.pumps_-_iso.pump_(diaphragm);html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="560" y="55" width="40" height="40" as="geometry" /></mxCell>',
             'screwpump': 'style="shape=mxgraph.pid.pumps_-_iso.pump_(screw);html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="550" y="199" width="40" height="41" as="geometry" /></mxCell>',
             'pump_std': 'style="shape=mxgraph.pid.pumps_-_iso.pump_(liquid);html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="650" y="118.5" width="40" height="43" as="geometry" /></mxCell>',
             'pump_centri': 'style="shape=mxgraph.pid.pumps_-_iso.pump_(centrifugal);html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="710" y="435" width="40" height="40" as="geometry" /></mxCell>',
             'pump_jet': 'style="shape=mxgraph.pid.pumps_-_iso.jet_pump_(liquid);html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="600" y="560" width="40" height="40" as="geometry" /></mxCell>',
             'heatexchanger_2': 'style="shape=mxgraph.pid.heat_exchangers.shell_and_tube_heat_exchanger_2;html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="380" y="590" width="40" height="40" as="geometry" /></mxCell>',
             'shelltube': 'style="shape=mxgraph.pid.heat_exchangers.heat_exchanger_(straight_tubes);html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="221" y="595" width="100" height="30" as="geometry" /></mxCell>',
             'condenser': 'style="shape=mxgraph.pid.heat_exchangers.condenser;html=1;pointerEvents=1;align=center;verticalLabelPosition=bottom;verticalAlign=top;dashed=0;" vertex="1" parent="1"><mxGeometry x="92" y="710" width="48" height="50" as="geometry" /></mxCell>',
             'filter_2': 'style="verticalLabelPosition=bottom;outlineConnect=0;align=center;dashed=0;html=1;verticalAlign=top;shape=mxgraph.pid.misc.filter_2;" vertex="1" parent="1"><mxGeometry x="614.5" y="570" width="40" height="45" as="geometry" /></mxCell>',
             'traycolumn': 'style="verticalLabelPosition=bottom;outlineConnect=0;align=center;dashed=0;html=1;verticalAlign=top;shape=mxgraph.pid2misc.column;columnType=tray" vertex="1" parent="1"><mxGeometry x="760" y="55.75" width="50" height="301" as="geometry" /></mxCell>',
             'fluidizedbed': 'style="verticalLabelPosition=bottom;outlineConnect=0;align=center;dashed=0;html=1;verticalAlign=top;shape=mxgraph.pid2misc.column;columnType=fluid" vertex="1" parent="1"><mxGeometry x="670" y="372" width="50" height="120" as="geometry" /></mxCell>',
             'reducer': 'style="verticalLabelPosition=bottom;align=center;dashed=0;html=1;verticalAlign=top;shape=mxgraph.pid.piping.concentric_reducer;" vertex="1" parent="1"><mxGeometry x="160" y="585" width="20" height="20" as="geometry" /></mxCell>',
             'membrane': 'style="verticalLabelPosition=bottom;outlineConnect=0;align=center;dashed=0;html=1;verticalAlign=top;shape=mxgraph.pid.misc.air_filter;" vertex="1" parent="1"><mxGeometry x="385" y="585" width="40" height="65" as="geometry" /></mxCell>'
}


class Unit():
    """ Process Flow Diagram Unit. """
    def __init__(self, tag, type):
        """
        :param tag:     Unit tag number.
        :param type:    Type of process unit (from components dict).
        """
        self.tag = tag
        self.type = "Unit"
        self.xml = f'<mxCell id="{tag}" value="{tag}" type="Unit" {component[type]}'


class Flow():
    """ Flow arrow. """
    def __init__(self, tag, source, target, nolabel=False, width=1, dashed=False, noarrow=False, color="black"):
        """
        :param tag:     Flow tag number.
        :param source:  Source of flow (unit tag number).
        :param target:  Target of flow (unit tag number).
        :param noarrow: Hide arrowhead.
        :param nolabel: Hide tag in PFD (True/False).
        :param width:   Line thickness.
        :param dashed:  Dashed line (True/False).
        :param color:   Line color.
        """
        self.tag = tag
        self.type = "Line"
        self.source = source
        self.target = target
        self.style = (f'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;movableLabel=1;exitX=1;'
                      f'exitY=0.5;exitDx=0;exitDy=0;jumpStyle=gap;jumpSize=10;strokeWidth={width};strokeColor={color};'
                      f'{"dashed=1;" if dashed else ""}'
                      f'{"noLabel=1;fontColor=none;" if nolabel else "noLabel=0;" }'
                      f'{"endArrow=none;endFill=0;" if noarrow else "" }')
        self.xml = f'<mxCell id="{tag}" value="{tag}" type="Line" style="{self.style}" parent="1" source="{source}" target="{target}" edge="1"><mxGeometry relative="1" as="geometry"/></mxCell>'


class Sensor():
    """ Sensor unit. """
    def __init__(self, tag, indicator, number):
        """
        :param tag:         Sensor tag number.
        :param indicator    Sensor icon upper text.
        :param number       Sensor icon lower text.
        """
        self.tag = tag
        self.type = "Sensor"
        self.xml = (f'<mxCell id="{tag}" type="Sensor" value="&lt;table cellpadding=&quot;4&quot; cellspacing=&quot;0&quot;'
                    f'border=&quot;0&quot; style=&quot;font-size: 8px; width: 100%; height: 100%;&quot;&gt;&lt;'
                    f'tbody style=&quot;font-size: 8px;&quot;&gt;&lt;tr style=&quot;font-size: 8px;&quot;&gt;&lt;td style=&quot;'
                    f'font-size: 8px;&quot;&gt;{indicator}&lt;/td&gt;&lt;/tr&gt;&lt;tr style=&quot;font-size: 8px;&quot;&gt;&lt;td '
                    f'style=&quot;font-size: 8px;&quot;&gt;{number}&lt;/td&gt;&lt;/tr&gt;&lt;/tbody&gt;&lt;/table&gt; " '
                    f'style="html=1;movableLabel=1;outlineConnect=0;align=center;dashed=0;aspect=fixed;shape=mxgraph.pid2inst.discInst;'
                    f'mounting=room;fontSize=8;" vertex="1" parent="1"><mxGeometry x="60" y="80" width="30" height="30" as="geometry" />'
                    f'</mxCell>')


class Connector(Flow):
    """ Connector line (no arrow). """
    def __init__(self, tag, source, target, noarrow=True, nolabel=True, width=1, dashed=True, color="black"):
        """
        :param tag:     Connector tag number.
        :param soruce:  Source of connector (tag number).
        :param target:  Target of connector (tag number).
        :param noarrow: Hide arrow end of line.
        :param nolabel: Hide tag in PFD (True/False).
        :param width:   Line thickness.
        :param dashed:  Dashed line (True/False).
        :param color:   Line color.
        """
        super().__init__(tag, source, target, noarrow=True, nolabel=True, width=1, dashed=True, color="black")


def write_pfd(file, components):
    """
    Write XML for app.diagrams.net Process Flow Diagram of components.

    If file exist, units, flows and sensors will be updated in case of deviations in defined components or flows, or flow styles.
    Resulting XML can be imported in browser editor at https://app.diagram.net

    :param file:        File name (example.xml).
    :param components:  List of included defined process components (tags).
    """
    # Build component xml and tag dictionary
    xml = ""
    tags = {}
    for tag in components:
        xml = tag.xml + xml
        if tag.type == "Line":
            source = tag.source
            target = tag.target
            style = tag.style
        else:
            source = None
            target = None
            style = None
        tags[tag.tag] = [tag.xml, source, target, style, tag.type] # Tag dictionary with xml and info on flows

    if not path.exists(file): # Create new XML-file:
        text= f'New Process Flow Diagram written to "{file}".'
        pfd = f'<?xml version="1.0" encoding="UTF-8"?><mxfile host="app.diagrams.net" modified="{datetime.datetime.now()}" agent="pchemeng.tools.simplepfd" etag="Ym8JUHmCbybyuN_C31Ly" version="12.9.13" type="device"><diagram id="S1Gz87AjEctzsXtTaDJA" name="Page-1"><mxGraphModel dx="1422" dy="757" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0"><root><mxCell id="0" /><mxCell id="1" parent="0" />{xml}</root></mxGraphModel></diagram></mxfile>'
        soup = BeautifulSoup(pfd, "xml")

        # Position all units in an inital diagonal pattern without overlap
        i = 0
        for id in soup.find_all('mxCell'):
            if id.get('type') == "Unit":
                x = y = i = i + 30
                id.find('mxGeometry')['x'] = x
                id.find('mxGeometry')['y'] = y

    else:  # Update existing XML-file:
        if path.exists(file):
            text = f'Process Flow Diagram file "{file}" checked for updates and saved.'
            with open(file) as f:
                soup = BeautifulSoup(f, "xml")

            # Collect file tags and xml:
            file_tags = {}
            for id in soup.find_all('mxCell'):
                if id.get('id') not in ['0', '1', None]:
                    file_tags[id.get('id')] = id

            # Delete xml-tag in file if it is not in the defined list of components:
            for tag in file_tags.keys():
                if tag not in tags.keys():
                    print(f'PFD Tag {tag} not in list of components => It will be deleting from PFD.')
                    soup.find('mxCell', {'id': tag}).decompose()

            # Insert tag if it is not already in the xml-file:
            for tag in tags.keys():
                if tag not in file_tags.keys():
                    print(f'New tag - {tag} - registered. Will be added to PFD.')
                    soup.find('root').append(BeautifulSoup(tags[tag][0], "xml"))

            # If tag is flow or connector, update style - and tag if connections changed:
            for id in soup.find_all('mxCell'):
                if id.get('type') == "Line":
                #if id.get('source') != None:
                    tag = id.get('id')
                    source = id.get('source')
                    target = id.get('target')
                    style = id.get('style')

                    if style != tags[tag][3]:
                        print(f'{tags[tag][4]} - {tag} - changed style. Will be updated in PFD.')
                        id['style'] = tags[tag][3]

                    if ((tags[tag][1]) != source) or ((tags[tag][2]) != target):
                        print(f'Flow - {tag} - changed source or target. Will be updated in PFD.')
                        soup.find('mxCell', {'id': tag}).decompose()
                        soup.find('root').append(BeautifulSoup(tags[tag][0], 'xml'))

    f = open(file, "w")
    f.write(str(soup.prettify()))
    f.close()
    print(f'{text} Open in https://app.diagrams.net/ for editing. Export as uncompressed XML for keeping editable PFD format.')


def components_from_mel(file):
    """
    Define PFD components and flows from MEL (main equipment list)

    CSV formatting:
                    - ',' as column separation
                    - ';' as separation of tag flows in flows_to column
                    - Flow styles inside '()' separated by '&')

    CSV headers applied for PFD rendering:

                     tag - unit or flow tag name
                     type - type of component (units are component dict keys)
                     flows_to - tag names as sources for outgoing unit flows: '<Tag name 1>(<styles>);<Tag name 2>(<styles>)'
                                'None' if no outgoing flows.

    MEL can also contain any other extra columns - these will not affect PFD rendering.

    MEL CSV example:

    tag,type,flows_to
    Tank 1,vessel,P1
    P1,pump,C1(dashed=True&color=red&nolabel=True)
    C1,packedcolumn,air(nolabel=True&dashed=True);Tank 1(width=11&nolabel=True)
    air,text,None

    :params file:       MEL file name (.csv with abobe format
    :returns:           component list (for appplication with write_pdf() funcion
    """
    mel = pd.read_csv(file, sep=',')

    # Add given components:
    components = []
    for i in mel.index:
        tag = mel.iloc[i]['tag'].lstrip(" ").rstrip(" ")
        type = mel.iloc[i]['type'].lstrip(" ").rstrip(" ")
        components.append(Unit(tag, type))

    # Add given flows: (flow tag names are automatic numbered F#)
    y = 0
    for i in mel.index:
        tag = mel.iloc[i]['tag'].lstrip(" ").rstrip(" ")
        flows_to = mel.iloc[i]['flows_to'].split(';')

        for flow in flows_to:
            if flow != "None":
                flow = flow.rstrip(" ").lstrip(" ")
                if '(' in flow:  # If styles are given
                    target = re.findall(r'(.*?)\(.*?\)', flow)[0]
                    styles = re.findall(r'\((.*?)\)', flow)[0].split('&')
                    kwargs_style = {}
                    for style in styles:
                        kwargs_style[style.split('=')[0]] = style.split('=')[1]
                else:
                    target = flow
                    kwargs_style = {}
                components.append(Flow(f'F{y}', tag, target, **kwargs_style))
            y = y + 1
    return components


def example():
    """
    Example of functionality (PFD defined object oriented or from MEL)
    PFD written to 'example.xml'
    """

    # Define units, sensors and flows:
    boxA = Unit('Box A', 'box')
    boxB = Unit('Box B', 'box')
    flow1 = Flow('flow','Box A','Box B', width=3, dashed=False, color='green', nolabel=True)
    conn1 = Connector('reg','Box A','Box B', width=1, color='green')
    T1 = Sensor('T1','TT','01')
    conn2 = Connector('conn-1','T1','Box A',nolabel=True)
    conn3 = Connector('conn-2','T1','Box B',nolabel=True)


    # Define units part of process flow diagram;
    object_component = [boxA, conn1, flow1, boxB, T1, conn2, conn3]

    # Define units from MEL;
    mel_components = components_from_mel('mel.csv')

    # Write XML-file for import in DrawIO:
    write_pfd("example.xml", object_component + mel_components)


if __name__ == "__main__":
    example()
