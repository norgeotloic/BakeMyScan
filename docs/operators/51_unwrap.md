# Unwrapping

This operator is just a convenience button to unwrap a model.

The user can choose between 3 options:
* **Basic**: Will do a basic UV unwrap of the model in edit mode. Only useful with hand-created seams, as the result will often be too stretched for organic models and scans.
* **Smart**: Applies a "Smart UV project" on the selected model
* **Smarter**: Applies a "Smart UV project" on the selected model, and a few rounds of packing + scaling to optimize the layout.

In the future, I'd like to incorporate an efficient packing solution at this step, as the UV layouts from blender leave a lot of space not used by textures...
