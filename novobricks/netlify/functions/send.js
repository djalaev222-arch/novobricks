exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const CHAT_ID   = process.env.TELEGRAM_CHAT_ID;

  if (!BOT_TOKEN || !CHAT_ID) {
    return { statusCode: 500, body: 'Server configuration error' };
  }

  let data;
  try {
    data = JSON.parse(event.body);
  } catch {
    return { statusCode: 400, body: 'Invalid JSON' };
  }

  const { type, name, phone, email, comment, answers } = data;
  let text = '';

  if (type === 'modal') {
    text =
      `🔔 *Новая заявка — Заказать звонок*\n\n` +
      `👤 *Имя:* ${name || '—'}\n` +
      `📞 *Телефон:* ${phone || '—'}`;
    if (comment) text += `\n💬 *Комментарий:* ${comment}`;
  } else if (type === 'lead') {
    text =
      `🔔 *Новая заявка — Расчёт стоимости*\n\n` +
      `👤 *Имя:* ${name || '—'}\n` +
      `📞 *Телефон:* ${phone || '—'}`;
    if (email)   text += `\n📧 *Email:* ${email}`;
    if (comment) text += `\n💬 *Комментарий:* ${comment}`;
  } else if (type === 'brick_quiz' || type === 'tile_quiz') {
    const label = type === 'brick_quiz' ? 'Кирпич' : 'Плитка';
    text =
      `🔔 *Заявка из квиза — ${label}*\n\n` +
      `👤 *Имя:* ${name || '—'}\n` +
      `📞 *Телефон:* ${phone || '—'}`;
    if (email) text += `\n📧 *Email:* ${email}`;
    if (Array.isArray(answers) && answers.length) {
      text += `\n\n📝 *Ответы:*`;
      answers.forEach((a, i) => {
        if (a.answer) text += `\n${i + 1}. ${a.question}\n   → ${a.answer}`;
      });
    }
    if (comment) text += `\n\n💬 *Комментарий:* ${comment}`;
  } else {
    text = `🔔 *Новая заявка*\n\n👤 ${name || '—'}\n📞 ${phone || '—'}`;
  }

  try {
    const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'Markdown' }),
    });

    if (!res.ok) {
      const err = await res.text();
      console.error('Telegram error:', err);
      return { statusCode: 502, body: 'Telegram API error' };
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ok: true }),
    };
  } catch (err) {
    console.error('Fetch error:', err);
    return { statusCode: 500, body: 'Internal server error' };
  }
};
