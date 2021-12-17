import os
import sys
import argparse
import subprocess
from getpass import getpass
from urllib.parse import urlparse
from seeq import spy
from typing import Sequence, List
# noinspection PyProtectedMember
from seeq.spy._errors import *
# noinspection PyProtectedMember
from seeq.spy import _url
from seeq.sdk import SystemApi, ConfigurationInputV1, ConfigurationOptionInputV1
from ._copy import copy_notebooks

NB_EXTENSIONS = {'widgetsnbextension': 'jupyter-js-widgets',
                 'ipyvuetify': 'jupyter-vuetify',
                 'ipyvue': 'jupyter-vue',
                 'bqplot': 'bqplot'}

DEPLOYMENT_FOLDER = 'deployment'
DEPLOYMENT_NOTEBOOK = "PlotCurve.ipynb"
ACCESS_KEY_NAME = 'PlotCurve'
ACCESS_KEY_DESCRIPTION = 'A tool for fitting curves to tabular data and pushing resulting formulas to Seeq'


def permissions_defaults(permissions_group: List[str], permissions_users: List[str]):
    if permissions_group is None:
        permissions_group = ['Everyone']

    if permissions_users is None:
        permissions_users = []
    return permissions_group, permissions_users


def install_app(sdl_url_, *, sort_key='a',
                permissions_group: Sequence[str] = ('Everyone',), permissions_users: Sequence[str] = ()):
    """
    Installs Plot Curve as an Add-on Tool in Seeq Workbench

    Parameters
    ----------
    sdl_url_: str
        URL of the SDL container.
        E.g. https://my.seeq.com/data-lab/6AB49411-917E-44CC-BA19-5EE0F903100C/
    sort_key: str, default None
        A string, typically one character letter. The sort_key determines the
        order in which the Add-on Tools are displayed in the tool panel
    permissions_group: list
        Names of the Seeq groups that will have access to each tool
    permissions_users: list
        Names of Seeq users that will have access to each tool
    Returns
    --------
    -: None
        Plot Curve will appear as Add-on Tool(s) in Seeq Workbench
    """

    add_on_details = {
        "Name": ACCESS_KEY_NAME,
        "Description": ACCESS_KEY_DESCRIPTION,
        "Icon": "fa fa-line-chart",
        "Target URL": f'{sdl_url_}/apps/{DEPLOYMENT_FOLDER}/{DEPLOYMENT_NOTEBOOK}',
        "Link Type": "window",
        "Window Details": "popup=1,toolbar=0,location=0,left=800,top=200,height=915,width=1200",
        "Sort Key": sort_key,
        "Reuse Window": False,
        "Groups": permissions_group,
        "Users": permissions_users
    }

    copy_notebooks(des_folder=DEPLOYMENT_FOLDER, src_folder='deployment_notebook',
                   overwrite_folder=False, overwrite_contents=True)
    spy.addons.install(add_on_details, include_workbook_parameters=True, update_tool=True)


def logging_attempts(_user):
    count = 0
    allowed_attempts = 20
    while count <= allowed_attempts:
        try:
            if _user is None or count >= 1:
                _user = input("\nAccess Key or Username: ")

            passwd = getpass("Access Key Password: ")
            spy.login(username=_user, password=passwd, ignore_ssl_errors=True)
            break
        except (SPyRuntimeError, SPyValueError):
            count += 1
            try_again = None
            while try_again != 'yes' and try_again != 'no':
                try_again = input("\nTry again (yes/no)? [yes] ")
                if try_again == '' or try_again.lower() == 'y':
                    try_again = 'yes'
                if try_again.lower() == 'n':
                    try_again = 'no'
            print("-" * 60)
            if try_again.lower() == 'no':
                raise
            if count > allowed_attempts:
                raise RuntimeError("Number of login attempts exceeded")


