import sys, os, json
try:
    import spikeinterface.full as si
except:
    exit("spikeinterface[full] must be installed to review sorting\n")

try:
    import spikeinterface_gui
except:
    exit("spikeinterface_gui must be installed to review sorting\n")


def review(filename:str):
    
    
    if   os.path.isfile(filename):
        try:
            with open(filename)  as fd:
                last = json.load(fd)
            print(f" > Read {filename}")
        except BaseException as e:
            exit(f'Cannot load file `{filename}`: {e}')
    elif os.path.isdir(filename):
        if os.path.isfile(filename+'/jgui_state.json'):
            filename = filename+'/jgui_state.json'
            try:
                with open(filename)  as fd:
                    last = json.load(fd)
                print(f" > Read {filename}")
            except BaseException as e:
                exit(f'Found file `{filename}` but cannot load it: {e}')
            
        else:
            sslhfiles = list(__import__('glob').glob(f'{filename}/sslh-*.json'))
            if len(sslhfiles) == 0:
                exit(f'Could not find any sslh-*.json files')
            elif len(sslhfiles) > 1:
                exit(f'Found more than one sslh-*.json file. You need to specify which one you want to use. The options are:{sslhfiles}')
            filename = sslhfiles[0]
            try:
                with open(filename)  as fd:
                    last = json.load(fd)
                print(f" > Read {filename}")
            except BaseException as e:
                exit(f'Found file `{filename}` but cannot load it: {e}')
    else:
        #DB>>
        # print(filename)
        # print(os.path.isfile(filename),os.path.isdir(filename))
        #<<DB
        exit(f'Something wrong!')
    if "job_steps" in last:
        last["job_evn"]["base directory"] = os.path.dirname( filename )
        preproc_step  = [ step['identifier'] for step in last["job_steps"] if step['function'] == 'preprocessing' ]
        if len(preproc_step) == 0:
            exit(f'Cannot find preprocessing step in the `{filename}`')
        elif len(preproc_step) > 1:
            exit(f'Too many preprocessing steps in the `{filename}`')
        preproc_step = preproc_step[0]
        preproc_dir  = last["job_evn"]["base directory"]+'/'+(last[preproc_step]['folder'] if 'folder' in last[preproc_step] else preproc_step)
        rc  = si.load_extractor(preproc_dir)
        print(f" > extraced recoding from: {preproc_dir}")
        
        analyzer_step = [ step['identifier'] for step in last["job_steps"] if step['function'] == 'analyzer' ]
        if len(analyzer_step) == 0:
            exit(f'Cannot find analyzer step in the `{filename}`')
        elif len(analyzer_step) > 1:
            exit(f'Too many analyzer steps in the `{filename}`')
        analyzer_step = analyzer_step[0]
        analyzer_dir  = last["job_evn"]["base directory"]+'/'+(last[analyzer_step]['folder'] if 'folder' in last[analyzer_step] else analyzer_step)
        we  = si.load_sorting_analyzer(folder=analyzer_dir)
        print(f" > load analyzer from   : {analyzer_dir}")
    else:
        last['running directory'] = os.path.dirname( filename )
        rc  = si.load_extractor(last['running directory']+'/'+(last['preprocessing']['folder'] if 'folder' in last['preprocessing'] else "preprocessed"))
        print(f" > extraced recoding: "+last['running directory']+'/'+(last['preprocessing']['folder'] if 'folder' in last['preprocessing'] else "preprocessed"))
        we  = si.load_sorting_analyzer(folder=last['running directory']+'/'+(last['analyzer']['folder'] if 'folder' in last['analyzer'] else 'analyzer'))
        print(f" > load analyzer   : "+last['running directory']+'/'+(last['analyzer']['folder'] if 'folder' in last['analyzer'] else 'analyzer'))
    
    app = spikeinterface_gui.mkQApp()
    win = spikeinterface_gui.MainWindow(we, verbose=True, curation=True)
    print(' > Created main window ')
    win.show()
    print(' > Called show() ')
    # run the main Qt6 loop
    app.exec()

# review(sys.argv[1])
