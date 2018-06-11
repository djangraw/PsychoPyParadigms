#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Disconnect EGI EEG system
"""

# === Set up
isEegConnected = True
tcpipAddress = '10.10.10.42'
tcpipPort = 55513

# === Initialize
if isEegConnected == False:
    print('Using Fake EGI system for debugging...')
    # # This will import the debugging version of the PyNetStation module,
    # #  which will not actually attempt a connection but will check to make sure
    # #  your code is properly functioning.
    import egi.fake as egi  # FOR TESTING WITHOUT CONNECTION TO NETSTATION COMPUTER
else:
    print('Setting up EGI system...')
    # # This will import the single-threaded version of the PyNetStation module
    import egi.simple as egi # FOR RUNNING CONNECTED TO NETSTATION COMPUTER -- USE THIS IN A REAL EXPERIMENT

# === Netstation Obj
# # Create the NetStation event-sending object. After this you can call
# #  the methods via the object instance, in this case 'ns'.
ns = egi.Netstation()

# === Establish Cxn
# # The next line is for connecting the actual, single-threaded module version to the computer.
if isEegConnected:
    print('Connecting to EGI system...')
    ns.connect(tcpipAddress, tcpipPort)  # sample address and port -- change according to your network settings

# === Link Expt to Session
# # This sends some initialization info to NetStation for recording events.
print('Starting/synching session...')
ns.BeginSession()
# # This synchronizes the clocks of the stim computer and the NetStation computer.
ns.sync()

# === DISCONNECT
print('Ending session...')
#ns.StopRecording()
ns.EndSession()
print('Disconnecting...')
ns.disconnect()
print('Done!')