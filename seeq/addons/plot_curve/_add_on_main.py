from seeq.addons.plot_curve.ui_components import AppLayout
from seeq.addons.plot_curve.backend import BackEnd


class PlotCurve:

    def __init__(self, workbook=None, worksheet=None, url=None):
        self.workbook = workbook
        self.worksheet = worksheet
        self.url = url

        # instantiate an instance of the backend...
        self.backend = BackEnd(self.workbook, self.worksheet)

        # instantiate an instance of the front end with backend callbacks...
        self.plot_curve_component = AppLayout(get_workbench_signals=self.backend.get_workbench_signals,
                                              update_equation_parameter=self.backend.update_active_equation_parameter,
                                              file_loaded_callback=self.backend.on_file_load,
                                              change_active_tab=self.backend.on_tab_change,
                                              get_active_equation_parameter=self.backend.get_active_equation_parameter,
                                              get_equation_representation=self.backend.get_equation_representation,
                                              get_fitted_function=self.backend.get_fitted_function,
                                              push_formulas_to_seeq=self.backend.push_formulas,
                                              valid_formulas=self.backend.valid_formulas)

        # hook up reactive components (backend to front end communication)
        self.backend.file_change_events.subscribe(self.plot_curve_component.tabbed_dataframe.initialize_dataframe)
        self.backend.file_change_events.subscribe(self.plot_curve_component.increment_stepper)
        self.backend.data_change_events.subscribe(self.plot_curve_component.chart.data_changed)
        self.backend.message_events.subscribe(self.plot_curve_component.chart.set_information_panel_message)

    def run(self):
        return self.plot_curve_component
