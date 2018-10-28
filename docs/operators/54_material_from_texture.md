# New material from texture

By providing an image texture, this operator will try to create a PBR material containing similar textures in the same directory.

For instance, if the texture you select is called "elephant_normal.png", the operator will create a new material and assign the texture to the normal slot (as it recognized the suffix "normal").

It will then look for other textures in the directory starting with "elephant", and will try to assign the textures to appropriate slots according to the method explained on [this page concerning texture names](/docs/about_texture_names.md).

"elephant_base_color.tiff" would therefore be linked to the albedo, and "elephant_rough.jpeg" to the roughness. "elephant_sghret.jpg" however will be ignored and left unused...
