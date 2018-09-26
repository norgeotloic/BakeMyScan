### Remesh different parts of the model with mmgs

The previous feature therefore allows you to remesh different parts of the model independantly, like I did with [this model of a Napoleon statue on Sketchfab](https://skfb.ly/6xHwD), remeshing details such as the sword separately from the horse's body:

![napo](https://user-images.githubusercontent.com/37718992/44310717-26dd4200-a3db-11e8-953c-2bdf2e6263e8.jpg)

To do so, you'll have to separate your model into different "submodels", while keeping the boundaries between them intact:

1. In Edit-mode, select all the edges separating the zones you wish to remesh independently (using **Edge loops**, **Select boundary loop**, or just the plain **Ctrl + right click** method for instance)
2. Use **Mark as sharp** to... mark them as sharp
3. Use the **Edge split** operator to split the regions you segmented
4. Select each region with **Select linked** or **Ctrl + L**, and separate them into a different object with **Separate (or p)** -> **Selection**. You could also just select everything and use **Separate** -> **Loose parts** if your model does not have loose parts you do not want to remesh separately.

You should now have as many objects as regions you created, which you can then remesh independently with the **MMGS** button, specifying a custom hausdorff ratio for each of them (keep in mind that the ratio is with the selected object's size, you'll therefore have to adjust!).

Once all your remeshed parts have been re-imported, you can then join them into an unique object by using **Join** or **Ctrl + J**, and jump to Edit-mode to **Remove doubles** vertices.
