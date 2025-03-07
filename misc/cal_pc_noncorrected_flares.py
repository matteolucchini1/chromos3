                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                # Long script to check the influence of flares
def power_spectrum(path_lc, path_bkg):

    import numpy as np
    import numpy.fft as fft
    import math

    try:
        # Reading in the lightcurve data for each path/file
        rate, t, dt, n_bins, error = np.loadtxt(path_lc,dtype=float,unpack=True)
        bkg_rate = np.loadtxt(path_bkg, dtype=float, unpack=True)
    except IOError:
        print 'ERROR: Lightcurve does not exist'
        return

    # Determine the number of bins
    try:
        n_bins = int(n_bins[0])
    except IndexError:
        print 'ERROR: No data in lightcurve file'
        return

    # Determine the (time) width of each bin
    dt = dt[0]

    # Express the length of each segment size in units of dt
    n = 512/dt
    # n should already be a power of 2 - but in case if isn't
    # this line will round it off to the nearest power of 2
    n_seg = pow(2, int(math.log(n, 2) + 0.5))

    # Whether you wish subtract white noise
    white_noise_subtraction = True

    # A list with indexes of segment end points
    segment_endpoints = []

    # The length of a segment starts at zero
    length = 0

    # Calculate where the data should be cut
    for j in xrange(1, n_bins):

        # Check for gaps; in case of a gap, set length to zero.
        if (t[j] - t[j-1]) < 1.5*dt:
            length = length+1
        else:
            length = 0

        # Check if the length has reached the required segment size
        if length == n_seg:

            # If so, add the endpoint to the endpoint list
            segment_endpoints.append(j)
            # And reset the length to zero:
            length = 0

    # Calculating the number of segments
    number_of_segments = len(segment_endpoints)
    # Stop calculations if no segments can be found
    if number_of_segments == 0:
        print 'WARNING: No segments found'
        return

    # Initialise the power spectrum array
    power_spectrum = np.zeros((n_seg))
    # Necessary for errors on power colour values
    power_spectrum_squared = np.zeros((n_seg))

    # Initialise rate arrays
    rate_tot = []
    bkg_tot = []

    # For each segment
    for j in xrange(number_of_segments):
        # Make an array containing the segment of the light curve
        segment = rate[segment_endpoints[j]-n_seg : segment_endpoints[j]]
        bkg_segment = bkg_rate[segment_endpoints[j]-n_seg : segment_endpoints[j]]

        # Calculate the fast Fourier transform
        four_trans = fft.fft(segment, n_seg, 0)

        # Calculate the normalisation of the powerspectrum
        # (rms normalisation)
        norm = (2*dt)/(float(n_seg)*(np.mean(segment)**2))

        # Add the normalisation of the square of the FFT
        # to the power spectrum
        power_spectrum += norm*(np.absolute(four_trans))**2
        # Add the normalisation of the squared power spectrum
        power_spectrum_squared += (norm*(np.absolute(four_trans))**2)**2

        # For calculating the total white noise
        if white_noise_subtraction:
            rate_tot.extend(segment)
            bkg_tot.extend(bkg_segment)

    # Calculate the mean power spectrum
    power_spectrum = power_spectrum/float(number_of_segments)

    # Calculate the mean power spectrum
    power_spectrum_squared = power_spectrum_squared/float(number_of_segments)

    # Calculating the error on the power spectrum
    power_spectrum_error = power_spectrum/np.sqrt(float(number_of_segments))

    # Calculate the white noise & subtract from the power spectrum
    if white_noise_subtraction:
        white_noise = (2*(np.mean(rate_tot)+np.mean(bkg_tot))/np.mean(rate_tot)**2)
        power_spectrum -= white_noise

    # Note the range of the power spectrum - this is due to the output
    # of the FFT function, which adds the negative powers at the end of
    # the list
    ps = power_spectrum[1:n_seg/2]
    ps_error = power_spectrum_error[1:n_seg/2]
    ps_squared = power_spectrum_squared[1:n_seg/2]

    # Calculate the corresponding frequency grid
    # (assuming that dt is the same for all)
    frequency = fft.fftfreq(n_seg, dt)[1:n_seg/2]

    # Calculate the error on the frequencies
    frequency_error = (1.0/(2*dt*float(n_seg)))*np.ones(n_seg/2 - 1)

    return ps, ps_error, ps_squared, number_of_segments, frequency, frequency_error


