// EcoQuest - small amount of vanilla JavaScript

// Mobile navigation toggle
(function () {
  var btn = document.getElementById("navToggle");
  var nav = document.getElementById("navLinks");
  if (!btn || !nav) return;
  btn.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();

// Animate progress bars from 0 to their value
document.querySelectorAll(".bar > span[data-width]").forEach(function (el) {
  requestAnimationFrame(function () { el.style.width = el.dataset.width + "%"; });
});

// Confirm before destructive actions: <form data-confirm="Are you sure?">
document.querySelectorAll("form[data-confirm]").forEach(function (form) {
  form.addEventListener("submit", function (e) {
    if (!window.confirm(form.dataset.confirm)) e.preventDefault();
  });
});

// Quiz: show one question at a time with question navigation
(function () {
  var form = document.getElementById("quizForm");
  if (!form) return;
  var questions = form.querySelectorAll(".quiz-q");
  var navButtons = document.querySelectorAll(".qnav button");
  var prev = document.getElementById("prevBtn");
  var next = document.getElementById("nextBtn");
  var submit = document.getElementById("submitBtn");
  var counter = document.getElementById("qCounter");
  var current = 0;

  function show(i) {
    current = i;
    questions.forEach(function (q, idx) { q.classList.toggle("active", idx === i); });
    navButtons.forEach(function (b, idx) { b.classList.toggle("current", idx === i); });
    prev.disabled = i === 0;
    next.style.display = i === questions.length - 1 ? "none" : "inline-flex";
    submit.style.display = i === questions.length - 1 ? "inline-flex" : "none";
    counter.textContent = "Question " + (i + 1) + "/" + questions.length;
  }
  function markAnswered() {
    questions.forEach(function (q, idx) {
      var answered = q.querySelector("input:checked") !== null;
      navButtons[idx].classList.toggle("answered", answered);
    });
  }
  // Instant feedback: the server checks the first choice for each question and locks it
  var combo = 0, correctCount = 0, answeredCount = 0;
  questions.forEach(function (q) {
    q.addEventListener("change", function (e) {
      var radio = e.target;
      if (!radio.matches("input[type=radio]") || q.dataset.locked) return;
      q.dataset.locked = "1";
      var data = new FormData();
      data.append("csrf_token", form.dataset.csrf); data.append("question_id", q.dataset.qid); data.append("option_id", radio.value);
      fetch(form.dataset.checkUrl, { method: "POST", body: data, credentials: "same-origin" })
        .then(function (r) { if (!r.ok) throw new Error("check failed"); return r.json(); })
        .then(function (res) {
          q.querySelectorAll("input[type=radio]").forEach(function (inp) {
            var lab = inp.closest(".option");
            if (String(res.correct_id) === inp.value) lab.classList.add("right");
            else if (inp.checked) lab.classList.add("wrong");
            if (inp.checked) {
              var hidden = document.createElement("input");
              hidden.type = "hidden"; hidden.name = inp.name; hidden.value = inp.value; form.appendChild(hidden);
            }
            inp.disabled = true;
          });
          answeredCount++;
          if (res.is_correct) { combo++; correctCount++; } else { combo = 0; }
          var fb = q.querySelector("[data-feedback]");
          fb.className = "feedback " + (res.is_correct ? "ok" : "bad");
          fb.textContent = (res.is_correct ? "✅ Correct! +10 XP" : "❌ Not quite.") + (res.explanation ? " " + res.explanation : "") +
            (res.is_correct && combo >= 3 ? "  🔥 Combo x" + combo + "!" : "");
          document.getElementById("quizCombo").textContent = combo;
          document.getElementById("quizCorrect").textContent = correctCount;
          document.getElementById("quizAnswered").textContent = answeredCount + "/" + questions.length;
        })
        .catch(function () { q.dataset.locked = ""; });
    });
  });
  prev.addEventListener("click", function () { if (current > 0) show(current - 1); });
  next.addEventListener("click", function () { if (current < questions.length - 1) show(current + 1); });
  navButtons.forEach(function (b, idx) { b.addEventListener("click", function () { show(idx); }); });
  form.addEventListener("change", markAnswered);
  form.addEventListener("submit", function (e) {
    var unanswered = Array.prototype.filter.call(questions, function (q) { return !q.querySelector("input:checked"); }).length;
    if (unanswered > 0 && !window.confirm(unanswered + " question(s) are unanswered. Submit anyway?")) e.preventDefault();
  });
  show(0);
})();

// Chart helper used by dashboards: drawChart(canvasId, type, labels, datasets, options)
function drawChart(id, type, labels, datasets, extra) {
  var canvas = document.getElementById(id);
  if (!canvas || typeof Chart === "undefined") return;
  var palette = ["#16a34a", "#0284c7", "#f59e0b", "#7c3aed", "#dc2626", "#0d9488"];
  datasets.forEach(function (d, i) {
    if (!d.backgroundColor) d.backgroundColor = type === "doughnut" ? palette : palette[i % palette.length];
  });
  new Chart(canvas, {
    type: type,
    data: { labels: labels, datasets: datasets },
    options: Object.assign({ responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: datasets.length > 1 || type === "doughnut" } } }, extra || {})
  });
}
