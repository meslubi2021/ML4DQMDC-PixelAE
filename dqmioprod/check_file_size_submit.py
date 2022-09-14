###################################################################
# Check the size of a nanoDQMIO file as a function of its content #
###################################################################

import sys
import os
import argparse
import json
sys.path.append('../jobsubmission')
import condortools as ct

if __name__=='__main__':

  # read arguments
  parser = argparse.ArgumentParser(description='Check file size')
  parser.add_argument('--cmssw', required=True,
                      help='Path to CMSSW release for working environment.')
  parser.add_argument('--rawfile', required=True,
                      help='Raw file as input.')
  parser.add_argument('--cmsdriver', required=True,
                      help='Path to txt file with cmsDriver command.')
  parser.add_argument('--conf', required=True,
                      help='Path to file with configurable nanoDQMIO contents.')
  parser.add_argument('--outdirname', default='output_check_file_size',
                      help='Results directory to be created in the specified CMSSW area.')
  parser.add_argument('--runmode', choices=['condor','local'], default='condor',
                      help='Choose from "condor" or "local";'
                             +' in case of "condor", will submit job to condor cluster;'
                             +' in case of "local", will run interactively in the terminal.')
  parser.add_argument('--jobflavour', default='workday',
                        help='Set the job flavour in lxplus'
                             +' (see https://batchdocs.web.cern.ch/local/submit.html)')
  args = parser.parse_args()
  cmssw = os.path.join(os.path.abspath(args.cmssw),'src')
  rawfile = os.path.abspath(args.rawfile)
  cmsdriverfile = os.path.abspath(args.cmsdriver)
  conffile = os.path.abspath(args.conf)
  outdirname = args.outdirname
  runmode = args.runmode
  jobflavour = args.jobflavour

  # print arguments
  print('Running with following configuration:')
  for arg in vars(args):
    print('  - {}: {}'.format(arg,getattr(args,arg)))

  # check all arguments
  if not os.path.exists(cmssw):
    raise Exception('ERROR: CMSSW version {} does not exist.'.format(cmssw))
  if not os.path.exists(rawfile):
    raise Exception('ERROR: input file {} does not exist.'.format(rawfile))
  if not os.path.exists(cmsdriverfile):
    raise Exception('ERROR: cmsDriver file {} does not exist.'.format(cmsdriverfile))
  if not os.path.exists(conffile):
    raise Exception('ERROR: configuration file {} does not exist.'.format(conffile))

  # check the output directory
  outdir = os.path.join(cmssw,outdirname)
  if os.path.exists(outdir):
    raise Exception('ERROR: output dir {} already exists.'.format(outdir))

  # check nanoDQMIO configuration file
  nanoconffile = os.path.join(cmssw,'DQMServices/Core/python/nanoDQMIO_perLSoutput_cff.py')
  if not os.path.exists(nanoconffile):
    raise Exception('ERROR: configuration file {} does not exist.'.format(nanoconffile))

  # make the commands
  cmds = []
  cwd = os.path.abspath(os.getcwd())
  cmds.append( 'cd {}'.format(cmssw) )
  cmds.append( 'cmsenv' )
  cmds.append( 'cd {}'.format(cwd) )
  pcmd = 'python check_file_size.py'
  argstoremove = ['runmode', 'jobflavour']
  for arg in vars(args):
    if( arg not in argstoremove ):
      pcmd += ' --{} {}'.format(arg,getattr(args,arg))
  cmds.append(pcmd)

  # submit the job
  if runmode=='local':
    scriptname = 'local_check_file_size.sh'
    ct.initJobScript(scriptname, home='auto')
    with open(scriptname,'a') as f:
      for cmd in cmds: f.write('{}\n'.format(cmd))
    os.system('bash {}'.format(scriptname))
  if runmode=='condor':
    ct.submitCommandsAsCondorJob('cjob_check_file_size', cmds,
                      home='auto', jobflavour=jobflavour)
