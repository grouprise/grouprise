function create_alert(message, type) {
    const alert = document.createElement("div");
    alert.classList.add("alert");
    alert.classList.add("alert-page");
    alert.classList.add(`alert-${type}`);
    alert.innerHTML = message;
    
    return alert;
}

function message_factory(type) {
    return function(message) {
        return new Promise((resolve) => {
            const alert = create_alert(message, type);

            alert.addEventListener("animationend", function remove() {
                alert.removeEventListener("animationend", remove, false);
                alert.remove();
                resolve();
            }, false);

            document.body.appendChild(alert);
            alert.classList.add("alert-auto");
        });
    }
}

const success = message_factory("success");
const danger = message_factory("danger");
const info = message_factory("info");

export { success, danger, info };


