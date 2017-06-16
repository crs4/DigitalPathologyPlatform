---
layout: default
title: ROIs Annotations
---
# ROIs Annotations

## Audience
This section of the tutorial is intended for the users of the <span style="color:red">ROIs Reviewers</span> group, which are allowed to draw regions of interest and take measures on the images.

## Worklist
In the worklist page, pending ROIs Annotations have one of these buttons beside:

- "Start ROIs Annotation" (green), when any slide has been reviewed yet;
- "Continue ROIs Annotation" (yellow), when the evaluation of at least one slide of the case has been started.

By clicking one of those buttons, users can access to the ROIs Annotations phase.

![confirm_rois](./img/3.1.worklist_rois_ed.png)

## ROIs Review Steps
This page which shows the list of all the slides related to the selected case. Depending on the status of the slide reviews, users can:

- **start** the review with the green "Start slide review" button, in case of not-started-yet reviews; 
- **continue** the review with the blue "Continue slide review" button, if the review has been already initiated; 
- **reopen** an already completed review with the yellow "Reopen review" button. 

<span style="color:red">❗</span> The Reopen operation is available **only if** any Clinical Annotation Step for that slide has been started yet by a Clinical Reviewer.

In case of slides classified as "bad quality", the ROIs review can not be reopened and it is marked with the grey disabled "Slide review completed" button.

![slidelist](./img/4.slidelist.png)
&nbsp;




## Preliminary review - Slide Quality Control
When opening for the first time a Slide, user will perform a Preliminary review on the image. From this point on, the user can navigate on the viewer and zoom in/out to see the full details of the slide using the navigation panel. He/she has to specify the type of staining (choosing among the options) and a quality evaluation. If the quality of the image is considered not good enough to perform the analysis, the user must select a reason and, optionally, add notes. In that case, by saving, the review of the current slide is closed and the user will be redirected on the slide list page. If the quality is good, the user will be redirected to the ROIs editing page.  
Note that, if the image does not have a good quality but the user still wants to go ahead with the analysis, he/she can do it by selecting the "Good quality" button and, preferably, adding a comment to explain that.

![preliminary_review](./img/5.preliminary_review.png)


![staining](./img/6.staining.png)
![quality_control](./img/7.quality_control.png)
![quality_commernt](./img/7.2.comment.png)

&nbsp;

## ROIs Editing

After the Preliminary Review is completed and only if the images was marked as “Good”, the User can access the interface of the ROIs editing operations. He\she can navigate on the image, see the already created ROIs (in the ROIs list block), create new ROIs, clear all the existing ones or confirm to close the drawing step (see details below).

![editing_home](./img/8.editing_home.png)

&nbsp;

## New Slice - Polygon-drawing Tool
To add a ROI, the user can click on the "New item" menu and choose one of the options (only a slice if it is the very first ROI). To draw the shape, the user can choose among the polygon-drawing tool (shown as example in the figures) and the freehand one. To use the polygon-drawing tool simply drop points on the image and confirm with the “ ✔ ” button after the desired shape has been completed. Alternatively, the shape can be discharged with the “ ✗ ” button if the user is not satisfied with it. Then, add the number of cores and save the ROI, which will be added to the ROIs list in the left side. The eye button is to center and adapt the ROI to the viewer. The same functionality can be obtained by clicking on a ROI from the ROIs list.

![new_slice](./img/9.new_slice.png)

![new_slice](./img/10.new_slice_tools.png)
![new_slice](./img/11.new_slice_accept.png)
![new_slice](./img/12.new_slice_save.png)


![slice_view](./img/13.slice_view.png)

&nbsp;

## New Core - Freehand-drawing Tool
The procedure is the same seen for the slice. As an example, here is used the freehand-drawing tool that can be activated by clicking on a point of the viewer and keeping the mouse pressed dragging it until the shape is completed. Releasing the mouse will create the shape and automatically accept it. Note that a new core can be added only if at least one slice is already present and it must be, even partially, contained inside a slice.

![new_core](./img/14.new_core.png)
![new_core_tools](./img/15.new_core_tools.png)

![new_core_save](./img/16.new_core_save.png)

&nbsp;

## Error Message
The system discharges core ROIs that are entirely outside the perimeter of a slice. In that case, a pop-up with an error message will be displayed to inform the user. Otherwise, if the shape is partially contained inside the slice, only the intersection will be maintained. The system will behave the same for focus region drawn partially outside a core (see below an example).  

![hierarchy_error](./img/17.hierarchy_error.png)

## Ruler Tool
To get the measure of the core length, the User can drop points like he/she does using the polygon-drawing tool. By accepting the polyline with the “✔” button, the measure will be recorded. Ruler tool can also be deactivated with the “✗” button. The core ROI can be saved only if its measure exists.

![ruler_tool](./img/18.ruler_tool.png)

Optionally, the user can get the measure of the tumor (if present) in the same way using the ruler tool for the tumor length.

![ruler_tool_tumor](./img/18.2.ruler_tool_tumor.png)

For each measure, the user can change the unity of measure (millimetres or micrometres) through the drop-down menu beside the value. 

![core_view_uom](./img/18.4.core_view_uom.png)

&nbsp;

## New Focus Region
The User can add a focus region just like he/she did with the core. Note that a focus region can be added only if at least a core exists and it must be drawn inside a core to be accepted.

![new_focus_region](./img/19.new_focus_region.png)
![new_focus_region_tools](./img/20.new_focus_region_tools.png)

If the focus region is drawn partially outside the core, the system will automatically save only the intersection of the shapes.

![inters_1](./img/19.fr_inters_1.png)
![inters_2](./img/19.fr_inters_2.png)

The user has to measure the length of the region with the ruler tool and can specify if it is a tumor region with the check button. Tumor regions are drawn in red while non-tumor regions are green.

![new_focus_region_save_tumor](./img/21.new_focus_region_save_tumor.png) 	

![new_focus_region_view_tumor](./img/22.new_focus_region_view_tumor.png)

![new_focus_region_view_normal](./img/24.new_focus_region_view_normal.png)

&nbsp;

## ROIs List
The list of the ROIs is automatically populated every time the User add a new region of interest. This panel is useful to jump quickly from a ROI to another one, display it centered and adapted to the viewer and read the related annotations.

![tree_moving](./img/23.tree_moving.png)

&nbsp;

## Delete a Single ROI
When a ROI is selected, it can be deleted with the “Delete” button, but the User should be careful because the system implements a “cascade” deleting. It means that if the ROI is a slice, also any contained core or focus region will be deleted. The same happens if the ROI is a core: all the focus region children will be deleted too. 

<span style="color:red">❗</span> This operation is **irreversible**.

![cascade_deleting](./img/25.cascade_deleting.png)

&nbsp;

## Clear All the Existing ROIs
In the top-right corner, the “Clear ROIs” button is to delete at the same time all the existing ROIs. 

<span style="color:red">❗</span> This operation is **irreversible**.  


![clear_rois](./img/26.clear_rois.png) 

&nbsp;

## Confirm ROIs Review step

By confirming the ROIs the user closes the editing phase, and he/she will be redirect to the worklist containing the pending annotations to proceed. This button becomes available only if at least a slice ROI has been added. 

![confirm_rois](./img/28.confirm_rois.png)

## ROIs annotations completed
After completing the last ROIs review in the slide list of a case, the ROIs annotation for the case is completed and the user is redirected to the Worklist page. From this point on, the Clinical Annotations phase for that case can start for both the <span style="color:red">ROIs</span> and the <span style="color:blue">Clinical</span> Reviewers.

