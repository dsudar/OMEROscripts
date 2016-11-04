#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 hcs_scripts/Screen_RenderSettings.py

This script sets the rendering settings for all images in a list of screens

@author Damir Sudar
<a href="mailto:dsudar@qimagingsys.com">dsudar@qimagingsys.com</a>
@version 0.1
From example by Will Moore
"""

import omero.scripts as scripts
from omero.gateway import BlitzGateway
import omero.util.script_utils as script_utils
import omero
import time

from omero.rtypes import rint, rlong, rstring, robject, unwrap

COLOURS = script_utils.COLOURS

startTime = 0

def printDuration(output=True):
    global startTime
    if startTime == 0:
        startTime = time.time()
    if output:
        print "Script timer = %s secs" % (time.time() - startTime)


def set_rendersettings_screen(conn, scriptParams, screen):

    updateService = conn.getUpdateService()

    resetToImport = "Reset_To_Imported" in scriptParams and \
        scriptParams['Reset_To_Imported'] is True

    colourMap = {}
    if "Channel_Colours" in parameterMap:
        for c, colour in enumerate(parameterMap["Channel_Colours"]):
            if colour in COLOURS:
                colourMap[c] = COLOURS[colour]
    print "colourMap", colourMap

    print "Setting rendering settings for Screen: %d %s" \
        % (screen.getId(), screen.getName())

    # sort plates by name (and possible filter by name in future)
    plates = list(screen.listChildren())
    PlateCount = len(plates)
#    if "Filter_Names" in scriptParams:
#        filterBy = scriptParams["Filter_Names"]
#        print "Filtering images for names containing: %s" % filterBy
#        images = [i for i in images if (i.getName().find(filterBy) >= 0)]
#    images.sort(key=lambda x: x.name.lower())

    return

    for plate in plates:
        print "    working on plate : %d %s " \
            % (plate.getId(), plate.getName())

        for well in plate.listChildren():
             index = well.countWellSample()
             for i in xrange(0,index):
                  image = well.getImage(i)
                  if resetToImport:
                      image.resetDefaults(save=True)
                  else:
                      image.setColorRenderingModel()
                      channels = [1, 2, 3, 4]
                      colorList = ['0000FF', '00FF00', 'FF0000', 'EE82EE']
                      image.setActiveChannels(channels, colors=colorList)
                      image.saveDefaults()

    return


def set_rendersettings(conn, scriptParams):

    updateService = conn.getUpdateService()

    message = ""

    # Get the object IDs
    objs, logMessage = script_utils.getObjects(conn, scriptParams)
    message += logMessage

    # Return if all input screens are not found or excluded
    if not objs:
        return message

    # Filter object IDs by permissions (future)
#    IDs = [ob.getId() for ob in objs if ob.canLink()]
#    if len(IDs) != len(objs):
#        permIDs = [str(ob.getId()) for ob in objs if not ob.canLink()]
#        message += "You do not have permission to change rendering settings on images in"\
#            " screen(s): %s." % ",".join(permIDs)
#    if not IDs:
#        return None, message

    for ob in objs:
        set_rendersettings_screen(conn, scriptParams, ob)

    return message


def runAsScript():
    """
    The main entry point of the script, as called by the client via the
    scripting service, passing the required parameters.
    """
    printDuration(False)    # start timer

    ckeys = COLOURS.keys()
    ckeys.sort()
    cOptions = [rstring(col) for col in ckeys]

    dataTypes = [rstring('Screen')]

    client = scripts.client(
        'HCS _RenderSettings.py',
        """Sets the rendering settings for all images in a list of screens""",

        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Choose container of images (only Screen supported)",
            values=dataTypes, default="Screen"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="List of Screen IDs to process").ofType(rlong(0)),

        scripts.Bool(
            "Reset_To_Imported", grouping="3", default=False,
            description="Reset all rendering settings to original Imported values"
            "Arguments below will be ignored"),

        scripts.List(
            "Channel_Colours", grouping="4",
            description="List of Colours for channels.", default="White",
            values=cOptions).ofType(rstring("")),

        scripts.List(
            "Channel_Names", grouping="5",
            description="List of Names for channels in the new image."),

        version="0.0.1",
        authors=["Damir Sudar"],
        institutions=["Quantitative Imaging Systems LLC"],
        contact="ome-users@lists.openmicroscopy.org.uk",
    )

    try:
        scriptParams = client.getInputs(unwrap=True)
        print scriptParams

        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)

        # set the desired rendering settings
        message = set_rendersettings(conn, scriptParams)

        client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()
        printDuration()

if __name__ == "__main__":
    runAsScript()
