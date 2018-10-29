import ClientSide #custom package

import numpy as np
import argparse
import json
import os

import ClassifierFunctions as cf

from matplotlib import pyplot as plt
from future.builtins.misc import input

    

USER_INFO = "user_profile.json"
URL = #you'll need me to send you the link
FAMILIES = ["triclinic","monoclinic","orthorhombic","tetragonal",
        "trigonal","hexagonal","cubic"]

DEFAULT_SESSION = "session.json"

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str,
                        dest='fpath', help='path to the image',
                        metavar='FPATH',default=None,required=False)

    parser.add_argument('--apikey', type=str,
                        dest='key', help='apikey to securely access service',
                        metavar='KEY', required=False)

    parser.add_argument('--is-profile',
                    dest='profile', help='set if the data will is an image or a profile',
                    default=False, action="store_true",required=False)

    parser.add_argument('--session',
                        dest='session',help='Keep user preferences for multirun sessions',
                        metavar='SESSION',required=False, default=None)


    return parser



def main():
    parser = build_parser()
    options = parser.parse_args()
    if options.fpath is None:
        print("No path to data provided.\n Please enter filepath to your data")
        options.fpath = input()


    print("loading data from {}".format(options.fpath))
    image_data, calibration = ClientSide.Load_Image(options.fpath)

    # opens the user specified session
    if options.session:
        with open(options.session,'r') as f:
            session = json.load(f)

    # opens the default session    
    else:
        with open(DEFAULT_SESSION,'r') as f:
            session = json.load(f)

    # set session data
    fam = session["crystal_family"]
    provide_family = session["known_family"]
    display_type = session["display_type"]
    auto_calibrate = session["auto_calibrate"]

    try:
        print("Loading calibration from {}".format(auto_calibrate))  
        with open(auto_calibrate,'r') as f:
            calibration = json.load(f)
    except:
        print("No calibration could be loaded from {}\nPlease check the file exists and is formatted properly".format(auto_calibrate))
        calibration = cf.set_calibration(options.profsile)
 

    # Change the processing based on data type
    if options.profile==True:

        # Choose which profile if there are multiple
        image_data = cf.choose_profile(image_data)
    
    else:
        plt.imshow(np.log(image_data))
        plt.show(block=False)
        #plt.show()


    # Load user configuration from provided path
    with open(USER_INFO) as f:
        user_info = json.load(f)

    # Change the Processing based on the type of data
    if options.profile==True:
        radial_profile = {"brightness":image_data,
                            "pixel_range":np.array(range(image_data.shape[0]))}

    else:
        radial_profile = ClientSide.Extract_Profile(image_data)    


    peak_locs = ClientSide.Find_Peaks(radial_profile,calibration,options.profile,display_type)


    print (peak_locs)
    # Choose which peaks to classify on
    peak_locs = cf.choose_peaks(peak_locs,display_type)

    print (peak_locs)
    if provide_family =="yes":
        while fam is None:
            temp_fam = input("What family does the Crystal belong to?\n")
            if temp_fam in FAMILIES:
                fam = temp_fam
            else:
                print("Invalid choice. choose from {}\n".format(str(FAMILIES)[1:-1]))

    classificated = ClientSide.Send_For_Classification(peak_locs,user_info,URL,fam)  

    print(classificated)

if __name__ == "__main__":
    main()

