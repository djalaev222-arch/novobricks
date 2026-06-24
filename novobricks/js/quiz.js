'use strict';

const QUIZ_DATA = {
  brick: {
    title: 'Подбор кирпича',
    questions: [
      {
        text: 'Для чего вам нужен кирпич?',
        options: [
          'Строительство дома / коттеджа',
          'Облицовка фасада',
          'Забор / ограждение',
          'Ландшафтные работы (мангал, дорожки)',
        ],
      },
      {
        text: 'Какой тип кирпича вас интересует?',
        options: [
          'Керамический (обожжённая глина)',
          'Клинкерный (высокая прочность)',
          'Облицовочный / декоративный',
          'Помогите мне выбрать',
        ],
      },
      {
        text: 'Предпочтительный цвет кирпича?',
        options: [
          'Классический красный',
          'Коричневый / шоколадный',
          'Белый / светлый',
          'Песочный / бежевый',
        ],
      },
      {
        text: 'Фактура поверхности?',
        options: [
          'Гладкая',
          'Рельефная / рустик',
          'Состаренная / антик',
          'Колотая / скол',
        ],
      },
      {
        text: 'Формат кирпича?',
        options: [
          'Стандартный (250 × 120 × 65 мм)',
          'Полуторный (250 × 120 × 88 мм)',
          'Евроформат (250 × 85 × 65 мм)',
          'Нестандартный — уточним при звонке',
        ],
      },
      {
        text: 'Примерное количество?',
        options: [
          'До 1 000 штук',
          '1 000 — 5 000 штук',
          '5 000 — 20 000 штук',
          'Более 20 000 штук',
        ],
      },
      {
        text: 'Желаемый срок получения?',
        options: [
          'Срочно (до 1 недели)',
          '1–2 недели',
          'В течение месяца',
          'Пока не определился',
        ],
      },
      {
        text: 'Планируемый бюджет (за 1 000 шт.)?',
        options: [
          'До 10 000 ₽',
          '10 000 — 20 000 ₽',
          '20 000 — 40 000 ₽',
          'Более 40 000 ₽',
        ],
      },
    ],
  },

  tile: {
    title: 'Подбор плитки',
    questions: [
      {
        text: 'Где будет укладываться плитка?',
        options: [
          'Пол в помещении',
          'Стена в помещении',
          'Фасад / наружная отделка',
          'Уличные площадки / дорожки',
        ],
      },
      {
        text: 'Тип помещения?',
        options: [
          'Ванная / санузел',
          'Кухня',
          'Гостиная / спальня',
          'Улица / терраса',
        ],
      },
      {
        text: 'Стиль интерьера?',
        options: [
          'Классика / прованс',
          'Лофт / индустриальный',
          'Минимализм / скандинавский',
          'Современный / хай-тек',
        ],
      },
      {
        text: 'Цветовая гамма?',
        options: [
          'Светлые нейтральные тона',
          'Тёмные насыщенные оттенки',
          'Тёплые (бежевый, терракот)',
          'Холодные (серый, синий)',
        ],
      },
      {
        text: 'Размер плитки?',
        options: [
          'Малый (до 30 × 30 см)',
          'Средний (30 × 60 — 60 × 60 см)',
          'Крупный (60 × 120 см и более)',
          'Мозаика',
        ],
      },
      {
        text: 'Поверхность плитки?',
        options: [
          'Матовая',
          'Глянцевая / полированная',
          'Рельефная / структурная',
          'Противоскользящая',
        ],
      },
      {
        text: 'Площадь укладки?',
        options: [
          'До 20 м²',
          '20 — 50 м²',
          '50 — 100 м²',
          'Более 100 м²',
        ],
      },
      {
        text: 'Когда планируете покупку?',
        options: [
          'Срочно (эта неделя)',
          'В течение месяца',
          'Через 2–3 месяца',
          'Пока изучаю варианты',
        ],
      },
    ],
  },
};

// Detect quiz type from body data attribute
const quizType  = document.body.dataset.quiz;
const quizData  = QUIZ_DATA[quizType];

