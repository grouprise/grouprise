import closest from "closest";

import { $, $$, component } from "./util/dom";
import tcon from "./util/transformicons";

import date from "./transforms/date";
import editor from "./transforms/editor";
import time from "./transforms/time";
import user_content from "./transforms/user-content";
import group_header from "./transforms/group-header";
import gallery from "./transforms/gallery";
import input from "./transforms/input";

tcon.add($(".tcon-wrap"));
$$("input, textarea").forEach((el) => input(el, { target: closest(el, ".form-group") }));


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

import fireworks from "./fireworks";
const today = new Date();
if(today.getFullYear() === 2016 && today.getMonth() === 8 && today.getDate() === 13 && location.pathname === "/") {
    fireworks();
}
