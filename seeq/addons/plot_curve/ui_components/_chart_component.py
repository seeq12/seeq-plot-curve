import typing

import ipyvuetify as vue
import ipywidgets as widgets
from IPython.display import Math, display_latex
import numpy as np
import pandas as pd
from pathlib import Path
from seeq.addons.plot_curve.backend import Equation
from seeq.addons.plot_curve.utils import threaded
from seeq.addons.plot_curve.utils import MessageType
import time
import traitlets
import warnings
from typing import Callable, List, Union, Optional, Any
from bqplot import pyplot as plt
from sympy import printing

CURRENT_DIR = Path(__file__).parent.resolve()

warnings.simplefilter('ignore', np.RankWarning)


class ChartComponent(vue.VuetifyTemplate):
    plot_widget = traitlets.Any().tag(sync=True, **widgets.widget_serialization)
    equation = traitlets.Any().tag(sync=True, **widgets.widget_serialization)
    seeq_dependent_variable = traitlets.Unicode().tag(sync=True, allow_null=True)
    submit_disabled = traitlets.Bool(default_value=True).tag(sync=True, allow_null=False)
    submission_in_progress = traitlets.Bool(default_value=False).tag(sync=True, allow_null=False)
    success_snackbar = traitlets.Bool(default_value=False).tag(sync=True, allow_null=False)
    failure_snackbar = traitlets.Bool(default_value=False).tag(sync=True, allow_null=False)
    info_snackbar = traitlets.Bool(default_value=False).tag(sync=True, allow_null=False)
    multiple_signal_prompt = traitlets.Bool(default_value=False).tag(sync=True, allow_null=False)
    snackbar_msg = traitlets.Unicode().tag(sync=True, allow_null=True)

    def __init__(self, *args,
                 get_workbench_signals: Callable[[], List] = None,
                 update_equation_parameter: Callable[[str, Union[int, str]], None] = None,
                 get_active_equation_parameter: Callable[[str], Any] = None,
                 get_equation_representation: Callable[[], str] = None,
                 get_fitted_function: Callable[[], Callable] = None,
                 push_formulas_to_seeq: Callable[[Optional[Any]], None] = None,
                 valid_formulas: Callable[[], int] = None, **kwargs):

        self.template_file = str(CURRENT_DIR.joinpath('templates', 'ChartComponent.vue'))
        self.equation = display_latex(Math(''))
        self.output_signal = ''
        self.seeq_dependent_variable = ''
        self.active_dataframe = pd.DataFrame()
        self.units = ''
        self.tab_state = {}
        self.active_tab = None
        self.tabs_with_valid_data = []
        self.fit_coefficients = None
        self.active_equation = None

        super().__init__(*args, **kwargs)

        self.order_picker = vue.BtnToggle(v_model="value", dense=True, toggle_exclusive=True, color='#007960',
                                          mandatory=True, rounded=True,
                                          children=[vue.Btn(
                                                children=[widgets.HTMLMath(f'$${latex_repr}$$')])
                                                            for latex_repr in Equation.supported_equations()])
        self.order_picker.v_model = 2

        self.output_signal = vue.TextField(hint=f'The signal name given to the formula pushed to Seeq', v_model="",
                                           color='#007960', label='Output Signal Name', style_='font-size:1.0em')

        self.independent_picker = vue.Select(hint='Column to use for the independent (x axis) on the plot',
                                             label="Independent Variable", color="#007960",
                                             v_model='', style_='font-size:1.0em')
        self.dependent_picker = vue.Select(hint='Column to use for the dependent (y axis) on the plot',
                                           label="Dependent Variable", color="#007960", v_model='',
                                           style='font-size:1.0em')

        self.signal_picker_autocomplete = vue.Autocomplete(v_model='seeq_dependent_variable', items=[],
                                                           color='#007960', label='Independent Signal',
                                                           style_='font-size:1.0em',
                                                           hint='The Seeq signal to use for "x" in the equation.  The '
                                                                'units of this signal should be convertible to the '
                                                                'units of the Independent Variable.')

        # update callback methods
        self.get_workbench_signals = get_workbench_signals
        self.update_equation_parameter = update_equation_parameter
        self.get_active_equation_parameter = get_active_equation_parameter
        self.get_equation_representation = get_equation_representation
        self.get_fitted_function = get_fitted_function
        self.push_formulas_to_seeq = push_formulas_to_seeq
        self.valid_formulas = valid_formulas

        self.populate_autocomplete_signals()

        # update submission button disable status on change in the pre-requisites...
        self.signal_picker_autocomplete.observe(self.update_button_status)
        self.output_signal.observe(self.update_button_status)

        # monitor for changes to tab state...
        self.signal_picker_autocomplete.on_event('change', self.on_signal_picker_change)
        self.output_signal.on_event('change', self.on_output_signal_change)
        self.independent_picker.on_event('change', self.on_independent_picker_change)
        self.dependent_picker.on_event('change', self.on_dependent_picker_change)
        self.order_picker.on_event('change', self.on_order_change)

        self.components = {
            "signal-picker-autocomplete": self.signal_picker_autocomplete,
            "independent-picker": self.independent_picker,
            "dependent-picker": self.dependent_picker,
            "order-picker": self.order_picker,
            "output-field": self.output_signal
        }

    # Equation Parameter Change Methods
    def on_signal_picker_change(self, *args):
        if self.update_equation_parameter:
            self.update_equation_parameter("independent_signal", args[-1])

    def on_output_signal_change(self, *args):
        if self.update_equation_parameter:
            self.update_equation_parameter("output_signal", args[-1])

    def on_independent_picker_change(self, *args):
        if self.update_equation_parameter:
            self.update_equation_parameter("independent_variable", args[-1])
        self.update_chart()

    def on_dependent_picker_change(self, *args):
        if self.update_equation_parameter:
            self.update_equation_parameter("dependent_variable", args[-1])
        self.update_chart()

    def on_order_change(self, *args):
        if self.update_equation_parameter:
            self.update_equation_parameter("order", args[-1])
        self.update_chart()

    # UI Update methods
    @threaded
    def populate_autocomplete_signals(self):
        self.signal_picker_autocomplete.items = self.get_workbench_signals() if self.get_workbench_signals else None

    def update_button_status(self, _):
        self.submit_disabled = self.signal_picker_autocomplete.v_model == "" or self.output_signal.v_model == ""

    def update_chart(self, *_):
        equation_string_repr = self.get_equation_representation()
        latex_representation = printing.latex(equation_string_repr)
        self.equation = widgets.HTMLMath(f'$${latex_representation}$$')
        self.plot_widget = self._construct_plot_widget()

    def _construct_plot_widget(self):

        x_data = self.get_active_equation_parameter('x_data')
        y_data = self.get_active_equation_parameter('y_data')
        x_units = self.get_active_equation_parameter('x_units')
        y_units = self.get_active_equation_parameter('y_units')
        independent_variable = self.get_active_equation_parameter('independent_variable')
        dependent_variable = self.get_active_equation_parameter('dependent_variable')

        figure = plt.figure()
        figure.layout.min_height = '300px'
        figure.layout.height = 'auto'
        figure.layout.width = 'auto'
        figure.fig_margin = {'top': 20, 'bottom': 70, 'left': 50, 'right': 45}

        function_grid = np.linspace(x_data[0], x_data[-1], num=50)

        fitted_func = self.get_fitted_function()
        fitted_data = fitted_func(function_grid)

        plt.scatter(x_data, y_data, colors='darkslategray')
        plt.plot(function_grid, fitted_data, colors='#007960')
        plt.xlim(x_data[0] - 0.25 * (x_data[-1] - x_data[0]), x_data[-1] + 0.25 * (x_data[-1] - x_data[0]))

        figure.axes[0].grid_lines = 'none'
        figure.axes[1].grid_lines = 'none'
        figure.axes[0].num_ticks = 8
        figure.axes[0].label = f"{independent_variable} ({x_units})"
        figure.axes[1].label = f"{dependent_variable} ({y_units})"
        figure.axes[0].label_offset = '40px'
        figure.axes[1].label_offset = '40px'

        return figure

    # Event handling methods
    @threaded
    def set_information_panel_message(self, message=None):

        self.snackbar_msg = message['message']
        self.success_snackbar = message['type'] == MessageType.SUCCESS
        self.info_snackbar = message['type'] == MessageType.INFORMATION
        self.failure_snackbar = message['type'] == MessageType.ERROR

    def data_changed(self, data=None):

        self.active_tab = data['tab']
        self.active_dataframe = data['data']
        self.units = data['units']

        self.independent_picker.items = list(data['data'].columns)
        self.dependent_picker.items = list(data['data'].columns)

        self.output_signal.v_model = self.get_active_equation_parameter('output_signal')
        self.signal_picker_autocomplete.v_model = self.get_active_equation_parameter('independent_signal')

        # what we would like here is defaults, so that if the order returns none,
        if self.get_active_equation_parameter('order') is None:
            self.update_equation_parameter('order', 2)
        self.order_picker.v_model = self.get_active_equation_parameter('order')

        if self.get_active_equation_parameter('independent_variable') is None:
            self.update_equation_parameter('independent_variable', self.independent_picker.items[0])
        self.independent_picker.v_model = self.get_active_equation_parameter('independent_variable')

        if self.get_active_equation_parameter('dependent_variable') is None:
            self.update_equation_parameter('dependent_variable', self.dependent_picker.items[1])
        self.dependent_picker.v_model = self.get_active_equation_parameter('dependent_variable')

        self.update_chart()

    def vue_submit(self, _):
        if self.valid_formulas() == 1:
            self.submission_in_progress = True
            self.push_formulas_to_seeq()              # type: ignore
            self.submission_in_progress = False
        elif self.valid_formulas() > 1:
            self.multiple_signal_prompt = True

    def vue_submit_all(self, _):
        self.submission_in_progress = True
        self.multiple_signal_prompt = False
        self.push_formulas_to_seeq(only_active=False)  # type: ignore
        self.submission_in_progress = False

    def vue_submit_active(self, _):
        self.submission_in_progress = True
        self.multiple_signal_prompt = False
        self.push_formulas_to_seeq()                   # type: ignore
        self.submission_in_progress = False
