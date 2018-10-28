# MMGS

![napo](https://user-images.githubusercontent.com/37718992/46110737-e72d2580-c1e4-11e8-8814-2bcb6cc57bb5.png)

[mmgs](http://mmgtools.org) is a powerful command-line remeshing tool, and provides a solid alternative to solutions such as Instant Meshes, Meshlab or the plain "Decimate" modifier in blender for instance.

The "basic" options available through the blender interface are described below.

## Hausdorff distance (ratio)

In a few words, mmgs processes an object by constraining the maximal distance between the resulting surface and the original one. This maximal distance is called the Hausdorff distance:

* A high Hausdorff distance will yield a final mesh more distant from the original model, but containing far less polygons.
* A lower Hausdorff distance however will give you a better approximation of the surface, but the polycount will be higher.

To ignore the impact of the size of the model, I have set the Hausdorff parameter as a **ratio of the longest model’s dimension** in the add-on.

Therefore, a 3 meters object with a Hausdorff Ratio set to 0.002 will return a surface approximation constrained to a 0.6cm distance from the original mesh. Here is an example using Suzanne as the original model:

![suzanne](https://user-images.githubusercontent.com/37718992/46110743-e7c5bc00-c1e4-11e8-8057-a783c55e3f0e.jpg)

More precise info about the Hausdorff parameter is available on [MMGPlatform website](https://www.mmgtools.org/mmg-remesher-try-mmg/mmg-remesher-options/mmg-remesher-option-hausd)

## Ignore angle detection

Keep that checked if your model is "organic", without sharp edges, for instance for the result from a 3D scan.

If your model contains sharp angles, you'll want to uncheck that button.

Below is the effect of this parameter on a model containing sharp edges, with a hausdorff ratio set to 0.001. Note that it went way better for the non-smooth model:

![smoothcube](https://user-images.githubusercontent.com/37718992/46110742-e7c5bc00-c1e4-11e8-8bba-66277341da9a.jpg)

## Advanced options

The two previous options can cover most of the usage cases for mmgs, but I also provided theother available arguments as "advanced" options, which correspond to arguments explained in more details in [mmgs documentation](https://www.mmgtools.org/mmg-remesher-try-mmg/mmg-remesher-options).
