import fabricpy

mod = fabricpy.ModConfig(
    id="examplemod",
    name="Example Mod",
    description="An example mod for demonstration purposes.",
    version="1.0.0",
    authors=["Your Name"],
)

class MyItem(fabricpy.Item):
    def __init__(self):
        super().__init__()
        self.id = "my_special_item"
        self.name = "Special Item"
        self.max_stack_size = 16
        self.texture_path = "assets/examplemod/textures/item/my_special_item.png"

mod.registerItem(MyItem())

mod.compile()