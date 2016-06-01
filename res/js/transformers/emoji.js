import { $$} from "../util/dom";
import emoji_regex from "emoji-regex";

$$(".content-body").forEach((el) => {
    el.innerHTML = el.innerHTML.replace(emoji_regex(), "<span class='emoji' data-emoji='$&'></span>");
});
