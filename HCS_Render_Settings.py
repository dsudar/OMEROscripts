#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 hcs_scripts/HCS_Render_Settings.py

This script sets the rendering settings for all images in a list
of screens or plates

@author Damir Sudar
<a href="mailto:dsudar@qimagingsys.com">dsudar@qimagingsys.com</a>
@version 0.0.1
From examples by Will Moore
"""

import omero.scripts as scripts
from omero.gateway import BlitzGateway
import omero.util.script_utils as script_utils
import omero
import time

from omero.rtypes import rint, rlong, rstring, robject, unwrap

COLORS = {
    'Red': 'FF0000',
    'Green': '00FF00',
    'Blue': '0000FF',
    'Yellow': 'FFFF00',
    'White': 'FFFFFF',
    'Violet': 'EE85EE',
    'Indigo': '4F0684',
    'Black': '000000',
    'Orange': 'FEC806',
    'Gray': '828282',
    'NoChange': None, }


startTime = 0

def printDuration(output=True):
    global startTime
    if startTime == 0:
        startTime = time.time()
    if output:
        print "Script timer = %s secs" % (time.time() - startTime)


def set_rendersettings_plate(conn, scriptParams, plate):

    updateService = conn.getUpdateService()

    resetToImport = "Reset_To_Imported" in scriptParams and \
        scriptParams['Reset_To_Imported'] is True

    colorList = [None, None, None, None, None, None, None]
    if "Channel_Colours" in scriptParams:
        for c, colour in enumerate(scriptParams["Channel_Colours"]):
            if colour in COLORS:
                colorList[c] = COLORS[colour]
    # print "colorList", colorList

    allchannels = range(1, len(colorList) + 1)
    channels = []
    if 'Channels' in scriptParams:
        channels = [i for i in scriptParams['Channels']]

#    print "allchannels", allchannels
#    print "channels", channels

    rangeList = []
    if "Source_ImageID" in scriptParams and len(scriptParams["Source_ImageID"]) > 0:
        ii = scriptParams['Source_ImageID']
        try:
            imageID = long(ii)
            simage = conn.getObject("Image", imageID)
        except ValueError:
            return

        for ch in simage.getChannels():
#            print "  Levels:", ch.getWindowStart(), "-", ch.getWindowEnd()
            rangeList.append([ch.getWindowStart(), ch.getWindowEnd()])
#            print rangeList

    print "    working on plate {} {}:".format(plate.getId(), plate.getName())

    for well in plate.listChildren():
         index = well.countWellSample()
         for i in xrange(0,index):
              image = well.getImage(i)
              if resetToImport:
                  image.resetDefaults(save=True)
              else:
                  image.setColorRenderingModel()
                  if rangeList != []:
                      image.setActiveChannels(allchannels, colors=colorList, windows=rangeList)
                  else:
                      image.setActiveChannels(allchannels, colors=colorList)
                  if channels != []:
                      image.setActiveChannels(channels)
                  image.saveDefaults()

    return


def set_rendersettings(conn, scriptParams):

    updateService = conn.getUpdateService()

    message = ""

    # Get the object IDs
    objs, logMessage = script_utils.getObjects(conn, scriptParams)
    message += logMessage

    # Return if all input containers are not found or excluded
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
        dataType = scriptParams["Data_Type"]
        if (dataType == "Screen"):
            print "Setting rendering settings for Screen: %d %s" \
                % (ob.getId(), ob.getName())

            # sort plates by name (and possible filter by name in future)
            plates = list(ob.listChildren())

            for plate in plates:
                set_rendersettings_plate(conn, scriptParams, plate)

        elif (dataType == "Plate"):
            set_rendersettings_plate(conn, scriptParams, ob)
        else:
    	    message += "Invalid Data_Type"

    return message


def runAsScript():
    """
    The main entry point of the script, as called by the client via the
    scripting service, passing the required parameters.
    """
    printDuration(False)    # start timer

    ckeys = COLORS.keys()
    ckeys.sort()
    cOptions = [rstring(col) for col in ckeys]

    dataTypes = [rstring('Screen'), rstring('Plate')]

    client = scripts.client(
        'HCS_Render_Settings.py',
        """Sets the rendering settings for all images in a list of screens or plates""",

        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Choose container of images (Screen and Plate supported)",
            values=dataTypes, default="Screen"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="List of Screen or Plate IDs to process").ofType(rlong(0)),

        scripts.Bool(
            "Reset_To_Imported", grouping="3", default=False,
            description="Reset all rendering settings to original Imported values."
            " Arguments below will be ignored"),

        scripts.List(
            "Channel_Colours", grouping="4",
            description="List of Colours for channels.", default="NoChange",
            values=cOptions).ofType(rstring("")),

        scripts.List(
            "Channels", grouping="5",
            description="Optional list of channels to enable. All channels"
            " enabled by default.").ofType(omero.rtypes.rint(0)),

        scripts.String(
             "Source_ImageID", grouping="6",
             description="Optional source imageID from which to take min/max"
             " rendering settings per channel."),

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
