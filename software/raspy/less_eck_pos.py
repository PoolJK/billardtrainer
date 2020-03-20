from visual_items.rectangle import Rectangle


class EckertPositionDrill:
    def __init__(self):
        self.objects = []
        self.landing_zone = Rectangle(-100, -100, 200)
        self.objects.append(self.landing_zone)

    def get_objects(self):
        return self.objects
