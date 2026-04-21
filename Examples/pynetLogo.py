import pynetlogo

# Launch NetLogo GUI
netlogo = pynetlogo.LogoLink(gui=True, netlogo_home='./NetLogo7.0.0')
# Load your model
netlogo.load_model('./NetLogo7.0.0/models/Sample Models/Social Science/Traffic Basic.nlogox')

# # Set parameters from Python
# netlogo.command('set number-of-vehicles 50')

# Run one tick``
# netlogo.command('go')

# Read results
# num_passengers = netlogo.report('count passengers')
