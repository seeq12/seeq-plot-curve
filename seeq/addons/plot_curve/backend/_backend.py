import io
from collections import Counter

import pandas as pd
from pint import UndefinedUnitError, UnitRegistry
from rx.subject import Subject

from seeq import spy
from seeq.addons.plot_curve.backend import Equation
from seeq.addons.plot_curve.utils import MessageType, tracker
from seeq.sdk.api_client import ApiException


class BackEnd:
    def __init__(self, workbook, worksheet):
        self.file_change_events = Subject()
        self.data_change_events = Subject()
        self.message_events = Subject()

        self.loaded_dataframe = pd.DataFrame()
        self.active_dataframe = pd.DataFrame()

        self.equations = {}
        self.tabs = []
        self.units = []
        self.active_tab = None

        self.unit_registry = UnitRegistry()

        self.workbook = workbook
        self.worksheet = worksheet

    @property
    @tracker(project=__name__)
    def _url(self):
        host = spy.client.host.replace('/api','')
        return  f"{host}/workbook/{self.workbook}/worksheet/{self.worksheet}"

    @tracker(project=__name__)
    def get_workbench_signals(self):
        try:
            return list(spy.pull(self._url, header='Name', quiet=True, errors='catalog').columns)

        except KeyError:
            self.message_events.on_next({'type': MessageType.ERROR,
                                         'message': f'The workbench URL ({self._url}) contains no valid signals'})
        except Exception as e:
            self.message_events.on_next({'type': MessageType.ERROR,
                                         'message': f'{str(e)}'})

    @tracker(project=__name__)
    def update_active_equation_parameter(self, component, value):
        setattr(self.equations[self.active_tab], component, value)

        # update the units if we are adjusting the dependent or independent variable...
        if component == 'independent_variable':
            setattr(self.equations[self.active_tab], 'x_units', self.units[value])
            setattr(self.equations[self.active_tab], 'x_data', self.active_dataframe[value].astype('float64').to_list())
        if component == 'dependent_variable':
            setattr(self.equations[self.active_tab], 'y_units', self.units[value])
            setattr(self.equations[self.active_tab], 'y_data', self.active_dataframe[value].astype('float64').to_list())

    @tracker(project=__name__)
    def get_active_equation_parameter(self, parameter):
        if hasattr(self.equations[self.active_tab], parameter):
            return getattr(self.equations[self.active_tab], parameter)
        else:
            return None

    @tracker(project=__name__)
    def get_equation_representation(self):
        return self.equations[self.active_tab].equation

    @tracker(project=__name__)
    def get_fitted_function(self):
        return self.equations[self.active_tab].fitted_function

    @tracker(project=__name__)
    def on_file_load(self, raw_data):
        self.loaded_dataframe = pd.read_csv(io.StringIO(raw_data), sep=',')
        self.loaded_dataframe = self.validate_dataframe(self.loaded_dataframe)
        self.loaded_dataframe['Curve'] = self.loaded_dataframe['Curve'].ffill()
        self.units = self.loaded_dataframe.iloc[:1, 1:].to_dict('records')[0]
        self.tabs = [x for x in list(self.loaded_dataframe.iloc[1:, 0].unique())]
        self.equations = {tab: Equation() for tab in self.tabs}
        self.file_change_events.on_next({'tabs': self.tabs, 'data': self.loaded_dataframe})

    def validate_dataframe(self, df):
        """
        Attempt to validate and correct the format of the dataframe, or raise an error if it cannot be handled.
        :param df:
        :return:
        """

        # verify the first column contains curves which have at least 3 points, else raise a warning...
        first_column = df[df.columns[0]].ffill()
        unique_curves = [x for x in first_column[2:]]
        for curve, points in Counter(unique_curves).items():
            if points < 3:
                self.message_events.on_next({'type': MessageType.ERROR,
                                             'message': f'The curve {curve} has only {points} data point.  '
                                                        f'Curves should have at least 3 data points.'})

        # validate units...
        units = [str(unit) for name, unit in df.iloc[0][1:].items()]
        for unit in units:
            self._validate_unit(unit)

        # Forward Fill nans in the first column, and fix the formatting of Curve and Units
        df = df.ffill()
        df_columns = df.columns.tolist()
        df_columns[0] = 'Curve'
        df.columns = df_columns

        df.iat[0, 0] = 'Units'

        return df

    def _validate_unit(self, unit):

        # verify units have been provided...
        if len(unit.strip()) == 0 or unit == 'nan':
            self.message_events.on_next({'type': MessageType.ERROR,
                                         'message': 'Each of the variable columns must have a specified unit.  '
                                                    'Please fix the input file and try again.'})
            return

        # verify for exponents, that the carat symbol is used...
        contains_number = any(char.isdigit() for char in unit)
        contains_exp = '^' in unit
        if contains_number and not contains_exp:
            self.message_events.on_next({'type': MessageType.ERROR,
                                         'message': f'The unit {unit} contains a number but no exponent.  '
                                                    f'Seeq uses ^ to indicate an exponent.  Before proceeding, '
                                                    f'please check the units in your data.'})

        # verify the unit can be parsed by pint
        base_unit = ''.join([i for i in unit if not i.isdigit()]).replace('**', '').replace('^', '')
        if base_unit != '%':
            try:
                self.unit_registry.parse_expression(base_unit)
            except UndefinedUnitError:
                self.message_events.on_next({'type': MessageType.ERROR,
                                             'message': f'There was an error parsing unit {base_unit}.  Verify '
                                                        f'that this unit is a valid type prior to proceeding.  The '
                                                        f'first row should contain Variable names, the second must '
                                                        f'contain valid units.'})

    @tracker(project=__name__)
    def on_tab_change(self, tab):
        self.active_tab = tab
        self.active_dataframe = self.loaded_dataframe[self.loaded_dataframe['Curve'] == tab].drop('Curve', axis=1)
        self.data_change_events.on_next({'tab': tab, 'data': self.active_dataframe, 'units': self.units})

    @tracker(project=__name__)
    def valid_formulas(self):
        return len([equation for equation in self.equations.values() if equation.fully_defined])

    @tracker(project=__name__)
    def push_formulas(self, only_active=True):
        try:
            if only_active:
                self.equations[self.active_tab].push_formula_to_seeq(workbook=self.workbook,
                                                                     worksheet=self.worksheet, url=self._url)
                self.message_events.on_next({'type': MessageType.SUCCESS,
                                             'message': f"Signal {self.equations[self.active_tab].output_signal} has "
                                                        f"been pushed to <a href='{self._url}'"
                                                        f"target='_blank'>active worksheet</a> in Seeq.  "
                                                        f"It is recommended to verify units have been correctly "
                                                        f"converted and the signal appears as intended."})
            else:
                for tab in self.tabs:
                    self.equations[tab].push_formula_to_seeq(workbook=self.workbook,
                                                             worksheet=self.worksheet, url=self._url)
                    self.message_events.on_next({'type': MessageType.SUCCESS,
                                                 'message': f"Signal {self.equations[tab].output_signal} has "
                                                            f"been pushed to <a href='{self._url}'"
                                                            f"target='_blank'>active worksheet</a> in Seeq.  "
                                                            f"It is recommended to verify units have been correctly "
                                                            f"converted and the signal appears as intended."})
        except ApiException as e:
            if 'is already in the workbook' in str(e):
                self.message_events.on_next({'type': MessageType.ERROR,
                                             'message': 'An identical formula already exists in the workbook'})
            elif 'is not compatible with ' in str(e):
                seeq_signal = self.equations[self.active_tab].independent_signal
                provided_units = self.equations[self.active_tab].x_units
                self.message_events.on_next({'type': MessageType.ERROR,
                                             'message': f'Seeq was unable to convert units from {provided_units} to the'
                                                        f' units of the Seeq Signal ({seeq_signal}).  Verify units are '
                                                        f'compatible and reload the app before proceeding...'})
        except Exception as e:  # noinspection PyBroadException
            self.message_events.on_next({'type': MessageType.ERROR,
                                         'message': f'{str(e)}'})



