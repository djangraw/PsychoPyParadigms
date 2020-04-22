#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
RecoverPavloviaCsvsFromDatabase.py
Recover the .csv files of individual subjects from a multi-subject pavlovia database.

Created on Wed Apr 22 08:01:54 2020
@author: jangrawdc
"""

# Import packages
import pandas as pd
import numpy as np
import os.path
import argparse
import time

# Declare main function
def RecoverPavloviaCsvsFromDatabase(dbFile,outFolder='.'):
    """ Recover the .csv files of individual subjects from a multi-subject pavlovia database.
    
    INPUTS:
    - dbFile is a Pavlovia database file (.csv) containing data from multiple subjects.
    - outFolder is the folder where individual subject output files should go (default: '.').
    
    OUTPUTS:
    - A .csv file for each subject will be saved in outFolder, named <subj>_<experimentName>_<datetime>.csv.
    """
    
    # Make sure file & folder exist
    assert os.path.exists(dbFile), 'Pavlovia database file %s does not exist!'%dbFile
    assert os.path.exists(outFolder), 'Output folder %s does not exist!'%outFolder
    
    # Time processing
    tStart = time.time();
    
    # Import file
    print('===== Reading Pavlovia database file %s...'%dbFile)
    dfAll = pd.read_csv(dbFile);
    
    # Separate data
    subjs = np.unique(dfAll.participant)
    nSubj = np.size(subjs)
    print('===== Separating data from %d subjects...'%nSubj)
    for subj in subjs:
        print('-- Subject %s'%subj)
        dfThis = dfAll.loc[dfAll.participant==subj,:].reset_index(drop=True);
        expName = dfThis['__experimentName'].values[0]
        datetime = dfThis['__datetime'].values[0]
        outFile = '%s_%s_%s.csv'%(subj,expName,datetime)
        print('   Saving %s...'%outFile)
        dfThis.to_csv('%s/%s'%(outFolder,outFile),index=False);
    print('==== Done! Took %.1f seconds.'%(time.time()-tStart))    

# %% Make command-line argument parser
parser = argparse.ArgumentParser(description='Recover the .csv files of individual subjects from a multi-subject pavlovia database.')
# Add arguments
parser.add_argument('--dbFile', required=True, help='Pavlovia database file (.csv)')
parser.add_argument('--outFolder', default='.', help='folder where individual subject output files should go')

# %% ==== COMMAND-LINE MAIN FUNCTION ==== 

if __name__ == '__main__':
    
    # Parse inputs
    args = parser.parse_args();
 
    # Import data
    RecoverPavloviaCsvsFromDatabase(args.dbFile,args.outFolder)