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
const contestantName = document.getElementById('contestant-name');
const resigterForm = document.getElementById('register-form');
const registerBtn = document.getElementById('register-btn');
resigterForm.addEventListener('submit', function(event) {
    event.preventDefault();
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "../api/add", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.timeout = 10000;
    xhr.onload = function() {
        registerBtn.disabled = false;
        registerBtn.innerHTML = "Tham gia";
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
        localStorage.setItem("UserId", userId);
        localStorage.setItem("Authorization", token);
        contestantName.textContent = resigterForm.name;
        resigterForm.hidden = true;
        document.getElementById("waiting").hidden = false;
    };
    xhr.onerror = function() {
        alert("Đã xảy ra lỗi");
        registerBtn.disabled = false;
        registerBtn.innerHTML = "Tham gia";
    };
    xhr.ontimeout = function() {
        alert("Yêu cầu thất bại: Hết thời gian chờ phản hồi từ máy chủ");
        registerBtn.disabled = false;
        registerBtn.innerHTML = "Tham gia";
    }
    let data = {
        name: resigterForm.name.value,
        color: document.documentElement.style.getPropertyValue('--theme-color'),
    }
    registerBtn.disabled = true;
    registerBtn.innerHTML = 'Vui lòng chờ...';
    xhr.send(JSON.stringify(data));
});

// Workspace navigation handler
const workspaces = [
    document.getElementById('problem'),
    document.getElementById('submission'),
    document.getElementById('ranking')
];
const workspacesButtons = [
    document.getElementById('problem-btn'),
    document.getElementById('submission-btn'),
    document.getElementById('ranking-btn')
];

function toggleSection(window, button) {
    workspaces.forEach(workspace => {
        workspace.hidden = true;
    });
    workspacesButtons.forEach(btn => {
        btn.classList.remove('selected');
    });
    window.hidden = false;
    button.classList.add('selected');
}

for (let i = 0; i < workspaces.length; i++) {
    workspacesButtons[i].addEventListener('click', function() {
        toggleSection(workspaces[i], workspacesButtons[i]);
    });
}

// Problem selector 
const problemSelector = document.getElementById('problem-selector');
const submitProblemSelector = document.getElementById('submit-problem-selector');
function addProblem(name) {
    let option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    problemSelector.appendChild(option);
    let option2 = document.createElement('option');
    option2.value = name;
    option2.textContent = name;
    submitProblemSelector.appendChild(option2);
}

const problemDisplay = document.getElementById('problem-display');
problemSelector.addEventListener('change', function() {
    let problem = problemSelector.value;
    if (problem == "") problemDisplay.src = "about:blank";
    else problemDisplay.src = "../api/content/" + problem + ".pdf";
});

// Language selector
const submitLanguageSelector = document.getElementById('submit-language-selector');
function addLanguage(name) {
    let option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    submitLanguageSelector.appendChild(option);
}

// Websocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws`);
ws.timeout = 10000;
ws.onmessage = function(event) {
    let data = JSON.parse(event.data);
    switch (data.event) {
        case "CONTEST_STARTED":
            startContest(data.duration);
            data.problems.forEach(addProblem);
            data.supported_languages.forEach(addLanguage);
            break;
        case "CONTEST_STOPPED":
            endContest();
            break;
        case "CONTEST_RESET":
            reset();
            break;
    }
}
ws.onclose = function() {
    alert('Mất kết nối tới máy chủ.');
    reset();
};
ws.onerror = function() {
    alert('Đã xảy ra lỗi khi kết nối tới máy chủ.');
    reset();
};
ws.ontimeout = function() {
    alert('Hết thời gian chờ phản hồi từ máy chủ.');
    reset();
}

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
    confirm('Bạn có chắc chắn muốn kết thúc lượt thi của mình?') ? reset() : null;
});

// Reset all data
function reset() {
    localStorage.clear();
    window.location.reload();
}

// Submission handler
// TODO
const submitForm = document.getElementById("submit-form");
const submitBtn = document.querySelector("#submit-form button");
submitForm.addEventListener('submit', function(event) {
    event.preventDefault();
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "../api/submit", true);
    xhr.timeout = 10000;
    xhr.onload = function() {
        submitBtn.disabled = false;
        submitBtn.innerHTML = "Nộp bài";
        if (xhr.status !== 200) {
            alert(`Yêu cầu thất bại (${xhr.status}): ${xhr.responseText}`);
            return;
        }
    };
    xhr.onerror = function() {
        alert("Đã xảy ra lỗi");
        submitBtn.disabled = false;
        submitBtn.innerHTML = "Nộp bài";
    };
    xhr.ontimeout = function() {
        alert("Yêu cầu thất bại: Hết thời gian chờ phản hồi từ máy chủ");
        submitBtn.disabled = false;
        submitBtn.innerHTML = "Nộp bài";
    }
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Vui lòng chờ...';
    xhr.send(new FormData(submitForm));
});


// Restore session
