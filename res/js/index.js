import { component, replace } from "./util/dom";
import { evented_function } from "./util/events";
import date from "./components/date";
import editor from "./components/editor";
import time from "./components/time";
import user_content from "./components/user-content";
import image_upload from "./components/image-upload";
import group_header from "./components/group-header";

// create evented functions
const _replace = evented_function(replace);

// add evented function event listeners
_replace.on("call", init);


function init(search_in = document) {
    // initialize components on load
    component("date", date, search_in);
    component("editor", editor, search_in);
    component("time", time, search_in);
    component("user-content", user_content, search_in);
    component("group-header", group_header, search_in);
    component("image-upload", image_upload, { root: search_in, conf: { replace: _replace } });
}

init();
