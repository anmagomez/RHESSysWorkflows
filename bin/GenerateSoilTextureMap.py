#!/usr/bin/env python
"""@package GenerateSoilTextureMap

@brief Import percent sand and percent clay raster maps into a GRASS location
and generate soil texture map using r.soils.texture. 

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2013, University of North Carolina at Chapel Hill
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the University of North Carolina at Chapel Hill nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF NORTH CAROLINA AT CHAPEL HILL
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


@author Brian Miles <brian_miles@unc.edu>


Pre conditions
--------------
1. Configuration file must define the following sections and values:
   'GRASS', 'GISBASE'

2. The following metadata entry(ies) must be present in the manifest section of the metadata associated with the project directory:
   soil_raster_avgsand
   soil_raster_avgclay

3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   
4. Requires r.soils.texture GRASS extension: http://grasswiki.osgeo.org/wiki/GRASS_AddOns#r.soils.texture

Post conditions
---------------
1. Will write the following entry(ies) to the GRASS section of metadata associated with the project directory:
   soil_avgsand_rast
   soil_avgclay_rast
   soil_texture_rast

Usage:
@code
PYTHONPATH=${PYTHONPATH}:../EcohydroWorkflowLib python2.7 ./GenerateSoilTextureMap.py -p ../../../scratchspace/scratch7
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys, errno
import argparse

from rhessys.params import paramDB
import rhessys.constants as paramConst

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Generate soil texture map for dataset in GRASS GIS')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
manifest = RHESSysMetadata.readManifestEntries(context)
if not 'soil_raster_avgsand' in manifest:
    sys.exit("Metadata in project directory %s does not contain a soil_raster_avgsand raster" % (context.projectDir,))
if not 'soil_raster_avgclay' in manifest:
    sys.exit("Metadata in project directory %s does not contain a soil_raster_avgclay raster" % (context.projectDir,))

metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])
paramDB = paramDB()

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
moduleEtc = context.config.get('GRASS', 'MODULE_ETC')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

# Import percent sand and percent clay raster maps into GRASS
percentSandRasterPath = os.path.join(context.projectDir, manifest['soil_raster_avgsand'])
result = grassLib.script.run_command('r.in.gdal', input=percentSandRasterPath, output='soil_avgsand', overwrite=args.overwrite)
if result != 0:
    sys.exit("Failed to import soil_raster_avgsand into GRASS dataset %s/%s, results:\n%s" % \
             (grassDbase, metadata['grass_location'], result) )
RHESSysMetadata.writeGRASSEntry(context, 'soil_avgsand_rast', 'soil_avgsand')
    
percentClayRasterPath = os.path.join(context.projectDir, manifest['soil_raster_avgclay'])
result = grassLib.script.run_command('r.in.gdal', input=percentClayRasterPath, output='soil_avgclay', overwrite=args.overwrite)
if result != 0:
    sys.exit("Failed to import soil_raster_avgclay into GRASS dataset %s/%s, results:\n%s" % \
             (grassDbase, metadata['grass_location'], result) )
RHESSysMetadata.writeGRASSEntry(context, 'soil_avgclay_rast', 'soil_avgclay')

# Generate soil texture map
schemePath = os.path.join(moduleEtc, 'USDA.dat')
if not os.access(schemePath, os.R_OK):
    raise IOError(errno.EACCES, "Not allowed to read r.soils.texture scheme %s" % (schemePath,) )
soilTexture = os.path.join(modulePath, 'r.soils.texture')
result = grassLib.script.read_command(soilTexture, sand='soil_raster_avgsand', clay='soil_raster_avgclay',
                                      scheme=schemePath, output='soil_texture', overwrite=args.overwrite)
if None == result:
    sys.exit("r.soils.texture failed, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'soil_texture_rast', 'soil_texture')

# Fetch relevant soil default files from param DB
pipe = grassLib.script.pipe_command('r.stats', flags='licn', input='soil_texture')
textures = {}
for line in pipe.stdout:
    (dn, cat, num, ) = line.strip().split()
    if cat != 'NULL':
        textures[cat] = int(dn)
pipe.wait()
print("Writing soil default files to %s" % (paths.RHESSYS_DEF) )
for key in textures.keys():
    #print("texture %s has dn %d" % (key, textures[key]) )
    paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, key, None, None, None, None, None, None, None, None, limitToBaseClasses=True)
    paramDB.writeParamFiles(paths.RHESSYS_DEF)

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)