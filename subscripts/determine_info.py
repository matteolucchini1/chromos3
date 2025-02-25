# Function to create a database of the files present and their properties
# Written by David Gardenier, 2015-2016

def determine_info():
    '''
    Function to split out the files created by Phil's script in find_data_files
    over each obsid folder, allowing code to be executed per obsid. Also
    creates a file with information on each observation
    '''
    purpose = 'Finding information on data files'
    print(len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'=')

    import os
    import pandas as pd
    import glob
    from collections import defaultdict
    import paths
    import logs
    import execute_shell_commands as shell
    import database

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    os.chdir(paths.data)

    with open(paths.obsid_list,'r') as f:
        obsids = [l.strip() for l in f.readlines()]

    db = pd.read_csv(paths.database)
    db['P'] = ['P' + o.split('-')[0] for o in db['obsids']]
    db['paths_obsid'] = paths.data + db['P'] + '/' + db['obsids'] + '/'

    # Find all files created by Phil's xtescan2 script
    all_files = []

    for f in db['P'].unique():
        p = os.path.join(paths.data, f, paths.selection + '*.list*')
        all_files.extend(glob.glob(p))

    # Remove all 500us event files
    # See above Table 1 on heasarc.gsfc.nasa.gov/docs/xte/recipes/bitmasks.html
    all_files = [a for a in all_files if '500us' not in a]

    d = defaultdict(list)

    # Split out values per obsid per mode
    for a in all_files:

        mode = a.split('.')[-2]

        if 'E_' in mode:
            with open(a) as e:
                for line in e:
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0]
                    time = line.split(' ')[2]
                    resolution = line.split(' ')[1].split('_')[1]

                    d['obsids'].append(obsid)
                    d['paths_data'].append(path)
                    d['times'].append(time)
                    d['resolutions'].append(resolution)
                    d['modes'].append('event')
                    d['bitsize'].append(float('NaN'))

        if 'Standard2f' in mode:
            with open(a) as s:
                for i, line in enumerate(s):
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0].split('.')[0]
                    time = line.split(' ')[2]

                    d['obsids'].append(obsid)
                    d['paths_data'].append(path)
                    d['times'].append(time)
                    d['resolutions'].append('16s')
                    d['modes'].append('std2')
                    d['bitsize'].append(float('NaN'))

        if 'Standard1b' in mode:
            with open(a) as s:
                for i, line in enumerate(s):
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0].split('.')[0]
                    time = line.split(' ')[2]

                    d['obsids'].append(obsid)
                    d['paths_data'].append(path)
                    d['times'].append(time)
                    d['resolutions'].append('125ms')
                    d['modes'].append('std1')
                    d['bitsize'].append(float('NaN'))

        if 'GoodXenon1' in mode:
            with open(a) as g:
                for line in g:
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0].split('.')[0]
                    time = line.split(' ')[2]
                    resolution = line.split(' ')[1].split('_')[1]

                    d['obsids'].append(obsid)
                    d['paths_data'].append(path)
                    d['times'].append(time)
                    d['resolutions'].append(resolution)
                    d['modes'].append('gx1')
                    d['bitsize'].append(float('NaN'))

        if 'GoodXenon2' in mode:
            with open(a) as g:
                for line in g:
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0].split('.')[0]
                    time = line.split(' ')[2]
                    resolution = line.split(' ')[1].split('_')[1]

                    d['obsids'].append(obsid)
                    d['paths_data'].append(path)
                    d['times'].append(time)
                    d['resolutions'].append(resolution)
                    d['modes'].append('gx2')
                    d['bitsize'].append(float('NaN'))

        if mode.startswith('B_'):
            with open(a) as e:
                for line in e:
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0]
                    time = line.split(' ')[2]
                    resolution = line.split(' ')[1].split('_')[1]
                    bitsize = mode.split('_')[-1]

                    d['obsids'].append(obsid)
                    d['paths_data'].append(path)
                    d['times'].append(time)
                    d['resolutions'].append(resolution)
                    d['modes'].append('binned')
                    d['bitsize'].append(bitsize)

    # Add information to database
    new_data = pd.DataFrame(d)
    new_c = ['paths_data', 'times', 'resolutions', 'modes', 'bitsize']
    db = database.merge(db, new_data, new_c)

    d = defaultdict(list)

    # List all data files per obsid, per mode, per res
    for obsid in db.obsids.unique():
        print(obsid)
        condo = (db.obsids == obsid)
        for mode in db[condo].modes.unique():
            condm = condo & (db.modes==mode)
            for res in db[condm].resolutions.unique():
                condr = condm & (db.resolutions==res)

                sf = mode

                # Ensure goodxenon files are listed together
                if mode[:2] == 'gx':
                    condr = condo & ((db.modes=='gx1') | (db.modes=='gx2')) & (db.resolutions==res)
                    sf = 'gx'

                # Create subdatabase of values
                sdb = db[condr]
                sdb.drop_duplicates('paths_data')

                # Write paths to file per obsid per mode per resolution
                filename = 'paths_' + sf + '_' + res
                path_to_output = sdb.paths_obsid.values[0] + filename

                # Remove previous versions
                data = list(set(sdb.paths_data))

                with open(path_to_output, 'w') as text:
                    text.write('\n'.join(data) + '\n')

                d['obsids'].append(obsid)
                d['modes'].append(mode)
                d['resolutions'].append(res)
                d['paths_po_pm_pr'].append(path_to_output)

    #Add to database
    new_data = pd.DataFrame(d)
    db = database.merge(db, new_data, ['paths_po_pm_pr'])
    unfound_obsids = db[db.modes.isnull()].obsids.values
    if len(unfound_obsids) > 0:
        print('ERROR: NO DATA FOR THESE OBSIDS', unfound_obsids)
        db = db[db.modes.notnull()]

    database.save(db)
    logs.stop_logging()
