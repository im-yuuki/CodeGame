document.addEventListener('DOMContentLoaded', function() {
    const registerSection = document.getElementById('register');
    const contestSection = document.getElementById('contest');
    const statisticSection = document.getElementById('statistic');

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
        themeSelectors.forEach(selector => {
            let color = getComputedStyle(selector).backgroundColor;
            selector.addEventListener('click', function () {
                document.documentElement.style.setProperty('--theme-color', color);
                themeSelectors.forEach(s => s.classList.remove('selected'));
                selector.classList.add('selected');
            });
        });
    
    // Register handler
    const resigterForm = document.getElementById('register-form');
    resigterForm.addEventListener('submit', function(event) {
        event.preventDefault();
        let btn = document.getElementById('register-btn');
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "../api/contestant/add", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.timeout = 10000;
        xhr.onload = function() {
            btn.disabled = false;
            btn.innerHTML = "Tham gia";
            if (xhr.status !== 200) {
                alert(`Yêu cầu thất bại (${xhr.status}): ${xhr.responseText}`);
                return;
            }
            let resp = JSON.parse(xhr.responseText);
            userId = resp.uid;
            token = resp.token;
            if (userId == null || token == null) {
                alert("Invalid response from server");
                return;
            }
            localStorage.setItem("UserId", userId)
            localStorage.setItem("Authorization", token)
            resigterForm.hidden = true;
            document.getElementById("waiting").hidden = false;
        };
        xhr.onerror = function() {
            alert("");
            btn.disabled = false;
            btn.innerHTML = "Tham gia";
        };
        xhr.ontimeout = function() {
            alert("Yêu cầu thất bại: Hết thời gian chờ phản hồi từ máy chủ");
            btn.disabled = false;
            btn.innerHTML = "Tham gia";
        }
        let data = {
            name: resigterForm.name.value,
            color: document.documentElement.style.getPropertyValue('--theme-color'),
        }
        btn.disabled = true;
        btn.innerHTML = 'Vui lòng chờ...';
        xhr.send(JSON.stringify(data));
    });

    // Workspace navigation handler
    const wProblem = document.getElementById('problem');
    const wSubmission = document.getElementById('submission');
    const wRanking = document.getElementById('ranking');
    const btnProblem = document.getElementById('problem-btn');
    const btnSubmission = document.getElementById('submission-btn');
    const btnRanking = document.getElementById('ranking-btn');

    function setToggler(window, button) {
        button.addEventListener('click', function() {
            if (window.hidden) {
                window.hidden = false;
                button.classList.add('selected');
            }
            else {
                window.hidden = true;
                button.classList.remove('selected');
            }
        });
    }

    setToggler(wProblem, btnProblem);
    setToggler(wSubmission, btnSubmission);
    setToggler(wRanking, btnRanking);

    // Websocket connection
    // const ws = new WebSocket(`ws://${window.location.host}/ws`);
    // ws.timeout = 10000;
    // ws.onmessage = function(event) {
    //     let data = JSON.parse(event.data);
    //     switch (data.event) {
    //         case "CONTEST_STARTED":
    //             startContest(data.duration);
    //             break;
    //         case "CONTEST_STOPPED":
    //             endContest();
    //             break;
    //         case "CONTEST_RESET":
    //             reset();
    //             break;
    //     }
    // }
    // ws.onclose = function() {
    //     alert('Mất kết nối tới máy chủ.');
    //     reset();
    // };
    // ws.onerror = function() {
    //     alert('Đã xảy ra lỗi khi kết nối tới máy chủ.');
    //     reset();
    // };
    // ws.ontimeout = function() {
    //     alert('Hết thời gian chờ phản hồi từ máy chủ.');
    //     reset();
    // }

    // Start contest
    const countdownInterval = undefined;
    const timerTxt = document.getElementById('timer-txt');
    function startContest(countdown) {
        registerSection.hidden = true;
        contestSection.hidden = false;
        statisticSection.hidden = true;
        let timer = countdown;
        let minutes, seconds;
        countdownInterval = setInterval(() => {
            minutes = Math.floor(timer / 60);
            seconds = timer % 60;
            timerTxt.textContent = `${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            if (--timer < 0) endContest();
        }, 1000);
    }

    // End contest
    let contestEnded = false;
    function endContest() {
        if (contestEnded) return;
        contestEnded = true;
        clearInterval(countdownInterval);
        localStorage.clear();
        alert("Phiên thi đã kết thúc.");
        registerSection.hidden = true;
        contestSection.hidden = true;
        statisticSection.hidden = false;
    }

    const exitBtn = document.getElementById('exit-btn');
    exitBtn.addEventListener('click', function() {
        confirm('Bạn có chắc chắn muốn đầu hàng?') ? reset() : null;
    });

    // Reset all data
    function reset() {
        localStorage.clear();
        window.location.reload();
    }
});