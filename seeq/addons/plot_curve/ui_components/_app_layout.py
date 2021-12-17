import ipyvuetify as vue
import traitlets
from pathlib import Path
from seeq.addons.plot_curve.utils import threaded
from seeq.addons.plot_curve.utils import MessageType

from IPython.display import display, HTML, Javascript
from seeq.addons.plot_curve.ui_components import Header, TabbedDataFrame, ChartComponent, FileReader


CURRENT_DIR = Path(__file__).parent.resolve()


class AppLayout(vue.VuetifyTemplate):

    file_contents = traitlets.Unicode().tag(sync=True, allow_null=True)
    stepper_step = traitlets.Unicode(default_value='1').tag(sync=True)
    failure_snackbar = traitlets.Bool(default_value=False).tag(sync=True, allow_null=False)
    snackbar_msg = traitlets.Unicode().tag(sync=True, allow_null=True)

    def __init__(self, *args, **kwargs):
        self.template_file = str(CURRENT_DIR.joinpath('templates', 'AppLayout.vue'))
        super().__init__(*args, **kwargs)

        # component definitions
        self.header = Header(**kwargs)
        self.file_reader = FileReader(**kwargs)
        self.tabbed_dataframe = TabbedDataFrame(**kwargs)
        self.chart = ChartComponent(**kwargs)
        self.components = {'header': self.header,
                           'file-reader': self.file_reader,
                           'tabbed-dataframe': self.tabbed_dataframe,
                           'chart-widget': self.chart}

    def increment_stepper(self, *_):
        self.stepper_step = '2'

    # Event handling methods
    @threaded
    def set_information_panel_message(self, message=None):
        self.snackbar_msg = message['message']
        self.failure_snackbar = message['type'] == MessageType.ERROR