if (!quizData) {
  console.error('Unknown quiz type:', quizType);
}

// State
let currentStep = 0;
const answers   = new Array(quizData ? quizData.questions.length : 0).fill(null);

// Elements
const quizIntro    = document.getElementById('quizIntro');
const quizBody     = document.getElementById('quizBody');
const quizForm     = document.getElementById('quizForm');
const quizSuccess  = document.getElementById('quizSuccess');
const quizQuestion = document.getElementById('quizQuestion');
const progressFill = document.getElementById('progressFill');
const progressLabel= document.getElementById('progressLabel');
const prevBtn      = document.getElementById('prevBtn');
const nextBtn      = document.getElementById('nextBtn');
const startBtn     = document.getElementById('startQuiz');
const leadForm     = document.getElementById('leadForm');

function show(el) { el && el.classList.remove('hidden'); }
function hide(el) { el && el.classList.add('hidden'); }

function renderQuestion() {
  const total    = quizData.questions.length;
  const question = quizData.questions[currentStep];
  const pct      = ((currentStep + 1) / total) * 100;

  progressFill.style.width  = pct + '%';
  progressLabel.textContent = `Вопрос ${currentStep + 1} из ${total}`;

  quizQuestion.innerHTML = `
    <h2 class="quiz-question__title">${question.text}</h2>
    <div class="quiz-options">
      ${question.options.map((opt, i) => `
        <button
          class="quiz-option${answers[currentStep] === i ? ' selected' : ''}"
          data-index="${i}"
          type="button"
          aria-pressed="${answers[currentStep] === i}"
        >
          <div class="quiz-option__radio"></div>
          <span class="quiz-option__text">${opt}</span>
        </button>
      `).join('')}
    </div>
  `;

  quizQuestion.querySelectorAll('.quiz-option').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.dataset.index, 10);
      answers[currentStep] = idx;
      quizQuestion.querySelectorAll('.quiz-option').forEach(b => {
        b.classList.toggle('selected', parseInt(b.dataset.index, 10) === idx);
        b.setAttribute('aria-pressed', String(parseInt(b.dataset.index, 10) === idx));
      });
      nextBtn.removeAttribute('disabled');
    });
  });

  // Prev button visibility
  prevBtn.style.visibility = currentStep === 0 ? 'hidden' : 'visible';

  // Next button label
  nextBtn.textContent = currentStep === total - 1 ? 'Готово →' : 'Далее →';

  // Disable next if no answer selected
  if (answers[currentStep] === null) {
    nextBtn.setAttribute('disabled', 'true');
  } else {
    nextBtn.removeAttribute('disabled');
  }
}

// START QUIZ
if (startBtn) {
  startBtn.addEventListener('click', () => {
    hide(quizIntro);
    show(quizBody);
    renderQuestion();
  });
}

// PREV
if (prevBtn) {
  prevBtn.addEventListener('click', () => {
    if (currentStep > 0) {
      currentStep--;
      renderQuestion();
    }
  });
}

// NEXT
if (nextBtn) {
  nextBtn.addEventListener('click', () => {
    if (answers[currentStep] === null) return;
    const total = quizData.questions.length;
    if (currentStep < total - 1) {
      currentStep++;
      renderQuestion();
    } else {
      // Show lead form
      hide(quizBody);
      show(quizForm);
    }
  });
}

// LEAD FORM SUBMIT
if (leadForm) {
  leadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = leadForm.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Отправляем…';
    submitBtn.disabled = true;

    const formData = new FormData(leadForm);
    const payload  = {
      quizType,
      answers: quizData.questions.map((q, i) => ({
        question: q.text,
        answer:   answers[i] !== null ? q.options[answers[i]] : null,
      })),
      name:    formData.get('name'),
      phone:   formData.get('phone'),
      email:   formData.get('email') || '',
      comment: formData.get('comment') || '',
    };

    try {
      await fetch('/.netlify/functions/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: `${quizType}_quiz`, ...payload }),
      });
    } catch {}

    hide(quizForm);
    show(quizSuccess);
  });
}
