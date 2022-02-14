from copy import deepcopy
import json
import io
import ipyvuetify as vue
import pandas as pd
from pathlib import Path
from rx.subject import Subject
import traitlets
from typing import Callable


CURRENT_DIR = Path(__file__).parent.resolve()


class TabbedDataFrame(vue.VuetifyTemplate):
    headers = traitlets.List().tag(sync=True, allow_null=True)
    items = traitlets.List().tag(sync=True, allow_null=True)
    file_contents = traitlets.Unicode().tag(sync=True, allow_null=True)
    tabs = traitlets.List([]).tag(sync=True, allow_null=True)

    def __init__(self, *args,
                 change_active_tab: Callable[[str], None] = None, **kwargs):

        self.template_file = str(CURRENT_DIR.joinpath('templates', 'TabbedDataFrame.vue'))
        super().__init__(*args, **kwargs)
        self.dataframe = pd.DataFrame()
        self.active_tab = None
        self.units = None
        self.change_active_tab = change_active_tab

    def initialize_dataframe(self, data):
        self.tabs = data['tabs']
        self.dataframe = data['data']

    @staticmethod
    def clean_header(text):
        return text.strip().replace('_', ' ').replace('-', ' ').title()

    def vue_tab_change(self, change):
        self.active_tab = self.tabs[change]
        self.set_table_contents(self.active_tab)

        if self.change_active_tab:
            self.change_active_tab(self.active_tab)

    def set_table_contents(self, active_tab):
        units = self.dataframe.iloc[0].to_dict()
        units.pop('Curve')
        self.units = units
        df = deepcopy(self.dataframe)
        active_curve_data = df[df['Curve'] == active_tab].drop('Curve', axis=1)

        self.headers = [{"text": f'{self.clean_header(name)} ({unit})', "value": name}
                        for name, unit in zip(list(active_curve_data.columns), self.units.values())]
        self.items = json.loads(active_curve_data.to_json(orient='records'))
