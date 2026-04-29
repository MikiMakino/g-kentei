'use strict';

let questions = [];
let pool = [];
let cur = 0;
let score = 0;
let done = false;

async function init() {
  try {
    const res = await fetch('questions.json');
    questions = await res.json();

    if (questions.length === 0) {
      showError('generate_questions.py を実行して問題を生成してください。');
      return;
    }

    const cats = [...new Set(questions.map(q => q.category))];
    const sel = document.getElementById('cat-sel');
    cats.forEach(c => {
      const o = document.createElement('option');
      o.value = c; o.textContent = c;
      sel.appendChild(o);
    });

    sel.addEventListener('change', updateCount);
    updateCount();

    document.getElementById('start-btn').addEventListener('click', startQuiz);
    document.getElementById('retry-btn').addEventListener('click', () => show('start-screen'));
  } catch {
    showError('問題データの読み込みに失敗しました。\ngenerate_questions.py を実行してください。');
  }
}

function updateCount() {
  const cat = document.getElementById('cat-sel').value;
  const n = cat === 'all' ? questions.length : questions.filter(q => q.category === cat).length;
  document.getElementById('q-count').textContent = `${n}問`;
}

function startQuiz() {
  const cat = document.getElementById('cat-sel').value;
  const src = cat === 'all' ? questions : questions.filter(q => q.category === cat);
  pool = shuffle([...src]);
  cur = 0; score = 0; done = false;
  show('quiz-screen');
  render();
}

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function render() {
  done = false;
  const q = pool[cur];

  document.getElementById('prog-fill').style.width = `${(cur / pool.length) * 100}%`;
  document.getElementById('cat-badge').textContent = q.category;
  document.getElementById('q-num').textContent = `${cur + 1} / ${pool.length}`;
  document.getElementById('q-text').textContent = q.question;

  const container = document.getElementById('opts');
  container.innerHTML = '';

  q.options.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className = 'opt';
    btn.innerHTML = `<span class="opt-lbl">${'ABCD'[i]}</span><span>${opt}</span>`;
    btn.addEventListener('click', () => pick(i));
    container.appendChild(btn);
  });
}

function pick(idx) {
  if (done) return;
  done = true;

  const q = pool[cur];
  const correct = idx === q.answer;
  if (correct) score++;

  document.querySelectorAll('.opt').forEach((btn, i) => {
    btn.disabled = true;
    if (i === q.answer) btn.classList.add('correct');
    else if (i === idx) btn.classList.add('wrong');
  });

  const exp = document.createElement('div');
  exp.className = `exp ${correct ? 'ok' : 'ng'}`;
  exp.innerHTML = `
    <div class="exp-head">${correct ? '○ 正解！' : '× 不正解'}</div>
    <p class="exp-body">${q.explanation}</p>
    <button class="btn btn-primary" id="next-btn">
      ${cur + 1 < pool.length ? '次の問題 →' : '結果を見る'}
    </button>
  `;
  document.getElementById('opts').appendChild(exp);
  document.getElementById('next-btn').addEventListener('click', next);
}

function next() {
  cur++;
  if (cur < pool.length) render();
  else result();
}

function result() {
  const pct = Math.round((score / pool.length) * 100);
  document.getElementById('score-area').innerHTML = `
    <div class="score-ring">
      <span class="score-pct">${pct}%</span>
      <span class="score-detail">${score} / ${pool.length}問 正解</span>
    </div>
  `;
  const msg = pct >= 80 ? '合格ライン到達！この調子で！'
            : pct >= 60 ? 'もう少し！苦手な章を復習しよう'
            : 'ノートを読み返してから再チャレンジ！';
  document.getElementById('result-msg').textContent = msg;
  show('result-screen');
}

function show(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function showError(msg) {
  document.querySelector('#start-screen .card').innerHTML =
    `<p style="color:#f44336;text-align:center;line-height:1.8;padding:20px 0">${msg.replace(/\n/g,'<br>')}</p>`;
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('./sw.js').catch(() => {}));
}

init();
