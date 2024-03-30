import datetime
import json
import traceback
from typing import List

import numpy as np
import pandas as pd
from sympy import S, symbols

from seeq import spy
from seeq.addons.plot_curve.utils import tracker
from seeq.sdk import FormulasApi
from seeq.sdk.api_client import ApiException

AVAILABLE_COLORS = {'#1ECBE1', '#E1341E', '#2DD2C0', '#2F2CD3', '#B038C7', '#CA3599', '#9BB847',
                    '#9C6B63', '#63949C', '#E35D1C', '#19E916', '#E11E71', '#C1F50A', '#E1A91E',
                    '#718E77', '#8E7188', '#E5F10E', '#B7486B', '#D9266D', '#EBEC13'}


class Equation:

    def __init__(self, order: int = None, independent_variable: str = None, dependent_variable: str = None,
                 independent_signal: str = None, output_signal: str = None, x_data: List[float] = None,
                 y_data: List[float] = None, x_units: str = None, y_units: str = None):

        self.order = order
        self.independent_variable = independent_variable
        self.dependent_variable = dependent_variable
        self.independent_signal = independent_signal
        self.output_signal = output_signal
        self.x_data = x_data
        self.y_data = y_data
        self.x_units = x_units
        self.y_units = y_units

    @staticmethod
    @tracker(project=__name__)
    def supported_equations():
        return [f'x^{x}' for x in range(4)]

    @staticmethod
    @tracker(project=__name__)
    def _target_signal(target, workbook, url):
        try:
            active_signal_names = list(spy.pull(url, header='Name', quiet=True, errors='catalog').columns)
            active_signal_ids = list(spy.pull(url, header='ID', quiet=True, errors='catalog').columns)
        except KeyError:
            return None

        for signal, signal_id in zip(active_signal_names, active_signal_ids):
            if signal == target:
                return spy.search({'Name': signal, 'ID': signal_id}, workbook=workbook, quiet=True)

        return None

    @property
    @tracker(project=__name__)
    def _fit_coefficients(self):
        return np.polyfit(self.x_data, self.y_data, self.order)

    @property
    @tracker(project=__name__)
    def equation(self):
        return sum(S("{:.2e}".format(v))*symbols("x")**i for i, v in enumerate(self._fit_coefficients[::-1]))

    @property
    @tracker(project=__name__)
    def fitted_function(self):
        return np.poly1d(self._fit_coefficients)

    @property
    @tracker(project=__name__)
    def seeq_formula(self):
        conversion = f"$converted_signal = $signal.convertUnits('{self.x_units}').setUnits('')"
        splice = (f"$splicedSignal = $converted_signal.remove($converted_signal."
                  f"isNotBetween({str(min(self.x_data))}, {str(max(self.x_data))}))")
        exponents = list(range(len(self._fit_coefficients)))
        exponents.reverse()
        terms = list()
        for coefficient, exponent in zip(self._fit_coefficients, exponents):
            terms.append(f"({coefficient})*$splicedSignal^{exponent}")

        equation_expression = '(' + ' + '.join(terms) + f").setunits('{self.y_units}')"

        return conversion + '\n' + splice + '\n' + equation_expression

    @property
    @tracker(project=__name__)
    def fully_defined(self):
        valid_output_signal = self.output_signal is not None and len(self.output_signal) > 0
        valid_independent_signal = self.independent_signal is not None and len(self.independent_signal) > 0
        return valid_output_signal and valid_independent_signal

    @tracker(project=__name__)
    def push_formula_to_seeq(self, workbook, worksheet, url):

        target_signal = self._target_signal(self.independent_signal, workbook, url)
        calculation = pd.DataFrame([{'Type': 'Signal',
                                     'Name': self.output_signal,
                                     'Formula': self.seeq_formula,
                                     'Formula Parameters':
                                         {'$signal': target_signal}}])

        # backup the current display items to allow reversion...
        workbook_search = spy.workbooks.search({'ID': workbook}, quiet=True)
        retrieved_workbook = spy.workbooks.pull(workbook_search, specific_worksheet_ids=[worksheet], quiet=True)[0]
        display_items = retrieved_workbook.worksheets[0].display_items

        # test unit compatibility with the formula run sdk and exit on any seeq errors...
        formula_sdk = FormulasApi(spy.client)
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=1)

        def iso_datestring(datetime_object):
            day, time = str(datetime_object).split()
            return f'{day}T{time}Z'

        try:
            formula_sdk.run_formula(start=iso_datestring(start),
                                    end=iso_datestring(end),
                                    formula=self.seeq_formula.replace('\\n', '\n'),
                                    parameters=[f'signal={target_signal["ID"][0]}'])
        except Exception as e:
            self.last_formula_run_error = json.loads(e.body)
            if self.last_formula_run_error['errorType'] == 'INCOMPATIBLE_UNITS':
                raise TypeError('The units of the independent variable have a mismatch and are incompatible.')
            elif 'is not compatible with' in self.last_formula_run_error['statusMessage']:
                raise TypeError('The units of the independent variable have a mismatch and are incompatible.')
            else:
                raise TypeError(f'Seeq Error : {self.last_formula_run_error["statusMessage"]}')


        # push the formula to seeq, and add a new row to the push_output...
        push_output = spy.push(metadata=calculation, workbook=workbook, worksheet=worksheet, quiet=True)
        new_display_item = display_items.iloc[0].copy()
        for key, val in push_output[['Name', 'ID', 'Type']].to_dict().items():
            new_display_item[key] = val[0]

        non_used_colors = AVAILABLE_COLORS - set(display_items['Color'])
        new_display_item['Color'] = list(non_used_colors)[0]
        new_display_item['Lane'] = display_items['Lane'].max() + 1

        if new_display_item['ID'] in display_items['ID'].values:
            retrieved_workbook.worksheets[0].display_items = display_items.reset_index()
            spy.workbooks.push(retrieved_workbook, specific_worksheet_ids=[worksheet], quiet=True)
            raise ValueError(f"The formula is already in the workbook {workbook}")

        # push the new display item to seeq, and revert in the case of a unit mismatch...
        try:
            modified_display_items = display_items.append(new_display_item).reset_index()
            retrieved_workbook.worksheets[0].display_items = modified_display_items
            spy.workbooks.push(retrieved_workbook, specific_worksheet_ids=[worksheet], quiet=True)
            spy.pull(url, quiet=True)   # will raise an API exception in the case of a unit mismatch...
        except ApiException as e:
            if 'is not compatible with' in e.body:
                retrieved_workbook.worksheets[0].display_items = display_items.reset_index()
                spy.workbooks.push(retrieved_workbook, specific_worksheet_ids=[worksheet], quiet=True)
                raise
        except Exception:
            print(f'There was an unknown except when modifying the display items : {traceback.format_exc()}')
            raise

