---
layout: default
title: ROIs editing
---

## Preliminary review
When opening for the first time a Slide, user will perform a Preliminary review on the image. From this point on, the user can navigate on the viewer and zoom in/out to see the full details of the slide, he/she has to specify the type of staining (choosing among the options) and a quality evaluation. If the quality of the image is considered not good enough to perform the analysis, the user must specify a reason and, optionally, add notes. In that case, by saving, the review of the current slide is closed and the user will be redirect on the slide list page. If the quality is good, the user will be redirect to the ROIs editing page.  
Note that, if the image does not have a good quality but the user still wants to go ahead with the analysis, he/she can do it by selecting the "Good quality" button and, preferably, adding a comment to explain that.

![preliminary_review](./img/5.preliminary_review.png)


![staining](./img/6.staining.png)
![quality_control](./img/7.quality_control.png)
![quality_comment](./img/7.2.comment.png)

&nbsp;

## ROIs editing

After the Preliminary Review is completed and only if the images was marked as “Good” user can access the interface of the ROIs editing mode. He\she can navigate on the image, see the already created ROIs (in the ROIs list block), create new ROIs or clear all the existing ones (see details below).

![editing_home](./img/8.editing_home.png)

&nbsp;

## New slice
Clicking on the “New item” button, the user can draw a slice (only a slice if it is the very first ROI) choosing among the polygon-drawing tool (shown as example in the figures) and the freehand one. To use the polygon-drawing tool simply drop points on the image and confirm with the “ ✔ ” button after the desired shape has been completed. Alternatively, the shape can be discharged with the “ ✗ ” button if the user is not satisfied with it. Then, add the number of cores and save the ROI, which will be added to the ROIs list in the left side. The eye button is to center and adapt the ROI to the viewer. The same functionality can be obtained by clicking on a ROI from the ROIs list.

![new_slice](./img/9.new_slice.png)
![new_slice](./img/10.new_slice_tools.png)
![new_slice](./img/11.new_slice_accept.png)
![new_slice](./img/12.new_slice_save.png)


![slice_view](./img/13.slice_view.png)

&nbsp;

## New core
The procedure is the same seen for the slice. As an example, here is used the freehand-drawing tool that can be activated by clicking on a point of the viewer and keeping the mouse pressed dragging it until the shape is completed, releasing the mouse will create the shape and automatically accept it. Note that a new core can be added only if at least one slice is already present.

![new_core](./img/14.new_core.png)
![new_core_tools](./img/15.new_core_tools.png)

![new_core_save](./img/16.new_core_save.png)

&nbsp;

## Error message
It should be noted that the system accepts core ROIs only if the shape is contained entirely inside the perimeter of a slice. Otherwise, a pop-up with an error message will be displayed and the shape will be discharged.

![hierarchy_error](./img/17.hierarchy_error.png)

## Ruler tool
To get the measure of the core length the user can drop points like he/she does using the polygon-drawing tool. By accepting the polyline with the “✔” button, the measure will be displayed. Ruler tool can also be deactivated with the “✗” button. The core ROI can be saved only its measure
exists.

![ruler_tool](./img/18.ruler_tool.png)

Optionally, the user can get the measure of the tumor (if present) in the same way using the ruler tool for the tumor length.

![ruler_tool_tumor](./img/18.2.ruler_tool_tumor.png)

![core_view_uom](./img/18.4.core_view_uom.png)

&nbsp;

## New focus region
The user can add a focus region just like he/she does with the core. Note that a focus region can be added only if at least a core exists and it must be drawn inside a core to be accepted.

![new_focus_region](./img/19.new_focus_region.png)
![new_focus_region_tools](./img/20.new_focus_region_tools.png)

![new_focus_region_save_tumor](./img/21.new_focus_region_save_tumor.png) 	

The user has to measure the length of the region with the ruler tool and to specify if it is a tumor region or not with the flag. Tumor regions are drawn in red while non-tumor regions are green.

![new_focus_region_view_tumor](./img/22.new_focus_region_view_tumor.png)

![new_focus_region_view_normal](./img/24.new_focus_region_view_normal.png)

&nbsp;

## ROIs list
The list of the ROIs is automatically populated every time the user add a new region of interest. Moreover it is useful to jump quickly from a ROI to another one and display the related annotations.

![tree_moving](./img/23.tree_moving.png)

&nbsp;

## Delete a single ROI
When a ROI is selected, it can be deleted with the “Delete” button, but the user should be careful because the system implements a “cascade” deleting. It means that if the ROI is a slice, also any contained core or focus region will be deleted. The same happens if the ROI is a core: all the focus region children will be deleted too. The delete process is irreversible.

![cascade_deleting](./img/25.cascade_deleting.png)

&nbsp;

## Clear all the existing ROIs
In the top-right corner, the “Clear ROIs” button is to delete at the same time all the existing ROIs. The user will be warned with a pop-up that this operation is irreversible.  


![clear_rois](./img/26.clear_rois.png) 

&nbsp;

## Confirm ROIs

By confirming the ROIs the user closes the editing phase, and he/she will be redirect to the worklist containing the pending annotations to proceede.

![confirm_rois](./img/28.confirm_rois.png)

In the worklist the user can find a button beside the case that says "Start clinical annotation" (this happens when all the slides of the case are marked as good) or "Continue clinical annotation" (when there exist some bad qality images in the case). The former is green while the latter is yellow.

&nbsp;
