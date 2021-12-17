import ipyvuetify as vue
import traitlets
from pathlib import Path
from typing import Callable

CURRENT_DIR = Path(__file__).parent.resolve()


class FileReader(vue.VuetifyTemplate):
    allowed_extensions = traitlets.Unicode(default_value='.csv').tag(sync=True)
    file_contents = traitlets.Unicode(default_value='').tag(sync=True, allow_null=True)

    def __init__(self, *args,
                 file_loaded_callback: Callable[[str], None] = None, **kwargs):
        self.template_file = str(CURRENT_DIR.joinpath('templates', 'FileReader.vue'))
        super().__init__(*args, **kwargs)
        self.file_loaded_callback = file_loaded_callback
        self.observe(self.on_file_loaded, names='file_contents')

    def on_file_loaded(self, _):
        if self.file_loaded_callback:
            self.file_loaded_callback(self.file_contents)

