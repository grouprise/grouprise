import "./setup";

import { $$, component, mapCall } from "luett";
import closest from "closest";

import date from "./transforms/date";
import editor from "./transforms/editor";
import time from "./transforms/time";
import user_content from "./transforms/user-content";
import gallery from "./transforms/gallery";
import transform_icon from "./transforms/transformicons";
import input from "./transforms/input";
import snake from "./transforms/snake";
import openable from "./transforms/openable";
import clipboard from "./transforms/clipboard";
import browser_warning from "./transforms/browser-warning";
import carousel from "./transforms/carousel";

function init(search_in = document) {
    const opts = { root: search_in };
    
    // initialize components on load
    component("date", date, opts);
    component("editor", editor, opts);
    component("time", time, opts);
    component("user-content", user_content, opts);
    component("gallery", gallery, opts);
    component("snake", snake, opts);
    component("openable", openable, opts);
    component("clipboard", clipboard, opts);
    component("browser-warning", browser_warning, opts);
    component("carousel", carousel, opts);
    component("tcon", transform_icon, opts);

    // initialize components not based on component interface
    mapCall($$("input, textarea"), (el) => input(el, { target: closest(el, ".form-group") }));
}

init();
