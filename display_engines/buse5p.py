from .engine_base import EngineBase


class Engine(EngineBase):
    """
    Engine for 5-panel BUSE display.
    Entire width is used for time drawing.
    """

    def __init__(self, config):
        super().__init__(config)
        self.panels = 5

    def draw_time(self, time_data):
        """
        Draw time using full display area
        """
        return self.predraw_time(time_data)