def power_colour(path):
    '''
    Function to calculate the power colour values per power spectrum.
    Integrates between 4 areas under the power spectrum (variance), and takes
    the ratio of the variances to calculate the power colour values.
    '''
    import numpy as np

    # Define the frequency bands in Hz
    frequency_bands = [0.0039,0.031,0.25,2.0,16.0]

    # Import data
    try:
        all_data = np.loadtxt(path,dtype=float)
        inverted_data = np.transpose(all_data)
    except IOError:
        print 'ERROR: Power spectrum not present'
        return

    # Give the columns their names
    power_spectrum = inverted_data[0]
    power_spectrum_error = inverted_data[1]
    frequency = inverted_data[2]
    frequency_error = inverted_data[3]
    power_spectrum_squared = inverted_data[4]
    number_of_segments = inverted_data[5][0]

    variances = []
    variance_errors = []
    index_frequency_bands = []

    # Convert frequency bands to index values from in the frequency list
    for fb in frequency_bands:
        index = min(range(len(frequency)), key=lambda i: abs(frequency[i]-fb))
        index_frequency_bands.append([index])

    # Group indexes into sets of style [low, high)
    for i, e in enumerate(index_frequency_bands[:-1]):
        e.append(index_frequency_bands[i+1][0]-1)

    del index_frequency_bands[-1]

    # Integrate the power spectra within the frequency bands
    bin_width = frequency[1]-frequency[0]

    for e in index_frequency_bands:
        variance = bin_width*sum(power_spectrum[e[0]:e[1]])
        variances.append(variance)

        # Calculate errors on the variance
        # (see appendix Heil, Vaughan & Uttley 2012)
        # M refers to the number of segments
        one_over_sqrt_M = 1/float(np.sqrt(number_of_segments))
        prop_std = sum(power_spectrum_squared[e[0]:e[1]])
        variance_error = bin_width*one_over_sqrt_M*np.sqrt(prop_std)
        variance_errors.append(variance_error)

    pc1 = variances[2]/float(variances[0])
    pc2 = variances[1]/float(variances[3])

    pc1_error = np.sqrt((variance_errors[2]/float(variances[2]))**2 +
                        (variance_errors[0]/float(variances[0]))**2)*pc1
    pc2_error = np.sqrt((variance_errors[1]/float(variances[1]))**2 +
                        (variance_errors[3]/float(variances[3]))**2)*pc2

    # Applying similar filter to Lucy, only plotting if variance constrained
    # within 3sigma
    for i, e in enumerate(variance_errors):
        v = variances[i]

        if v - 3*e > 0:
            constrained = True
        else:
            constrained = False
            break

    return pc1, pc1_error, pc2, pc2_error, constrained


