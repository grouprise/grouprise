import Snake from "./transforms/snake";

Snake(document.querySelector(".snake"), { on_finish: () => location.href = "https://stadtgestalten.org" });
