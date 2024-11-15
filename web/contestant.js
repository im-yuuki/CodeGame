document.addEventListener("DOMContentLoaded", function() {
    const registerSection = document.getElementById("register");
    const contestSection = document.getElementById("contest");
    const statisticSection = document.getElementById("statistic");
    const registerForm = document.getElementById("register-form");
    const finalScore = document.getElementById("final-score");
    const contestantName = document.getElementById("contestant-name");
    const submitProblemSelector = document.getElementById("submit-problem-selector");
    const submitLanguageSelector = document.getElementById("submit-language-selector");
    const problemSelector = document.getElementById("problem-selector");
    const submissionList = document.getElementById("submission-list");
    const registerBtn = document.getElementById("register-btn");
    const problemDisplay = document.getElementById("problem-display");
    const submitForm = document.getElementById("submit-form");
    const timerTxt = document.getElementById("timer-txt");
    const exitBtn = document.getElementById("exit-btn");
    const rankingList = document.getElementById("ranking-list");
    const rankingSample = document.getElementById("ranking-sample");

    const submitBtn = document.querySelector("#submit-form button");
    const userCardResult = document.querySelector("#user-card .result");

    const themeSelectors = document.querySelectorAll(".theme-selector");

    function getColor(status) {
        switch (status) {
            case "ACCEPTED": return "green";
            case "WRONG_ANSWER": return "red";
            case "TIME_LIMIT_EXCEEDED": return "orange";
            case "MEMORY_LIMIT_EXCEEDED": return "orange";
            case "RUNTIME_ERROR": return "purple";
            case "COMPILATION_ERROR": return "purple";
            default: return "black";
        }
    }

    function getShortenedStatus(status) {
        switch (status) {
            case "ACCEPTED": return "AC";
            case "WRONG_ANSWER": return "WA";
            case "TIME_LIMIT_EXCEEDED": return "TLE";
            case "MEMORY_LIMIT_EXCEEDED": return "MLE";
            case "RUNTIME_ERROR": return "RE";
            case "COMPILATION_ERROR": return "CE";
            case "INTERNAL_ERROR": return "IE";
            default: return "-";
        }
    }

    function setName(name) {
        contestantName.innerText = name;
    }

    function getToken() {
        let _localStorageItem = localStorage.getItem("Authorization");
        if (_localStorageItem === null) return "";
        return _localStorageItem;
    }

    function updateSubmission(id, problem, lang, result, time) {
        // Query for existing submission
        let item = submissionList.querySelector(`[data-id="${id}"]`);
        let _new = false;
        if (item === null) {
            _new = true;
            item = document.getElementById("submission-sample").cloneNode(true);
            item.setAttribute("data-id", id);
            item.classList.remove("hidden");
        }
        item.querySelector(".color-indicator").style.backgroundColor = getColor(result);
        item.querySelector(".description h3").innerText = problem;
        item.querySelector(".description span").innerText = lang;
        let resultField = item.querySelector(".result .status")
        resultField.innerText = result;
        resultField.style.color = getColor(result);
        let min = Math.floor(time / 60);
        let sec = time % 60;
        item.querySelector(".result .time").innerText = (min > 0 ? min + "m" : "") + sec + "s";
        if (_new) {
            submissionList.appendChild(item);
            submissionList.scrollTop = submissionList.scrollHeight;
        }
    }
    
    // Manage contestant cards in top bar and ranking list
    let userId = "";

    function deployContestantList(contestantList, problemList) {
        contestantList.forEach(contestant => {
            let item = rankingSample.cloneNode(true);
            item.classList.remove("hidden");

            item.setAttribute("data-id", contestant.uid);
            item.querySelector(".color-indicator").style.backgroundColor = contestant.color;
            item.querySelector(".description h3").innerText = contestant.name;
            let resultDiv = item.querySelector(".result");
            let scoreDiv = item.querySelector(".result div:last-child")
            // Score
            scoreDiv.querySelector("h3").innerText = contestant.score;
            // Progress
            let sample = item.querySelector(".result .hidden");
            problemList.forEach(problem => {
                let clone = sample.cloneNode(true);
                clone.setAttribute("data-id", problem);
                clone.classList.remove("hidden");
                clone.querySelector("h4").innerText = problem;
                let status = clone.querySelector("span");
                status.innerText = getShortenedStatus(contestant.progress.problem);
                status.style.color = getColor(contestant.progress.problem);
                resultDiv.insertBefore(clone, scoreDiv);
            });
            rankingList.appendChild(item);
            if (contestant.uid === userId) {
                resultDiv.childNodes.forEach(node => {
                    if (node.classList) if (node.classList.contains("hidden")) return;
                    userCardResult.appendChild(node.cloneNode(true));
                });
            }
        });
    }

    function updateContestantScore(id, score, finished) {
        let item = rankingList.querySelector(`div[data-id="${id}"]`);
        if (item === null) return;
        item.querySelector(".result div h3").innerText = score;
        if (finished) item.querySelector(".description span").hidden = false;
        if (id === userId) {
            document.querySelector("#user-card .result div h3").innerText = score;
            finalScore.innerText = score;
        }
        sortRankingList();
    }

    function updateContestantProgress(id, problem, status) {
        let item = rankingList.querySelector(`div[data-id="${id}"]`);
        if (item === null) return;
        let problemDiv = item.querySelector(`div[data-id="${problem}"]`);
        if (problemDiv === null) return;
        let statusField = problemDiv.querySelector("span");
        if (statusField.innerText !== "AC") {
            statusField.innerText = getShortenedStatus(status);
            statusField.style.color = getColor(status);
        }
        if (id === userId) {
            let userProblemDiv = document.querySelector(`#user-card .result div[data-id="${problem}"]`);
            let span = userProblemDiv.querySelector("span");
            if (span.innerText === "AC") return;
            span.innerText = getShortenedStatus(status);
            span.style.color = getColor(status);
        }
    }

    function sortRankingList() {
        let items = Array.from(rankingList.children);

        // Sort items based on the score
        items.sort((a, b) => {
            let scoreA = parseInt(a.querySelector(".result div h3").innerText);
            let scoreB = parseInt(b.querySelector(".result div h3").innerText);
            return scoreB - scoreA;
        });

        // Replace items only if their position has changed
        items.forEach((item, index) => {
            if (rankingList.children[index] !== item) {
                rankingList.insertBefore(item, rankingList.children[index]);
            }
        });
    }


    // Prevent right-click
    document.addEventListener("contextmenu", function(event) {
        event.preventDefault();
    });

    // Prevent text selection
    document.addEventListener("selectstart", function(event) {
        event.preventDefault();
    });

    // Prevent image dragging
    document.querySelectorAll("img").forEach(function(img) {
        img.addEventListener("dragstart", function(event) {
            event.preventDefault();
        });
    });

    // Theme selector
    themeSelectors.forEach(selector => {
        let color = getComputedStyle(selector).backgroundColor;
        selector.addEventListener("click", function () {
            document.documentElement.style.setProperty("--theme-color", color);
            themeSelectors.forEach(s => s.classList.remove("selected"));
            selector.classList.add("selected");
        });
    });

    // Register handler
    registerForm.addEventListener("submit", function(event) {
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
            if (resp.uid === undefined || resp.name === undefined || resp.token === undefined) {
                alert("Invalid response from server");
                return;
            }
            localStorage.setItem("Authorization", resp.token);
            userId = resp.uid;
            setName(resp.name);
            registerForm.hidden = true;
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
        let color = document.documentElement.style.getPropertyValue("--theme-color");
        if (color === "") color = "rgb(50, 136, 189)";
        let data = {
            name: registerForm.name.value,
            color: color,
        }
        registerBtn.disabled = true;
        registerBtn.innerHTML = "Vui lòng chờ...";
        xhr.send(JSON.stringify(data));
    });

    // Workspace navigation handler
    const workspaces = [
        document.getElementById("problem"),
        document.getElementById("submission"),
        document.getElementById("ranking")
    ];
    const workspacesButtons = [
        document.getElementById("problem-btn"),
        document.getElementById("submission-btn"),
        document.getElementById("ranking-btn")
    ];

    function toggleSection(window, button) {
        workspaces.forEach(workspace => {
            workspace.hidden = true;
        });
        workspacesButtons.forEach(btn => {
            btn.classList.remove("selected");
        });
        window.hidden = false;
        button.classList.add("selected");
    }

    for (let i = 0; i < workspaces.length; i++) {
        workspacesButtons[i].addEventListener("click", function() {
            toggleSection(workspaces[i], workspacesButtons[i]);
        });
    }

    // Problem selectors
    function addProblem(name) {
        let option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        problemSelector.appendChild(option);
        let option2 = document.createElement("option");
        option2.value = name;
        option2.textContent = name;
        submitProblemSelector.appendChild(option2);
    }

    problemSelector.addEventListener("change", function() {
        let problem = problemSelector.value;
        if (problem === "") problemDisplay.src = "about:blank";
        else problemDisplay.src = "../api/content/" + problem + ".pdf";
    });

    // Language selector
    function addLanguage(name) {
        let option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        submitLanguageSelector.appendChild(option);
    }

    // Websocket connection
    const ws = new WebSocket("../ws");
    ws.timeout = 10000;
    ws.onmessage = function(event) {
        let data = JSON.parse(event.data);
        switch (data.event) {
            case "CONTEST_STARTED":
                if (userId === "") {
                    alert("Phiên thi đã bắt đầu, bạn vui lòng đợi phiên thi tiếp theo.");
                    registerSection.hidden = true;
                    contestSection.hidden = true;
                    statisticSection.hidden = false;
                    return;
                }
                data.problems.forEach(addProblem);
                data.supported_languages.forEach(addLanguage);
                deployContestantList(data.contestants, data.problems);
                startContest(data.duration);
                break;
            case "CONTEST_STOPPED":
                if (userId === "") return;
                endContest();
                break;
            case "CONTEST_RESET":
                reset();
                break;
            case "CONTESTANT_FINISHED":
                updateContestantScore(data.uid, data.score, true);
                if (data.uid === userId) endContest();
                break;
            case "SUBMISSION_RESULT":
                if (data.contestant === userId) updateSubmission(data.id, data.problem, data.language, data.status, data.time);
                updateContestantProgress(data.contestant, data.problem, data.status);
                updateContestantScore(data.contestant, data.score, false);
                break;
        }
    }
    ws.onclose = function() {
        alert("Mất kết nối tới máy chủ.");
        reset();
    };
    ws.onerror = function() {
        alert("Đã xảy ra lỗi khi kết nối tới máy chủ.");
        reset();
    };
    ws.ontimeout = function() {
        alert("Hết thời gian chờ phản hồi từ máy chủ.");
        reset();
    }

    // Start contest
    let countdownInterval = undefined;
    function startContest(countdown) {
        registerSection.hidden = true;
        contestSection.hidden = false;
        statisticSection.hidden = true;
        let end = Math.floor(Date.now() / 1000) + countdown;
        let timer, minutes, seconds;
        countdownInterval = setInterval(() => {
            timer = end - Math.floor(Date.now() / 1000);
            minutes = Math.floor(timer / 60);
            seconds = timer % 60;
            timerTxt.textContent = `${minutes < 10 ? "0" : ""}${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
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

    // Exit button
    function markFinished() {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "../api/finish", true);
        xhr.setRequestHeader("Authorization", getToken());
        xhr.timeout = 10000;
        xhr.onload = function() {
            if (xhr.status !== 200) {
                alert(`Yêu cầu thất bại (${xhr.status}): ${xhr.responseText}`);
                return;
            }
            endContest();
        };
        xhr.onerror = function() {
            alert("Đã xảy ra lỗi");
        };
        xhr.ontimeout = function() {
            alert("Yêu cầu thất bại: Hết thời gian chờ phản hồi từ máy chủ");
        }
        xhr.send();
    }

    exitBtn.addEventListener("click", function() {
        confirm("Bạn có chắc chắn muốn kết thúc lượt thi của mình?") ? markFinished() : null;
    });

    // Reset all data
    function reset() {
        window.location.reload();
    }

    // Submission handler
    submitForm.addEventListener("submit", function(event) {
        event.preventDefault();
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "../api/submit", true);
        xhr.timeout = 10000;
        xhr.setRequestHeader("Authorization", getToken());
        xhr.onload = function() {
            submitBtn.disabled = false;
            submitBtn.innerHTML = "Nộp bài";
            if (xhr.status !== 200) {
                alert(`Yêu cầu thất bại (${xhr.status}): ${xhr.responseText}`);
            }
            let data = JSON.parse(xhr.responseText);
            if (data.id === undefined || data.problem === undefined || data.language === undefined || data.result === undefined || data.time === undefined) {
                alert("Phản hồi từ máy chủ không hợp lệ");
                return;
            }
            updateSubmission(data.id, data.problem, data.language, data.result, data.time);
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
        submitBtn.innerHTML = "Vui lòng chờ...";
        xhr.send(new FormData(submitForm));
    });

    // Restore session
    function startNormal() {
        registerSection.hidden = false;
        localStorage.clear()
    }

    if (getToken() !== "") {
        let xhr = new XMLHttpRequest();
        xhr.open("GET", "../api/restore", true);
        xhr.setRequestHeader("Authorization", getToken());
        xhr.timeout = 10000;
        xhr.onload = function() {
            if (xhr.status !== 200) {
                startNormal();
                return;
            }
            let data = JSON.parse(xhr.responseText);
            if (data.uid === undefined || data.name === undefined) {
                alert("Phản hồi từ máy chủ không hợp lệ");
                return;
            }
            userId = data.uid;
            setName(data.name)
            if (data.color !== undefined) {
                document.documentElement.style.setProperty("--theme-color", data.color);
            }
            if (data.contestants !== undefined) {
                data.contestants.forEach(contestant => {
                    if (contestant.progress === undefined) contestant.progress = {};
                    if (contestant.score === undefined) contestant.score = 0;
                });
            }
            else data.contestants = [];
            switch (data.contest_progress) {
                case "NOT_STARTED":
                    registerSection.hidden = false;
                    registerForm.hidden = true;
                    document.getElementById("waiting").hidden = false;
                    break;
                case "IN_PROGRESS":
                    data.contest.problems.forEach(addProblem);
                    data.contest.supported_languages.forEach(addLanguage);
                    deployContestantList(data.contestants, data.contest.problems);
                    data.submissions.forEach(submission => {
                        updateSubmission(submission.id, submission.problem, submission.language, submission.result, submission.time);
                    })
                    data.contestants.forEach(contestant => {
                        for (const key in contestant.progress) {
                            updateContestantProgress(contestant.uid, key, contestant.progress[key]);
                        }
                        updateContestantScore(contestant.uid, contestant.score, contestant.finished > 0);
                    });
                    startContest(data.contest.duration - data.contest.elapsed)
                    break;
                case "FINISHED":
                    deployContestantList([])
                    endContest();
                    break;
            }
        }
        xhr.onerror = function() {
            startNormal();
        };
        xhr.ontimeout = function() {
            alert("Yêu cầu thất bại: Hết thời gian chờ phản hồi từ máy chủ");
            reset();
        }
        xhr.send();
    }
    else startNormal();
});