import logging
import json
import os
import shutil
from seeq.addons.plot_curve import __version__
from pathlib import Path
from zipfile import ZipFile

ADDON = "seeq_plot_curve"
build_logger = logging.getLogger('build')
build_logger.addHandler(logging.StreamHandler())


PARENT_DIR = Path(__file__).resolve().parent
TEMP_DIR = PARENT_DIR/"temp_folder"

def configure_version(): 
    data = None
    with open ('addon.json', 'r') as file: 
        data = json.load(file)
    
    current_version = data['version']
    new_version = __version__
    print("Existing addon version: ", current_version, " incoming addon version: ", new_version)
    final_version = current_version
    # This step will capture version changes in seeq.addons.plot_curve.__version__
    # but the addon.json file still will need manual update as good practice for version control 
    if current_version < new_version: 
        data['version'] = new_version
        final_version = new_version
        print("Updating addon version to version: ", new_version)
    else:
        print("Updating addon version unnecessary")

    with open('addon.json', 'w') as file: 
        data = json.dump(data, file)
    
    return final_version 

version = configure_version()


final_artifacts = ['add-on-tool/PlotCurve.ipynb',
    ('add-on-tool/seeq_plot_curve-'+__version__+'-py3-none-any.whl'),
    'add-on-tool/requirements.txt',
    'addon.json']

def test_temp_directory():
    print("Running tests on pre-zipped package")
    count = 0
    for artifact in final_artifacts:
        temp = TEMP_DIR/artifact
        assert Path.exists(temp), ("Test failure, failed to locate: " + str(artifact) + " in final package")
        count+=1
    print("Packaging smoke test verified presence all", count, "of", count, "artifacts for addon: ", ADDON, "in the pre-zipped archive")


def test_zipped_package():
    print("Runing tests on zipped package")
    version = __version__
    zipName = "seeq-plot-curve-" + version + ".addon"
    print ("Extracting zipping files into", zipName)

    zipPath = PARENT_DIR/('seeq-plot-curve-'+version+'.addon')

    if not zipPath.exists():
        raise Exception("seeq-plot-curve-" + version + ".addon to be used for extraction does not exist")

    with ZipFile(zipPath, 'r') as zip_ref:
        target_dir = "test_temp_dir"
        os.makedirs(target_dir, exist_ok =True)

        zip_ref.extractall(target_dir)

    count = 0
    for artifact in final_artifacts:
        temp = Path("test_temp_dir")
        assert Path.exists(temp/ artifact), ("Test failure, failed to locate: " + str(artifact) + " in final package")
        count+=1
    print("Packaging smoke test verified presence all", count, "of", count, "artifacts for addon: ", ADDON, " in the final archive.")

    temp_folder_path = "test_temp_dir"
    try:
        shutil.rmtree(temp_folder_path)
        if(not os.path.exists("temp_folder/")):
            print("Successfully removed temp_folder")
    except FileNotFoundError:
        print("Attempting clean up unsuccessful. No temp_folder/ found in: ", ADDON)


if __name__ =="__main__":
    test_temp_directory()
    test_zipped_package()
