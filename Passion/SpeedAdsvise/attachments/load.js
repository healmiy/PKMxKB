const autoLoadDuration = 5; //In Seconds
const eventList = ["keydown", "mousemove", "wheel", "touchmove", "touchstart", "touchend"];
const autoLoadTimeout = setTimeout(runScripts, autoLoadDuration * 1000);

eventList.forEach(function(event) {
    window.addEventListener(event, triggerScripts, { passive: true })
});

function triggerScripts() {
    runScripts();
    clearTimeout(autoLoadTimeout);
    eventList.forEach(function(event) {
         window.removeEventListener(event, triggerScripts, { passive: true });
    });
}

function runScripts() {
    document.querySelectorAll("script[tag]").forEach(function(scriptTag) {
        scriptTag.setAttribute("src", scriptTag.getAttribute("tag"));
    });
}