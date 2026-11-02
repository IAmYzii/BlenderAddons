"""Tool packages live here, one folder per tool.

Each tool package must define:
    label        - name shown in the add-on preferences
    description  - one line shown next to the toggle
    register()   - register the tool's classes and properties
    unregister() - undo register()

Tools are discovered automatically from the TOOLS list below; add a new tool by adding
its folder and its name here (order = order in preferences).
"""

TOOLS = (
    "exploded_view",
    "material_assign",
)
