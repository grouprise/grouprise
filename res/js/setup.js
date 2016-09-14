import { $ } from "./util/dom";

// load config
window.app = {
    conf: JSON.parse($("#app-configuration").textContent)
};
