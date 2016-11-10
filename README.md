# OMEROscripts

Dataset_To_Well.py: moves all images in a single Dataset to a single specified Well
in a Plate as fields in that Well. If the Plate already exists, provide the Plate ID
and if it doesn't yet exist, provide a name to be given to the new Plate and get
back the Plate ID for that new Plate. 

Wells_To_Plate.py: generate (a) Plate(s) from all the Fields in (a) Well(s).
Optionally, add the new Plate to a Screen. 

HCS_Render_Settings: apply new rendering settings to all images in a list of Screens
or Plates in bulk and has the following options:
1) reset to imported (all others below are then ignored)
2) only change the assigned colors per channel (without changing the min/max
3) turn on/off certain channel's visibility
4) set the min/max from an example image provided
In principle one should be able to apply multiple options simultaneously but there's
a bug somewhere that causes some strange behaviour. 

