import "./setup";

import closest from "closest";

import { $, $$, component, each } from "./util/dom";

import date from "./transforms/date";
import editor from "./transforms/editor";
import time from "./transforms/time";
import user_content from "./transforms/user-content";
import group_header from "./transforms/group-header";
import gallery from "./transforms/gallery";
import transform_icon from "./transforms/transformicons";
import input from "./transforms/input";
import snake from "./transforms/snake";
import openable from "./transforms/openable";
import clipboard from "./transforms/clipboard";


function init(search_in = document) {
    // initialize components on load
    component("date", date, search_in);
    component("editor", editor, search_in);
    component("time", time, search_in);
    component("user-content", user_content, search_in);
    component("group-header", group_header, search_in);
    component("gallery", gallery, search_in);
    component("snake", snake, search_in);
    component("openable", openable, search_in);
    component("clipboard", clipboard, search_in);

    // initialize components not based on component interface
    transform_icon($(".tcon-wrap"));
    each($$("input, textarea"), (el) => input(el, { target: closest(el, ".form-group") }));
}

init();