def cal_ps_with_flares(pathdata,pathdatabase):
    '''
    Function to generate power spectral density based on RXTE lightcurves.
    '''

    # Let the user know what's going to happen
    purpose = 'Creating Power Spectra'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import sys
    sys.path.insert(0, '/scratch/david/master_project/scripts/subscripts')

    import os
    import pandas as pd
    import glob
    from collections import defaultdict
    from math import isnan
    import execute_shell_commands as shell
    import database

    # Get database
    os.chdir(pathdata)
    db = pd.read_csv(pathdatabase)

    d = defaultdict(list)
    for path_lc_bkg_corrected, group in db.groupby('bkg_corrected_lc'):

        # Check whether x-ray flare was present
        if 'lc_no_flare' in group:
            if pd.notnull(group.lc_no_flare.values[0]):
                path_lc = group.bkg_corrected_lc.values[0]
                path_bkg = group.rebinned_bkg.values[0]
            else:
                continue
        else:
            print 'No flares in entire object'
            continue

        # Determine parameters
        obsid = group.obsids.values[0]
        path_obsid = group.paths_obsid.values[0]
        mode = group.modes.values[0]
        res = group.resolutions.values[0]

        print obsid, mode, res

        # Calculate power spectrum
        output = power_spectrum(path_lc, path_bkg)

        if output:
            ps, ps_er, ps_sq, num_seg, freq, freq_er = output
            path_ps = path_obsid + mode + '_' + res + '_with_flare.ps'

            # Create file within obsid folder
            with open(path_ps, 'w') as f:
                # For each value in a power spectrum
                for i, value in enumerate(ps):
                    line = (repr(value) + ' ' +
                            repr(ps_er[i]) + ' ' +
                            repr(freq[i]) + ' ' +
                            repr(freq_er[i]) + ' ' +
                            repr(ps_sq[i]) + ' ' +
                            repr(num_seg) + '\n')
                    f.write(line)

            d['bkg_corrected_lc'].append(path_lc_bkg_corrected)
            d['ps_with_flare'].append(path_ps)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['ps_with_flare'])
    database.save(db,location=pathdatabase[:-4]+'_2.csv')


def cal_pc_with_flares(pathdata,pathdb):
    '''
    Function to generate power spectral density based on RXTE lightcurves.
    '''
    pathdatabase=pathdb[:-4]+'_2.csv'
    # Let the user know what's going to happen
    purpose = 'Creating Power Colours'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    from collections import defaultdict
    from math import isnan

    import sys
    sys.path.insert(0, '/scratch/david/master_project/scripts/subscripts')
    import execute_shell_commands as shell
    import database

    # Get database
    os.chdir(pathdata)
    db = pd.read_csv(pathdatabase)

    d = defaultdict(list)
    for ps, group in db.groupby('ps_with_flare'):

        # Determine parameters
        obsid = group.obsids.values[0]
        path_obsid = group.paths_obsid.values[0]
        mode = group.modes.values[0]
        res = group.resolutions.values[0]

        print obsid, mode, res

        # Calculate power colour
        output = power_colour(ps)

        if output:
            pc1, pc1err, pc2, pc2err, constraint = output

            d['ps_with_flare'].append(ps)
            d['pc1_wf'].append(pc1)
            d['pc1_err_wf'].append(pc1err)
            d['pc2_wf'].append(pc2)
            d['pc2_err_wf'].append(pc2err)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['pc1_wf','pc1_err_wf','pc2_wf','pc2_err_wf'])
    database.save(db,location=pathdb[:-4]+'_2.csv')


if __name__=='__main__':

    # Quick script to run pipeline over multiple objects
    import os
    import glob
    import sys

    objects = ['4u_1705_m44',
              'xte_J1808_369',
              'cir_x1',
              'EXO_0748_676',
              'HJ1900d1_2455',
              'v4634_sgr',
              '4U_1728_34',
              '4U_0614p09',
              '4U_1702m43',
              'J1701_462',
              'aquila_X1',
              '4U_1636_m53',
              'cyg_x2',
              'gx_5m1',
              'gx_340p0',
              'sco_x1',
              'gx_17p2',
              'gx_349p2']

    filein = '/scratch/david/master_project/scripts/misc/paths.txt'
    fileout = '/scratch/david/master_project/scripts/subscripts/paths.py'

    f = open(filein,'r')
    filedata = f.read()
    f.close()

    for arg in objects:
        newdata = filedata.replace("OBJECT",arg)

        f = open(fileout,'w')
        f.write(newdata)
        f.close()

        try:
            print arg, '\n============='
            pathdatabase = '/scratch/david/master_project/' + arg + '/info/database_'+arg+'.csv'
            pathdata = '/scratch/david/master_project/' + arg
            cal_ps_with_flares(pathdata,pathdatabase)
            cal_pc_with_flares(pathdata,pathdatabase)
        except:
            print sys.exc_info()
            continue
