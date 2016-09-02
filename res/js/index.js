import { component } from "./util/dom";
import date from "./transforms/date";
import editor from "./transforms/editor";
import time from "./transforms/time";
import user_content from "./transforms/user-content";
import group_header from "./transforms/group-header";
import gallery from "./transforms/gallery";


function init(search_in = document) {
    // initialize components on load
    component("date", date, search_in);
    component("editor", editor, search_in);
    component("time", time, search_in);
    component("user-content", user_content, search_in);
    component("group-header", group_header, search_in);
    component("gallery", gallery, search_in);
}

init();
