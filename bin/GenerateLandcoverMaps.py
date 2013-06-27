#!/usr/bin/env python
"""@package GenerateLandcoverMaps

@brief Import landcover raster maps into a GRASS location and generate 
landcover, lai, and impervious coverage maps.

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

2. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
   landcover_rast
   
3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   paramdb
   paramdb_dir
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   landcover_road_rule
   landcover_impervious_rule
   landcover_stratum_rule
   landcover_landuse_rule
   landcover_lai_rule
   
Post conditions
---------------
1. Will write the following entry(ies) to the GRASS section of metadata associated with the project directory:
   roads_rast
   impervious_rast
   landuse_rast
   stratum_rast
 
Usage:
@code
GenerateLandcoverMaps.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys, shutil
import argparse
import importlib

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Generate landcover maps in GRASS GIS')
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
grassMetadata = RHESSysMetadata.readGRASSEntries(context)
if not 'landcover_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a landcover raster" % (context.projectDir,))

metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))
if not 'paramdb_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a ParamDB directory" % (context.projectDir,))
if not 'paramdb' in metadata:
    sys.exit("Metadata in project directory %s does not contain a ParamDB" % (context.projectDir,))

paramDbPath = os.path.join(context.projectDir, metadata['paramdb'])
if not os.access(paramDbPath, os.R_OK):
    sys.exit("Unable to read RHESSys parameters database %s" % (paramDbPath,) )
paramDbPath = os.path.abspath(paramDbPath)

roadRulePath = os.path.join(context.projectDir, metadata['landcover_road_rule'])
if not os.access(roadRulePath, os.R_OK):
    sys.exit("Unable to read rule %s" % (roadRulePath,) )    
imperviousRulePath = os.path.join(context.projectDir, metadata['landcover_impervious_rule'])
if not os.access(imperviousRulePath, os.R_OK):
    sys.exit("Unable to read rule %s" % (imperviousRulePath,) )
landuseRulePath = os.path.join(context.projectDir, metadata['landcover_landuse_rule'])
if not os.access(landuseRulePath, os.R_OK):
    sys.exit("Unable to read rule %s" % (landuseRulePath,) )
stratumRulePath = os.path.join(context.projectDir, metadata['landcover_stratum_rule'])
if not os.access(stratumRulePath, os.R_OK):
    sys.exit("Unable to read rule %s" % (stratumRulePath,) )

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])

# Import ParamDB from project directory
sys.path.append( os.path.join(context.projectDir, metadata['paramdb_dir']) )
params = importlib.import_module('rhessys.params')
paramConst = importlib.import_module('rhessys.constants')
paramDB = params.paramDB(filename=paramDbPath)

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

landcoverRast = grassMetadata['landcover_rast']

# Reclassify landcover into stratum map
result = grassLib.script.read_command('r.reclass', input=landcoverRast, output='stratum', 
                           rules=stratumRulePath, overwrite=args.overwrite)
if None == result:
    sys.exit("r.reclass failed to create stratum map, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'stratum_rast', 'stratum')

# Fetch relevant stratum default files from param DB
pipe = grassLib.script.pipe_command('r.stats', flags='licn', input='stratum')
rasterVals = {}
for line in pipe.stdout:
    (dn, cat, num) = line.strip().split()
    if cat != 'NULL':
        rasterVals[cat] = int(dn)
pipe.wait()
print("Writing stratum default files to %s" % (paths.RHESSYS_DEF) )
for key in rasterVals.keys():
    print("stratum '%s' has dn %d" % (key, rasterVals[key]) )
    paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, key, None, None, None, None, None, None, None, None)
    assert(paramsFound)
    paramDB.writeParamFiles(paths.RHESSYS_DEF)

# Reclassify landcover into landuse map
result = grassLib.script.read_command('r.reclass', input=landcoverRast, output='landuse', 
                           rules=landuseRulePath, overwrite=args.overwrite)
if None == result:
    sys.exit("r.reclass failed to create stratum map, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'landuse_rast', 'landuse')

# Fetch relevant landuse default files from param DB
pipe = grassLib.script.pipe_command('r.stats', flags='licn', input='landuse')
rasterVals = {}
for line in pipe.stdout:
    (dn, cat, num) = line.strip().split()
    if cat != 'NULL':
        rasterVals[cat] = int(dn)
pipe.wait()
print("Writing landuse default files to %s" % (paths.RHESSYS_DEF) )
for key in rasterVals.keys():
    print("landuse '%s' has dn %d" % (key, rasterVals[key]) )
    paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, key, None, None, None, None, None, None, None, None)
    assert(paramsFound)
    paramDB.writeParamFiles(paths.RHESSYS_DEF)

# Reclassify landcover into road map
result = grassLib.script.read_command('r.reclass', input=landcoverRast, output='roads', 
                           rules=roadRulePath, overwrite=args.overwrite)
if None == result:
    sys.exit("r.reclass failed to create roads map, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'roads_rast', 'roads')    

# Reclassify landcover into impervious map
result = grassLib.script.read_command('r.reclass', input=landcoverRast, output='impervious', 
                           rules=imperviousRulePath, overwrite=args.overwrite)
if None == result:
    sys.exit("r.reclass failed to create impervious map, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'impervious_rast', 'impervious')    

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)