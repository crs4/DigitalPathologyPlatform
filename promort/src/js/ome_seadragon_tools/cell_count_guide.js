/*
 * Copyright (c) 2019, CRS4
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

AnnotationsEventsController.CELLULAR_COUNT_HELPER_TOOL = 'cell_count_helper';

AnnotationsEventsController.prototype.initializeCellularCountHelperTool = function (box_size, box_config,
                                                                                    switch_on_id, switch_off_id) {
    //by default, initialize dummy tool
    this.initializeDummyTool();

    if (!(AnnotationsEventsController.CELLULAR_COUNT_HELPER_TOOL in this.initialized_tools)) {
        this.annotation_controller.tmp_helper = undefined;
        this.annotation_controller.tmp_helper_id = 'tmp_helper';
        this.annotation_controller.helper_config = box_config;
        this.annotation_controller.helper_box_size = box_size;

        this.annotation_controller.getBoxSizeInPixels = function () {
            return (this.helper_box_size * (1.0/this.image_mpp));
        };

        this.annotation_controller.createHelperBox = function (x, y) {
            var box_size = this.getBoxSizeInPixels();
            var real_x = (x-(box_size/2)) + this.x_offset;
            var real_y = (y-(box_size/2)) + this.y_offset;
            this.drawRectangle(this.tmp_helper_id, real_x, real_y, box_size, box_size,
                undefined, this.helper_config, true);
            this.tmp_helper = this.getShape(this.tmp_helper_id);
            $("#" + this.canvas_id).trigger('cellular_count_helper.created',
                [this.tmp_helper_id]);
        };

        this.annotation_controller.deleteHelperBox = function () {
            if (typeof this.tmp_helper !== 'undefined') {
                this.deleteShape(this.tmp_helper_id);
                this.tmp_helper = undefined;
            }
        };

        this.annotation_controller.serializeHelperBox = function () {
            var helper_box_json = this.getShapeJSON(this.tmp_helper_id);
            helper_box_json.shape_id = this.getFirstAvailableLabel('cc_helper');
            this.deleteHelperBox();
            $("#" + this.canvas_id).trigger('cellular_count_helper.saved',
                [helper_box_json]);
        };

        var cellular_count_helper_tool = new paper.Tool();

        cellular_count_helper_tool.annotations_controller = this.annotation_controller;

        cellular_count_helper_tool.onMouseDown = function (event) {
            this.annotations_controller.deleteHelperBox();
            this.annotations_controller.createHelperBox(event.point.x, event.point.y);
        };

        cellular_count_helper_tool.onMouseDrag = function (event) {
            this.annotations_controller.deleteHelperBox();
            this.annotations_controller.createHelperBox(event.point.x, event.point.y);
        };

        cellular_count_helper_tool.onMouseUp = function (event) {
            $("#" + this.annotations_controller.canvas_id).trigger('cellular_count_helper.placed');
        };

        this.initialized_tools[AnnotationsEventsController.CELLULAR_COUNT_HELPER_TOOL] = cellular_count_helper_tool;

        this.bindControllers = function (switch_on_id, switch_off_id) {
            if (typeof switch_on_id !== 'undefined') {
                this._bind_switch(switch_on_id, AnnotationsEventsController.CELLULAR_COUNT_HELPER_TOOL);
            }

            if (typeof switch_off_id !== 'undefined') {
                $("#" + switch_off_id).bind(
                    'click',
                    {annotation_controller: this.annotation_controller},
                    function (event) {
                        event.data.annotation_controller.serializeHelperBox();
                    }
                );
            }
        };

        this.bindControllers(switch_on_id, switch_off_id);

    } else {
        console.warn('Tool "' + AnnotationsEventsController.CELLULAR_COUNT_HELPER_TOOL +'" already initialized');
    }
};