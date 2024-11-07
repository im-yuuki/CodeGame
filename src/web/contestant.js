document.addEventListener('DOMContentLoaded', function() {
    // Prevent right-click
    document.addEventListener('contextmenu', function(event) {
        event.preventDefault();
    });

    // Prevent text selection
    document.addEventListener('selectstart', function(event) {
        event.preventDefault();
    });

    // Prevent image dragging
    document.querySelectorAll('img').forEach(function(img) {
        img.addEventListener('dragstart', function(event) {
            event.preventDefault();
        });
    });

    // Show hidden menu only when Ctrl key is pressed
    const hiddenMenu = document.getElementById('hidden-menu');

    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey) hiddenMenu.hidden = false;
    });

    document.addEventListener('keyup', function(event) {
        if (!event.ctrlKey) hiddenMenu.hidden = true;
    });

    // Theme selector
    const themeSelectors = document.querySelectorAll('.theme-selector');
    for (let i = 0; i < themeSelectors.length; i++) {
        themeSelectors[i].addEventListener('click', function() {
            const color = themeSelectors[i].computedStyleMap().get('background-color').toString();
            document.documentElement.style.setProperty('--theme-color', color);
        });
    }

    const resigterForm = document.getElementById('register-form');
    resigterForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const btn = document.getElementById('register-btn');
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "../api/contestant/add", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.timeout = 10000;
        xhr.onload = function() {
            btn.disabled = false;
            btn.innerHTML = "Tham gia";
            if (xhr.status !== 200) {
                toastr.error("Yêu cầu thất bại. Mã lỗi: " + xhr.status);
                return;
            }
            resigterForm.hidden = true;
            document.getElementById("waiting").hidden = false;
        };
        xhr.onerror = function() {
            toastr.error("Đã xảy ra lỗi khi kết nối với máy chủ");
            btn.disabled = false;
            btn.innerHTML = "Tham gia";
        };
        const data = {
            name: resigterForm.name.value,
            color: document.documentElement.style.getPropertyValue('--theme-color'),
        }
        btn.disabled = true;
        btn.innerHTML = 'Vui lòng chờ...';
        xhr.send(JSON.stringify(data));
    });
});