def get_installed_extensions():
    stdout, stderr = subprocess.Popen('jupyter nbextension list', shell=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return set([x.split('/')[0] for x in str(stdout).split() if x.endswith('extension')])


# noinspection PyBroadException
def install_nbextensions():
    installed_extensions = get_installed_extensions()

    # install any extensions which are not already installed...
    for extension, installed_name in NB_EXTENSIONS.items():
        if installed_name not in installed_extensions:
            stdout = None
            stderr = None
            try:
                stdout, stderr = subprocess.Popen(f'jupyter nbextension install --user --py {extension}',
                                                  shell=True, stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE).communicate()
            except Exception:
                print(f'Output : {stdout}')
                print(f'Error : {stderr}')
            try:
                stdout, stderr = subprocess.Popen(f'jupyter nbextension enable --user --py {extension}',
                                                  shell=True, stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE).communicate()
            except Exception:
                print(f'Output : {stdout}')
                print(f'Error : {stderr}')

    # verify required extensions are installed and raise an error if anything could not be installed...
    installed_extensions = get_installed_extensions()
    for required_extension in NB_EXTENSIONS.values():
        if required_extension in installed_extensions:
            print(f"    Required nbextension {required_extension} has been successfully installed...")
        else:
            raise RuntimeError(f"There was an error installing required nbextension {required_extension}")


def cli_interface():
    """ Installs Plot Curve as a Seeq Add-on Tool """
    parser = argparse.ArgumentParser(description='Install Plot Curve as a Seeq Add-on Tool')
    parser.add_argument('--nbextensions_only', action='store_true',
                        help='Only installs the nbextensions without installing or updating the Add-on Tools'
                             'links')
    parser.add_argument('-u', '--username', type=str,
                        help='Username or Access Key of Seeq admin user installing the tool(s) ')
    parser.add_argument('--seeq_url', type=str, nargs='?',
                        help="Seeq hostname URL with the format https://my.seeq.com/ or https://my.seeq.com:34216")
    parser.add_argument('--users', type=str, nargs='*', default=[],
                        help="List of the Seeq users to will have access to the Plot Curve Add-on Tool,"
                             " default: %(default)s")
    parser.add_argument('--groups', type=str, nargs='*', default=['Everyone'],
                        help="List of the Seeq groups to will have access to the Plot Curve Add-on Tool, "
                             "default: %(default)s")
    return parser.parse_args()


def enable_addon_tools():
    system_api = SystemApi(spy.client)
    config_option_input = ConfigurationOptionInputV1(path='Features/AddOnTools/Enabled', value=True)
    system_api.set_configuration_options(body=ConfigurationInputV1([config_option_input]))


if __name__ == '__main__':

    args = cli_interface()
    if args.nbextensions_only:
        print("\n\nInstalling and enabling nbextensions")
        install_nbextensions()
        sys.exit(0)
    user = args.username
    logging_attempts(user)
    seeq_url = args.seeq_url
    if seeq_url is None:
        seeq_url = input(f"\n Seeq base URL [{spy.client.host.split('/api')[0]}]: ")
        if seeq_url == '':
            seeq_url = spy.client.host.split('/api')[0]
    url_parsed = urlparse(seeq_url)
    seeq_url_base = f"{url_parsed.scheme}://{url_parsed.netloc}"

    project_id = spy.utils.get_data_lab_project_id()
    sdl_url = f'{seeq_url_base}/data-lab/{project_id}'
    if project_id is None:
        print("\nThe project ID could not be found. Please provide the SDL project URL with the format "
              "https://my.seeq.com/data-lab/6AB49411-917E-44CC-BA19-5EE0F903100C/\n")
        sdl_url = input("Seeq Data Lab project URL: ")
        project_id = spy.utils.get_data_lab_project_id_from_url(sdl_url)
        if not project_id:
            raise RuntimeError(f'Could not install {args.apps} because the SDL project ID could not be found')
    sdl_url_sanitized = _url.SeeqURL.parse(sdl_url).url

    # App Installation
    if not spy.user.is_admin:
        print('You must be an admin user to install AddOns')
        sys.exit(1)

    print(f"\nThe Plot Curve App will be installed on the SDL notebook: {sdl_url_sanitized}\n"
          f"If this is not your intent, you can quit the installation now ")
    print('\n[enter] to continue or type "quit" to exit installation')
    choice = None
    while choice != '' and choice != 'quit':
        choice = input()
        if choice == '':
            print("\nInstalling Plot Curve App...")
            print("----------------------------")
            print("Enabling Add On Tools...")
            enable_addon_tools()
            print("Installing and enabling nbextensions")
            install_nbextensions()
            install_app(sdl_url_sanitized, permissions_group=args.groups, permissions_users=args.users)
        elif choice == 'quit':
            print("\nExited installation")
        else:
            print(f'\nCommand "{choice}" is not valid')
            print('\n[enter] to continue the installation or type "quit" to exit installation')
