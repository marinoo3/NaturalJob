function loadEditor() {
    const easyMDE = new EasyMDE({
        element: document.querySelector('#md-content'),
        sideBySideFullscreen: false,
        hideIcons: ["image", "preview", "side-by-side", "fullscreen", "guide", "|"]
    });
    EasyMDE.toggleSideBySide(easyMDE);
}


loadEditor();
