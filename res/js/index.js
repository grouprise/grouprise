import { component } from "./util/dom";
import date from "./components/date";
import editor from "./components/editor";
import emoji from "./transformers/emoji";

// initialize components on load
component("date", date);
component("editor", editor);
