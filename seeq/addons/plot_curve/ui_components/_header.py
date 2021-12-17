import ipyvuetify as vue
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()


class Header(vue.VuetifyTemplate):
    template_file = str(CURRENT_DIR.joinpath('templates', 'Header.vue'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)