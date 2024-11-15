document.addEventListener('DOMContentLoaded', function() {
    const rankingList = document.getElementById("ranking");
    const rankingSample = document.getElementById("ranking-sample");
    const timerBox = document.getElementById("timer");
    const timerTxt = document.getElementById("timer-txt");

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

    // Websocket connection
    const ws = new WebSocket("../ws");
    ws.timeout = 10000;
    ws.onmessage = function(event) {
        let data = JSON.parse(event.data);
        switch (data.event) {
            case "NEW_CONTESTANT":
                addPreContestant(data.name, data.color);
                break;
            case "CONTEST_STARTED":
                deployContestantList(data.contestants, data.problems);
                startTimer(data.duration);
                break;
            case "CONTEST_STOPPED":
                endTimer();
                break;
            case "CONTEST_RESET":
                window.location.reload();
                break;
            case "CONTESTANT_FINISHED":
                updateContestantScore(data.uid, data.score, true);
                break;
            case "SUBMISSION_RESULT":
                updateContestantProgress(data.contestant, data.problem, data.status);
                updateContestantScore(data.contestant, data.score, false);
                break;
        }
    }
    ws.onclose = function() {
        alert("Kết nối tới máy chủ đã bị đóng.");
        window.location.reload();
    }

    let countdownInterval = undefined;
    function startTimer(countdown) {
        timerBox.classList.remove("disabled");
        let end = Math.floor(Date.now() / 1000) + countdown;
        let timer, minutes, seconds;
        countdownInterval = setInterval(() => {
            timer = end - Math.floor(Date.now() / 1000);
            minutes = Math.floor(timer / 60);
            seconds = timer % 60;
            timerTxt.textContent = `${minutes < 10 ? "0" : ""}${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
            if (--timer < 0) endTimer();
        }, 1000);
    }

    function endTimer() {
        clearInterval(countdownInterval);
    }

    function addPreContestant(name, color) {
        let item = rankingSample.cloneNode(true);
        item.classList.remove("hidden");
        item.querySelector(".color-indicator").style.backgroundColor = color;
        item.querySelector(".description h3").innerText = name;
        item.querySelector(".result div:last-child").innerText = "";
        rankingList.appendChild(item);
    }

    function deployContestantList(contestantList, problemList) {
        rankingList.innerHTML = "";
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
        });
    }

    function updateContestantScore(id, score, finished) {
        let item = rankingList.querySelector(`div[data-id="${id}"]`);
        if (item === null) return;
        item.querySelector(".result div h3").innerText = score;
        if (finished) item.querySelector(".description span").hidden = false;
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
});