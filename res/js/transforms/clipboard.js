import Clipboard from "clipboard";
import { success, danger } from "../util/notify";

export default (el, opts) => {
    const clipboard = new Clipboard(el, {
        text: opts.conf.text
    });

    clipboard.on("success", function() {
        success("URL wurde kopiert");
    });

    clipboard.on("error", function() {
        danger("URL konnte nicht kopiert werden. Bitte markiere den Text und kopiere ihn per Hand.")
    });
}
