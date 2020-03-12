from visual_items.rectangle import Rectangle

class EckertPositoinDrill:
    def __init__(self):
        self.objects = []
        self.landing_zone = Rectangle(50, 50, 100)
        self.objects.append(self.landing_zone)

    def get_objects(self):
        return self.objects
